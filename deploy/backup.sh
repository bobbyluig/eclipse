##############################
# Build Numba and dependencies.
##############################

# Get oprofile. Needed ONLY by llvmlite 0.9.0. No longer needed in Git repository.
cd ~
apt-get -y install libedit-dev libpopt-dev libiberty-dev binutils-dev
wget http://prdownloads.sourceforge.net/oprofile/oprofile-1.1.0.tar.gz
tar zxvf oprofile-1.1.0.tar.gz
cd oprofile-1.1.0
./configure
make -j4 && make install
cd ~
rm -rf oprofile-1.1.0 oprofile-1.1.0.tar.gz

# Build LLVM and install.
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

# Install numba.
pip3 install numba

######################
# Arduino development.
######################

apt-get -y install arduino-core picocom python python-pip python-dev
pip install ino