import logging
import os
import re
import serial
import struct
from serial.tools import list_ports

logger = logging.getLogger('universe')


class Maestro:
    def __init__(self, port=None, timeout=0):
        """
        :param port: The virtual port number.
        :param timeout: Timeout option for each transfer.
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
            self.usb = serial.Serial(self.port)
            logger.debug('Using command port "{}".'.format(self.usb.port))
        except:
            raise ConnectionError('Unable to connect to servo controller at {}.'.format(self.port))

        # Struct objects are faster.
        self.struct = struct.Struct('<H')

        # Data buffer.
        self.data = bytearray()

    def flush(self):
        """
        Flush data buffer and clear. Send the data buffer to the Maestro.
        """

        if len(self.data) > 0:
            self.usb.write(self.data)
            self.data.clear()

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

    ##########################################################
    # Begin implementation of buffer-capable compact protocol.
    ##########################################################

    def set_target(self, servo):
        """
        Move a servo to its target.
        :param servo: A servo object.
        """
        # Logging.
        logger.debug('Setting servo %s\'s position to %s.' % (servo.channel, servo.target))

        # Use endian format suitable for Maestro.
        lsb, msb = self.endianize(servo.target)

        # Compose and add to buffer.
        self.data.extend((0x84, servo.channel, lsb, msb))

    # Set servo speed.
    def set_speed(self, servo, speed):
        """
        Set the servo speed.
        :param servo: A servo object.
        :param speed: The speed in 0.25 us / 10 ms.
        """

        # Logging.
        logger.debug('Setting servo %s\'s speed to %s.' % (servo.channel, speed))

        # Use endian format suitable for Maestro.
        lsb, msb = self.endianize(speed)

        # Compose and add to buffer.
        self.data.extend((0x87, servo.channel, lsb, msb))

        # Update object. However, this will not be accurate until flush.
        servo.vel = speed

    # Set servo acceleration.
    def set_acceleration(self, servo, accel):
        """
        Set the servo acceleration.
        :param servo: A servo object.
        :param accel: The acceleration in 0.25 us / 10 ms / 80 ms. See documentation for different PWM.
        """

        # Logging.
        logger.debug('Setting servo %s\'s acceleration to %s.' % (servo.channel, accel))

        # Use endian format suitable for Maestro.
        lsb, msb = self.endianize(accel)

        # Compose and add to buffer.
        self.data.extend((0x89, servo.channel, lsb, msb))

        # Update object. However, this will not be accurate until flush.
        servo.accel = accel

    ##########################################
    # Begin implementation of bulk operations.
    ##########################################

    def get_multiple_positions(self, servos):
        """
        Get multiple positions.
        :param servos: Servo objects.
        """

        data = bytearray()

        for servo in servos:
            data.extend((0x90, servo.channel))

        self.usb.write(data)

        for servo in servos:
            reply = self.usb.read(size=2)
            servo.pwm = self.struct.unpack(reply)[0]

    def set_multiple_targets(self, servos):
        """
        Set multiple targets with one command. Faster than multiple set_target().
        Only use for contiguous blocks!
        :param servos: Servo objects.
        """

        # Count the number of targets. Required by controller.
        count = len(servos)

        # Sort.
        servos = sorted(servos, key=lambda servo: servo.channel)

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

        # Send command.
        self.usb.write((0x90, servo.channel))

        # Receive 2 bytes of data and unpack
        reply = self.usb.read(size=2)
        pwm = self.struct.unpack(reply)[0]

        # Set servo data.
        servo.pwm = pwm

    def get_moving_state(self):
        """
        Checks if any servos are moving.
        :return: Returns True if one or more servos are moving, else False.
        """

        # Send command.
        self.usb.write((0x93,))

        # Check and return.
        if self.usb.read() == b'\x00':
            return False
        else:
            return True

    def get_errors(self):
        """
        Gets errors.
        :return: Returns an integer reprenstation of an error or None if there are no errors.
        """

        # Send command.
        self.usb.write((0xA1,))

        # Process and return.
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

        # Send command.
        self.usb.write((0xAE,))

        # Check and return.
        if self.usb.read() == chr(0):
            return False
        else:
            return True

    ###################################################
    # Begin implementation of complex helper functions.
    ###################################################

    def end_together(self, servos, time=0, update=False):
        """
        Move all servos to their respective targets such that they arrive together.
        This will reset all accelerations to 0 and flush buffer.
        :param servos: Servo objects.
        :param time: The time in ms for the operation. Set to 0 for max speed.
        :param update: Whether of not to update servo positions.
        """

        # Flush buffer.
        self.flush()

        # Update servo positions as needed.
        if update:
            for servo in servos:
                self.get_position(servo)

        # Max speed.
        if time == 0:
            time = max([abs(servo.target - servo.pwm) / servo.max_vel * 10 for servo in servos])

        # Compute and set the velocity for every servo.
        for servo in servos:
            # Set acceleration to zero.
            self.set_acceleration(servo, 0)

            # Compute velocity as a change in 0.25us PWM / 10ms.
            delta = abs(servo.target - servo.pwm)
            vel = int(round(delta / time * 10))

            # Set velocity.
            self.set_speed(servo, vel)

        # Flush buffer to execute settings.
        self.flush()

        # Move all servos to their respective targets.
        for servo in servos:
            self.set_target(servo)

        # Flush to execute move.
        self.flush()
