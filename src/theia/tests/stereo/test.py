import cv2
import threading
import numpy as np

k = np.array([[795.690125, 0, 335.536987],
              [0, 802.111267, 225.562576],
              [0, 0, 1]])
d = np.array([-0.0019273272, 0.3212610781, 0.0141755575, 0.0021216469])
newcamera, roi = cv2.getOptimalNewCameraMatrix(k, d, (640, 480), 1)

stereo = cv2.StereoSGBM_create(0, 16, 21)

left = cv2.VideoCapture(1)
right = cv2.VideoCapture(0)

l = None
r = None

def read_left():
    global l, left, newcamera

    while True:
        _, x = left.read()
        l = cv2.undistort(x, k, d, None, newcamera)

def read_right():
    global r, right, newcamera

    while True:
        _, x = right.read()
        x = cv2.flip(x, -1)
        r = cv2.undistort(x, k, d, None, newcamera)

x = threading.Thread(target=read_left)
x.start()
y = threading.Thread(target=read_right)
y.start()

while True:
    if l is not None and r is not None:
        disparity = stereo.compute(cv2.cvtColor(l, cv2.COLOR_BGR2GRAY), cv2.cvtColor(r, cv2.COLOR_BGR2GRAY))
        disparity = cv2.convertScaleAbs(disparity)
        cv2.imshow('disparity', disparity)
        cv2.imshow('left', l)
        cv2.imshow('right', r)

        cv2.waitKey(1)