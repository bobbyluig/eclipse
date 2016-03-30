// Global variables.
var settings = {};

// Controllers.
var ctrlMenu ={};
var ctrlModal = {};

rivets.formatters.eq = function(value, args) {
    return value === args;
};

$(document).ready(function() {
    // Begin loading.
    loadComponents();
    loadSettings();

    $('.ui.dropdown').dropdown({
        action: 'hide'
    });

    $('.menu .item').tab();

    rivets.bind($('#comm-modal'), {data: settings.comm, run: ctrlModal});
    rivets.bind($('#team-modal'), {run: ctrlModal});
    rivets.bind($('#menu'), {data: settings.style, run: ctrlMenu});

    // End loading.
    $('.dimmer.active').removeClass('active');
});

$(window).bind('beforeunload', function() {
    saveSettings();
    return "Unloading will cause loss of current mission state. Are you sure you want to do this?";
});