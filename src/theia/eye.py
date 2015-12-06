import numpy as np
import cv2
import logging
import urllib.request

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

                return None, i

    @staticmethod
    def set(self, *args, **kwargs):
        return

    @staticmethod
    def isOpened(self):
        return True



class Eye:
    def __init__(self, source):
        self.optogram = None
        self.frame = None

        if 'http' in str(source):
            self.cap = IPCamera(source)
        else:
            self.cap = cv2.VideoCapture(source)

            if not self.cap.isOpened():
                raise Exception("Unable to connect to video source '%s'." % source)

            self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

            logger.info('Opening capture at %sx%s' % (self.width, self.height))

    def close(self):
        self.cap.release()

    def updateFrame(self):
        if self.frame is not None:
            self.optogram = self.frame.copy()
        _, self.frame = self.cap.read()

    def getGrayFrame(self):
        self.updateFrame()
        return cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

    def getColorFrame(self):
        self.updateFrame()
        return self.frame.copy()

    def getBothFrames(self):
        self.updateFrame()
        return self.frame.copy(), cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
