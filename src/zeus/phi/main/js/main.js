// Global variables.
var settings = {};

// Global controllers.
var ctrlMenu ={};
var ctrlModal = {};

rivets.formatters.eq = function(value, args) {
    return value === args;
};

$(document).ready(function() {
    loadSettings();

    $('.ui.dropdown').dropdown({
        action: 'hide'
    });

    rivets.bind($('#comm-modal'), {data: settings.comm, run: ctrlModal});
    rivets.bind($('#team-modal'), {run: ctrlModal});
    rivets.bind($('#menu'), {data: settings.style, run: ctrlMenu});
});

$(window).bind('beforeunload', function() {
    return "Unloading will cause loss of current mission state. Are you sure you want to do this?";
});

function saveSettings() {
    return false;
}

function loadSettings() {
    // Need to implement HTML5 storage.

    settings = {
        comm: jQuery.extend(true, {}, defaultComm),
        style: jQuery.extend(true, {}, defaultStyle)
    }
}