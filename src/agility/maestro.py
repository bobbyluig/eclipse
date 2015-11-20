import serial, os, struct, logging

logger = logging.getLogger(__name__)


class Servo:
    def __init__(self, channel, min_deg, max_deg, min_pwm, max_pwm, max_vel, direction=1):
        self.channel = channel # 0 to 17
        self.min_deg = min_deg # -360 to 360 as (degrees)
        self.max_deg = max_deg # -360 to 360 as (degrees)
        self.min_pwm = min_pwm * 4 # 0 to 4000 as (us pwm)
        self.max_pwm = max_pwm * 4 # 0 to 4000 as (us pwm)
        self.max_vel = max_vel # 0 to 1000, as (ms / 60deg)
        self.direction = direction

        # Dynamic current data.
        self.deg = (self.min_deg + self.max_deg) / 2
        self.vel = 0
        self.accel = 0

        # User defined target. Also used to store last target.
        self.target = self.deg

        # Compute constants.
        self.k_deg2mae = (self.max_pwm - self.min_pwm) / (self.max_deg - self.min_deg)
        self.k_mae2deg = (self.max_deg - self.min_deg) / (self.max_pwm - self.min_pwm)
        self.k_vel2mae = (60 * self.k_deg2mae) / self.max_vel * 10
        self.k_mae2vel = self.max_vel / ((60 * self.k_deg2mae) * 10)

    # Convert degrees to quarter us `.
    def deg_to_maestro(self, deg):
        return round(self.min_pwm + self.k_deg2mae * (deg - self.min_deg))

    # Convert quarter us PWM to degrees.
    def maestro_to_deg(self, pwm):
        return self.min_deg + self.k_mae2deg * (pwm - self.min_pwm)


class Maestro:
    def __init__(self, port=None, timeout=0):
        # Determine the operating system and port strings.
        # Command port is used for USB Dual Port mode.
        if os.name == 'nt':
            self.port = port or 3
        else:
            self.port = '/dev/ttyACM' + str(port or 0)

        # Start a connection using pyserial.
        try:
            self.usb = serial.Serial(self.port)
            logger.debug('Using command port "%s".' % self.usb.port)
        except:
            logger.critical('Unable to connect to servo controller.')

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
        # Normalize and convert target to PWM.
        target = servo.deg_to_maestro(servo.target)

        # logger.
        logger.debug('Setting servo %s\'s position to %s.' % (servo.channel, target))

        # Use endian format suitable for Maestro.
        lsb, msb = self.endianize(target)

        # Compose and add to buffer.
        self.data.extend((0x84, servo.channel, lsb, msb))

        # Update object.
        servo.deg = servo.target

    # Set servo speed.
    def set_speed(self, servo, speed):
        # logger.
        logger.debug('Setting servo %s\'s speed to %s.' % (servo.channel, speed))

        # Use endian format suitable for Maestro.
        lsb, msb = self.endianize(speed)

        # Compose and add to buffer.
        self.data.extend((0x87, servo.channel, lsb, msb))

        # Update object.
        servo.vel = speed

    # Set servo acceleration.
    def set_acceleration(self, servo, accel):
        # logger.
        logger.debug('Setting servo %s\'s acceleration to %s.' % (servo.channel, accel))

        # Use endian format suitable for Maestro.
        lsb, msb = self.endianize(accel)

        # Compose and add to buffer.
        self.data.extend((0x89, servo.channel, lsb, msb))

    ##########################################
    # Begin implementation of bulk operations.
    ##########################################

    # Set multiple targets with one command. Faster than multiple set_target().
    def set_multiple_targets(self, *servos):
        # Count the number of targets. Required by controller.
        count = len(servos)

        # Data header.
        data = bytearray((0x9F, count))

        # Iterate through all servos, appending to data as needed.
        for servo in servos:
            target = servo.deg_to_maestro(servo.target)
            lsb, msb = self.endianize(target)
            data.extend((servo.channel, lsb, msb))

            # Update object.
            servo.pwm = target
            servo.deg = servo.target

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
        servo.deg = servo.maestro_to_deg(pwm)

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
        self.usb.write(chr(0xA4))

    # Restart script.
    def restart(self, subroutine, parameter=None):
        # Construct command depending on parameter.
        if parameter is None:
            data = chr(0xA7) + chr(subroutine)
        else:
            lsb, msb = self.endianize(parameter)
            data = chr(0xA8) + chr(lsb) + chr(msb)

        # Send data.
        self.usb.write(data)

    # Get script status.
    def get_script_status(self):
        # Send command.
        self.usb.write(chr(0xAE))

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

        # Compute and set the velocity for every servo.
        for servo in servos:
            # Update servo positions as needed.
            if update:
                self.get_position(servo)

            # Set acceleration to zero.
            self.set_acceleration(servo, 0)

            # Compute velocity as a change in 0.25us PWM / 10ms.
            delta = abs(servo.target - servo.deg) * servo.k_deg2mae
            vel = int(round(delta / (time / 10)))

            # Set velocity.
            self.set_speed(servo, vel)

        # Flush buffer to execute settings.
        self.flush()

        # Move all servos to their respective targets.
        self.set_multiple_targets(*servos)
