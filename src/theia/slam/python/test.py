from pyslam import *
import cv2
import time
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

cap = cv2.VideoCapture(0)

mSensor = eSensor.MONOCULAR

params = TrackerParams()
params.fx = 795.690125
params.fy = 802.111267
params.cx = 335.536987
params.cy = 225.562576
params.k1 = -0.0019273272
params.k2 = 0.3212610781
params.p1 = 0.0141755575
params.p2 = 0.0021216469

params.fps = 30.0
params.rgb = False


# Load vocabulary.
mpVocabulary = ORBVocabulary()
bVocLoaded = mpVocabulary.load2('voc.txt')
if not bVocLoaded:
	print('Unable to load vocabulary!')
	sys.exit(0)

	
# Create objects.
print('Creating objects.')
mpKeyFrameDatabase = KeyFrameDatabase(mpVocabulary)
mpMap = Map()
mpTracker = Tracking(mpVocabulary, mpMap, mpKeyFrameDatabase, params, mSensor)
mpLocalMapper = LocalMapping(mpMap, mSensor == eSensor.MONOCULAR)
mpLoopCloser = LoopClosing(mpMap, mpKeyFrameDatabase, mpVocabulary, mSensor != eSensor.MONOCULAR)

# Set pointers.
print('Setting pointers.')
mpTracker.set_local_mapper(mpLocalMapper)
mpTracker.set_loop_closer(mpLoopCloser)
mpLocalMapper.set_loop_closer(mpLoopCloser)
mpLoopCloser.set_local_mapper(mpLocalMapper)

# Start all threads.
print('Starting modules.')
mpLocalMapper.run()
mpLoopCloser.run()

# Create 3D plotter.
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')

# Main loop.
i = 0
while i < 500:
	_, frame = cap.read()
	p = mpTracker.grab_one(frame, time.time())
	if p is not None:
		print(i, p.ravel())
		ax.scatter(p[2], -p[0])
		i += 1

plt.show()