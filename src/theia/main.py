import cv2
import numpy as np

from cerebral import logger as l
import logging

import time

from theia.tracker import DSST
from theia.matcher import LineMatcher
from theia.util import CIE76

from concurrent.futures import ThreadPoolExecutor
from threading import Lock

logger = logging.getLogger('universe')


class Oculus:
    def __init__(self):
        # Create tracker.
        self.tracker = DSST(enableTrackingLossDetection=True, psrThreshold=10, cellSize=4, padding=2)

        # Create matcher.
        self.matcher = LineMatcher()

        # Template scoring dictionary.
        self.scores = {}

        # Threading.
        self.matcher_lock = Lock()
        self.executor = ThreadPoolExecutor(max_workers=2)

        # Variables.
        self.count = 0
        self.initialized = False
        self.found = False

        # Settings.
        self.class_id = 'prey'          # Class ID for tracker.
        self.max_templates = 200        # Maximum number of templates in the database.
        self.threshold = 80             # Minimum acceptable matcher threshold.
        self.insert_interval = 10       # Minimum number of frames between template insertion.
        self.rank_interval = 5          # Minimum number of frames between rank.

    def initialize(self, frame, bb):
        """
        Initialize the Oculus tracking system.
        :param frame: The input frame.
        :param bb: The bounding box in (x, y, w, h).
        """

        if self.initialized:
            return

        # Initialize tracker.
        self.tracker.init(frame, bb)
        self.count = 1
        self.found = True

        # Initialize matcher.
        roi = self.get_roi(frame, bb)

        # Create initial template with high bias.
        self.executor.submit(self.insert_template, roi, score=10)

        # Initialization is complete.
        self.initialized = True

    def track(self, frame):
        """
        Track one frame. Must be used after initialization.
        :param frame: A color image.
        :return: (success, bb) where bb is (x, y, w, h).
        """

        if not self.initialized:
            return None, None

        if len(self.scores) >= self.max_templates:
            self.executor.submit(self.clean)

        self.found = self.tracker.update(frame)
        bb = self.tracker.get_bounding_box()

        if not self.found:
            # Tracking lost. Attempt recovery.
            matches = self.matcher.match(frame, self.threshold)

            if len(matches) > 0:
                best = matches[0]
                self.found = self.tracker.update_at(frame, (best.x, best.y, best.width, best.height))

                if self.found:
                    template_id = best.template_id
                    score = 2 * best.similarity / self.matcher.num_templates_in_class(self.class_id)
                    self.scores[template_id] += score

        else:
            if self.count % self.insert_interval == 0:
                # Reached insert interval. Priority over rank.
                roi = self.get_roi(frame, bb)
                self.executor.submit(self.insert_template, roi)

            if self.count % self.rank_interval == 0:
                # Reached rank interval.
                self.executor.submit(self.rank, frame)

            if self.count > max(self.rank_interval, self.insert_interval):
                # Reset counter.
                self.count = 1

        # Advance one.
        self.count += 1

        return self.found, bb

    def rank(self, frame):
        """
        Rank templates currently in database.
        :param frame: The current frame, where target is known to exist.
        """

        with self.matcher_lock:
            matches = self.matcher.match(frame, self.threshold)

            for match in matches:
                # Scale score based on number of entries.
                score = (match.similarity - self.threshold) / self.matcher.num_templates_in_class(self.class_id)
                template_id = match.template_id
                self.scores[template_id] += score

    def insert_template(self, template, score=0):
        """
        Insert a template.
        :param template: The template to be inserted.
        :param score: Initial score. Change to bias.
        """

        with self.matcher_lock:
            template_id = self.matcher.add_template(template, self.class_id)
            self.scores[template_id] = score

    def remove_template(self, template_id):
        """
        Remove a template.
        :param template_id: The template ID.
        """

        with self.matcher_lock:
            self.matcher.remove_template(self.class_id, template_id)
            del self.scores[template_id]

    @staticmethod
    def get_roi(image, bb):
        """
        Gets ROI from bounding box.
        :param image: Input image.
        :param bb: Bounding box in (x, y, w, h).
        :return: The ROI.
        """

        y0, y1 = int(round(bb[1])), int(round(bb[1] + bb[3]))
        x0, x1 = int(round(bb[0])), int(round(bb[0] + bb[2]))

        return image[y0:y1, x0:x1]

    def clean(self):
        """
        Purge low rank templates.
        Call when there is some time and templates are either full or about to be full.
        """

        with self.matcher_lock:
            if len(self.scores) < 5:
                return

            # Compute mean.
            mean = sum(self.scores.values()) / len(self.scores)

            # Get bad indices.
            bad = [template_id for (template_id, score) in self.scores.items() if score < mean]

            for template_id in bad:
                self.matcher.remove_template(self.class_id, template_id)
                del self.scores[template_id]


class Theia:
    @staticmethod
    def get_sand_color(image):
        """
        Returns the color of sand in a given image.
        :param image: The image ROI as an 8-bit numpy array.
        :return: The sand color name.
        """

        image = np.float32(image / 255)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

        lab = cv2.mean(image)[:3]
        lab = np.array(lab)

        labs = np.array([
            (29.7821,  58.9401, -36.4980),  # Purple
            (74.9322,  23.9359,  78.9565),  # Orange
            (46.2288, -51.6991,  49.8975)   # Green
        ])

        colors = ['purple', 'orange', 'green']

        distances = CIE76(lab, labs)
        index = np.argmin(distances)

        return colors[index]

    @staticmethod
    def get_foreground(eye, frames, blur=True):
        """
        Gets the foreground given an eye object.
        This uses the MOG2 background/foreground segmentation algorithm.
        This allows for identification of moving PreyBOTS.
        :param eye: An eye (camera) object.
        :param frames: The number of initial frames to capture.
        :param blur: Apply a smoothing gaussian blur to remove grains.
        :return: A binary image, where white is the foreground object.
        """

        subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
        ksize = (5, 5)

        for i in range(frames):
            frame = eye.get_color_frame()
            if blur:
                frame = cv2.GaussianBlur(frame, ksize, 0)
            subtractor.apply(frame)

        frame = eye.get_color_frame()
        if blur:
            frame = cv2.GaussianBlur(frame, ksize, 0)
        mask = subtractor.apply(frame)

        return mask

    @staticmethod
    def bound_blobs(image, count, order=False):
        """
        Get n blobs with the largest area.
        Ues only with binary images.
        :param image: A binary image.
        :param count: The number of blobs to find.
        :param order: Order from largest to smallest.
        :return: An array of bounding rectangles.
        """

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

    @staticmethod
    def data_optical_flow(frame1, frame2, blobs):
        """
        Dense optical flow using Farneback.
        This identifies blobs, directions, & velocities of moving PreyBOTs.
        Takes two colored frames and an array of blobs.
        Detection based on edges and NOT color.
        :param frame1: The first frame.
        :param frame2: The second frame.
        :param blobs: An array of blobs.
        :return: An array of format (averageMagnitude, averageAngle)
        """

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
    def graphic_optical_flow(frame1, frame2):
        """
        Computes the optical flow for the entire image.
        :param frame1: The first frame.
        :param frame2: The second frame.
        :return: A BGR image.
        """

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

    @staticmethod
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