from agility.maestro import *
from agility.pololu.usc import Usc
from agility.pololu.reader import BytecodeReader
from agility.pololu.enumeration import uscParameter
import time

if __name__ == '__main__':

    infile = 'in.4th'
    outfile = 'out.txt'

    controller = Usc()

    print(controller.getRawParameter(uscParameter.PARAMETER_SERIAL_DEVICE_NUMBER))

    '''
    reader = BytecodeReader()

    f = open('agility/forth/%s' % infile)
    data = f.read()
    f.close()

    program = reader.read(data, True)
    reader.writeListing(program, 'agility/forth/%s' % outfile)

    controller.loadProgram(program)
    controller.setScriptDone(0)
    '''
