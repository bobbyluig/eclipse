ctrlMenu.changeTeam = function () {
    var functions = {};
    var context = {run: functions};

    functions.teamRed = function () {
        settings.style.color = 1;
        settings.style.name = 'Eclipse Technologies';
    };
    functions.teamBlue = function () {
        settings.style.color = 2;
        settings.style.name = 'Paragon Industries';
    };

    ctrlModal.modal('team', false, context);
};

ctrlMenu.resetOne = function (category) {
    for (var property in settings[category]) {
        if (settings[category].hasOwnProperty(property) && defaults[category].hasOwnProperty(property)) {
            settings[category][property] = defaults[category][property];
        }
    }
};

ctrlMenu.comSettings = function () {
    var functions = {};
    var context = {run: functions, com: settings.com};

    functions.reset = function () {
        ctrlMenu.resetOne('com');
    };

    ctrlModal.modal('com', false, context);
};

ctrlMenu.speechSettings = function () {
    var functions = {};
    var context = {
        voices: ctrlSpeech.voices,
        speech: settings.speech,
        run: functions
    };

    functions.reset = function () {
        ctrlMenu.resetOne('speech');
    };

    ctrlModal.modal('speech', false, context);
};

ctrlMenu.saveSettings = function () {
    var data = JSON.stringify(settings);
    localStorage.setItem('settings', data);
};

ctrlMenu.resetSettings = function () {
    var functions = {};
    var strings = {
        header: 'Reset Confirmation',
        content: 'Are you sure you want to perform a reset? Doing so will clear all mission and configuration data.'
    };
    var context = {run: functions, data: strings};

    functions.yes = function () {
        ctrlMenu.softReset();
    };
    functions.no = function () {
    };

    ctrlModal.modal('choice', false, context);
};

ctrlMenu.softReset = function () {
    for (var category in settings) {
        if (settings.hasOwnProperty(category) && defaults.hasOwnProperty(category)) {
            for (var property in settings[category]) {
                if (settings[category].hasOwnProperty(property) && defaults[category].hasOwnProperty((property))) {
                    settings[category][property] = defaults[category][property];
                }
            }
        }
    }
};

ctrlMenu.hardReset = function() {
    settings = defaults;
};

ctrlMenu.loadSettings = function () {
    var data = localStorage.getItem('settings');

    if (data) {
        settings = JSON.parse(data);
    }
    else {
        this.hardReset();
    }
};
