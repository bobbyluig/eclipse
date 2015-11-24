from agility.pololu.usc import Usc
from agility.pololu.reader import BytecodeReader
from tools.timer import time_me
from agility.maestro import Maestro
from pprint import pprint

usc = Usc()
maestro = Maestro()


def get_errors():
    maestro.get_errors()


@time_me(100)
def get_variables():

    variables = usc.getVariables('variables')
    servos = usc.getVariables('servos')
    stack = usc.getVariables('stack')
    callStack = usc.getVariables('callStack')


@time_me(1)
def script_test():
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


@time_me(1)
def settings_test():
    settings = usc.getUscSettings()
    usc.saveSettings(settings, 'agility/pololu/settings.dat')
    settings = usc.loadSettings('agility/pololu/settings.dat')
    usc.fixSettings(settings)
    usc.setUscSettings(settings, False)


if __name__ == '__main__':
    # script_test()
    # settings_test()
    get_variables()