import logging
import os
import re
import time
import serial
from serial import SerialTimeoutException
import struct
from threading import Lock
from serial.tools import list_ports

logger = logging.getLogger('universe')


class Maestro:
    """
    Implementation of the controller for Pololu Mini Maestro Controller.
    This class communicates with only one maestro on the virtual command port.

    This implementation is thread-safe.
    However, a servo can only belong to at most one thread.
    Having a servo in multiple threads will cause errors.
    """

    def __init__(self, port=None, baud=115200):
        """
        :param port: The virtual port number.
        :param baud: Baud rate. Should use maximum.
        """

        if port is not None:
            self.port = port
        else:
            # Determine the operating system and port strings.
            # Command port is used for USB Dual Port mode.
            # Can automatically determine from a scan.
            ports = list(list_ports.grep(r'(?i)1ffb:008b'))

            if os.name == 'nt':
                if len(ports) == 2:
                    if 'Command' in ports[0][1]:
                        self.port = ports[0][0]
                    else:
                        self.port = ports[1][0]
                else:
                    raise ConnectionError('Unable to determine the Command port automatically. Please specify.')
            else:
                if len(ports) == 2:
                    # Assuming nothing was messed with, the command port is the lower port.
                    if int(re.search(r'(\d+)$', ports[1][0]).group(0)) > int(re.search(r'(\d+)$', ports[0][0]).group(0)):
                        self.port = ports[0][0]
                    else:
                        self.port = ports[1][0]
                else:
                    raise ConnectionError('Unable to determine the Command port automatically. Please specify.')

        # Start a connection using pyserial.
        try:
            self.usb = serial.Serial(self.port, baudrate=baud, write_timeout=0)
            logger.debug('Using command port "{}".'.format(self.usb.port))
        except:
            raise ConnectionError('Unable to connect to servo controller at {}.'.format(self.port))

        # Struct objects are faster.
        self.struct = struct.Struct('<H')

        # Locks.
        self.read_lock = Lock()

    def write(self, buffer):
        """
        Send data to the Maestro.
        :param buffer: The data to send.
        """

        self.usb.write(buffer)

    def close(self):
        """
        Close the USB port.
        """

        self.usb.close()

    ##########################################
    # Begin implementation of static methods.
    ##########################################

    @staticmethod
    def endianize(value):
        """
        Endian formatting for Pololu commands.
        :param value: Integer value.
        :return: (lsb, msb)
        """
        return value & 0x7F, (value >> 7) & 0x7F

    ############################################
    # Begin implementation of digital protocol.
    ############################################

    def rotate(self, stepper, degrees, t):
        """
        Send some pulses in a given time with equal spacing per pulse.
        Blocking until completion.
        :param stepper: Stepper object.
        :param degrees: The number of degrees to turn.
        :param t: The total time.
        """

        steps = stepper.deg_to_steps(degrees)

        if steps == 0:
            return

        if steps > 0:
            direction = 1
            self.usb.write((0x84, stepper.c1, 64, 62))
        else:
            direction = -1
            self.usb.write((0x84, stepper.c1, 104, 7))

        steps = abs(steps)

        x = t / (2 * steps) / 1000
        low_pulse = (0x84, stepper.c2, 104, 7)
        high_pulse = (0x84, stepper.c2, 64, 62)

        for i in range(steps):
            self.usb.write(high_pulse)
            time.sleep(x)
            self.usb.write(low_pulse)
            time.sleep(x)

            stepper.step_one(direction)

    ##########################################################
    # Begin implementation of buffer-capable compact protocol.
    ##########################################################

    def set_target(self, servo, send=True):
        """
        Move a servo to its target.
        :param servo: A servo object.
        :param send: Whether or not to send instruction immediately.
        :return: The instruction tuple.
        """

        # Logging.
        logger.debug('Setting servo {}\'s position to {}.'.format(servo.channel, servo.target))

        # Use endian format suitable for Maestro.
        lsb, msb = self.endianize(servo.target)

        # Compose and send or return.
        ins = (0x84, servo.channel, lsb, msb)

        if send:
            self.usb.write(ins)

        return ins

    def set_speed(self, servo, speed, send=True):
        """
        Set the servo speed.
        :param servo: A servo object.
        :param speed: The speed in 0.25 us / 10 ms.
        :param send: Whether or not to send instruction immediately.
        :return: The instruction tuple.
        """

        # Logging.
        logger.debug('Setting servo {}\'s speed to {}.'.format(servo.channel, speed))

        # Use endian format suitable for Maestro.
        lsb, msb = self.endianize(speed)

        # Update object. However, this will not be accurate until send.
        servo.vel = speed

        # Compose and send or return.
        ins = (0x87, servo.channel, lsb, msb)

        if send:
            self.usb.write(ins)

        return ins

    def set_acceleration(self, servo, accel, send=True):
        """
        Set the servo acceleration.
        :param servo: A servo object.
        :param accel: The acceleration in 0.25 us / 10 ms / 80 ms. See documentation for different PWM.
        :param send: Whether or not to send instruction immediately.
        :return: The instruction tuple.
        """

        # Logging.
        logger.debug('Setting servo {}\'s acceleration to {}.'.format(servo.channel, accel))

        # Use endian format suitable for Maestro.
        lsb, msb = self.endianize(accel)

        # Update object. However, this will not be accurate until flush.
        servo.accel = accel

        # Compose and add to buffer.
        ins = (0x89, servo.channel, lsb, msb)

        if send:
            self.usb.write(ins)

        return ins

    ##########################################
    # Begin implementation of bulk operations.
    ##########################################

    def get_multiple_positions(self, servos):
        """
        Get multiple positions.
        :param servos: Servo objects.
        """

        data = bytearray()
        count = len(servos)
        size = 2 * count

        for servo in servos:
            data.extend((0x90, servo.channel))

        with self.read_lock:
            self.usb.write(data)
            reply = self.usb.read(size=size)

        for i in range(count):
            data = reply[2 * i: 2 * i + 2]
            servos[i].pwm = self.struct.unpack(data)[0]

    def set_multiple_targets(self, servos):
        """
        Set multiple targets with one command. Faster than multiple set_target().
        Only use for contiguous blocks!
        :param servos: Servo objects.
        """

        # Count the number of targets. Required by controller.
        count = len(servos)

        # Sort.
        servos = sorted(servos, key=lambda s: s.channel)

        # Start channel
        start = servos[0].channel

        # Data header.
        data = bytearray((0x9F, count, start))

        # Iterate through all servos, appending to data as needed.
        for servo in servos:
            target = servo.deg_to_maestro(servo.target)

            # Check contiguity.
            if servo.channel != start:
                raise Exception('Channels not contiguous!')
            else:
                start += 1

            lsb, msb = self.endianize(target)
            data.extend((lsb, msb))

            # Update object.
            servo.pwm = target

        # Write.
        self.usb.write(data)

    ##########################################
    # Begin implementation of read operations.
    ##########################################

    def get_position(self, servo):
        """
        Get the position of one servo.
        :param servo: A servo object.
        """

        with self.read_lock:
            # Send command and get reply.
            self.usb.write((0x90, servo.channel))
            reply = self.usb.read(size=2)

        # Unpack data.
        pwm = self.struct.unpack(reply)[0]

        # Set servo data.
        servo.pwm = pwm

    def get_moving_state(self):
        """
        Checks if any servos are moving.
        :return: Returns True if one or more servos are moving, else False.
        """

        with self.read_lock:
            # Send command and receive.
            self.usb.write((0x93,))
            reply = self.usb.read()

        # Check and return.
        if reply == b'\x00':
            return False
        else:
            return True

    def get_errors(self):
        """
        Gets errors.
        :return: Returns an integer reprenstation of an error or None if there are no errors.
        """

        with self.read_lock:
            # Send command and receive.
            self.usb.write((0xA1,))
            reply = self.usb.read(size=2)

        if reply:
            return self.struct.unpack(reply)[0]
        else:
            return None

    ###############################################
    # Begin implementation of accessory operations.
    ###############################################

    def set_pwm(self, time, period):
        """
        Set the PWM.
        :param time: The time parameter as specified by the documentation.
        :param period: THe period parameter as specified by the documentation.
        """

        # Use endian format suitable for Maestro.
        lsb1, msb1 = self.endianize(time)
        lsb2, msb2 = self.endianize(period)

        # Compose.
        data = (0x8A, lsb1, msb1, lsb2, msb2)

        # Write.
        self.usb.write(data)

    def go_home(self):
        """
        Return all servos to their home positions.
        """
        # Send command.
        self.usb.write((0xA2,))

    ############################################
    # Begin implementation of script operations.
    ############################################

    def stop_script(self):
        """
        Stops the running script.
        """

        # Send command.
        self.usb.write((0xA4,))

    # Restart script.
    def restart(self, subroutine, parameter=None):
        """
        Starts or restarts a script.
        :param subroutine: The subroutine number.
        :param parameter: An integer parameter to put on the stack for consumption.
        """

        # Construct command depending on parameter.
        if parameter is None:
            data = (0xA7, subroutine)
        else:
            lsb, msb = self.endianize(parameter)
            data = (0xA8, lsb, msb)

        # Send data.
        self.usb.write(data)

    def get_script_status(self):
        """
        Get a script status.
        :return: Returns True if script is running and False if it is not.
        """

        with self.read_lock:
            # Send command and receive.
            self.usb.write((0xAE,))
            reply = self.usb.read()

        # Check and return.
        if reply == b'\x00':
            return False
        else:
            return True

    ###################################################
    # Begin implementation of complex helper functions.
    ###################################################

    def end_in(self, servo, t=0, update=False):
        """
        Move one servo to it's target in t time.
        :param servo: A servo object.
        :param t: The time in ms for the operation. Set to 0 for max speed.
        :param update: Whether of not to update servo's position.
        """

        # Update servo positions as needed.
        if update:
            self.get_position(servo)

        # Max speed.
        if t == 0:
            t = abs(servo.target - servo.pwm) / servo.max_vel * 10

        # Already at target.
        if t == 0:
            return

        # Faster send.
        buffer = bytearray()

        # Set acceleration to zero.
        ins = self.set_acceleration(servo, 0, send=False)
        buffer.extend(ins)

        # Compute velocity as a change in 0.25us PWM / 10ms.
        delta = abs(servo.target - servo.pwm)
        vel = int(round(delta / t * 10))

        # Set velocity.
        ins = self.set_speed(servo, vel, send=False)
        buffer.extend(ins)

        # Send data.
        self.write(buffer)

        # Synchronize instruction.
        self.set_target(servo)

    def end_together(self, servos, t=0, update=False):
        """
        Move all servos to their respective targets such that they arrive together.
        This will reset all accelerations to 0 and flush buffer.
        :param servos: Servo objects.
        :param t: The time in ms for the operation. Set to 0 for max speed.
        :param update: Whether of not to update servo positions.
        """

        # Update servo positions as needed.
        if update:
            self.get_multiple_positions(servos)

        # Max speed.
        if t == 0:
            t = max([abs(servo.target - servo.pwm) / servo.max_vel * 10 for servo in servos])

        # Already at target.
        if t == 0:
            return

        # Faster send.
        buffer = bytearray()

        # Compute and set the velocity for every servo.
        for servo in servos:
            # Set acceleration to zero.
            ins = self.set_acceleration(servo, 0, send=False)
            buffer.extend(ins)

            # Compute velocity as a change in 0.25us PWM / 10ms.
            delta = abs(servo.target - servo.pwm)
            vel = int(round(delta / t * 10))

            # Set velocity.
            ins = self.set_speed(servo, vel, send=False)
            buffer.extend(ins)

        # Send data.
        self.write(buffer)

        # Synchronize instructions.
        buffer = bytearray()

        # Move all servos to their respective targets.
        for servo in servos:
            ins = self.set_target(servo, send=False)
            buffer.extend(ins)

        # Send to execute move.
        self.write(buffer)
