from oculus import Saliency
import cv2

s = Saliency(640, 480)
cap = cv2.VideoCapture(0)

while True:
    _, frame = cap.read()
    saliency = s.compute(frame)
    cv2.imshow('saliency', saliency)

    cv2.waitKey(1)