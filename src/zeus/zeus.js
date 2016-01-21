// Global variables.
var user = 'Zeus';
var key = '+Ew~77XrvW-c<6sZ';
var url = 'wss://192.168.12.18/ws/';
var ws = null;

// Speak functions.
function speak(args) {
    var msg = new SpeechSynthesisUtterance();
    msg.lang = 'en-US';
    // msg.voice = speechSynthesis.getVoices().filter(function(voice) { return voice.name == 'Google UK English Male'; })[0];
    msg.text = args[0];
    window.speechSynthesis.speak(msg);
}

//  Communication.
function onChallenge(session, method, extra) {
    if (method === 'wampcra') {
        return autobahn.auth_cra.sign(key, extra.challenge);
    } else {
        throw 'Unknown challenge method: ' + extra.challenge;
    }
}

var connection = new autobahn.Connection({
    url: url,
    realm: 'lycanthrope',
    authmethods: ['wampcra'],
    authid: user,
    onchallenge: onChallenge
});

connection.onopen = function(session) {
    console.log('Connected session with ID: ' + session.id);
    ws = session;

    // Register everything.
    ws.register('zeus.speak', speak);
};

connection.open();