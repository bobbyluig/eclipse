import numpy as np


def CIE76(lab_color_vector, lab_color_matrix):
    """
    Computes one or more Delta Es using CIE76.
    :param lab_color_vector: A numpy array of the sample LAB color.
    :param lab_color_matrix: A numpy vector of the predefined LAB colors.
    :return: A numpy array of CIE76 distances.
    """

    return np.sqrt(np.sum(np.power(lab_color_vector - lab_color_matrix, 2), axis=1))