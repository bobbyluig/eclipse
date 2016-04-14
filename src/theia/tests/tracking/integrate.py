import cv2
from theia.main import Oculus, Theia
from theia.eye import Eye


oculus = Oculus()
eye = Eye(0)

while True:
    frame = eye.get_color_frame()
    cv2.imshow('preview', frame)
    k = cv2.waitKey(1)

    if not k == -1:
        break

frame = eye.get_color_frame()
tl, br = Theia.get_rect(frame)
bb = (tl[0], tl[1], br[0] - tl[0], br[1] - tl[1])

oculus.initialize(frame, bb)

while True:
    frame = eye.get_color_frame()
    found, pos = oculus.track(frame)

    if found:
        frame = cv2.rectangle(frame, (int(pos[0]), int(pos[1])), (int(pos[0] + pos[2]), int(pos[1] + pos[3])),
                              (0, 255, 0), 3)
    else:
        frame = cv2.rectangle(frame, (int(pos[0]), int(pos[1])), (int(pos[0] + pos[2]), int(pos[1] + pos[3])),
                              (0, 0, 255), 3)

    cv2.imshow('frame', frame)
    k = cv2.waitKey(1)

    if not k == -1:
        break