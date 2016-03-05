import cv2
import numpy as np


def feature_tracking(img1, img2, kp1):
    kp2, st, err = cv2.calcOpticalFlowPyrLK(img1, img2, kp1, None, **lk_params)

    kp1 = kp1[st == 1]
    kp2 = kp2[st == 1]

    return kp1, kp2

fast = cv2.FastFeatureDetector_create(20)

lk_params = dict(winSize  = (21, 21),
                 maxLevel = 3,
                 criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))

img1 = cv2.imread('KITTI_VO/00/image_2/%06d.png' % 0)
img2 = cv2.imread('KITTI_VO/00/image_2/%06d.png' % 1)

img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

kp1 = fast.detect(img1)

kp1, kp2 = feature_tracking(img1, img2, kp1)

focal = 718.8560
pp = (607.1928, 185.2157)

_, E = cv2.findEssentialMat(kp2, kp1, focal=focal, pp=pp, method=cv2.RANSAC, prob=0.999, threshold=1.0)
_, R, t, mask = cv2.recoverPose(E, kp2, kp1, focal=focal, pp=pp)






