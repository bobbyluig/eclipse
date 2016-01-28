import cv2
import numpy as np
import common

__author__ = 'Lujing Cen'


class Tracker:
    def __init__(self):
        self.targets = []

    @staticmethod
    def add_target(self, frame, rect):
        x0, y0, x1, y1 = rect
        roi = frame[y0:y1, x0:x1]
        # roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        roi = cv2.GaussianBlur(roi, (5, 5), 2)
        hsvPlane = cv2.split(roi)
        mean, standev = cv2.meanStdDev(hsvPlane[0])

        minHue = mean[0] - standev[0] * 3
        maxHue = mean[0] + standev[0] * 3

        new = cv2.inRange(frame, np.array((minHue[0], 0, 0)), np.array((maxHue[0], 255, 255)))

        # e_kernal = np.ones((5, 5), np.uint8)
        # new = cv2.erode(new, e_kernal)

        # d_kernal = np.ones((20, 20), np.uint8)
        # new = cv2.dilate(new, d_kernal)

        cv2.imshow('roi', roi)
        cv2.imshow('new', new)

    def track(self, frame):
        return self.targets


class App:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)

        self.frame = None
        self.paused = False
        self.tracker = Tracker()
        self.hsv = [0, 0, 0, 0, 0, 0]

        cv2.namedWindow('track')
        cv2.namedWindow('hsv')

        cv2.createTrackbar('h_min', 'hsv', 144, 255, self.nothing)
        cv2.createTrackbar('h_max', 'hsv', 255, 255, self.nothing)
        cv2.createTrackbar('s_min', 'hsv', 90, 255, self.nothing)
        cv2.createTrackbar('s_max', 'hsv', 255, 255, self.nothing)
        cv2.createTrackbar('v_min', 'hsv', 100, 255, self.nothing)
        cv2.createTrackbar('v_max', 'hsv', 255, 255, self.nothing)

        self.rect_sel = common.RectSelector('track', self.on_rect)

    def on_rect(self, rect):
        self.tracker.add_target(self.frame, rect)

    def update_hsv(self):
        self.hsv[0] = cv2.getTrackbarPos('h_min', 'hsv')
        self.hsv[1] = cv2.getTrackbarPos('h_max', 'hsv')
        self.hsv[2] = cv2.getTrackbarPos('s_min', 'hsv')
        self.hsv[3] = cv2.getTrackbarPos('s_max', 'hsv')
        self.hsv[4] = cv2.getTrackbarPos('v_min', 'hsv')
        self.hsv[5] = cv2.getTrackbarPos('v_max', 'hsv')

    def nothing(self, x):
        pass

    def run(self):
        while True:
            playing = not self.paused and not self.rect_sel.dragging
            if playing or self.frame is None:
                ret, frame = self.cap.read()
                if not ret:
                    break
                self.frame = frame.copy()

            if playing:
                tracked = self.tracker.track(self.frame)
                for item in tracked:
                    continue

            self.update_hsv()

            hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
            hsv = cv2.blur(hsv, (3, 3))
            hsv = cv2.inRange(hsv, np.array((self.hsv[0], self.hsv[2], self.hsv[4])), np.array((self.hsv[1], self.hsv[3], self.hsv[5])))
            hsv = cv2.dilate(hsv, np.ones((5, 5), np.uint8), iterations=3)
            cv2.imshow('hsv_result', hsv)

            final = self.frame.copy()
            _, contours, hierarchy = cv2.findContours(hsv, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            max_area = 0
            contour = None
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > max_area:
                    max_area = area
                    contour = cnt

            if contour is not None:
                M = cv2.moments(contour)
                cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
                cv2.circle(final, (cx, cy), 5, (0, 255, 0), thickness=2)

            cv2.imshow('final', final)

            vis = self.frame.copy()
            self.rect_sel.draw(vis)
            cv2.imshow('track', vis)

            ch = cv2.waitKey(int(1000/30)) & 0xFF
            if ch == ord(' '):
                self.paused = not self.paused
            if ch == 27:
                break

if __name__ == '__main__':
    App().run()