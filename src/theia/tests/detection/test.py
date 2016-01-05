from oculus import Line2DParameters, Line2D
import cv2
import time


p = Line2DParameters()
p.useGaussian = True
line = Line2D(p)


def cam():
    camera = cv2.VideoCapture(0)

    while True:
        _, frame = camera.read()
        line.test(frame)
        cv2.waitKey(1)


def image():
    frame = cv2.imread('duck.jpg')
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    template = cv2.imread('roi.jpg')
    # template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    line.test2(frame, template)

image()
