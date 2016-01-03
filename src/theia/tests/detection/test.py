from oculus import Line2DParameters, Line2D
import cv2


cap = cv2.VideoCapture(0)

p = Line2DParameters()
line = Line2D(p)

_, frame = cap.read()

line.test(frame)

cv2.waitKey(0)