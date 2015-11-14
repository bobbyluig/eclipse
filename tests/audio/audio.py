import numpy as np
from pydub import AudioSegment
import math
import time
import pyaudio
from collections import deque

__author__ = 'Lujing Cen'


class Apollo:
    def __init__(self, fs=44100, source=None):
        if source:
            self.source = source
        else:
            self.source = None

        self.fs = fs
        self.data = None
        self.audio = None

    def load(self):
        if self.source and self.audio is None:
            self.audio = AudioSegment.from_file(self.source)
            self.audio = self.audio.set_channels(1)
        else:
            print('Audio file missing or already loaded!')

    def analyze(self):
        if self.audio is not None and self.data is None:
            self.data = np.fromstring(self.audio._data, np.int16)
        elif self.data is not None:
            print('Already analyzed!')
        else:
            print('Audio file not yet loaded!')

    def freq_to_step(self, freq):
        # n = log(f_n / f_0, a) where a = 2^(1/12)

        n = math.log(freq/440, math.pow(2, 1/12))
        exact = self.step_to_freq(round(n))
        diff = 1200 * math.log(freq/exact, 2)

        return round(n), diff

    def step_to_freq(self, steps, slack=0):
        # f_n = f_0 * (a)^n where a = 2^(1/12)

        if slack == 0:
            return 440 * math.pow(math.pow(2, 1/12), steps)
        else:
            exact = 440 * math.pow(math.pow(2, 1/12), steps)
            return (1 - slack) * exact, (1 + slack) * exact

    def fuzzy_detect(self):
        # frequency (Hz) = abs(fft_frequency_coefficient * sampling_rate)
        # Finds the frequency with the greatest magnitude via fft.

        # Obtain fourier transform
        w = np.fft.fft(self.data)

        # debug for dBs
        # db = np.abs(self.data)
        # max = np.argmax(db)

        # Obtain frequency coefficients from fourier
        freqs = np.fft.fftfreq(w.size)

        # Find peak in the coefficients
        idx = np.argmax(np.abs(w))
        freq = freqs[idx]
        freq_in_hertz = np.abs(freq * self.fs)

        return freq_in_hertz

    def full_detect(self):
        # Finds a more accurate frequency using quadratic approximation.

        # Use a Blackman window
        window = np.blackman(len(self.data))

        # Obtain fourier transform
        w = np.fft.rfft(self.data * window)
        w = np.abs(w) ** 2

        idx = w[1:].argmax() + 1

        if idx != w.size - 1:
            y0, y1, y2 = np.log(w[idx-1:idx+2:])
            x1 = (y2 - y0) * 0.5 / (2 * y1 - y2 - y0)
            freq = (idx + x1) * self.fs / len(self.data)
            return freq
        else:
            freq = idx * self.fs / len(self.data)
            return freq

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input_device_index=0, input=True, frames_per_buffer=8192)
# print('Starting stream!')
stream.start_stream()

howls = deque(maxlen=5)
c = 0

while True:
    audio = []
    for i in range(0, 2):
        data = stream.read(8192)
        data = np.fromstring(data, np.int16)
        audio.extend(data)

    a = Apollo()
    a.audio = True
    a.data = audio
    hz = a.fuzzy_detect()
    steps = a.freq_to_step(hz)
    howls.append(steps[0])
    if howls.count(-2) >= 2:
        howls.clear()
        c += 1
        print('%sx: Howl! ' % c)

stream.stop_stream()
# print('Stream ended!')


'''
audio = Apollo(source='violin_a.mp3')
audio.load()
audio.analyze()
a = audio.full_detect()
print(a)
'''

'''
hz = audio.fuzzy_detect()
steps = audio.freq_to_step(hz)
print(steps)
'''