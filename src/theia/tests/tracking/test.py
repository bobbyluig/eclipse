from oculus import DsstParameters, DsstTracker, KcfParameters, KcfTracker
import cv2
import os
import numpy as np
from cmt import CMT


class Eye:
    def __init__(self, source):
        self.optogram = None
        self.frame = None

        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            raise Exception("Unable to connect to video source '%s'." % source)
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

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


class KCF:
    def __init__(self, **kwargs):
        params = KcfParameters()

        self.params = params
        self.tracker = KcfTracker(self.params)
        self.initialized = False

    def init(self, image, boundingBox):
        success = self.tracker.reinit(image, boundingBox)

        if success:
            self.initialized = True
        else:
            raise Exception('Unable to initialize KCF tracker with given frame.')

    def update(self, image):
        return self.tracker.update(image)

    def updateAt(self, image, boundingBox):
        return self.tracker.updateAt(image, boundingBox)

    def getBoundingBox(self):
        return self.tracker.getBoundingBox()

    def getCenter(self):
        return self.tracker.getCenter()


class DSST:
    def __init__(self, **kwargs):
        params = DsstParameters()

        params.padding = kwargs.get('padding', 1.6)
        params.outputSigmaFactor = kwargs.get('outputSigmaFactor', 0.05)
        params.lambdaValue = kwargs.get('lambdaValue', 0.01)
        params.learningRate = kwargs.get('learningRate', 0.012)
        params.templateSize = kwargs.get('templateSize', 100)
        params.cellSize = kwargs.get('cellSize', 2)

        params.enableTrackingLossDetection = kwargs.get('enableTrackingLossDetection', False)
        params.psrThreshold = kwargs.get('psrThreshold', 13.5)
        params.psrPeakDel = kwargs.get('psrPeakDel', 1)

        params.enableScaleEstimator = kwargs.get('enableScaleEstimator', True)
        params.scaleSigmaFactor = kwargs.get('scaleSigmaFactor', 0.25)
        params.scaleStep = kwargs.get('scaleStep', 1.02)
        params.scaleCellSize = kwargs.get('scaleCellSize', 4)
        params.numberOfScales = kwargs.get('numberOfScales', 33)

        params.originalVersion = kwargs.get('originalVersion', False)
        params.resizeType = kwargs.get('resizeType', 1)
        params.useFhogTranspose = kwargs.get('useFhogTranspose', False)
        params.minArea = kwargs.get('minArea', 10)
        params.maxAreaFactor = kwargs.get('maxAreaFactor', 0.8)
        params.useCcs = kwargs.get('useCcs', True)

        self.params = params
        self.tracker = DsstTracker(self.params)
        self.initialized = False

    def init(self, image, boundingBox):
        success = self.tracker.reinit(image, boundingBox)

        if success:
            self.initialized = True
        else:
            raise Exception('Unable to initialize DSST tracker with given frame.')

    def reinit(self, image, boundingBox):
        self.tracker.reinit(image, boundingBox)

    def update(self, image):
        return self.tracker.update(image)

    def updateAt(self, image, boundingBox):
        return self.tracker.updateAt(image, boundingBox)

    def getBoundingBox(self):
        return self.tracker.getBoundingBox()

    def getCenter(self):
        return self.tracker.getCenter()


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


def vot():
    directory = 'C:/Users/bobbyluig/Desktop/vot2015/pedestrian2'
    gt = open(os.path.join(directory, 'groundtruth.txt'), 'r')
    i = 1

    tracker = DSST()

    while True:
        truth = gt.readline().strip().split(',')

        if len(truth) < 8:
            break

        truth = [float(t) for t in truth]

        x = truth[::2]
        y = truth[1::2]

        x0 = int(round(min(x)))
        x1 = int(round(max(x)))
        y0 = int(round(min(y)))
        y1 = int(round(max(y)))

        frame = cv2.imread(os.path.join(directory, '%08d.jpg' % i))

        if i == 1:
            tracker.init(frame, (x0, y0, x1 - x0, y1 - y0))
            frame = cv2.rectangle(frame, (x0, y0), (x1, y1), (0, 0, 255), 3)
        else:
            tracker.update(frame)
            pos = tracker.getBoundingBox()
            frame = cv2.rectangle(frame, (x0, y0), (x1, y1), (0, 255, 0), 3)
            frame = cv2.rectangle(frame, (int(pos[0]), int(pos[1])), (int(pos[0] + pos[2]), int(pos[1] + pos[3])), (0, 0, 255), 3)

        cv2.imshow('preview', frame)
        k = cv2.waitKey(30)

        if k != -1:
            break

        i += 1


def correlation_cmt_test(camera):
    eye = Eye(camera)
    eye.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    tracker = DSST(enableTrackingLossDetection=True, psrThreshold=8)
    found = True

    while True:
        frame = eye.getColorFrame()
        cv2.imshow('preview', frame)
        k = cv2.waitKey(1)
        if not k == -1:
            break

    frame, gray = eye.getBothFrames()
    tl, br = get_rect(frame)
    cmt = CMT(gray, tl, br)
    tracker.init(frame, (tl[0], tl[1], br[0]-tl[0], br[1]-tl[1]))

    while True:
        frame = eye.getColorFrame()

        if not found:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cmt.process_frame(gray)

            if cmt.has_result:
                bb = np.rint(cmt.bb)
                found = tracker.updateAt(frame, (int(bb[0]), int(bb[1]), int(bb[2]), int(bb[3])))
            else:
                found = tracker.update(frame)
        else:
            found = tracker.update(frame)

        pos = tracker.getBoundingBox()

        if found:
            frame = cv2.rectangle(frame, (int(pos[0]), int(pos[1])), (int(pos[0] + pos[2]), int(pos[1] + pos[3])), (0, 255, 0), 3)
        else:
            frame = cv2.rectangle(frame, (int(pos[0]), int(pos[1])), (int(pos[0] + pos[2]), int(pos[1] + pos[3])), (0, 0, 255), 3)

        cv2.imshow('frame', frame)
        k = cv2.waitKey(1)
        if not k == -1:
            break


def correlation_hom_test(camera):
    eye = Eye(camera)
    eye.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    tracker = DSST(enableTrackingLossDetection=True, psrThreshold=8)
    found = True

    failedSuggestions = 0

    detector = cv2.BRISK_create()

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    # matcher = cv2.FlannBasedMatcher(index_params, search_params)

    while True:
        frame = eye.getColorFrame()
        cv2.imshow('preview', frame)
        k = cv2.waitKey(1)
        if not k == -1:
            break

    frame, gray = eye.getBothFrames()
    tl, br = get_rect(frame)

    roi = gray[tl[1]:br[1], tl[0]:br[0]]
    kp1, des1 = detector.detectAndCompute(roi, None)

    use
    if len(kp1) == 0:


    h, w = roi.shape

    tracker.init(frame, (tl[0], tl[1], br[0]-tl[0], br[1]-tl[1]))

    while True:
        frame = eye.getColorFrame()

        if not found:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            kp2, des2 = detector.detectAndCompute(gray, None)

            matches = matcher.knnMatch(des1, des2, k=2)

            # store all the good matches as per Lowe's ratio test.
            good = []
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    good.append(m)

            if len(good) > 3:
                src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1,1,2)
                dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1,1,2)
                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                pts = np.float32([[0,0],[0,h-1],[w-1,h-1],[w-1,0]]).reshape(-1,1,2)
                dst = cv2.perspectiveTransform(pts, M)
                dst = np.int32(dst.ravel())
                x = dst[::2]
                y = dst[1::2]

                x0 = int(min(x))
                x1 = int(max(x))
                y0 = int(min(y))
                y1 = int(max(y))

                bb = (x0, y0, x1 - x0, y1 - y0)

                if any(x < 0 for x in bb):
                    continue
                else:
                    if failedSuggestions > 2:
                        tracker.init(frame, bb)
                        found = True
                    else:
                        found = tracker.updateAt(frame, bb)

                    if not found:
                        failedSuggestions += 1
                    else:
                        failedSuggestions = 0
        else:
            found = tracker.update(frame)

        pos = tracker.getBoundingBox()

        if found:
            frame = cv2.rectangle(frame, (int(pos[0]), int(pos[1])), (int(pos[0] + pos[2]), int(pos[1] + pos[3])), (0, 255, 0), 3)
        else:
            frame = cv2.rectangle(frame, (int(pos[0]), int(pos[1])), (int(pos[0] + pos[2]), int(pos[1] + pos[3])), (0, 0, 255), 3)

        cv2.imshow('frame', frame)
        k = cv2.waitKey(1)
        if not k == -1:
            break



correlation_hom_test(0)