import serial
from serial.tools import list_ports
from time import sleep


ports = list(list_ports.grep(r'(?i)0403'))
port = ports[0][0]

reader = serial.Serial(port=port, timeout=0)

while True:
    if reader.inWaiting() >= 16:
        data = reader.read(size=16)
        data = data.decode()

        # Assert for debugging verification.
        assert(data[0] == '\x02')
        assert(data[13:] == '\r\n\x03')

        rfid = data[1:13]

        print(rfid)
    else:
        sleep(0.1)
