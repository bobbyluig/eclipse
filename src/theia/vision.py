import cv2
import time, logging
import numpy as np
from DSST import DsstParameters, DsstTracker
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
    
def get_rect(im, title='get_rect'):
    mouse_params = {'tl': None, 'br': None, 'current_pos': None,
        'released_once': False}

    cv2.namedWindow(title)
    cv2.moveWindow(title, 100, 100)

    def onMouse(event, x, y, flags, param):

        param['current_pos'] = (x, y)

        if param['tl'] is not None and not (flags & cv2.EVENT_FLAG_LBUTTON):
            param['released_once'] = True

        if flags & cv2.EVENT_FLAG_LBUTTON:
            if param['tl'] is None:
                param['tl'] = param['current_pos']
            elif param['released_once']:
                param['br'] = param['current_pos']

    cv2.setMouseCallback(title, onMouse, mouse_params)
    cv2.imshow(title, im)

    while mouse_params['br'] is None:
        im_draw = np.copy(im)

        if mouse_params['tl'] is not None:
            cv2.rectangle(im_draw, mouse_params['tl'], mouse_params['current_pos'], (255, 0, 0))

        cv2.imshow(title, im_draw)
        _ = cv2.waitKey(10)

    cv2.destroyWindow(title)

    tl = (min(mouse_params['tl'][0], mouse_params['br'][0]),
        min(mouse_params['tl'][1], mouse_params['br'][1]))
    br = (max(mouse_params['tl'][0], mouse_params['br'][0]),
        max(mouse_params['tl'][1], mouse_params['br'][1]))

    return tl, br


def correlation_test(camera):
    eye = Eye(camera)
    eye.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    params = DsstParameters()
    tracker = DsstTracker(params)

    while True:
        frame = eye.getColorFrame()
        cv2.imshow('preview', frame)
        k = cv2.waitKey(1)
        if not k == -1:
            break

    frame = eye.getColorFrame()
    tl, br = get_rect(frame)
    tracker.reinit(frame, (tl[0], tl[1], br[0]-tl[0], br[1]-tl[1]))

    while True:
        frame = eye.getColorFrame()
        print(tracker.update(frame))
        pos = tracker.getPosition()
        frame = cv2.rectangle(frame, (int(pos[0]), int(pos[1])), (int(pos[0] + pos[2]), int(pos[1] + pos[3])), (0, 255, 0), 3)
        cv2.imshow('frame', frame)
        k = cv2.waitKey(1)
        if not k == -1:
            break


def full_test(camera):
    eye = Eye(camera)
    subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
    tracker = correlation_tracker(2**6, 32, 23, 0.001, 0.025, 0.001, 0.025)
    ksize = (5, 5)

    while True:
        frame = eye.getColorFrame()
        cv2.imshow('Full Tracking Test', frame)
        k = cv2.waitKey(1)
        if not k == -1:
            break

    count = 50

    for i in range(count):
        frame = eye.getColorFrame()

        display = frame.copy()
        cv2.putText(display, '%s' % (count - i), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow('Full Tracking Test', display)
        cv2.waitKey(1)

        frame = cv2.GaussianBlur(frame, ksize, 0)
        subtractor.apply(frame)

    frame = eye.getColorFrame()
    frame = cv2.GaussianBlur(frame, ksize, 0)
    mask = subtractor.apply(frame)

    blob = Theia.boundBlobs(mask, 1)[0]
    tracker.start_track(frame, rectangle(blob[0], blob[1], blob[0]+blob[2], blob[1]+blob[3]))

    while True:
        frame = eye.getColorFrame()
        tracker.update(frame)
        pos = tracker.get_position()
        frame = cv2.rectangle(frame, (int(pos.left()), int(pos.top())), (int(pos.right()), int(pos.bottom())), (0, 255, 0), 3)
        cv2.imshow('Full Tracking Test', frame)
        k = cv2.waitKey(1)
        if not k == -1:
            break


def cmt_test(camera):
    eye = Eye(camera)

    while True:
        frame = eye.getColorFrame()
        cv2.imshow('preview', frame)
        k = cv2.waitKey(int(1000 / 60))
        if not k == -1:
            break

    color, gray = eye.getBothFrames()
    tl, br = get_rect(color)

    cmt = CMT(gray, tl, br)

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

        k = cv2.waitKey(int(1000 / 60))
        if not k == -1:
            break


camera = 0
correlation_test(camera)
