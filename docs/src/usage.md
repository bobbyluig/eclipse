% Usage and Documentation
% Lujing Cen
% 7/30/2016

# Introduction

Welcome to the usage and documentation guide. This guide applies to DOG-1E5 and DOG-4S1. It is meant as a more thorough documentation of certain functions and classes and a guide for development and manual operation.

# Development

After cloning the package, all the prerequisites for the project must be installed. This project has not been tested in Mac but should work fine due to the versatility of Python.

### Project Hardware

- Pololu Mini Maestro 18
- SparkFun RedBoard
- Arduino UNO
- ODROID-C1+
- ODROID-C2
- Raspberry Pi 2 Model B
- Raspberry Pi 3

### Recommended Specifications

- Intel i7 (4th generation and up) if real-time SLAM is desired
- 16 GB of RAM
- 250+ GB HDD

### Development Requirements

- Windows 7 or higher, Linux Debian / Ubuntu, or OS X (untested but should work).
- CMake 2.8.7 or higher.
- Node.js and required components (for `phi` development).
- 64-bit Python 3.5+ (usage of new async and await syntax).
- Boost Python (sudo apt-get install libboost-dev-all should be good).
- OpenCV 3 and contrib module with Python 3 binding.
- C++14 capable compiler. Project tested on MSVC 2015.
- The latest version of the following Python packages and their dependencies: `numpy`, `pyserial`, `autobahn`, `pyusb`, `pyaudio`, `psutil`, `scipy`, `pyro4`, `matplotlib`, and `pydub`.
- Processor support for SSE2 intrinsics (on most Intel and AMD processors).

### Root Directory

The root directory for the Python code is the `src` folder. Ensure that your IDE (like PyCharm) knows that it is the root directory. Otherwise, make sure that the absolute path of `src` is in `PYTHONPATH`.

### Maestro USB Configuration

USB is quite interesting. Pololu's configuation software is written in C# and uses an outdated version of WinUSB. However, pyusb requires libusb-win32 (or equivalent). First, configure the Mini Maestro using the Pololu software. Ensure that CRC check is disabled and that the serial mode is set to "USB Dual Port." Other modes should work as well but this is the most stable and well-tested mode. You may modify other parameters to your liking but be prepared to change code parameters if things like period and timeout are changed from their default value.

For Windows, it is necessary after initial configuration to install a driver compatible with pyusb. This can be done using [zadig](http://zadig.akeo.ie/). Ensure that you replace the driver (which should be WinUSB) for the actual device and not its two virtual COM ports. To reuse the Pololu controller interface, open device manager and uninstall the device. After a refresh, the original driver should reappear. 

### Oculus and SLAM

If installing manually on Windows, you will need to compile `oculus`, which implements DSST and KCF corelation-based trackers and exposes them to Python 3. Check the README in `src/theia/oculus` for more information. You will also need to compile `slam`, which implements monocular location and mapping. Check `src/theia/slam` for more information. Basically, point CMake to the directory with `CMakeLists.txt` and create a new folder named `build` in the directory. Generate the correct configuration for MSVC. Make sure you use the right MSVC version that corresponds to the current Python version. Also, compile everything in 64-bit Release format. I tried to ensure that required modules are automatically found. However, you may have to manually compile and install things like Eigen and OpenCV 3. Have fun resolving the dependencies!

ORB-SLAM requires a training file, which is not included in the repository. The vocabulary can be donwload from the [original repository](https://github.com/raulmur/ORB_SLAM2/tree/master/Vocabulary).

### Zeus

To develop the front-end command interface, first install the required packages.

```bash
cd src/zeus/phi
npm install
```

The gulp configuration has been set to watch for updates automatically.

```bash
gulp build
gulp watch
```

Now, editing any project files will cause gulp to automatically update the webpage. Open `index.html` to view the command interface.

### Crossbar

No communication between devices can occur without [Crossbar](http://crossbar.io/). Follow the installation instructions on the site and then run the script below.

```bash
cd crossbar
crossbar start
```

Visit <https://127.0.0.1> after building `phi` and you should see the command interface.

### Style

In most cases, all code styling abides by [PEP 8](https://www.python.org/dev/peps/pep-0008/). All objects should use *CamelCase* and all functions should used *lower_case*. The use of *mixedCase* is present due to the nature of OpenCV and Pololu libraries where such is the prevailing style. Variables, especially those of a class, should also used *lower_case*. File names are always all lowercase with no underscores.

For JavaScript, functions and objects should use *mixedCase*. 

### Tests

There are no unit tests written. However, all tests are located in `tests` folders. Add tests there before moving them to main files to avoid confusion.

### IDE

I would personally recommend PyCharm professional. Autocomplete works really well, even with binary Python packages like OpenCV and Oculus. It also saves you a lot of time by finding various syntax, static semantic, and even some semantic errors. The professional version also supports JavaScript and web development. If you have a CSUDH email or another .edu email, you can get it for free. 

# Deployment

This section covers deploying code to the robot and using the command interface.

### Hardware Requirements

While the code can be deployed to pretty much any OS and hardware configuration, it is recommended that it is deployed to a 64-bit ARM computer with at least 1 GB of RAM. The computer must support NEON Intrinsics, so it must be an ARM-A processor. When in doubt, use the ODROID-C2 or Raspberry Pi 3.

### Installation

The project has only been tested on the [ODROBIAN Jessie OS](http://oph.mdrjr.net/odrobian/images/s905/). However, any Debian-based OS should work. Use the `deploy/install.sh` script to automatically install everything. Note that the script will clone Eclipse into the home directory. Make sure you run as root and follow instructions in the file.

### Wireless Configuration

All robots are configured to automatically connect to a WPA/WPA2 Wi-Fi named `Eclipse` with the password `eclipse4lyfe`. You can emulate this using a mobile hotspot or the paid Connectify app for PC. Configure wireless on the robots using `wicd-curses`. Make sure you check "Use these settings for all networks sharing this essid" and "Automatically connect to this network".

After connecting to the Wi-Fi network, the IP address of the computer running Crossbar needs to be identified. This information will need to be updated in all of the robots' `hippocampus.py` and the command interface.

### Command Interface

The command interface is pretty easy to use. More than one person can use it at the same time. The `w a s d` buttons control movement and `↑ ↓ ← →` controls the head. Get a Mac for cool voices. Be sure to connect to Crossbar before trying to do anything. All other buttons do what they say, with the exception of `watch`, which basically prepares the robot to accept manual movement commands.