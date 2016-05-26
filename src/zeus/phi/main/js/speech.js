ctrlSpeech.speak = function (voice, text) {
    if (!('speechSynthesis' in window)) {
        return;
    }

    var msg = new SpeechSynthesisUtterance();
    var v = ctrlSpeech.getVoice(voice);

    if (v) {
        msg.voice = v;
    }
    else {
        msg.voice = ctrlSpeech.getVoice('native');
    }

    if (ctrlSpeech.voices.length == 0) {
        return undefined;
    }

    msg.volume = settings.speech.volume;
    msg.rate = settings.speech.rate;
    msg.pitch = settings.speech.pitch;

    msg.text = text;

    window.speechSynthesis.speak(msg);
};

ctrlSpeech.getVoice = function (voice) {
    return ctrlSpeech.voices.find(function (x) {
        return x.name === voice;
    });
};

window.speechSynthesis.onvoiceschanged = function () {
    ctrlSpeech.voices = window.speechSynthesis.getVoices();
};

ctrlSpeech.voices = [];

ctrlSpeech.commands = {
    'pack :id walk': function (id) {
        ctrlPack.setRobot(id);
        ctrlPack.watch();
        ctrlPack.setVector([3, 0]);
    },

    'pack :id run': function (id) {
        ctrlPack.setRobot(id);
        ctrlPack.watch();
        ctrlPack.setVector([8, 0]);
    },

    'pack :id walk left': function (id) {
        ctrlPack.setRobot(id);
        ctrlPack.watch();
        ctrlPack.setVector([3, 0.2]);
    },

    'pack :id walk right': function (id) {
        ctrlPack.setRobot(id);
        ctrlPack.watch();
        ctrlPack.setVector([3, -0.2]);
    },

    'pack :id run left': function (id) {
        ctrlPack.setRobot(id);
        ctrlPack.watch();
        ctrlPack.setVector([8, 0.2]);
    },

    'pack :id run right': function (id) {
        ctrlPack.setRobot(id);
        ctrlPack.watch();
        ctrlPack.setVector([8, -0.2]);
    },

    'pack :id chase tail': function (id) {
        ctrlPack.setRobot(id);
        ctrlPack.watch();
        ctrlPack.setVector([0, 0.9]);
    },

    'pack :id turn right': function (id) {
        ctrlPack.setRobot(id);
        ctrlPack.watch();
        ctrlPack.setVector([0, -0.9]);
    },

    'pack :id home': function (id) {
        ctrlPack.setRobot(id);
        ctrlPack.stop();
        ctrlPack.zero();
    },

    'pack :id center head': function (id) {
        ctrlPack.setRobot(id);
        ctrlPack.centerHead();
    },

    'pack :id stop': function (id) {
        ctrlPack.setRobot(id);
        ctrlPack.stopWatch();
    }
};

ctrlSpeech.start = function () {
    annyang.start();
    ctrlLog.log('system', 'Voice control started.', 1);
};

ctrlSpeech.stop = function () {
    annyang.abort();
    ctrlLog.log('system', 'Voice control stopped.', 1);
};