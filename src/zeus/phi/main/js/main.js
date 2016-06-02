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
var ctrlPack = {
    pack1: {},
    pack2: {}
};


// Status resets.
state.com = {
    state: 'closed'
};

state.bind = {
    active: null
};

state.pack1 = {
    connected: false,
    session: 0,
    v1: 0,
    v2: 0,
    p1: 0,
    p2: 0
};

state.pack2 = {
    connected: false,
    session: 0,
    v1: 0,
    v2: 0,
    p1: 0,
    p2: 0
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