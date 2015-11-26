import numpy as np
import pyaudio
from collections import deque
import math, time, logging

logger = logging.getLogger('universe')


class Apollo:
    AUDIO_FORMAT = pyaudio.paInt16
    CHANNELS = 1
    SAMPLE_RATE = 44100
    CHUNK_SIZE = 8192
    CAPTURE_LEN = int(round(SAMPLE_RATE / CHUNK_SIZE * 0.25))

    def __init__(self, target, index=0):
        p = pyaudio.PyAudio()
        self.stream= p.open(self.SAMPLE_RATE, self.CHANNELS, self.AUDIO_FORMAT, input_device_index=index,
                            input=True, frames_per_buffer=self.CHUNK_SIZE)
        self.stream.start_stream()
        self.target = target
        self.howls = deque(maxlen=5)

    def stop(self):
        self.stream.stop_stream()

    def blockingDetect(self, callback, timeout=30):
        start = time.time()

        while time.time() - start < timeout:
            frames = []
            for i in range(self.CAPTURE_LEN):
                data = self.stream.read(self.CHUNK_SIZE)
                data = np.fromstring(data, np.int16)
                frames.append(data)

            frequency = self.fuzzyDetect(frames)
            steps = self.frequencyToStep(frequency)
            self.howls.append(steps)

            if self.howls.count(self.target) > 2:
                logger.info('Howl detected!')
                callback()
                break

    def instant_detect(self):
        frames = []
        for i in range(self.CAPTURE_LEN):
            data = self.stream.read(self.CHUNK_SIZE)
            data = np.fromstring(data, np.int16)
            frames.append(data)

        frequency = self.fuzzyDetect(frames)
        return self.target == self.frequencyToStep(frequency)

    @staticmethod
    def fuzzyDetect(data):
        # frequency (Hz) = abs(fft_frequency_coefficient * sampling_rate)
        # Finds the frequency with the greatest magnitude via fft.

        # Obtain fourier transform
        w = np.fft.fft(data)

        # debug for dBs
        # db = np.abs(self.data)
        # max = np.argmax(db)

        # Obtain frequency coefficients from fourier
        freqs = np.fft.fftfreq(w.size)

        # Find peak in the coefficients
        index = np.argmax(np.abs(w))
        freq = freqs[index]
        freq_in_hertz = np.abs(freq * Apollo.SAMPLE_RATE)

        return freq_in_hertz

    @staticmethod
    def frequencyToStep(freq, error=False):
        # n = log(f_n / f_0, a) where a = 2^(1/12)

        try:
            n = math.log(freq/440, math.pow(2, 1/12))
            n = int(round(n))
        except ValueError:
            n = None

        if n is None:
            return n
        elif error:
            exact = Apollo.stepToFrequency(n)
            diff = 1200 * math.log(freq/exact, 2)
            return n, diff
        else:
            return n

    @staticmethod
    def stepToFrequency(steps, slack=0):
        # f_n = f_0 * (a)^n where a = 2^(1/12)

        if slack == 0:
            return 440 * math.pow(math.pow(2, 1/12), steps)
        else:
            exact = 440 * math.pow(math.pow(2, 1/12), steps)
            return (1 - slack) * exact, (1 + slack) * exact
