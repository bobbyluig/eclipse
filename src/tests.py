from agility.pololu.usc import Usc
from agility.pololu.reader import BytecodeReader
from tools.timer import timeIt
from agility.maestro import Maestro
from pprint import pprint
from lykos.apollo import Apollo

try:
    usc = Usc()
except:
    pass

try:
    maestro = Maestro()
except:
    pass

try:
    apollo = Apollo(-2)
except:
    pass


def getErrors():
    maestro.get_errors()


def audioCapture():
    apollo.blockingDetect(lambda: print('Howl Detected'))


@timeIt(100)
def getVariables():

    variables = usc.getVariables('variables')
    servos = usc.getVariables('servos')
    stack = usc.getVariables('stack')
    callStack = usc.getVariables('callStack')


@timeIt(1)
def scriptTest():
    infile = 'in.4th'
    outfile = 'out.txt'

    reader = BytecodeReader()

    usc.clearErrors()

    f = open('agility/forth/%s' % infile)
    data = f.read()
    f.close()

    program = reader.read(data, False)
    reader.writeListing(program, 'agility/forth/%s' % outfile)
    usc.loadProgram(program)
    usc.setScriptDone(0)


@timeIt(1)
def settingsTest():
    settings = usc.getUscSettings()
    usc.saveSettings(settings, 'agility/pololu/settings.dat')
    settings = usc.loadSettings('agility/pololu/settings.dat')
    usc.fixSettings(settings)
    usc.setUscSettings(settings, False)


def testVideo(camera):
    speed_test(camera)
    dlib_test(camera)


if __name__ == '__main__':
    audioCapture()