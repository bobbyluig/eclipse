from agility.pololu.usc import Usc
from agility.pololu.reader import BytecodeReader
from tools.timer import time_me
from agility.maestro import Maestro


def get_errors():
    controller = Maestro()
    print(controller.get_errors())


@time_me(1)
def script_test():
    infile = 'in.4th'
    outfile = 'out.txt'

    controller = Usc()
    reader = BytecodeReader()

    controller.clearErrors()

    f = open('agility/forth/%s' % infile)
    data = f.read()
    f.close()

    program = reader.read(data, False)
    reader.writeListing(program, 'agility/forth/%s' % outfile)
    controller.loadProgram(program)
    controller.setScriptDone(0)


@time_me(1)
def settings_test():
    controller = Usc()

    settings = controller.getUscSettings()
    controller.saveSettings(settings, 'agility/pololu/settings.dat')
    settings = controller.loadSettings('agility/pololu/settings.dat')
    controller.fixSettings(settings)
    controller.setUscSettings(settings, False)

if __name__ == '__main__':
    script_test()
    # settings_test()