ctrlSpeech.speak = function (voice, text) {
    if (!window.speechSynthesis) {
        return;
    }

    var msg = new SpeechSynthesisUtterance();
    var v = this.getVoice(v);

    if (v) {
        msg.voice = v;
    }
    else {
        msg.voice = this.getVoice('native');
    }

    msg.volume = settings.voice.volume;
    msg.rate = settings.voice.rate;
    msg.pitch = settings.voice.pitch;

    msg.text = text;
    msg.lang = 'en-US';

    window.speechSynthesis.speak(msg);
};

ctrlSpeech.getVoice = function (voice) {
    var voices = window.speechSynthesis.getVoices();
    return voices.find(function (x) {
        return x.name === voice;
    });
};

ctrlSpeech.commands = {

};