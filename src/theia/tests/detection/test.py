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
    start = time.time()
    for i in range(100):
        cv2.Canny(frame, 50, 200)
        # line.test2(frame, template)
    print(time.time() - start)
    cv2.imshow("original", cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED))
    cv2.waitKey(0)

image()
