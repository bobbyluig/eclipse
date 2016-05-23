ctrlLog.log = function (logger, message, level) {
    var selector = this.getLogger(logger);
    var log = selector.data('log');

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

    /*
    selector.find('.item.hidden').each(function () {
        $(this).transition('fade down');
    });
    */
};

ctrlLog.init = function (logger) {
    var selector = this.getLogger(logger);

    var log = {};
    selector.data('log', log);
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

    var view = rivets.bind(selector, {log: log, style: settings.style});
    selector.data('view', view);

    this.log(selector, 'Logger initialized!', 1);
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