import cv2
from theia.matcher import LineMatcher

matcher = LineMatcher()
duck = cv2.imread('duck.png')
template = cv2.imread('roi.png')


id = matcher.add_template(template, 'duck')
matches = matcher.match(duck, 80)

for match in matches:
    print(match.x, match.y)