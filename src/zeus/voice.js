// Global variables.
var user = 'Voice';
var key = 'ALyfTuqZvHHbwQCE';
var url = 'wss://192.168.0.6/ws/';
var ws = null;


// Voice command functions.
var voice_walkForward = function() {
    ws.call('zeus.speak', ['Executing forward walk.']);
};

var voice_identify = function() {
    ws.call('dog.identify');
};

var voice_hello = function() {
    ws.call('dog.hello');
};

function startVoice() {
    var commands = {
        'DOG walk (forward)': voice_walkForward,
        'DOG identify (yourself)': voice_identify,
        'DOG hello': voice_hello
    };

    annyang.addCommands(commands);
    annyang.start();
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

    startVoice();
};

connection.open();