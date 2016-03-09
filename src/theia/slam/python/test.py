from pyslam import System, TrackerParams, Tracking
import cv2
import time

cap = cv2.VideoCapture(0)

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

print('Starting system.')

system = System()
success1 = system.load('voc.txt')
success2 = system.start()

if not success1 or not success2:
	print('Failed to load vocabulary!')
	
	
tracker = Tracking(params, 0)
system.bind_tracker(tracker)

while True:
	_, frame = cap.read()
	tracker.grab_one(frame, time.time())
	print(tracker.get_state())