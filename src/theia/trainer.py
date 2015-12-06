import cv2
import dlib
import os
from skimage import io


folder = 'C:/users/Bobbyluig/Desktop/train'
xml = os.path.join(folder, 'data.xml')
svm = os.path.join(folder, 'detector.svm')
timage = os.path.join(folder, '12084178_955201457921487_1396688245_n.jpg')


def train():
    options = dlib.simple_object_detector_training_options()
    options.add_left_right_image_flips = True
    options.C = 6
    options.num_threads = 8
    options.be_verbose = True

    dlib.train_simple_object_detector(xml, svm, options)

    print('Training done!')

    accuracy = dlib.test_simple_object_detector(xml, svm)

    print(accuracy)


def test():
    detector = dlib.simple_object_detector(svm)
    win_det = dlib.image_window()
    win_det.set_image(detector)
    win = dlib.image_window()
    img = io.imread(timage)
    dets = detector(img)
    win.clear_overlay()
    win.set_image(img)
    win.add_overlay(dets)
    dlib.hit_enter_to_continue()


test()