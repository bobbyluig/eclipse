#!/bin/bash

###############################################
# Install script for Project Lycanthrope.
# By Lujing Cen.
# Copyright (c) Eclipse Technologies 2015-2016.
# Use only with Debian 8 ("Jessie") ARMv7.
# Script must be executed as root.
# Requires at least 4GB of free space.
###############################################

# Update and upgrade.
apt-get -y update && apt-get -y upgrade

# Get 7zip.
apt-get -y install p7zip-full

#########################
# Python 3 and libraries.
#########################

# Get Python 3.5.
cd ~
apt-get -y install build-essential libssl-dev
wget https://www.python.org/ftp/python/3.5.0/Python-3.5.0.tgz
tar -zxvf Python-3.5.0.tgz
cd Python-3.5.0
./configure
make -j4 && make install
cd ..
rm -rf Python-3.5.0
rm -f Python-3.5.0.tgz

# Get Python libraries.
pip3 install numpy pyserial autobahn
apt-get -y install apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev
pip3 install pyaudio

####################
# Install OpenCV 3.
####################

# Get required libraries.
apt-get -y install git cmake pkg-config
apt-get -y install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
apt-get -y install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
apt-get -y install libatlas-base-dev gfortran

# Get contrib module.
cd ~
git clone https://github.com/Itseez/opencv_contrib.git
cd opencv_contrib
git checkout 3.0.0

# Get version 3.
cd ~
wget https://github.com/Itseez/opencv/archive/3.0.0.zip
7z x 3.0.0.zip
rm -f 3.0.0.zip

# Compile.
cd opencv-3.0.0
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
	-D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_C_EXAMPLES=ON \
	-D INSTALL_PYTHON_EXAMPLES=ON \
	-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
	-D BUILD_EXAMPLES=ON ..
make -j4 && make install
ldconfig

# Cleanup.
cd ~
rm -rf opencv-3.0.0 opencv_contrib
