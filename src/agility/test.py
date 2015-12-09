import serial
import time

usb = serial.Serial(4, 38400)

while True:
    data = usb.readline()
    print(data.decode().strip())