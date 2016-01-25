from asyncio import coroutine
import asyncio, cv2, base64
from autobahn.asyncio.wamp import ApplicationSession
import numpy as np
from shared.cerebral.autoreconnect import ApplicationRunner

__author__ = 'Lujing Cen'

cap = cv2.VideoCapture(0)


def getFrame():
    ret, frame = cap.read()
    frame = cv2.resize(frame, (0,0), fx=0.75, fy=0.75)
    # frame = cv2.inRange(frame, np.array((20, 50, 100)), np.array((180, 255, 255)))
    # frame = cv2.erode(frame, np.ones((5, 5), np.uint8), iterations=1)
    # frame = cv2.dilate(frame, np.ones((5, 5), np.uint8), iterations=3)
    # cv2.imwrite('../crossbar/test.jpg', frame)
    ret, buf = cv2.imencode('.jpg', frame)
    b64 = base64.standard_b64encode(buf)
    return b64.decode()


class MyComponent(ApplicationSession):
    @coroutine
    def onJoin(self, details):
        print('Done!')

        while True:
            yield from self.getFrame()
            yield from asyncio.sleep(1/30)

    @coroutine
    def getFrame(self):
        data = getFrame()
        self.publish('com.image', data)

    @coroutine
    def onDisconnect(self):
        print('Connection lost. Attempting to regain.')

if __name__ == '__main__':
    runner = ApplicationRunner(url='ws://localhost:8080/ws', realm='lycanthrope')
    runner.run(MyComponent)
