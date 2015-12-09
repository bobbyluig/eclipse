from oculus import DsstParameters, DsstTracker, KcfParameters, KcfTracker
import cv2


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

    def update(self, image):
        return self.tracker.update(image)

    def updateAt(self, image, boundingBox):
        return self.tracker.updateAt(image, boundingBox)

    def getBoundingBox(self):
        return self.tracker.getBoundingBox()

    def getCenter(self):
        return self.tracker.getCenter()