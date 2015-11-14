#!/bin/bash

###############################################
# Install script for Project Lycanthrope
# By Lujing Cen
# Copyright (c) Eclipse Technologies 2015-2016
# Use only with Debian 8 ("Jessie") ARMv7
# Script must be executed as root
###############################################

# Get Python 3.5
apt-get install build-essential libssl-dev
wget https://www.python.org/ftp/python/3.5.0/Python-3.5.0.tgz
tar -zxvf Python-3.5.0.tgz
cd Python-3.5.0
./configure
make && make install
cd ..
rm -rf Python-3.5.0
rm -f Python-3.5.0.tgz

# Get Python libraries
pip3 install numpy pyserial



