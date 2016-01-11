import serial, os, struct, logging, re
from serial.tools import list_ports

logger = logging.getLogger('universe')


class Servo:
    def __init__(self, channel, min_deg, max_deg, min_pwm, max_pwm, max_vel,
                 bias=0, direction=1):
        self.channel = channel # 0 to 17
        self.min_deg = min_deg # -360 to 360 as (degrees)
        self.max_deg = max_deg # -360 to 360 as (degrees)
        self.min_pwm = min_pwm * 4 # 0 to 4000 as (us)
        self.max_pwm = max_pwm * 4 # 0 to 4000 as (us)
        self.max_vel = max_vel # 0 to 1000, as (ms / 60deg)

        # Bias should be adjusted such that the servo is at kinematic "0" degree when it's target is 0 degrees.
        # This is used to compensate for ridge spacing and inaccuracies during installation.
        # Think of this like the "home" value of the servo.
        self.bias = bias

        # If the front of the servo is pointing in a negative axis, set this to negative 1.
        # This reverses the directionality of all angle inputs.
        self.direction = direction

        # Dynamic current data.
        self.pwm = 0
        self.vel = 0
        self.accel = 0

        # User defined target. Also used to store last target.
        # In units of 0.25 us.
        self.target = 0

        # Compute constants.
        self.k_deg2mae = (self.max_pwm - self.min_pwm) / (self.max_deg - self.min_deg)
        self.k_mae2deg = (self.max_deg - self.min_deg) / (self.max_pwm - self.min_pwm)
        self.k_vel2mae = (60 * self.k_deg2mae) / self.max_vel * 10
        self.k_mae2vel = self.max_vel / ((60 * self.k_deg2mae) * 10)

    def set_target(self, deg):
        # Account for direction and bias.
        deg = deg * self.direction + self.bias

        # Normalize.
        if deg > self.max_deg:
            deg -= 360
        elif deg < self.min_deg:
            deg += 360

        if deg > self.max_deg or deg < self.min_deg:
            raise Exception('Target out of range!')

        self.target = self.deg_to_maestro(deg)

    def at_target(self):
        return self.target == self.pwm

    # Convert degrees to 0.25 us `.
    def deg_to_maestro(self, deg):
        return round(self.min_pwm + self.k_deg2mae * (deg - self.min_deg))

    # Convert 0.25 us to degrees.
    def maestro_to_deg(self, pwm):
        return self.min_deg + self.k_mae2deg * (pwm - self.min_pwm)


class Maestro:
    def __init__(self, port=None, timeout=0):
        # Determine the operating system and port strings.
        # Command port is used for USB Dual Port mode.
        # Can automatically determine from a scan.
        ports = list(list_ports.grep(r'(?i)1ffb:008b'))

        if os.name == 'nt':
            if port is not None:
                self.port = port
            else:
                if len(ports) == 2:
                    if 'Command' in ports[0][1]:
                        self.port = ports[0][0]
                    else:
                        self.port = ports[1][0]
                else:
                    raise Exception('Unable to determine the Command port automatically. Please specify.')
        else:
            if port is not None:
                self.port = port
            else:
                if len(ports) == 2:
                    # Assuming nothing was messed with, the command port is the lower port.
                    if int(re.search(r'(\d+)$', ports[1][0]).group(0)) > int(re.search(r'(\d+)$', ports[0][0]).group(0)):
                        self.port = ports[0][0]
                    else:
                        self.port = ports[1][0]
                else:
                    raise Exception('Unable to determine the Command port automatically. Please specify.')

        # Start a connection using pyserial.
        try:
            self.usb = serial.Serial(self.port)
            logger.debug('Using command port "%s".' % self.usb.port)
        except:
            raise Exception('Unable to connect to servo controller at %s.' % self.port)

        # Data buffer.
        self.data = bytearray()

    # Flush data buffer and clear.
    def flush(self):
        if len(self.data) > 0:
            self.usb.write(self.data)
            self.data.clear()

    # Closing the USB port.
    def close(self):
        self.usb.close()

    ##########################################
    # Begin implementation of static methods.
    ##########################################

    # Endian formatting for Pololu commands.
    @staticmethod
    def endianize(value):
        return value & 0x7F, (value >> 7) & 0x7F

    ##########################################################
    # Begin implementation of buffer-capable compact protocol.
    ##########################################################

    # Move a servo to the target defined by its object representation.
    def set_target(self, servo):
        # Logging.
        logger.debug('Setting servo %s\'s position to %s.' % (servo.channel, servo.target))

        # Use endian format suitable for Maestro.
        lsb, msb = self.endianize(servo.target)

        # Compose and add to buffer.
        self.data.extend((0x84, servo.channel, lsb, msb))

    # Set servo speed.
    def set_speed(self, servo, speed):
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

    # Set multiple targets with one command. Faster than multiple set_target().
    # Only use for contiguous blocks!
    def set_multiple_targets(self, *servos):
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

    # Get the position of one servo. (An update operation on the object).
    def get_position(self, servo):
        # Send command.
        self.usb.write((0x90, servo.channel))

        # Receive 2 bytes of data and unpack
        reply = self.usb.read(size=2)
        pwm = struct.unpack('<H', reply)[0]

        # Set servo data.
        servo.pwm = pwm

    # Get if any servos are moving.
    def get_moving_state(self):
        # Send command.
        self.usb.write((0x93,))

        # Check and return.
        if self.usb.read() == b'\x01':
            return True
        else:
            return False

    # Get errors.
    def get_errors(self):
        # Send command.
        self.usb.write((0xA1,))

        # Process and return.
        reply = self.usb.read(size=2)
        if reply:
            return struct.unpack('<H', reply)[0]
        else:
            return None

    ###############################################
    # Begin implementation of accessory operations.
    ###############################################

    # Set PWM.
    def set_pwm(self, time, period):
        # Use endian format suitable for Maestro.
        lsb1, msb1 = self.endianize(time)
        lsb2, msb2 = self.endianize(period)

        # Compose.
        data = (0x8A, lsb1, msb1, lsb2, msb2)

        # Write.
        self.usb.write(data)

    # Go hard, or go home.
    def go_home(self):
        # Send command.
        self.usb.write(chr(0xA2))

    ############################################
    # Begin implementation of script operations.
    ############################################

    # Stop script.
    def stop_script(self):
        # Send command.
        self.usb.write((0xA4,))

    # Restart script.
    def restart(self, subroutine, parameter=None):
        # Construct command depending on parameter.
        if parameter is None:
            data = (0xA7, subroutine)
        else:
            lsb, msb = self.endianize(parameter)
            data = (0xA8, lsb, msb)

        # Send data.
        self.usb.write(data)

    # Get script status.
    def get_script_status(self):
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

    # Move all servos to their respective targets such that they arrive together.
    # This will reset all accelerations to 0 and flush buffer.
    # The time is how long the turn should take in milliseconds.
    # Update determines whether or not to update servo positions. Slow operation.
    def end_together(self, *servos, time=1000, update=False):
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
