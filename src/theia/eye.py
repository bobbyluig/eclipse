import numpy as np
import cv2
import logging

logger = logging.getLogger('universe')


class Eye:
    def __init__(self, source):
        self.frame = None
        self.cap = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            raise Exception("Unable to connect to video source '%s'." % source)

        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        logger.info('Opening capture at %sx%s' % (self.width, self.height))

    def close(self):
        self.cap.release()

    def updateFrame(self):
        _, self.frame = self.cap.read()

    def getGrayFrame(self):
        self.updateFrame()
        return cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

    def getColorFrame(self):
        self.updateFrame()
        return self.frame

    def getBothFrames(self):
        self.updateFrame()
        return self.frame, cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
