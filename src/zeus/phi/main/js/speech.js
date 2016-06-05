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

ctrlSpeech.getRobot = function (id) {
    if (id == 'one' || id == '1')
        return 'pack1';
    else if (id == 'too' || id == 'two' || id == '2' || id == 'to')
        return 'pack2';
    else
        return '';
};

ctrlSpeech.commands = {
    'pack :id walk': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        state[robot].direct.v1 = 3;
        state[robot].direct.v2 = 0;
        ctrlPack[robot].setVector();
    },

    'pack :id run': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        state[robot].direct.v1 = 8;
        state[robot].direct.v2 = 0;
        ctrlPack[robot].setVector();
    },

    'pack :id walk left': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        state[robot].direct.v1 = 3;
        state[robot].direct.v2 = 0.2;
        ctrlPack[robot].setVector();
    },

    'pack :id walk right': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        state[robot].direct.v1 = 3;
        state[robot].direct.v2 = -0.2;
        ctrlPack[robot].setVector();
    },

    'pack :id run left': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        state[robot].direct.v1 = 8;
        state[robot].direct.v2 = 0.2;
        ctrlPack[robot].setVector();
    },

    'pack :id run right': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        state[robot].direct.v1 = 8;
        state[robot].direct.v2 = -0.2;
        ctrlPack[robot].setVector();
    },

    'pack :id chase tail': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        state[robot].direct.v1 = 3;
        state[robot].direct.v2 = 0.8;
        ctrlPack[robot].setVector();
    },

    'pack :id turn right': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        state[robot].direct.v1 = 3;
        state[robot].direct.v2 = -0.8;
        ctrlPack[robot].setVector();
    },

    'pack :id stop': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        state[robot].direct.v1 = 0;
        state[robot].direct.v2 = 0;
        ctrlPack[robot].setVector();
    },

    'pack :id look left': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        state[robot].direct.p1 = 20;
        state[robot].direct.p2 = 0;
        ctrlPack[robot].setHead();
    },

    'pack :id look right': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        state[robot].direct.p1 = -20;
        state[robot].direct.p2 = 0;
        ctrlPack[robot].setHead();
    },

    'pack :id look up': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        state[robot].direct.p1 = 0;
        state[robot].direct.p2 = 10;
        ctrlPack[robot].setHead();
    },

    'pack :id look down': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        state[robot].direct.p1 = 0;
        state[robot].direct.p2 = -10;
        ctrlPack[robot].setHead();
    },

    'pack :id center head': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        state[robot].direct.p1 = 0;
        state[robot].direct.p2 = 0;
        ctrlPack[robot].setHead();
    },

    'pack :id zero': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        ctrlPack[robot].zero();
    },

    'pack :id watch': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        ctrlPack[robot].startWatch();
    },

    'pack :id push-up': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        ctrlPack[robot].pushup();
    },

    'pack :id stop thread': function (id) {
        var robot = ctrlSpeech.getRobot(id);

        if (!robot) {
            ctrlLog.log('system', 'Unknown identifier ' + id + '.', 2);
            return;
        }

        ctrlPack[robot].stop();
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