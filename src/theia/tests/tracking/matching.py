import cv2
from theia.matcher import LineMatcher

matcher = LineMatcher()
duck = cv2.imread('theia/src/tests/tracking/duck.jpg')
template = cv2.imread('theia/src/tests/tracking/roi.jpg')


id = matcher.add_template(template, 'duck')
matches = matcher.match(duck, 80)

for match in matches:
    print(match.x, match.y)