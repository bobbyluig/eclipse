from agility.pololu.usc import Usc
from agility.pololu.reader import BytecodeReader
from tools.timer import time_me


@time_me(2)
def script_test():
    infile = 'in.4th'
    outfile = 'out.txt'

    controller = Usc()
    reader = BytecodeReader()

    f = open('agility/forth/%s' % infile)
    data = f.read()
    f.close()

    program = reader.read(data, True)
    reader.writeListing(program, 'agility/forth/%s' % outfile)

    controller.loadProgram(program)
    controller.setScriptDone(1)


@time_me(2)
def settings_test():
    controller = Usc()

    settings = controller.getUscSettings()
    controller.saveSettings(settings, 'agility/pololu/settings.dat')
    settings = controller.loadSettings('agility/pololu/settings.dat')
    controller.fixSettings(settings)
    controller.setUscSettings(settings, False)

if __name__ == '__main__':
    script_test()
    settings_test()