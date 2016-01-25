// Global variables.
var user = 'Voice';
var key = 'ALyfTuqZvHHbwQCE';
var url = 'wss://192.168.12.18/ws/';
var ws = null;


// Voice command functions.
function startVoice() {
    var commands = {
        'DOG walk (forward)': function() { ws.call('dog.walk') },
        'DOG do pushups': function() { ws.call('dog.pushup') },
        'DOG stop': function() { ws.call('dog.stop') },
        'DOG go home': function() { ws.call('dog.home') },
        'DOG *phrase': function(phrase) { ws.call('dog.converse', [phrase])}
        /*
        'DOG identify (yourself)': function() { ws.call('dog.identify'); },
        'DOG hello': function() { ws.call('dog.hello'); },
        'DOG tell us about blue team\'s robot': function() { ws.call('dog.blue_team') }
        */
    };

    annyang.debug();
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
