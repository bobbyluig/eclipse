import cv2
import numpy as np
import math


def delta_e_cie1976(lab_color_vector, lab_color_matrix):
    """
    Calculates the Delta E (CIE1976) between `lab_color_vector` and all
    colors in `lab_color_matrix`.
    """

    return np.sqrt(np.sum(np.power(lab_color_vector - lab_color_matrix, 2), axis=1))


# noinspection PyPep8Naming
def delta_e_cie1994(lab_color_vector, lab_color_matrix,
                    K_L=1, K_C=1, K_H=1, K_1=0.045, K_2=0.015):
    """
    Calculates the Delta E (CIE1994) of two colors.
    K_l:
      0.045 graphic arts
      0.048 textiles
    K_2:
      0.015 graphic arts
      0.014 textiles
    K_L:
      1 default
      2 textiles
    """

    C_1 = np.sqrt(np.sum(np.power(lab_color_vector[1:], 2)))
    C_2 = np.sqrt(np.sum(np.power(lab_color_matrix[:, 1:], 2), axis=1))

    delta_lab = lab_color_vector - lab_color_matrix

    delta_L = delta_lab[:, 0].copy()
    delta_C = C_1 - C_2
    delta_lab[:, 0] = delta_C

    delta_H_sq = np.sum(np.power(delta_lab, 2) * np.array([-1, 1, 1]), axis=1)
    # noinspection PyArgumentList
    delta_H = np.sqrt(delta_H_sq.clip(min=0))

    S_L = 1
    S_C = 1 + K_1 * C_1
    S_H = 1 + K_2 * C_1

    LCH = np.vstack([delta_L, delta_C, delta_H])
    params = np.array([[K_L * S_L], [K_C * S_C], [K_H * S_H]])

    return np.sqrt(np.sum(np.power(LCH / params, 2), axis=0))


# noinspection PyPep8Naming
def delta_e_cmc(lab_color_vector, lab_color_matrix, pl=2, pc=1):
    """
    Calculates the Delta E (CIE1994) of two colors.
    CMC values
      Acceptability: pl=2, pc=1
      Perceptability: pl=1, pc=1
    """

    L, a, b = lab_color_vector

    C_1 = np.sqrt(np.sum(np.power(lab_color_vector[1:], 2)))
    C_2 = np.sqrt(np.sum(np.power(lab_color_matrix[:, 1:], 2), axis=1))

    delta_lab = lab_color_vector - lab_color_matrix

    delta_L = delta_lab[:, 0].copy()
    delta_C = C_1 - C_2
    delta_lab[:, 0] = delta_C

    H_1 = np.degrees(np.arctan2(b, a))

    if H_1 < 0:
        H_1 += 360

    F = np.sqrt(np.power(C_1, 4) / (np.power(C_1, 4) + 1900.0))

    # noinspection PyChainedComparisons
    if 164 <= H_1 and H_1 <= 345:
        T = 0.56 + abs(0.2 * np.cos(np.radians(H_1 + 168)))
    else:
        T = 0.36 + abs(0.4 * np.cos(np.radians(H_1 + 35)))

    if L < 16:
        S_L = 0.511
    else:
        S_L = (0.040975 * L) / (1 + 0.01765 * L)

    S_C = ((0.0638 * C_1) / (1 + 0.0131 * C_1)) + 0.638
    S_H = S_C * (F * T + 1 - F)

    delta_C = C_1 - C_2

    delta_H_sq = np.sum(np.power(delta_lab, 2) * np.array([-1, 1, 1]), axis=1)
    # noinspection PyArgumentList
    delta_H = np.sqrt(delta_H_sq.clip(min=0))

    LCH = np.vstack([delta_L, delta_C, delta_H])
    params = np.array([[pl * S_L], [pc * S_C], [S_H]])

    return np.sqrt(np.sum(np.power(LCH / params, 2), axis=0))


# noinspection PyPep8Naming
def delta_e_cie2000(lab_color_vector, lab_color_matrix, Kl=1, Kc=1, Kh=1):
    """
    Calculates the Delta E (CIE2000) of two colors.
    """

    L, a, b = lab_color_vector

    avg_Lp = (L + lab_color_matrix[:, 0]) / 2.0

    C1 = np.sqrt(np.sum(np.power(lab_color_vector[1:], 2)))
    C2 = np.sqrt(np.sum(np.power(lab_color_matrix[:, 1:], 2), axis=1))

    avg_C1_C2 = (C1 + C2) / 2.0

    G = 0.5 * (1 - np.sqrt(np.power(avg_C1_C2, 7.0) / (np.power(avg_C1_C2, 7.0) + np.power(25.0, 7.0))))

    a1p = (1.0 + G) * a
    a2p = (1.0 + G) * lab_color_matrix[:, 1]

    C1p = np.sqrt(np.power(a1p, 2) + np.power(b, 2))
    C2p = np.sqrt(np.power(a2p, 2) + np.power(lab_color_matrix[:, 2], 2))

    avg_C1p_C2p = (C1p + C2p) / 2.0

    h1p = np.degrees(np.arctan2(b, a1p))
    h1p += (h1p < 0) * 360

    h2p = np.degrees(np.arctan2(lab_color_matrix[:, 2], a2p))
    h2p += (h2p < 0) * 360

    avg_Hp = (((np.fabs(h1p - h2p) > 180) * 360) + h1p + h2p) / 2.0

    T = 1 - 0.17 * np.cos(np.radians(avg_Hp - 30)) + \
        0.24 * np.cos(np.radians(2 * avg_Hp)) + \
        0.32 * np.cos(np.radians(3 * avg_Hp + 6)) - \
        0.2 * np.cos(np.radians(4 * avg_Hp - 63))

    diff_h2p_h1p = h2p - h1p
    delta_hp = diff_h2p_h1p + (np.fabs(diff_h2p_h1p) > 180) * 360
    delta_hp -= (h2p > h1p) * 720

    delta_Lp = lab_color_matrix[:, 0] - L
    delta_Cp = C2p - C1p
    delta_Hp = 2 * np.sqrt(C2p * C1p) * np.sin(np.radians(delta_hp) / 2.0)

    S_L = 1 + ((0.015 * np.power(avg_Lp - 50, 2)) / np.sqrt(20 + np.power(avg_Lp - 50, 2.0)))
    S_C = 1 + 0.045 * avg_C1p_C2p
    S_H = 1 + 0.015 * avg_C1p_C2p * T

    delta_ro = 30 * np.exp(-(np.power(((avg_Hp - 275) / 25), 2.0)))
    R_C = np.sqrt((np.power(avg_C1p_C2p, 7.0)) / (np.power(avg_C1p_C2p, 7.0) + np.power(25.0, 7.0)))
    R_T = -2 * R_C * np.sin(2 * np.radians(delta_ro))

    return np.sqrt(
        np.power(delta_Lp / (S_L * Kl), 2) +
        np.power(delta_Cp / (S_C * Kc), 2) +
        np.power(delta_Hp / (S_H * Kh), 2) +
        R_T * (delta_Cp / (S_C * Kc)) * (delta_Hp / (S_H * Kh)))


def clusterColor(image, k=3, type='hsv'):
    """
    Extract the k most dominant colors in HSV format from an image.
    Runs RGB k-means clustering before conversion to HSV.
    :param image: An 8-bit numpy array in BGR format.
    :param int k: Number of unique colors to extract.
    :param str type: Return color space. Either hsv or lab.
    :return: A sorted array from greatest to least of format (HSV array, percent).
    """
    
    # Reshaped image to a vertical array of HSV points.
    data = image.reshape((-1, 3))
    data = np.float32(data)
    
    # Criteria for k-means and execution of k-means.
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    compactness, label, center = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    # Precompute.
    label = label.ravel()

    # Convert RGB. Scale center from [0, 255] to [0, 1] for float32.
    if type == 'hsv':
        center = cv2.cvtColor(np.array([center / 255], dtype=np.float32), cv2.COLOR_BGR2HSV)[0]
    elif type == 'lab':
        center = cv2.cvtColor(np.array([center / 255], dtype=np.float32), cv2.COLOR_BGR2LAB)[0]
    else:
        raise Exception('Unknown type %s' % type)

    colors = []
    
    # Get an array of tuples -> (center, percent).
    for i in range(k):
        t = (center[i], np.count_nonzero(label == i) / count)
        colors.append(t)
    
    # Sort the array from greatest to least.
    colors = sorted(colors, key=lambda x: x[1], reverse=True)
    
    return colors


def closestColor(lab, colors):

    # Convert to numpy matrix.
    c = np.array(colors)

    # Cimpute distances
    distances = delta_e_cie1976(lab, c)
    print(distances)

    return np.argmin(distances)
    
    
def averageChannel(image, channel=0):
    """
    Gets the average value of a single channel.
    :param image: An numpy array representing an image.
    :param channel: Channel number. Usually from 0-2 for BGR/HSV and 0-3 for BGRA.
    :return: The average of the indicated channel as a float.
    """

    hsv = np.array(image)
    h = hsv[:, :, channel].flatten()
    avg = np.mean(h)
    
    return avg
    

def absoluteColor(hue):
    """
    Returns a color name corresponding to a given hue.
    :param hue: The average hue.
    :return: A color name.
    """

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
    
    # Iterate and identify color.
    for color in COLORS:
        min = COLORS[color][0]
        max = COLORS[color][1]
        
        if min > max:
            if hue >= min or hue < max:
                return color
        else:
            if min <= hue < max:
                return color
    
    return None


c = [
    (255, 0, 0),
    (0, 255, 0),
    (192, 192, 192),
]
c = cv2.cvtColor(np.array([c], dtype=np.float32) / 255, cv2.COLOR_RGB2LAB)[0]

rgb = (255, 178, 102)
lab = cv2.cvtColor(np.array([[rgb]], dtype=np.float32) / 255, cv2.COLOR_RGB2LAB)[0][0]

closest = closestColor(lab, c)
print(closest)

'''
img = cv2.imread('sand.jpg')
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
avg = averageChannel(hsv)
print('Average color:', absoluteColor(avg * 2))
print('-' * 35)

colors = clusterColor(img)
c0 = absoluteColor(colors[0][0][0])
c1 = absoluteColor(colors[1][0][0])
c2 = absoluteColor(colors[2][0][0])
print('%-*s %-*s %-*s' % (15, 'Color', 10, 'Hue', 10, 'Percent'))
print('-' * 35)
print('%-*s %-*.2f %-*.2f' % (15, c0, 10, colors[0][0][0], 10, colors[0][1] * 100))
print('%-*s %-*.2f %-*.2f' % (15, c1, 10, colors[1][0][0], 10, colors[1][1] * 100))
print('%-*s %-*.2f %-*.2f' % (15, c2, 10, colors[2][0][0], 10, colors[2][1] * 100))
'''
