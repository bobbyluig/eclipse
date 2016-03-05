#/bin/sh

g++ -ggdb `pkg-config --cflags opencv` -o `basename calibration.cpp .cpp` calibration.cpp `pkg-config --libs opencv`
