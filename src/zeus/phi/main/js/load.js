ctrlLoad.loadTabs = function () {
    $('.tab').each(function () {
        var url = $(this).data('url');
        if (!url) {
            url = $(this).data('tab') + '.html';
        }

        $(this).load(url);
    });
};