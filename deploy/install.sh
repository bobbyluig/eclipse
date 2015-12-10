#!/bin/bash

###########################################################################
# Install script for Project Lycanthrope.
# By Lujing Cen.
# Copyright (c) Eclipse Technologies 2015-2016.
# Use only with Debian 8 ("Jessie") ARMv7. Script must be executed as root.
# Requires at least 4GB of free space for installation.
# Designed for MINIBIAN/ODROID Minimal Debian.
# MINIBIAN: https://minibianpi.wordpress.com/
# ODROID Debian: http://forum.odroid.com/viewtopic.php?f=114&t=8084
###########################################################################

#############
# User input.
#############

# Request user for new hostname.
echo "Enter robot hostname: "
read newhost

# Request GitHub password.
echo "Enter GitHub password: "
read password

#####################
# Configure hostname.
#####################

# Get current hostname.
hostn=$(cat /etc/hostname)

# Change hostname. Tengo sed.
sed -i "s/$hostn/$newhost/g" /etc/hosts
sed -i "s/$hostn/$newhost/g" /etc/hostname

###############################
# Update and get prerequisites.
###############################ss

# Update and upgrade.
apt-get -y update && apt-get -y upgrade

# Get apt-utils
apt-get -y install apt-utils

# Get required software.
apt-get -y install p7zip-full nano wireless-tools wpasupplicant usbutils wget connman libusb-dev

###################
# Clone repository.
###################

apt-get -y install git
cd ~
git clone https://bobbyluig:$password@github.com/bobbyluig/Eclipse.git

#########################
# Python 3 and libraries.
#########################

# Get Python 3.5.
cd ~
apt-get -y install build-essential libssl-dev
wget https://www.python.org/ftp/python/3.5.0/Python-3.5.0.tgz
tar zxvf Python-3.5.0.tgz
cd Python-3.5.0
./configure --enable-shared
make -j4 && make install
cd ~
rm -rf Python-3.5.0
rm -f Python-3.5.0.tgz

# Get Python libraries.
pip3 install numpy pyserial autobahn[accelerate] pyusb
apt-get -y install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev libav-tools
pip3 install pyaudio pydub

####################
# Install OpenCV 3.
####################

# Get required libraries.
apt-get -y install cmake pkg-config
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
	-D ENABLE_VFPV3=ON \
	-D ENABLE_NEON=ON \ 
	-D CMAKE_INSTALL_PREFIX=/usr/local \
	-D PYTHON3_LIBRARY=/usr/local/lib/libpython3.5m.so \
	-D INSTALL_C_EXAMPLES=OFF \
	-D INSTALL_PYTHON_EXAMPLES=OFF \
	-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
	-D BUILD_PERF_TESTS=OFF \
	-D BUILD_TESTS=OFF \
	-D BUILD_EXAMPLES=OFF ..
make CXXFLAGS="-O3 -mcpu=cortex-a5 -mfloat-abi=hard -mfpu=neon-fp16 -ffast-math" -j4 && make install
ldconfig

# Cleanup.
cd ~
rm -rf opencv-3.0.0 opencv_contrib

#################
# Install oculus.
#################

######################
# Arduino development.
######################

apt-get -y install arduino-core picocom python python-pip python-dev
pip install ino  
