ctrlLoad.loadTabs = function () {
    $('.tab').each(function () {
        var url = $(this).data('url');
        var name = $(this).data('tab');
        if (!url) {
            url = $(this).data('tab') + '.html';
        }

        $.get(url, function (data) {
            ctrlLoad.insertTab(name, data);
        });
    });
};

ctrlLoad.insertTab = function (name, html) {
    var query = '.tab[data-tab="' + name + '"]';
    var selector = $(query);

    var data = $.parseHTML(html);
    var tab = $(data);

    // Find all loggers and initialize.
    tab.find('.logger').each(function() {
        var logger = $(this);
        ctrlLog.init(logger);
    });

    // Initialize overall style.
    tab.find('.rv').each(function () {
        var rv = $(this);
        if (!rv.data('view')) {
            var view = rivets.bind(rv, {style: settings.style, wamp: ctrlWamp});
            rv.data('view', view);
        }
    });

    selector.append(tab);
};

// Status resets.
state.com = {
    state: 'closed'
};