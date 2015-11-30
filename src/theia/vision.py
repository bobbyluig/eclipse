import cv2
import time, logging
import numpy as np
from theia.eye import Eye
from theia.cmt import CMT

logger = logging.getLogger('universe')


class Theia:
    def __init__(self):
        self.cry = True

    ####################################################
    # Obtain background using MOG2.
    # This allows for identification of moving PreyBOTS.
    # Gaussian blur applied to remove grains.
    ####################################################

    @staticmethod
    def getForegroundMask(eye, frames, blur=True):
        subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
        ksize = (5, 5)

        for i in range(frames):
            frame = eye.getColorFrame()
            if blur:
                frame = cv2.GaussianBlur(frame, ksize, 0)
            subtractor.apply(frame)

        frame = eye.getColorFrame()
        if blur:
            frame = cv2.GaussianBlur(frame, ksize, 0)
        mask = subtractor.apply(frame)

        return mask

    ####################################
    # Get n blobs with the largest area.
    # This is a helper function.
    # Use only with binary images.
    ####################################

    @staticmethod
    def boundBlobs(image, count, order=False):
        _, contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        areas = np.array([cv2.contourArea(cnt) for cnt in contours])

        if len(areas) < count:
            count = len(areas)
            logger.info('Requested %s blobs. Only found %s blobs.' % (count, len(areas)))

        if count == 0:
            return None
        elif count == 1:
            index = np.argmax(areas)
            return [cv2.boundingRect(contours[index])]

        # Find the n largest areas.
        if order:
            indices = areas.argsort()[-count:][::-1]
        else:
            indices = np.argpartition(areas, -count)[-count:]

        # Create ROIs for each contour.
        contours = np.array(contours)
        contours = contours[indices]
        roi = [cv2.boundingRect(cnt) for cnt in contours]

        return roi

    ###################################################################
    # Dense optical flow using Farneback.
    # This identifies blobs, directions, & velocities of moving PreyBOTs.
    # Takes two colored frames and an array of blobs.
    # Detection based on edges and NOT color.
    ###################################################################

    @staticmethod
    def dataOpticalFlow(frame1, frame2, blobs):
        ksize = (5, 5)

        # Clean grains.
        frame1 = cv2.GaussianBlur(frame1, ksize, 0)
        frame2 = cv2.GaussianBlur(frame2, ksize, 0)

        # Color to gray.
        prev_points = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        next_points = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        flow = cv2.calcOpticalFlowFarneback(prev_points, next_points, None, 0.5, 3, 15, 3, 5, 1.1, 0)
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1], angleInDegrees=True)
        data = []

        for blob in blobs:
            # Crop to ROI.
            roiMag = mag[blob[1]:blob[1]+blob[3], blob[0]:blob[0]+blob[2]].flatten()
            roiAng = ang[blob[1]:blob[1]+blob[3], blob[0]:blob[0]+blob[2]].flatten()

            # Clean bad pixels.
            badIndices = np.where(roiMag < 0.5)[0]
            roiMag = np.delete(roiMag, badIndices)
            roiAng = np.delete(roiAng, badIndices)

            # Compute averages.
            avgMag = np.average(roiMag)
            avgAng = np.average(roiAng)

            # Append to data.
            data.append((avgMag, avgAng))

        return data

    @staticmethod
    def graphicOpticalFlow(frame1, frame2):
        ksize = (5, 5)

        # Clean grains.
        frame1 = cv2.GaussianBlur(frame1, ksize, 0)
        frame2 = cv2.GaussianBlur(frame2, ksize, 0)

        # Color to gray.
        prev_points = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        next_points = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # Create an empty image.
        hsv = np.zeros_like(frame1)
        hsv[..., 1] = 255

        # Compute flow.
        flow = cv2.calcOpticalFlowFarneback(prev_points, next_points, None, 0.5, 3, 15, 3, 5, 1.1, 0)
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1], angleInDegrees=True)
        hsv[..., 0] = ang / 2
        hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        return bgr

eye = Eye('vtest.avi')
frame = eye.getGrayFrame()
cv2.imwrite('frame.jpg', frame)
cmt = CMT(eye.getGrayFrame(), (501, 155), (501+30, 155+80))

while True:
    im_draw, im_gray = eye.getBothFrames()
    start = time.time()
    cmt.process_frame(im_gray)
    print(time.time() - start)

    if cmt.has_result:
        cv2.line(im_draw, cmt.tl, cmt.tr, (255, 0, 0), 4)
        cv2.line(im_draw, cmt.tr, cmt.br, (255, 0, 0), 4)
        cv2.line(im_draw, cmt.br, cmt.bl, (255, 0, 0), 4)
        cv2.line(im_draw, cmt.bl, cmt.tl, (255, 0, 0), 4)

    cv2.imshow('tracked', im_draw)

    k = cv2.waitKey(1)
    if k == 27:
        break

cv2.destroyAllWindows()