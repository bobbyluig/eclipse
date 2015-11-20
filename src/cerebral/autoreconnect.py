import signal
from autobahn.wamp import protocol
from autobahn.wamp.types import ComponentConfig
from autobahn.websocket.protocol import parseWsUrl
from autobahn.asyncio.websocket import WampWebSocketClientFactory
import asyncio
import txaio
import logging

txaio.use_asyncio()
logger = logging.getLogger(__name__)


class ExceededRetryCount(Exception):
    pass


class IReconnectStrategy(object):
    def get_retry_interval(self):
        raise NotImplementedError('get_retry_interval')

    def reset_retry_interval(self):
        raise NotImplementedError('reset_retry_interval')

    def increase_retry_interval(self):
        raise NotImplementedError('increase_retry_interval')

    def retry(self):
        raise NotImplementedError('retry')


class BackoffStrategy(IReconnectStrategy):
    def __init__(self, initial_interval=2, max_interval=512, factor=1):
        self._initial_interval = initial_interval
        self._retry_interval = initial_interval
        self._max_interval = max_interval
        self._factor = factor

    def get_retry_interval(self):
        return self._retry_interval

    def reset_retry_interval(self):
        self._retry_interval = self._initial_interval

    def increase_retry_interval(self):
        self._retry_interval *= self._factor

    def retry(self):
        return self._retry_interval <= self._max_interval


class PersistentStrategy(IReconnectStrategy):
    def __init__(self, interval=3):
        self.interval = interval

    def get_retry_interval(self):
        return self.interval

    def reset_retry_interval(self):
        pass

    def increase_retry_interval(self):
        pass

    def retry(self):
        return True


class ApplicationRunner(object):
    """
    This class is a slightly modified version of autobahn.asyncio.wamp.ApplicationRunner
    with auto reconnection feature to with customizable strategies.
    """

    def __init__(self, url, realm, extra=None, serializers=None,
                 debug=False, debug_wamp=False, debug_app=False,
                 ssl=None, loop=None, retry_strategy=PersistentStrategy()):
        """
        :param url: The WebSocket URL of the WAMP router to connect to (e.g. `ws://somehost.com:8090/somepath`)
        :type url: unicode
        :param realm: The WAMP realm to join the application session to.
        :type realm: unicode
        :param extra: Optional extra configuration to forward to the application component.
        :type extra: dict
        :param serializers: A list of WAMP serializers to use (or None for default serializers).
           Serializers must implement :class:`autobahn.wamp.interfaces.ISerializer`.
        :type serializers: list
        :param debug: Turn on low-level debugging.
        :type debug: bool
        :param debug_wamp: Turn on WAMP-level debugging.
        :type debug_wamp: bool
        :param debug_app: Turn on app-level debugging.
        :type debug_app: bool
        :param ssl: An (optional) SSL context instance or a bool. See
           the documentation for the `loop.create_connection` asyncio
           method, to which this value is passed as the ``ssl=``
           kwarg.
        :type ssl: :class:`ssl.SSLContext` or bool
        """
        self.url = url
        self.realm = realm
        self.extra = extra or dict()
        self.debug = debug
        self.debug_wamp = debug_wamp
        self.debug_app = debug_app
        self.serializers = serializers
        self.loop = loop or asyncio.get_event_loop()
        self.retry_strategy = retry_strategy
        self.closing = False

        self.isSecure, self.host, self.port, _, _, _ = parseWsUrl(url)

        if ssl is None:
            self.ssl = self.isSecure
        else:
            if ssl and not self.isSecure:
                raise RuntimeError(
                    'ssl argument value passed to %s conflicts with the "ws:" '
                    'prefix of the url argument. Did you mean to use "wss:"?' %
                    self.__class__.__name__)
            self.ssl = ssl

    def run(self, make):
        """
        Run the application component.
        :param make: A factory that produces instances of :class:`autobahn.asyncio.wamp.ApplicationSession`
           when called with an instance of :class:`autobahn.wamp.types.ComponentConfig`.
        :type make: callable
        """

        def create():
            cfg = ComponentConfig(self.realm, self.extra)
            try:
                session = make(cfg)
            except Exception as e:
                # the app component could not be created .. fatal
                asyncio.get_event_loop().stop()
                raise e
            else:
                session.debug_app = self.debug_app
                return session

        self.transport_factory = WampWebSocketClientFactory(create, url=self.url, serializers=self.serializers,
                                                       debug=self.debug, debug_wamp=self.debug_wamp)

        txaio.use_asyncio()
        txaio.config.loop = self.loop

        asyncio.ensure_future(self.connect(), loop=self.loop)
        # self.loop.add_signal_handler(signal.SIGTERM, self.stop)

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            # wait until we send Goodbye if user hit ctrl-c
            # (done outside this except so SIGTERM gets the same handling)
            pass

        self.closing = True

        if self.active_protocol:
            self.loop.run_until_complete(self.active_protocol._session.leave())
        self.loop.close()

    async def connect(self):
        self.active_protocol = None
        self.retry_strategy.reset_retry_interval()
        while True:
            try:
                _, protocol = await self.loop.create_connection(self.transport_factory, self.host, self.port, ssl=self.ssl)
                protocol.is_closed.add_done_callback(self.reconnect)
                self.active_protocol = protocol
                return
            except OSError:
                # print('Connection failed')
                if self.retry_strategy.retry():
                    retry_interval = self.retry_strategy.get_retry_interval()
                    logger.debug('Retrying in %s seconds.' % retry_interval)
                    await asyncio.sleep(retry_interval)
                else:
                    logger.warning('Exceeded retry count. Stopping event loop.')
                    self.loop.stop()
                    raise ExceededRetryCount()

                self.retry_strategy.increase_retry_interval()

    def reconnect(self, f):
        if not self.closing:
            asyncio.ensure_future(self.connect(), loop=self.loop)

    def stop(self, *args):
        self.loop.stop()