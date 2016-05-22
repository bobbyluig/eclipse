from cerebral.pack.hippocampus import Android
import numpy as np

robot = Android.robot
body = robot.body

off = [
    np.array([True, False, False, False]),
    np.array([False, True, False, False]),
    np.array([False, False, True, False]),
    np.array([False, False, False, True])
]

next_frame = [
    np.array([(0, 0, -11), (0, 0, -13), (0, 0, -13), (0, 0, -13)]),
    np.array([(0, 0, -13), (0, 0, -11), (0, 0, -13), (0, 0, -13)]),
    np.array([(0, 0, -13), (0, 0, -13), (0, 0, -11), (0, 0, -13)]),
    np.array([(0, 0, -13), (0, 0, -13), (0, 0, -13), (0, 0, -11)])
]

for i in range(4):
    body.adjust_crawl(off[i], next_frame[i])