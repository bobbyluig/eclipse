from agility.maestro import *
from agility.pololu.usc import Usc
from agility.pololu.reader import BytecodeReader
from agility.pololu.enumeration import uscParameter
import time, pickle
from pprint import pprint

if __name__ == '__main__':

    infile = 'in.4th'
    outfile = 'out.txt'

    controller = Usc()

    settings = controller.getUscSettings()
    settings.serialMode = 0
    controller.setUscSettings(settings, False)
    settings = controller.getUscSettings()
    pprint(vars(settings), depth=1)

    pickled = pickle.dumps(settings)
    print(pickled)

    '''
    reader = BytecodeReader()

    start = time.time()

    f = open('agility/forth/%s' % infile)
    data = f.read()
    f.close()

    program = reader.read(data, True)
    reader.writeListing(program, 'agility/forth/%s' % outfile)

    controller.loadProgram(program)
    controller.setScriptDone(0)

    print(time.time() - start)
    '''
