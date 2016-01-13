from oculus import DsstParameters, DsstTracker, KcfParameters, KcfTracker,\
    Line2D, Line2DParameters
import cv2
import os
import numpy as np
from cmt import CMT
from threading import Thread
import time


class Eye:
    def __init__(self, source, sequence=False):
        self.optogram = None
        self.frame = None
        self.source = source

        if sequence:
            self.imageSequence = True
            self.counter = 1
        else:
            self.imageSequence = False

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

        if self.imageSequence:
            self.frame = cv2.imread(self.source % self.counter)
            self.counter += 1
        else:
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

        params.padding = kwargs.get('padding', 1.7)
        params.lambdaValue = kwargs.get('lambdaValue', 0.0001)
        params.outputSigmaFactor = kwargs.get('outputSigmaFactor', 0.05)
        params.votScaleStep = kwargs.get('votScaleStep', 1.05)
        params.votScaleWeight = kwargs.get('votScaleWeight', 0.95)
        params.templateSize = kwargs.get('templateSize', 100)
        params.interpFactor = kwargs.get('interpFactor', 0.012)
        params.kernelSigma = kwargs.get('kernelSigma', 0.6)
        params.cellSize = kwargs.get('cellSize', 4)
        params.pixelPadding = kwargs.get('pixelPadding', 0)

        params.enableTrackingLossDetection = kwargs.get('enableTrackingLossDetection', False)
        params.psrThreshold = kwargs.get('psrThreshold', 13.5)
        params.psrPeakDel = kwargs.get('psrPeakDel', 1)

        params.useVotScaleEstimation = kwargs.get('useVotScaleEstimation', False)
        params.useDsstScaleEstimation = kwargs.get('useDsstScaleEstimation', True)

        params.scaleSigmaFactor = kwargs.get('scaleSigmaFactor', 0.25)
        params.scaleEstimatorStep = kwargs.get('scaleEstimatorStep', 1.02)
        params.scaleLambda = kwargs.get('scaleLambda', 0.01)
        params.scaleCellSize = kwargs.get('caleCellSize', 4)
        params.numberOfScales = kwargs.get('numberOfScales', 33)

        params.resizeType = kwargs.get('resizeType', 1)
        params.useFhogTranspose = kwargs.get('useFhogTranspose', False)
        params.minArea = kwargs.get('minArea', 10)
        params.maxAreaFactor = kwargs.get('maxAreaFactor', 0.8)
        params.nScalesVot = kwargs.get('nScalesVot', 3)
        params.votMinScaleFactor = kwargs.get('votMinScaleFactor', 0.01)
        params.votMaxScaleFactor = kwargs.get('votMaxScaleFactor', 40)
        params.useCcs = kwargs.get('useCcs', True)

        self.params = params
        self.tracker = KcfTracker(self.params)
        self.initialized = False

    def init(self, image, boundingBox):
        success = self.tracker.reinit(image, boundingBox)

        if success:
            self.initialized = True
        else:
            raise Exception('Unable to initialize KCF tracker with given frame.')

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

    tracker = DSST(enableTrackingLossDetection=True, psrThreshold=10, cellSize=4, padding=2)
    found = True

    failedSuggestions = 0

    detector = cv2.BRISK_create()
    computer = cv2.xfeatures2d.SURF_create()

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    matcher = cv2.BFMatcher()
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
    kp1 = detector.detect(roi, None)

    if len(kp1) == 0:
        print('Warning, no keypoints.')

    kp1, des1 = computer.compute(roi, kp1)

    h, w = roi.shape

    bb = (tl[0], tl[1], br[0]-tl[0], br[1]-tl[1])
    pos = bb
    tracker.init(frame, bb)

    count = 0

    while True:
        frame = eye.getColorFrame()

        found = tracker.update(frame)

        if not found:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            kp2 = detector.detect(gray, None)
            kp2, des2 = computer.compute(gray, kp2)

            matches = matcher.knnMatch(des1, des2, k=2)

            # store all the good matches as per Lowe's ratio test.
            good = []
            for m, n in matches:
                if m.distance < 0.8 * n.distance:
                    good.append(m)

            if len(good) > 10:
                src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1,1,2)
                dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1,1,2)
                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                if M is None:
                    continue

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
                    if failedSuggestions > 1:
                        tracker.init(frame, bb)
                        found = True
                    else:
                        found = tracker.updateAt(frame, bb)

                    if not found:
                        failedSuggestions += 1
                    else:
                        failedSuggestions = 0

        pos = tracker.getBoundingBox()

        if found:
            frame = cv2.rectangle(frame, (int(pos[0]), int(pos[1])), (int(pos[0] + pos[2]), int(pos[1] + pos[3])), (0, 255, 0), 3)
        else:
            frame = cv2.rectangle(frame, (int(pos[0]), int(pos[1])), (int(pos[0] + pos[2]), int(pos[1] + pos[3])), (0, 0, 255), 3)

        count += 1

        cv2.imshow('frame', frame)
        k = cv2.waitKey(1)
        if not k == -1:
            break


def correlation_template_test(camera, start=None, bb=None, sequence=False):
    eye = Eye(camera, sequence)

    if start is not None:
        eye.cap.set(cv2.CAP_PROP_POS_FRAMES, start)

    tracker = DSST(enableTrackingLossDetection=True, psrThreshold=10, cellSize=4, padding=2)
    found = True

    p = Line2DParameters()
    line = Line2D(p)

    if bb is None:
        while True:
            frame = eye.getColorFrame()
            cv2.imshow('preview', frame)
            k = cv2.waitKey(1)
            if not k == -1:
                break

        tl, br = get_rect(frame)

        bb = (tl[0], tl[1], br[0]-tl[0], br[1]-tl[1])

        print(bb)

        if not sequence:
            print(eye.cap.get(cv2.CAP_PROP_POS_FRAMES))
        else:
            print(eye.counter)

    frame = eye.getColorFrame()
    w, h = bb[2], bb[3]

    roi = frame[bb[1]:bb[1]+bb[3], bb[0]:bb[0]+bb[2]]
    index = line.addTemplate(roi, 'track')

    tracker.init(frame, bb)

    count = 0
    updateInterval = 10

    maxTemplates = 100
    templates = {index: 100}

    while True:
        frame = eye.getColorFrame()

        found = tracker.update(frame)
        pos = tracker.getBoundingBox()

        if not found:
            matches = line.match(frame, 75)
            if len(matches) > 0:
                bestMatch = list(matches)[0]
                found = tracker.updateAt(frame, (bestMatch.x, bestMatch.y, bestMatch.width, bestMatch.height))

                if found:
                    templates[bestMatch.template_id] += 1
        else:
            if count > updateInterval:
                if len(templates) == maxTemplates:
                    # Purge old templates.
                    minTimes = min(templates, key=templates.get)

                    line.removeTemplate('track', minTimes)
                    del[minTimes]

                roi = frame[pos[1]:pos[1]+pos[3], pos[0]:pos[0]+pos[2]]
                index = line.addTemplate(roi, 'track')
                templates[index] = 0

                count = 0

        if found:
            frame = cv2.rectangle(frame, (int(pos[0]), int(pos[1])), (int(pos[0] + pos[2]), int(pos[1] + pos[3])), (0, 255, 0), 3)
        else:
            frame = cv2.rectangle(frame, (int(pos[0]), int(pos[1])), (int(pos[0] + pos[2]), int(pos[1] + pos[3])), (0, 0, 255), 3)

        count += 1

        cv2.imshow('frame', frame)
        k = cv2.waitKey(1)
        k = chr(k & 255)

        if k == 'q':
            data = line.exportClass('track')
            file = open('track.yaml', 'w')
            file.write(data)
            file.close()
            break


frameNumber = 0
saveFolder = 'C:/users/bobbyluig/desktop/kenneth'
save = False


def showSave(name, image):
    global frameNumber, save

    cv2.imshow(name, image)

    if save:
        fileName = os.path.join(saveFolder, '%04d.png' % frameNumber)
        cv2.imwrite(fileName, image)

        frameNumber += 1


def kenneth():
    from PIL import Image, ImageFont, ImageDraw, ImageOps

    eye = Eye('C:\\Users\\bobbyluig\\Desktop\\Eclipse Large\\k.mp4')

    tracker = DSST(enableTrackingLossDetection=True, psrThreshold=10, cellSize=4, padding=2)
    found = True

    font = ImageFont.truetype("arialbd.ttf", 14)
    largeFont = ImageFont.truetype("arial.ttf", 50)

    strip = Image.new('RGB', (1280, 80), (0, 0, 0))
    draw = ImageDraw.Draw(strip)

    msg = 'Waiting for Tracker Initialization'
    tW, tH = draw.textsize(msg, font=largeFont)
    draw.text(((1280 - tW) / 2, (80 - tH) / 2), msg, font=largeFont, fill='white')

    while eye.cap.get(cv2.CAP_PROP_POS_FRAMES) < 209:
        frame = eye.getColorFrame()
        strip = np.array(strip)
        frame = np.concatenate((frame, strip), axis=0)

        showSave('frame', frame)

        k = cv2.waitKey(20)
        if not k == -1:
            break

    bb = (529, 102, 159, 249)
    frame = eye.getColorFrame()
    w, h = bb[2], bb[3]

    roi = frame[bb[1]:bb[1]+bb[3], bb[0]:bb[0]+bb[2]]
    roi = cv2.resize(roi, (w // 5, h // 5))
    template = cv2.Canny(roi, 50, 200)

    tracker.init(frame, bb)

    count = 0
    updateInterval = 10

    maxTemplates = 10
    templates = [template] + [None] * (maxTemplates - 1)
    templateUses = [100] + [0] * (maxTemplates - 1)

    while True:
        frame = eye.getColorFrame()

        found = tracker.update(frame)
        pos = tracker.getBoundingBox()

        tmp = cv2.resize(frame, (0,0), fx=0.2, fy=0.2)
        gray = cv2.cvtColor(tmp, cv2.COLOR_BGR2GRAY)
        edged = cv2.Canny(gray, 50, 200)
        values = np.array([])
        locs = []
        for template in templates:
            if template is not None:
                res = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF_NORMED)
                _, maxVal, _, maxLoc = cv2.minMaxLoc(res)
                values = np.append(values, maxVal)
                locs.append(maxLoc)

        index = np.argmax(values)
        maxLoc = locs[index]

        orangeIndex = None
        greenIndex = None

        if not found:
            if values[index] > 0.15:
                found = tracker.updateAt(frame, (maxLoc[0] * 5, maxLoc[1] * 5, pos[2], pos[3]))
                frame = cv2.rectangle(frame, (maxLoc[0] * 5, maxLoc[1] * 5),
                                      (int(maxLoc[0] * 5 + round(pos[2])), int(maxLoc[1] * 5 + round(pos[3]))), (255, 0, 255), 3)
                orangeIndex = index

            if found:
                templateUses[index] += 10
        else:
            if ((maxLoc[0] * 5 - pos[0])**2 + (maxLoc[1] * 5 - pos[1])**2) ** (1/2) < 90:
                templateUses[index] += 1
                greenIndex = index

            if count > updateInterval:
                if templates.count(None) == 0:
                    # Purge old templates.
                    minTimes = min(templateUses)
                    index = templateUses.index(minTimes)

                    templates[index] = None
                    templateUses[index] = 0

                if cv2.Laplacian(frame, cv2.CV_64F).var() > 50:
                    roi = frame[pos[1]:pos[1]+pos[3], pos[0]:pos[0]+pos[2]]
                    roi = cv2.resize(roi, (w // 5, h // 5))
                    template = cv2.Canny(roi, 50, 200)

                    freeIndex = templates.index(None)
                    templates[freeIndex] = template
                    # cv2.imshow('template', template)
                else:
                    print('Blurry frame. Discounted.')

                count = 0

        if found:
            frame = cv2.rectangle(frame, (int(pos[0]), int(pos[1])), (int(pos[0] + pos[2]), int(pos[1] + pos[3])), (0, 255, 0), 3)
        else:
            frame = cv2.rectangle(frame, (int(pos[0]), int(pos[1])), (int(pos[0] + pos[2]), int(pos[1] + pos[3])), (0, 0, 255), 3)

        strip = Image.new('RGB', (1280, 80), (0, 0, 0))
        draw = ImageDraw.Draw(strip)

        offset = 5
        for i in range(20):
            if templates[i] is not None:
                template = Image.fromarray(templates[i])
                template = template.convert('RGB')

                if orangeIndex == i:
                    template = ImageOps.expand(template, border=2, fill=(255, 0, 255))
                    strip.paste(template, (offset - 2, 6 - 2))
                elif greenIndex == i:
                    template = ImageOps.expand(template, border=2, fill=(0, 255, 0))
                    strip.paste(template, (offset - 2, 6 - 2))
                else:
                    strip.paste(template, (offset, 6))

                msg = str(templateUses[i])
                tW, tH = draw.textsize(msg, font=font)
                draw.text((offset + (31 - tW) / 2, 61), msg, font=font, fill='white')

            offset += 31 + 30 + 4

        count += 1

        strip = np.array(strip)
        frame = np.concatenate((frame, strip), axis=0)

        showSave('frame', frame)
        k = cv2.waitKey(1)
        if not k == -1:
            break

    '''
    i = 0
    for template in templates:
        cv2.imwrite('%s.png' % i, template)

        i += 1
    '''


def makeBB(array):
    x = array[::2]
    y = array[1::2]

    x0 = int(min(x))
    x1 = int(max(x))
    y0 = int(min(y))
    y1 = int(max(y))

    return (x0, y0, x1 - x0, y1 - y0)


# correlation_template_test('C:\\Users\\bobbyluig\\Desktop\\Eclipse Large\\k.mp4', 209, (529, 102, 159, 249))
correlation_template_test(0  )
# correlation_template_test('C:/users/bobbyluig/desktop/vot2015/tunnel/%08d.jpg', bb=makeBB([328.000,339.000,350.000,339.000,350.000,308.000,328.000,308.000]), sequence=True)
# kenneth()