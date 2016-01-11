from oculus import Saliency
import cv2

s = Saliency(1920, 1080)
cap = cv2.VideoCapture('C:/Users/bobbyluig/Desktop/Eclipse Large/tracking/tennis3.mp4')

while True:
    _, frame = cap.read()
    saliency = s.compute(frame)
    cv2.imshow('saliency', saliency)

    cv2.waitKey(1)