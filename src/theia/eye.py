import numpy as np
import cv2
from cerebral import logger as l
import logging
import urllib.request
from collections import deque

logger = logging.getLogger('universe')


class IPCamera:
    def __init__(self, url):
        self.stream = urllib.request.urlopen(url)
        self.b = bytearray()

    def read(self):
        max = 1000
        while max > 0:
            self.b.extend(self.stream.read(1024))
            x = self.b.find(b'\xff\xd8')
            y = self.b.find(b'\xff\xd9')

            max -= 1

            if x != -1 and y != -1:
                jpg = self.b[x:y+2]
                self.b = self.b[y+2:]

                jpg = np.asarray(jpg, dtype=np.uint8)
                i = cv2.imdecode(jpg, cv2.IMREAD_UNCHANGED)

                return True, i


class Eye:
    def __init__(self, source):
        self.history = deque(maxlen=5)
        self.frame = None

        self.cap = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            raise Exception('Unable to connect to video source "{}".'.format(source))

        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        logger.info('Opening capture at {}x{}.'.format(self.width, self.height))

    def close(self):
        self.cap.release()

    def update_frame(self):
        if self.frame is not None:
            self.history.appendleft(self.frame.copy())

        _, self.frame = self.cap.read()

    def get_gray_frame(self):
        self.update_frame()
        return cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

    def get_color_frame(self):
        self.update_frame()
        return self.frame.copy()

    def get_both_frames(self):
        self.update_frame()
        return self.frame.copy(), cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
