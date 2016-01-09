from oculus import Line2D, Line2DParameters
import cv2
import numpy as np


def getRectangle(im, title='get_rect'):
    mouse_params = {'tl': None, 'br': None, 'current_pos': None,
        'released_once': False}

    cv2.namedWindow(title)
    cv2.moveWindow(title, 100, 100)

    def onMouse(event, x, y, flags, param):

        param['current_pos'] = (x, y)

        if param['tl'] is not None and not (flags & cv2.EVENT_FLAG_LBUTTON):
            param['released_once'] = True

        if flags & cv2.EVENT_FLAG_LBUTTON:
            if param['tl'] is None:
                param['tl'] = param['current_pos']
            elif param['released_once']:
                param['br'] = param['current_pos']

    cv2.setMouseCallback(title, onMouse, mouse_params)
    cv2.imshow(title, im)

    while mouse_params['br'] is None:
        im_draw = np.copy(im)

        if mouse_params['tl'] is not None:
            cv2.rectangle(im_draw, mouse_params['tl'], mouse_params['current_pos'], (255, 0, 0))

        cv2.imshow(title, im_draw)
        _ = cv2.waitKey(10)

    cv2.destroyWindow(title)

    tl = (min(mouse_params['tl'][0], mouse_params['br'][0]),
        min(mouse_params['tl'][1], mouse_params['br'][1]))
    br = (max(mouse_params['tl'][0], mouse_params['br'][0]),
        max(mouse_params['tl'][1], mouse_params['br'][1]))

    return tl, br


def detect(source, classId):
    p = Line2DParameters()
    line = Line2D(p)

    try:
        file = open('%s.yaml' % classId, 'r')
        data = file.read()
        if len(data) > 0:
            line.importClass(data)
            print('Imported!')
    except:
        print('Unable to load!')

    camera = cv2.VideoCapture(source)

    while True:
        _, frame = camera.read()

        matches = line.match(frame, 70)
        matches = list(matches)

        for match in matches[:2]:
            frame = cv2.circle(frame, (match.x + match.width // 2, match.y + match.height // 2), 10, (0, 0, 255), -1)

        cv2.imshow('matches', frame)

        c = cv2.waitKey(1)
        c = chr(c & 255)

        if c == 'q':
            break


def train(source, classId):
    p = Line2DParameters()
    line = Line2D(p)

    try:
        file = open('%s.yaml' % classId, 'r')
        data = file.read()
        if len(data) > 0:
            line.importClass(data)
            print('Imported!')
    except:
        pass

    camera = cv2.VideoCapture(source)


    while True:
        _, frame = camera.read()
        cv2.imshow('training', frame)

        c = cv2.waitKey(1)
        c = chr(c & 255)

        if c == 'q':
            data = line.exportClass(classId)
            file = open('%s.yaml' % classId, 'w')
            file.write(data)
            file.close()
            break
        elif c == 'd':
            count = line.numTemplatesInClass(classId)
            if count > 0:
                line.removeTemplate(classId, count - 1)
                print('Previous template deleted!')
        elif c == 'n':
            tl, br = getRectangle(frame)
            roi = frame[tl[1]:br[1], tl[0]:br[0]]
            index = line.addTemplate(roi, classId)
            print('Added template %s' % index)


detect(0, '../tracking/track')