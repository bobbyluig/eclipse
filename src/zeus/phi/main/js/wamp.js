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
        ctrlRpc.subLogger('pack1');
        ctrlRpc.subLogger('pack2');
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

        ctrlLog.log('system', message, level);
    };

    this.connection.open();
};