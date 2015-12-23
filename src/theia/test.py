import cv2
import numpy as np


def kMeansImage(image, k=3):
	
	# Reshaped image to a vertical array of HSV points.
	data = hsv.reshape((-1, 3))
	data = np.float32(data)
	
	# Criteria for k-means and execution of k-means.
	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
	compactness, label, center = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
	
	# Precompute.
	label = label.ravel()
	count = len(label)
	
	colors = []
	
	# Get an array of tuples -> (center, percent).
	for i in range(k):
		t = (center[i], np.count_nonzero(label == i) / count)
		colors.append(t)
	
	# Sort the array from greatest to least.
	colors = sorted(colors, key=lambda x: x[1], reverse=True)
	
	return colors
	

def referenceColor(image, colors):
	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	hsv = cv2.mean(hsv)
	hsv = np.array(hsv[:3])
	
	colors = np.array(colors)
	
	distances = np.linalg.norm(colors - hsv, axis=1)
		
	return np.argmin(distances)
	
	
def averageChannel(image, channel=0):
	hsv = np.array(image)
	h = hsv[:, :, channel].flatten()
	avg = np.mean(h)
	
	return avg
	

def absoluteColor(avg):

	# Color constants.
	COLORS = {
		'red': (355.0, 10.5),
		'red-orange': (10.5, 20.5),
		'orange-brown': (20.5, 40.5),
		'orange-yellow': (40.5, 50.5),
		'yellow': (50.5, 60.5),
		'yellow-green': (60.5, 80.5),
		'green': (80.5, 140.5),
		'green-cyan': (140.5, 169.5),
		'cyan': (170.5, 200.5),
		'cyan-blue': (201.5, 220.5),
		'blue': (220.5, 240.5),
		'blue-magenta': (240.5, 280.5),
		'magenta': (280.5, 320.5),
		'magenta-pink': (320.5, 330.5),
		'pink': (330.5, 345.5),
		'pink-red': (345.5, 355.0)
	}

	# OpenCV's hue range is 0-180. Convert to 0-360.
	avg *= 2
	
	# Iterate and identify color.np.count_nonzero(label == i)
	for color in COLORS:
		min = COLORS[color][0]
		max = COLORS[color][1]
		
		if min > max:
			if avg >= min or avg < max:
				return color
		else:
			if min <= avg < max:
				return color
	
	return None
	
img = cv2.imread('purple.jpg')
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
avg = averageChannel(hsv)
print('Average color:', absoluteColor(avg))
print('-' * 35)

colors = kMeansImage(hsv)
c0 = absoluteColor(colors[0][0][0])
c1 = absoluteColor(colors[1][0][0])
c2 = absoluteColor(colors[2][0][0])
print('%-*s %-*s %-*s' % (15, 'Color', 10, 'Hue', 10, 'Percent'))
print('-' * 35)
print('%-*s %-*.2f %-*.2f' % (15, c0, 10, colors[0][0][0], 10, colors[0][1] * 100))
print('%-*s %-*.2f %-*.2f' % (15, c1, 10, colors[1][0][0], 10, colors[1][1] * 100))
print('%-*s %-*.2f %-*.2f' % (15, c2, 10, colors[2][0][0], 10, colors[2][1] * 100))
