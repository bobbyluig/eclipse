import numpy as np
import cv2

MIN_MATCH_COUNT = 10

img1 = cv2.imread('book2.jpg',0)		  # queryImage
img2 = cv2.imread('floor.jpg',0) # trainImage

color1 = cv2.imread('book2.jpg')
color2 = cv2.imread('floor.jpg')

# Initiate SIFT detector
orb = cv2.ORB_create(20000)

# find the keypoints and descriptors with SIFT
kp1, des1 = orb.detectAndCompute(img1,None)
kp2, des2 = orb.detectAndCompute(img2,None)

matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
matches = matcher.knnMatch(des1, trainDescriptors = des2, k = 2)


# store all the good matches as per Lowe's ratio test.
good = []
for m,n in matches:
	if m.distance < 0.8*n.distance:
		good.append(m)
		
if len(good)>MIN_MATCH_COUNT:
	src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
	dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

	M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
	matchesMask = mask.ravel().tolist()

	h,w = img1.shape
	pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
	dst = cv2.perspectiveTransform(pts,M)

	color2 = cv2.polylines(color2, [np.int32(dst)], True, (0, 255, 0), thickness=25)

else:
	print("Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT))
	matchesMask = None

cv2.imwrite('color2.jpg', color2)