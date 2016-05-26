// Default settings.
var defaults = {};

// Global variables.
var settings = {};
var state = {};
var wamp;

// Controllers.
var ctrlMenu ={};
var ctrlModal = {};
var ctrlWamp = {};
var ctrlRpc = {};
var ctrlLog = {};
var ctrlSpeech = {};
var ctrlPack = {};


// Status resets.
state.com = {
    state: 'closed'
};

// Main
$(document).ready(function() {
    // Begin loading.
    ctrlMenu.loadSettings();

    $('.ui.dropdown').dropdown({
        action: 'hide'
    });

    var body = $('body');

    body.find('.logger').each(function() {
        var logger = $(this);
        ctrlLog.init(logger);
    });
    
    annyang.addCommands(ctrlSpeech.commands);

    rivets.bind(body, {menu: ctrlMenu, state: state, wamp: ctrlWamp, pack: ctrlPack, speech: ctrlSpeech});
});

// Prevent accidental closing.
$(window).bind('beforeunload', function() {
    ctrlMenu.saveSettings();
    return "Unloading will cause loss of current mission state. Are you sure you want to do this?";
});