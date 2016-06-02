ctrlWamp.connect = function () {
    if (state.com.state != 'closed') {
        ctrlLog.log('system', 'Connection already exists.', 2);
        return;
    }
    else {
        state.com.state = 'connecting';
    }

    this.connection = new autobahn.Connection({
        url: settings.com.url,
        realm: settings.com.realm,
        max_retries: settings.com.max_retries,
        initial_retry_delay: settings.com.initial_retry_delay,
        max_retry_delay: settings.com.max_retry_delay,
        retry_delay_growth: settings.com.retry_delay_growth,

        authmethods: [settings.com.authmethod],
        authid: settings.com.authid,
        onchallenge: function (session, method, extra) {
            if (method == 'wampcra') {
                return autobahn.auth_cra.sign(settings.com.secret, extra.challenge);
            }
        }
    });

    this.connection.onopen = function (session) {
        wamp = session;

        state.com.state = 'open';
        ctrlLog.log('system', 'Connected!', 1);

        ctrlRpc.registerAll();
        ctrlWamp.subscribeAll();

        ctrlRpc.subLogger('pack1');
        ctrlRpc.subLogger('pack2');

        ctrlWamp.check();
    };

    this.connection.onclose = function (reason, details) {
        var message, level;

        if (details.will_retry) {
            message = 'Connection lost. Retrying.';
            level = 2;
            state.com.state = reason;
        }
        else {
            message = 'Connection lost.';
            level = 3;
            state.com.state = 'closed';
        }

        state.pack1.connected = false;
        state.pack2.connected = false;

        ctrlLog.log('system', message, level);
    };

    this.connection.open();
};

ctrlWamp.subscribeAll = function () {
    wamp.subscribe('wamp.session.on_join', function (data) {
        data = data[0];
        var session = data.session;
        var authid = data.authid;

        if (authid == 'DOG-1E5') {
            state.pack1.connected = true;
            state.pack1.session = session;

        }
        else if (authid == 'DOG-4S1') {
            state.pack2.connected = true;
            state.pack2.session = session;
        }
    });
    wamp.subscribe('wamp.session.on_leave', function (id) {
        id = id[0];

        if (state.pack1.session == id) {
            state.pack1.connected = false;
        }
        else if (state.pack2.session == id) {
            state.pack2.connected = false;
        }
    });
};

ctrlWamp.check = function () {
    wamp.call('wamp.session.list').then(
        function (res) {
            res.forEach(function (id) {
                wamp.call('wamp.session.get', [id]).then(
                    function (data) {
                        console.log(data.authid);
                        if (data.authid == 'DOG-1E5')
                            state.pack1.connected = true;
                        else if (data.authid == 'DOG-4S1')
                            state.pack2.connected = true;
                    }
                );
            });
        }
    );
};