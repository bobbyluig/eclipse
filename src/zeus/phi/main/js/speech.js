ctrlSpeech.speak = function (voice, text) {
    if (!('speechSynthesis' in window)) {
        return;
    }

    var msg = new SpeechSynthesisUtterance();
    var v = this.getVoice(voice);

    if (v) {
        msg.voice = v;
    }
    else {
        msg.voice = this.getVoice('native');
    }

    msg.volume = settings.speech.volume;
    msg.rate = settings.speech.rate;
    msg.pitch = settings.speech.pitch;

    msg.text = text;

    window.speechSynthesis.speak(msg);
};

ctrlSpeech.getVoice = function (voice) {
    return this.voices.find(function (x) {
        return x.name === voice;
    });
};

window.speechSynthesis.onvoiceschanged = function () {
    ctrlSpeech.voices = window.speechSynthesis.getVoices();
};

ctrlSpeech.voices = [];

ctrlSpeech.commands = {

};