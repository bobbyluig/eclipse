# Red Eclipse Framework

This repository contains all code used by Eclipse (Red Team) in the 2016 CARPA Initiative Challenge - The Lycanthrope Project.

## Style

In most cases, all code styling abides by [PEP 8](https://www.python.org/dev/peps/pep-0008/). All objects should use *CamelCase* and all functions should used *mixedCase*. The use of *mixedCase* is due to the nature of OpenCV and Pololu libraries where such is the prevailing style. Variables, especially those of a class, should also used *mixedCase* as such is the prevailing style (this does not abide by PEP 8). File names are always all lowercase with no underscores.

## Development

After cloning the package, all the prerequisites for the project must be installed. This project has not been tested in Mac but should work find due to the versatility of Python.

##### Test with the following hardware
- Pololu Mini Maestro 18
- SparkFun RedBoard
- ODROID-C1+
- Raspberry Pi 2 Model B

##### Project requires
- Windows 7+, Linux (tested on Debian, Raspbian and Ubuntu), or OS X (untested but should work).
- CMake 2.8.7 or higher.
- Python 3.5+ (usage of new async and await syntax).
- Boost Python (sudo apt-get install libboost-dev-all should be good).
- OpenCV 3 and contrib module with Python3 binding.
- The latest version of the following Python packages and their dependencies: `numpy`, `pyserial`, `autobahn`, `pyusb`, `pyaudio`.
- Processor support for SSE2 intrinsics (on most Intel and AMD processors) or NEON intrinsics (on ARM Cortex-A series).

The root directory for the Python code is the `src` folder. Ensure that your IDE (like PyCharm) knows that it is the root directory. Tests should be written in `test.py` before being moved to `main.py` or other files.

USB is quite interesting. Pololu's configuation software is written in C# and uses an outdated version of WinUSB. However, pyusb requires libusb-win32 (or equivalent). First, configure the Mini Maestro using the Pololu software. Ensure that CRC check is disabled and that the serial mode is set to "USB Dual Port." Other modes should work as well but this is the most stable and well-tested mode. You may modify other parameters to your liking but be prepared to change code parameters if things like period and timeout are changed from their default value.

For Windows, it is necessary after initial configuration to install a driver compatible with pyusb. This can be done using [zadig](http://zadig.akeo.ie/). Ensure that you replace the driver (which should be WinUSB) for the actual device and not its two virtual COM ports. To reuse the Pololu controller interface, open device manager and uninstall the device. After a refresh, the original driver should reappear. 

If installing manually, you will need to compile `oculus`, which implements DSST and KCF corelation-based trackers and exposes them to Python3. Check the README in `src/theia/oculus` for more information.

## Deployment
  
Deployment is done by first cloning the repository on a remote device. Execute `chmod +x install.sh` and then `./install.sh` in a support distibution indicated by `deploy/install.sh` to automatically install and compile all required libraries/software.

##### Deployment process
1. On the server, cd to the `crossbar` folder and run `crossbar start`.
2. Edit the IP addresses (if dynamic) on all devices including the server.
3. On the server, open `zeus` in a browser. Ensure that it can connect to the crossbar server on localhost.
4. On each remote robot device, cd to `src` and execute `python3 main.py` to start the programs.
5. View the command center (zeus) to ensure that all devices have connected.
