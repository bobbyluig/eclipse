#!/usr/bin/env bash

###########################################################################
# Install script for Project Lycanthrope.
# By Lujing Cen.
# Copyright (c) Eclipse Technologies 2015-2016.
# Use only with Debian 8 ("Jessie") ARMv8. Script must be executed as root.
# Requires at least 4GB of free space for installation.
# Designed for ARM64 architecture. Optimized for Cortex-A53.
# Run using $ source install.sh
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

# Get newest stuff.
# echo 'deb http://ftp.us.debian.org/debian stretch main non-free contrib' > custom.list
# cp custom.list /etc/apt/sources.list.d/
# rm custom.list

# Update and upgrade.
apt-get -y update && apt-get -y upgrade

# Get apt-utils
apt-get -y install apt-utils

# Get required software.
apt-get -y install p7zip-full nano wireless-tools wpasupplicant usbutils wget rfkill supervisor \
libusb-dev ca-certificates linux-headers-odrobian-s905 \
firmware-linux firmware-linux-free firmware-linux-nonfree firmware-realtek \
cmake pkg-config s905-zram

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
wget https://www.python.org/ftp/python/3.5.1/Python-3.5.1.tgz
tar zxvf Python-3.5.1.tgz
cd Python-3.5.1
./configure --enable-shared
make -j4 && make install
ldconfig
cd ~
rm -rf Python-3.5.1
rm -f Python-3.5.1.tgz

# Get port audio.
cd ~
apt-get -y install libasound-dev libav-tools portaudio19-dev

# Get Python libraries.
apt-get -y install libatlas-base-dev gfortran liblapack-dev libblas-dev libatlas-dev libfreetype6-dev

export NPY_NUM_BUILD_JOBS=4
pip3 install --upgrade pip
pip3 install numpy pyserial autobahn[accelerate] pyusb psutil scipy pyro4 matplotlib
pip3 install pyaudio pydub

####################
# Install OpenCV 3.
####################

# Get required libraries.
apt-get -y install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
apt-get -y install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev

# Get contrib module.
cd ~
git clone https://github.com/Itseez/opencv_contrib.git

# Get version 3.
cd ~
wget https://github.com/Itseez/opencv/archive/3.1.0.zip
7z x 3.1.0.zip
rm -f 3.1.0.zip

# Compile.
cd opencv-3.1.0
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
-D ENABLE_VFPV3=ON \
-D ENABLE_NEON=ON \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D PYTHON3_LIBRARY=/usr/local/lib/libpython3.5m.so \
-D INSTALL_C_EXAMPLES=OFF \
-D INSTALL_PYTHON_EXAMPLES=OFF \
-D BUILD_PERF_TESTS=OFF \
-D BUILD_TESTS=OFF \
-D BUILD_EXAMPLES=OFF ..
make CXXFLAGS="-O3 -mcpu=cortex-a53 -mfloat-abi=hard -mfpu=neon-fp-armv8 -ffast-math" -j4 && make install
ldconfig

# Cleanup.
cd ~
rm -rf opencv-3.1.0 opencv_contrib

#################
# Install oculus.
#################

apt-get -y install libboost-all-dev
cd ~/Eclipse/src/theia/oculus
mkdir build
cd build
cmake -D PYTHON3_NUMPY_INCLUDE_DIRS=/usr/local/lib/python3.5/site-packages/numpy/core/include ..
make CXXFLAGS="-O3 -mcpu=cortex-a53 -mfloat-abi=hard -mfpu=neon-fp-armv8 -ffast-math" && make install

#################
# MJPEG-Streamer.
#################

cd ~
git clone https://github.com/codewithpassion/mjpg-streamer.git
cd mjpg-streamer/mjpg-streamer
apt-get -y install imagemagick libv4l-dev
make USE_LIBV4L2=true clean all

cp mjpg_streamer /usr/local/bin
cp output_http.so input_file.so input_uvc.so /usr/local/lib/
cp -R www /usr/local/www

#############
# Copy files.
#############

cp ~/Eclipse/deploy/supervisor/edd.conf /etc/supervisor/conf.d/
supervisorctl reread
supervisorctl update
