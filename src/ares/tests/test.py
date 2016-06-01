from ares.main import Ares
from cerebral.pack1.hippocampus import Android


camera = Android.camera
robot = Android.robot
info = Android.info

ares = Ares(robot, camera, info)
data = ares.compute_vector(40000, 30000, 500, -10)
print(data)