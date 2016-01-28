import numpy as np
import cv2

__author__ = 'Lujing Cen'

# 0, 144, 168, 113, 255, 251 Triangle
#

'''
def nothing(x):
    pass

cv2.namedWindow('hsv', cv2.WINDOW_NORMAL)
cv2.namedWindow('img', cv2.WINDOW_NORMAL)
cv2.createTrackbar('h_min', 'hsv', 144, 180, nothing)
cv2.createTrackbar('h_max', 'hsv', 255, 180, nothing)
cv2.createTrackbar('s_min', 'hsv', 90, 255, nothing)
cv2.createTrackbar('s_max', 'hsv', 255, 255, nothing)
cv2.createTrackbar('v_min', 'hsv', 100, 255, nothing)
cv2.createTrackbar('v_max', 'hsv', 255, 255, nothing)
'''

'''
img = cv2.imread('shape.jpg')
img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
hsv = cv2.blur(hsv, (3, 3))
hsv = cv2.inRange(hsv, (0, 144, 168), (113, 255, 251))
hsv = cv2.dilate(hsv, np.ones((5, 5), np.uint8), iterations=3)
'''

img = cv2.imread('shape.jpg')
img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.medianBlur(gray, 5)
canny = cv2.Canny(gray, 50, 100)
cv2.imwrite('canny.jpg', canny)

font = cv2.FONT_HERSHEY_SIMPLEX

# ret, thresh = cv2.threshold(hsv, 127, 255, 1)
# img, contours, h = cv2.findContours(thresh, 1, 2)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
hsv = cv2.blur(hsv, (3, 3))
hsv = cv2.inRange(hsv, (0, 144, 168), (113, 255, 251))
canny = cv2.Canny(hsv, 50, 100)

canny = cv2.dilate(canny, np.ones((5, 5), np.uint8), iterations=2)
canny, conts, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

for c in conts:
    approx = cv2.approxPolyDP(c, 0.01*cv2.arcLength(c, True), True)
    if len(approx) == 3:
        cv2.drawContours(img, [c], -1, (0, 255, 0), 3)
        m = cv2.moments(c)
        x, y = int(m['m10']/m['m00']), int(m['m01']/m['m00'])
        cv2.rectangle(img, (x - 5, y - 5), (x + 5, y + 5), (0, 0, 255), -1)
        cv2.putText(img, 'Triangle', (x + 20, y + 20), font, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(img, '(%d, %d)' % (x, y), (x + 20, y - 10), font, 0.6, (255, 255, 255), 2, cv2.LINE_AA)


circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100)

if circles is not None:
    circles = np.round(circles[0, :]).astype("int")
    for (x, y, r) in circles:
        cv2.circle(img, (x, y), r, (0, 255, 0), 3)
        cv2.rectangle(img, (x - 5, y - 5), (x + 5, y + 5), (0, 0, 255), -1)
        cv2.putText(img, 'Circle', (x + 50, y + 20), font, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(img, '(%d, %d)' % (x, y), (x + 50, y - 10), font, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

cv2.imwrite('shape_out.jpg', img)

cv2.imshow('img1', img)
cv2.waitKey(0)

cv2.destroyAllWindows()