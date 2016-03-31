ctrlModal.cache = {};

ctrlModal.bind = function (selector, context) {
    var view = rivets.bind(selector, context);
    selector.data('view', view);
};

ctrlModal.show = function (selector, settings) {
    selector
        .modal(settings)
        .modal('show');
};

ctrlModal.create = function (data, context, settings) {
    var html = $.parseHTML(data);
    var selector = $(html);
    selector.appendTo('body');

    ctrlModal.bind(selector, context);

    var cache = selector.attr('id') != undefined;
    if (!cache) {
        settings.onHidden = function () {
            // Unbind.
            var view = $(this).data('view');
            view.unbind();

            // Destroy.
            $(this).remove();
        };
    }

    ctrlModal.show(selector, settings);
};

ctrlModal.modal = function (name, force, context) {
    var id = '#modal-' + name;
    var selector = $(id);

    var settings = {
        closeable: !force,
        selector: {
            close: '.close, .actions .button'
        }
    };

    if (selector.length && selector.data('view')) {
        // Modal exists and is bound. Simply show.
        ctrlModal.show(selector, settings);
    }
    else if (selector.length) {
        // Modal exists in DOM but is not bound.
        ctrlModal.bind(selector, context);
        ctrlModal.show(selector, settings);
    }
    else if (this.cache.hasOwnProperty(name)) {
        // Modal exists in cache.
        var data = this.cache[name];
        ctrlModal.create(data, context, settings);
    }
    else {
        // Modal does not exist. Fetch modal from server.
        ctrlModal.fetch(name, function(data) {
            ctrlModal.create(data, context, settings);
        });
    }
};

ctrlModal.fetch = function (name, callback) {
    var file = 'modals/' + name + '.html';

    if (this.cache.hasOwnProperty(name)) {
        // Data exists in cache.
        var data = this.cache[name];
        if (callback) {
            callback(data);
        }
    }
    else {
        // Fetch from server and place in cache.
        $.get(file, function (data) {
            ctrlModal.cache[name] = data;
            if (callback) {
                callback(data);
            }
        });
    }
};

ctrlModal.preload = function (names) {
    for (var name in names) {
        if (names.hasOwnProperty(name)) {
            this.fetch(name);
        }
    }
};