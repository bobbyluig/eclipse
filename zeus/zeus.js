var user = 'Zeus';
var key = '+Ew~77XrvW-c<6sZ';

function onchallenge(session, method, extra) {
    if (method === 'wampcra') {
        return autobahn.auth_cra.sign(key, extra.challenge);
    } else {
        throw 'Unknown challenge method: ' + extra.challenge;
    }
}

var connection = new autobahn.Connection({
    url: 'ws://127.0.0.1:8080/ws/',
    realm: 'lycanthrope',
    authmethods: ['wampcra'],
    authid: user,
    onchallenge: onchallenge
});

connection.onopen = function(session, details) {
    console.log('Connected session with ID: ' + session.id);
    session.call('com.agility', [1, 60]);
}

connection.open();