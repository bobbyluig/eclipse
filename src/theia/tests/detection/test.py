from oculus import Line2D, Line2DParameters, Match
import cv2
import time
import os
import psutil


p = Line2DParameters()
p.pyramid = [5, 5, 5]
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

    process = psutil.Process(os.getpid())
    startMem = process.memory_info().rss

    for i in range(1000):
        line.addTemplate(template, 'duck')

    print(process.memory_info().rss - startMem)

    '''
    start = time.time()
    for i in range(100):
        matches = line.match(frame, 80)
    print((time.time() - start) / 100)
    '''


def cv():
    total = 0
    frame = cv2.imread('duck.jpg')
    template = cv2.imread('roi.jpg')
    template = cv2.Canny(template, 50, 100)
    cv2.imwrite('roi.png', template)

    start = time.time()
    for i in range(1000):
        cv2.Canny(template, 50, 100)
    print(time.time() - start)

    # template = cv2.Canny(template, 50, 200)

    '''
    start = time.time()
    for i in range(2000):
        matches = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        cv2.minMaxLoc(matches)
    total += time.time() - start

    print(total)
    '''

cv()


