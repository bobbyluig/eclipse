# Red Eclipse Framework

This repository contains all code used in the 2016 CARPA Initiative Challenge - The Lycanthrope Project. Failure in any aspect of the project is not in any way related to deficiencies in the code of this framework.

## Style

In most cases, all code styling abides by [PEP 8](https://www.python.org/dev/peps/pep-0008/). All objects should use *CamelCase* and all functions should used *lower_case*. The use of *mixedCase* is present due to the nature of OpenCV and Pololu libraries where such is the prevailing style. Variables, especially those of a class, should also used *lower_case*. File names are always all lowercase with no underscores.

For JavaScript (`phi`), functions and objects should use *mixedCase*. 

## Development

After cloning the package, all the prerequisites for the project must be installed. This project has not been tested in Mac but should work fine due to the versatility of Python.

##### Test with the following hardware
- Pololu Mini Maestro 18
- SparkFun RedBoard
- Arduino UNO
- ODROID-C1+
- ODROID-C2
- Raspberry Pi 2 Model B
- Raspberry Pi 3

##### Recommended command center specifications
- Intel i7 (4th generation and up) if real-time multi-robot slam is desired.
- 16 GB ram. 8 GB is risky for `slam`.
- For `phi`, use a Mac because Macs have cool vnoices.

##### Project requires
- Windows 7+, Linux (tested on Debian Jessie+, Raspiban, and Odrobian), or OS X (untested but should work).
- CMake 2.8.7 or higher.
- Node.js and required components (for `phi` development).
- Python 3.5+ (usage of new async and await syntax).
- Boost Python (sudo apt-get install libboost-dev-all should be good).
- OpenCV 3 and contrib module with Python3 binding.
- C++11 capable compiler for robots. (GCC 4.9+, includes GCC 5).
- C++14 capable compiler for command center. Usage of `slam` requires 64-bit Python. Project tested on MSVC 2015.
- The latest version of the following Python packages and their dependencies: `numpy`, `pyserial`, `autobahn`, `pyusb`, `pyaudio`.
- Processor support for SSE2 intrinsics (on most Intel and AMD processors) or NEON intrinsics (on ARM Cortex-A series).

The root directory for the Python code is the `src` folder. Ensure that your IDE (like PyCharm) knows that it is the root directory. Tests should be written in test directories before being moved to `main.py` or other files.

USB is quite interesting. Pololu's configuation software is written in C# and uses an outdated version of WinUSB. However, pyusb requires libusb-win32 (or equivalent). First, configure the Mini Maestro using the Pololu software. Ensure that CRC check is disabled and that the serial mode is set to "USB Dual Port." Other modes should work as well but this is the most stable and well-tested mode. You may modify other parameters to your liking but be prepared to change code parameters if things like period and timeout are changed from their default value.

For Windows, it is necessary after initial configuration to install a driver compatible with pyusb. This can be done using [zadig](http://zadig.akeo.ie/). Ensure that you replace the driver (which should be WinUSB) for the actual device and not its two virtual COM ports. To reuse the Pololu controller interface, open device manager and uninstall the device. After a refresh, the original driver should reappear. 

If installing manually, you will need to compile `oculus`, which implements DSST and KCF corelation-based trackers and exposes them to Python3. Check the README in `src/theia/oculus` for more information. You will also need to compile `slam`, which implements monocular location and mapping. Check `src/theia/slam` for more information.

## Deployment
  
Deployment is done by first cloning the repository on a remote device. Execute `chmod +x install.sh` and then `./install.sh` in a support distibution indicated by `deploy/install.sh` to automatically install and compile all required libraries/software.

##### Deployment process
1. On the server, cd to the `crossbar` folder and run `crossbar start`.
2. Edit the IP addresses (if dynamic) on all devices including the server.
3. On the mission display, open `phi` in a browser. Ensure that it can connect to the crossbar server.
4. On each remote robot device, cd to `src` and execute `python3 eclipse.py` to start the programs.
