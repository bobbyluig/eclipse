How to build on Windows with Visual Studio 2013
=========

## 1. Requirement for building LSD Slam from source

[CMake 2.8+](www.cmake.org)

[Visual Studio 2013](http://www.visualstudio.com)

## 2. Dependencies (Boost, OpenCV, G2O)
They can be built from source or download my prebuilt from [Shared folder](https://drive.google.com/folderview?id=0B1nK6wk4wuKqcjBIUXNuR0stakU&usp=drive_web)

### For building dependencies from sources
#### Boost 1.5+
Download prebuilt from [Boost.org](www.boost.org) is also fine.
Make sure you get the prebuilts for Visual studio 2013 (VC12).

### OpenCV 2.8+
NOTE: downloading prebuilt from OpenCV.org won't work. You need to build from source.
Download source from [OpenCV.org](www.opencv.org).
Build using CMake configuration.

### G2O
Download source from [https://github.com/williammc/g2o](https://github.com/williammc/g2o).
Build using CMake configuration.

## 3. Now, build the LSD Slam source
Using CMake-gui to configure.

### `Step 1`: Start configuration with pressing `Configure` in CMake-GUI.

Note: you need to select "specify generator for this project" to Visual Studio 2013 and "Use default native compilers".
Results looks like this:

![Figure 1](doc/cmake-step1-configure.png)

This will output build files in selected build folder (e.x.: ~/lsd-slam/build-x86-vc12).
There are errors and warning, but don't worry; this will disappear if you do the next steps correctly.

### `Step2`: Edit dependencies' paths in 'LsdSlamDependencies_Config.cmake' 

The file locates in the build folder (e.x.: ~/lsd-slam/build-x86-vc12/LsdSlamDependencies_Config.cmake)
For instance, it looks like this:

![Figure 2](doc/cmake-step2-paths-edit.png)

### `Step3`: Go back to CMake-GUI and press `Configure` again, and then press `Generate`

The results would look like this:

![Figure 3](doc/cmake-step3-reconfigure.png)

### `Step4`: Open and build from Visual Studio 2013.

Double click on "set_paths_and_run_vc.bat" file in the build folder (e.x.: ~/lsd-slam/build-x86-vc12/set_paths_and_run_vc.bat)

![Figure 4](doc/cmake-step4-compile.png)


There you go, you can build and run sample app now.

Good luck & have fun!