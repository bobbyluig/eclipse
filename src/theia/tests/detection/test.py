from oculus import Line2D, Line2DParameters, Match
import cv2
import time


p = Line2DParameters()
line = Line2D(p)


def cam():
    camera = cv2.VideoCapture(0)

    while True:
        _, frame = camera.read()
        line.test(frame)
        cv2.waitKey(1)


def image():
    frame = cv2.imread('duck.jpg')
    template = cv2.imread('roi.jpg')

    line.addTemplate(template, 'duck')
    t = line.exportTemplate('duck', 0)

    line.removeTemplate('duck', 0)
    line.importTemplate(t)

    matches = line.match(frame, 80)
    print(list(matches))

image()
