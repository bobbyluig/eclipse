#!/usr/bin/env bash

apt-get -y update && apt-get -y upgrade
apt-get -y install git

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

cd ~
apt-get -y install libedit-dev libpopt-dev libiberty-dev binutils-dev # llvm-3.7-dev
wget http://prdownloads.sourceforge.net/oprofile/oprofile-1.1.0.tar.gz
tar zxvf oprofile-1.1.0.tar.gz
cd oprofile-1.1.0
./configure
make -j4 && make install
cd ~
rm -rf oprofile-1.1.0 oprofile-1.1.0.tar.gz

export NPY_NUM_BUILD_JOBS=4
pip3 install numpy

apt-get -y install cmake pkg-config

cd ~
wget http://llvm.org/releases/3.7.1/llvm-3.7.1.src.tar.xz
tar xf llvm-3.7.1.src.tar.xz
cd llvm-3.7.1.src
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release -DLLVM_TARGETS_TO_BUILD="AArch64" -DLLVM_USE_OPROFILE=ON -DPYTHON_EXECUTABLE=/usr/local/bin/python3.5 ..
make -j4 && make install
ldconfig
cd ~
rm -rf llvm-3.7.1.src

pip3 install numba