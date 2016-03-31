ctrlWamp.connect = function () {
    state.com.state = 'connecting';

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
        console.log('Connected!');
    };

    this.connection.onclose = function (reason, details) {
        state.com.state = reason;
    };

    this.connection.open();
};