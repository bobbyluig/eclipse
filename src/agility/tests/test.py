import serial
import time

usb = serial.Serial(5, 9600)

while True:
    data = usb.readline()
    print(data.decode('ascii').strip())