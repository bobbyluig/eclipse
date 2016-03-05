# LSD-SLAM: Large-Scale Direct Monocular SLAM

LSD-SLAM is a novel approach to real-time monocular SLAM. It is fully direct (i.e. does not use keypoints / features) and creates large-scale, 
semi-dense maps in real-time on a laptop. For more information see
[http://vision.in.tum.de/lsdslam](http://vision.in.tum.de/lsdslam)
where you can also find the corresponding publications and Youtube videos, as well as some 
example-input datasets, and the generated output as rosbag or .ply point cloud.


### Related Papers

* **LSD-SLAM: Large-Scale Direct Monocular SLAM**, *J. Engel, T. Schöps, D. Cremers*, ECCV '14

* **Semi-Dense Visual Odometry for a Monocular Camera**, *J. Engel, J. Sturm, D. Cremers*, ICCV '13


# How to build from source
The lsd slam code requires c++11 features.
Thus, it needs c++11 supported compiler to build the code from source.

## Windows (requiring Visual Studio 2013)
For windows build, please follow instructions from [Windows build](WindowsBuildInstruction.md)

## Android (requiring gcc4.7+)
TBA

## Linux (requiring gcc4.7+)

Building under Ubuntu

1. Install G2O

2. Install G2O debug versions of the lib

    a. run the following inside the build folder so debug is enabled and the libs build accordingly
	```
	cmake -DCMAKE_BUILD_TYPE=Debug .. 
	make
	sudo make install
	```

3. under lsd_slam source, create a folder
	```mkdir build```

4. ```cd build```

5. ```cmake ..```

6. ```make -j4```

This will build lsd_slam as a lib and also build the sample_app under LSD_SLAM_SOURCE/bin

Run the sample with
```
LSD_SLAM_SOURCE/bin/sample_app <video device id>

eg., to run with the video device /dev/video0

LSD_SLAM_SOURE/bin/sample_app 0
```

# License
LSD-SLAM is licensed under the GNU General Public License Version 3 (GPLv3), see http://www.gnu.org/licenses/gpl.html.

For commercial purposes, the original lsd slam authors also offer a professional version under different licencing terms.
