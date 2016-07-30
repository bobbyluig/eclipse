% Repair and Troubleshooting
% Lujing Cen
% 7/30/2016

# Introduction

Welcome to the repair and troubleshooting guide. This guide applies to DOG-1E5 and DOG-4S1. Hopefully, this guide will resolve any problems with robot demo operation.

The normal power up sequence should include the following visible steps:

1. ODROID powers on.
2. All legs move to uncalibrated zero position.
3. All legs move to calibrated zero position.
4. Sequence begins.

If this does not happen in the way it should, or the sequence fails, find the issue below and follow the instructions.

### ODROID does not power on.

There are multiple possibilties here. First, check if there is a solid red light. If there is none, this indicates that there is no power flowing to the ODROID. To resolve this, first check the voltage of the battery to ensure that it is functional and charged. Then, verify that there is indeed 5 volts running to the ODROID. If there is voltage running but the computer still does not turn on, it may be broken.

Proper boot up is indicated by the blue light. It should have a constant flash when the kernel is running. If this does not happen, then the SD card is either corrupt or damaged (this happend to us).

### ODROID powers on, but legs do not move.

Again, check the voltage. Verify that the Mini Maestro has power. To perform a servo test, move all the legs slightly out of zero position. When the Mini Maestro powers on, they should all move to uncalibrated zero. If one does not, a servo is probably damaged.

### Legs move, but sequence does not start.

This is probably an issue with the software inside of the ODROID. It is highly unlikely to happen. Simply restart the computer. If it still does not work, you may have to manually test by logging in to the ODROID.

### Sequence is not stable.

If the robot is tripping, a servo is probably damaged. However, if that is not the case, it may just be that the center of mass changed. Refer to the usage guide for calibration.

### The battery is broken.

Buy another one.

### A piece of the robot is broken.

Make another one.

### A servo is broken.

This is a fun thing to repair. Once the broken servo is located, the leg will need to be disassembled. However, it needs to be calibrated. Do not assemble before calibration!

First, disconnect the Maestro from the ODROID. Hook up the Maestro to another computer. It only needs power. Once it is powered on, the servos should to move to their optimal zero position. Now, assemble the leg as close to zero position as possible. Remember, once you tighten everything, there is no going back without taking everything apart! 

Now that the leg is assembled, locate the the proper `hippocampus.py` in either `src/cerebral/pack1` (DOG-1E5) or `src/cerebral/pack2` (DOG-4S1). Locate the leg with the broken servo. Set all `bias` to 0, then execute the code below. Replace `packX` with the proper number.

```python
from cerebral.packX.hippocampus import Android
from agility.main import Agility

# Robot by reference.
robot = Android.robot
agility = Agility(robot)

# Zero
agility.zero()
```

For every servo that is not at the correct zero position, tweak its bias until it is. After that, reconnect everything and the robot should be fully functional again. Do not ask if the bias is positive or negative. Testing both cases is way faster. Trust me.

### The ODROID is broken.

Rebuilding the image takes a few hours, but is not difficult. Obtain the [ODROBIAN Jessie OS](http://oph.mdrjr.net/odrobian/images/s905/) and load it onto an SD card. Log in to the ODROID using Ethernet and move `src/deploy` over using SFTP. Go to the `deploy` directory and run the code.

```bash
chmod +x install.sh
source install.sh
```

Assuming everything is okay (it probably won't be lol), the basic image is now installed and ready for demo usage. For manual control, you'll need to set up wireless communications. This is covered in the usage guide.
