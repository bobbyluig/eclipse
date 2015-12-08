# Oculus

OpenCV is slightly behind on implementation of newer long and short-term trackers. Oculus is a Python module designed to rectify this problem. Oculus implements two trackers, DSST and KCF. DSST is the winner of [VOT 2014](http://www.votchallenge.net/vot2014/download/vot_2014_paper.pdf) and is also the winner in the 2015 OpenCV challenge (with modifications). KCF placed 3rd in VOT 2014 but is more than 3 times faster than DSST when scale is static.

## Installation

Currently, there is no Python installer. You will first need all of the prerequisites of the main project. 

First, configure Boost Python. If you're on Windows, you'll need to compile it yourself. Go to `tools/build` and run `bootstrap.bat`. Then, execute `b2 install`. Add `C:/boost-build-engine/bin` to PATH. Go to the root of the Boost folder and run `b2 -a --with-python address-model=32 toolset=msvc runtime-link=static`. You can choose 64-bit address model if that corresponds to your Python version.

After building, execute the following with the proper directory locations:

1. `setx BOOST_ROOT C:/boost_x_xx_x`
2. `setx BOOST_LIBRARYDIR C:/boost_x_xx_x/stage/lib`

You will also need to set your OpenCV Enviroment Variable if you have not already done so. Follow the instruction at [OpenCV - Set Enviroment Variable](`http://docs.opencv.org/2.4/doc/tutorials/introduction/windows_install/windows_install.html#windowssetpathandenviromentvariable`) (it's outdated but the procedure is the same. The path is one which contains the binaries).

After resolving prerequisites, build and install using the following steps:

1. `cd oculus`
2. `mkdir build`
3. `cd build`
4. `cmake ..`
5. `make && make install` (DO NOT -j4 on devices with less than 2GB of memory!)

This will create `oculus.pyd` on Windows or `oculus.so` in Linux and install it into the correct location. To remove, simply find the file and delete it.

## Credits

The entire library was originally written by Klaus Hagg in the repository [cf_tracking](https://github.com/klahaag/cf_tracking). The library also uses the [SSE2NEON](https://github.com/jratcliff63367/sse2neon) header.


## References

```
@article{henriques2015tracking,
title = {High-Speed Tracking with Kernelized Correlation Filters},
author = {Henriques, J. F. and Caseiro, R. and Martins, P. and Batista, J.},
journal = {Pattern Analysis and Machine Intelligence, IEEE Transactions on},
year = {2015}
```

```
@inproceedings{danelljan2014dsst,
title={Accurate Scale Estimation for Robust Visual Tracking},
author={Danelljan, Martin and H{\"a}ger, Gustav and Khan, Fahad Shahbaz and Felsberg, Michael},
booktitle={Proceedings of the British Machine Vision Conference BMVC},
year={2014}}
```

```
@inproceedings{danelljan2014colorattributes,
title={Adaptive Color Attributes for Real-Time Visual Tracking},
author={Danelljan, Martin and Khan, Fahad Shahbaz and Felsberg, Michael and Weijer, Joost van de},
booktitle={Conference on Computer Vision and Pattern Recognition (CVPR)},
year={2014}}
```

```
@article{lsvm-pami,
title = "Object Detection with Discriminatively Trained Part Based Models",
author = "Felzenszwalb, P. F. and Girshick, R. B. and McAllester, D. and Ramanan, D.",
journal = "IEEE Transactions on Pattern Analysis and Machine Intelligence",
year = "2010", volume = "32", number = "9", pages = "1627--1645"}
```

```
@misc{PMT,
author = {Piotr Doll\'ar},
title = {{P}iotr's {C}omputer {V}ision {M}atlab {T}oolbox ({PMT})},
howpublished = {\url{http://vision.ucsd.edu/~pdollar/toolbox/doc/index.html}}}
```

```
@inproceedings{bolme2010mosse,
author={Bolme, David S. and Beveridge, J. Ross and Draper, Bruce A. and Yui Man Lui},
title={Visual Object Tracking using Adaptive Correlation Filters},
booktitle={Conference on Computer Vision and Pattern Recognition (CVPR)},
year={2010}}
```
