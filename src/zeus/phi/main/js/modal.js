ctrlModal.bind = function (selector, context) {
    var view = rivets.bind(selector, context);
    selector.data('view', view);
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
        selector
            .modal(settings)
            .modal('show');
    }
    else if (selector.length) {
        // Modal exists but is not bound.
        ctrlModal.bind(selector, context);
        selector
            .modal(settings)
            .modal('show');
    }
    else {
        // Modal does not exist. Fetch modal from server.
        var file = 'modals/' + name + '.html';

        $.get(file, function (data) {
            var html = $.parseHTML(data);
            selector = $(html);
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

            selector
                .modal(settings)
                .modal('show');
        });
    }
};

ctrlModal.preload = function (names) {
    for (var name in names) {
        var file = 'modals/' + name + '.html';
        $.get(file, function (data) {
            $('body').append(data);
        });
    }
};