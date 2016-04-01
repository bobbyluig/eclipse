// Default settings.
var defaults = {};

// Global variables.
var settings = {};
var state = {};
var wamp;

// Controllers.
var ctrlLoad = {};
var ctrlMenu ={};
var ctrlModal = {};
var ctrlWamp = {};
var ctrlRpc = {};
var ctrlLog = {};

// Main
$(document).ready(function() {
    // Begin loading.
    ctrlLoad.loadTabs();
    ctrlMenu.loadSettings();

    $('.ui.dropdown').dropdown({
        action: 'hide'
    });

    $('.menu .item').tab();

    rivets.bind($('#menu'), {style: settings.style, menu: ctrlMenu, state: state});

    // End loading.
    $('.dimmer.active').removeClass('active');
});

// Prevent accidental closing.
$(window).bind('beforeunload', function() {
    ctrlMenu.saveSettings();
    return "Unloading will cause loss of current mission state. Are you sure you want to do this?";
});