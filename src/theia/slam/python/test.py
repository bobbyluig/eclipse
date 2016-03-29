from pyslam import *
import cv2
import time
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def test_camera():
    cap = cv2.VideoCapture(0)

    params = TrackerParams()
    params.sensor = eSensor.MONOCULAR

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
    mpTracker = Tracking(mpVocabulary, mpMap, mpKeyFrameDatabase, params)
    mpLocalMapper = LocalMapping(mpMap, True)
    mpLoopCloser = LoopClosing(mpMap, mpKeyFrameDatabase, mpVocabulary, False)

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
        p = mpTracker.grab_mono(frame, time.time())
        if p is not None:
            print(i, p.ravel())
            ax.scatter(p[2], -p[0])
            i += 1

    plt.show()


def test_kitti0():
    left = cv2.VideoCapture('C:/users/bobbyluig/Desktop/00/image_0/%06d.png')
    right = cv2.VideoCapture('C:/users/bobbyluig/Desktop/00/image_1/%06d.png')

    params = TrackerParams()
    params.sensor = eSensor.STEREO

    params.fx = 718.856
    params.fy = 718.856
    params.cx = 607.1928
    params.cy = 185.2157

    params.fps = 30.0
    params.rgb = False

    params.bf = 386.1448
    params.mThDepth = 35

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
    mpTracker = Tracking(mpVocabulary, mpMap, mpKeyFrameDatabase, params)
    mpLocalMapper = LocalMapping(mpMap, False)
    mpLoopCloser = LoopClosing(mpMap, mpKeyFrameDatabase, mpVocabulary, True)

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

    for i in range(10):
        _, left_img = left.read()
        _, right_img = right.read()
        cv2.imshow('frame', left_img)

        p = mpTracker.grab_stereo(left_img, right_img, time.time())
        state = mpTracker.get_state()
        if p is not None:
            print(i, state, p.ravel())
        else:
            print(i, state)

        cv2.waitKey(1)

    mpLocalMapper.set_monocular(True)
    mpLoopCloser.set_fix_scale(False)
    params.sensor = eSensor.MONOCULAR
    mpTracker.change_settings(params)

    for i in range(4530):
        _, left_img = left.read()
        cv2.imshow('frame', left_img)

        p = mpTracker.grab_mono(left_img, time.time())
        state = mpTracker.get_state()
        if p is not None:
            print(i, p.ravel())
        else:
            print(i, state)

        cv2.waitKey(1)

    cv2.waitKey()


def test_multi():
    first = cv2.VideoCapture('C:/users/bobbyluig/Desktop/00/image_0/%06d.png')
    second = cv2.VideoCapture('C:/users/bobbyluig/Desktop/00/image_1/%06d.png')

    params = TrackerParams()
    params.sensor = eSensor.MONOCULAR

    params.fx = 718.856
    params.fy = 718.856
    params.cx = 607.1928
    params.cy = 185.2157

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
    tracker1 = Tracking(mpVocabulary, mpMap, mpKeyFrameDatabase, params)
    tracker2 = Tracking(mpVocabulary, mpMap, mpKeyFrameDatabase, params)
    mpLocalMapper = LocalMapping(mpMap, True)
    mpLoopCloser = LoopClosing(mpMap, mpKeyFrameDatabase, mpVocabulary, False)

    # Set pointers.
    print('Setting pointers.')
    tracker1.set_local_mapper(mpLocalMapper)
    tracker2.set_local_mapper(mpLocalMapper)
    tracker1.set_loop_closer(mpLoopCloser)
    tracker2.set_loop_closer(mpLoopCloser)
    mpLocalMapper.set_loop_closer(mpLoopCloser)
    mpLoopCloser.set_local_mapper(mpLocalMapper)

    # Start all threads.
    print('Starting modules.')
    mpLocalMapper.run()
    mpLoopCloser.run()

    for i in range(100):
        _, first_img = first.read()
        # cv2.imshow('first', first_img)

        p = tracker1.grab_mono(first_img, time.time())
        state = tracker1.get_state()
        if p is not None:
            print(i, p.ravel())
        else:
            print(i, state)

        # cv2.waitKey(1)

    success = tracker2.force_localize()
    assert success
    tracker2.inform_only_tracking(True)

    for i in range(4440):
        _, first_img = first.read()
        # cv2.imshow('first', first_img)
        # _, second_img = second.read()
        # cv2.imshow('second', second_img)

        p1 = tracker1.grab_mono(first_img, time.time())
        state = tracker1.get_state()
        if p1 is not None:
            print('p1', i, p1.ravel())
        else:
            print('p1', i, state)

        '''
        p2 = tracker2.grab_mono(second_img, time.time())
        state = tracker2.get_state()
        if p2 is not None:
            print('p2', i, p2.ravel())
        else:
            print('p2', i, state)
        '''


        # cv2.waitKey(1)

    cv2.waitKey()


test_multi()