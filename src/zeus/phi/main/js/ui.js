var defaultStyle = {
    color: 0,
    name: 'EDD 2016',
    link: 'http://google.com'
};

ctrlMenu.teamSetting = function() {
    $('#team-modal')
        .modal({
            selector: {
                close: '.actions .button'
            }
        })
        .modal('show');
};

ctrlMenu.saveSettings = saveSettings;

ctrlMenu.reset = function() {
    // Need confirmation.
    resetSettings();
};

ctrlModal.teamRed = function () {
    settings.style.color = 1;
    settings.style.name = 'Eclipse Technologies';
};
ctrlModal.teamBlue = function() {
    settings.style.color = 2;
    settings.style.name = 'Paragon Industries';
};

function saveSettings() {
    var data = JSON.stringify(settings);
    localStorage.setItem('settings', data);
}

function resetSettings() {
    settings = {
        comm: jQuery.extend(true, {}, defaultComm),
        style: jQuery.extend(true, {}, defaultStyle)
    }
}

function loadSettings() {
    // Need to implement HTML5 storage.
    var data = localStorage.getItem('settings');

    if(data) {
        settings = JSON.parse(data);
    }
    else {
        resetSettings();
    }
}

function loadComponents() {
    $('.tab').each(function() {
        var url = $(this).data('url');
        if(!url) {
            url = $(this).data('tab') + '.html';
        }

        $(this).load(url);
    });
}