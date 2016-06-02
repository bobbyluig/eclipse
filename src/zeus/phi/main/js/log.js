ctrlLog.log = function (logger, message, level) {
    var selector = this.getLogger(logger);
    var name = selector.data('name');
    var log = ctrlLog.loggers[name];

    var d = new Date();
    var time = d.toLocaleTimeString('en-US', {hour12: false});
    var event = {
        message: message,
        time: time,
        level: level
    };

    log.events.push(event);
    log.new += 1;

    if (log.scroll) {
        var display = selector.find('div.scrollable');
        display = $(display);
        display.scrollTop(display.prop('scrollHeight'));
    }


    var voice = settings.speech[name];
    ctrlSpeech.speak(voice, message);
    
};

ctrlLog.loggers = {};

ctrlLog.init = function (logger) {
    var selector = ctrlLog.getLogger(logger);

    var log = {};
    var name = selector.data('name');
    ctrlLog.loggers[name] = log;

    log.new = 0;
    log.events = [];
    log.scroll = true;
    log.changeScroll = function () {
        log.scroll = !log.scroll;
    };
    log.zero = function() {
        log.new = 0;
    };
    log.clear = function() {
        log.events = [];
        log.zero();
    };

    rivets.bind(selector, $.extend({log: log}, bindings));
    ctrlLog.log(selector, 'Logger initialized!', 1);
};

ctrlLog.getLogger = function (logger) {
    if ($.type(logger) === 'string') {
        var query = '.logger[data-name="' + logger + '"]';
        return $(query);
    }
    else {
        return logger;
    }
};