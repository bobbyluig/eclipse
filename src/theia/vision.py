import cv2
import time
import numpy as np
from theia.eye import Eye


class Theia:
    def __init__(self):
        self.cry = True

    ####################################################
    # Obtain background using MOG2.
    # This allows for identification of moving PreyBOTS.
    # Gaussian blur applied to remove grains.
    ####################################################

    @staticmethod
    def getForegroundMask(eye, frames):
        subtractor = cv2.createBackgroundSubtractorMOG2(history=frames, detectShadows=False)
        ksize = (21, 21)

        for i in range(frames):
            frame = eye.getColorFrame()
            frame = cv2.GaussianBlur(frame, ksize, 0)
            subtractor.apply(frame)

        frame = eye.getColorFrame()
        frame = cv2.GaussianBlur(frame, ksize, 0)
        mask = subtractor.apply(frame)

        return mask

    ###################################################################
    # Dense optical flow using Farneback.
    # This identifies blob, direction, & velocity of moving PreyBOTs.
    # Takes two colored frames.
    # Detection based on edges and NOT color.
    ###################################################################

    @staticmethod
    def denseOpticalFlow(frame1, frame2):
        ksize = (21, 21)
        frame1 = cv2.GaussianBlur(frame1, ksize, 0)
        frame2 = cv2.GaussianBlur(frame2, ksize, 0)

        prev_points = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        next_points = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        hsv = np.zeros_like(frame1)
        hsv[..., 1] = 255

        flow = cv2.calcOpticalFlowFarneback(prev_points, next_points, None, 0.5, 3, 15, 3, 5, 1.1, 0)
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        hsv[..., 0] = ang * 180 / np.pi / 2
        hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        return bgr

eye = Eye(0)
eye.close()