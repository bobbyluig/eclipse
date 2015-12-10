import serial
import time

usb = serial.Serial(4, 9600)

while True:
    usb.write([69])
    data = usb.readline()
    print(data.decode('ascii').strip())