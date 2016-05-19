from agility.maestro import Maestro
from agility.main import Stepper

stepper = Stepper(0, 1, 200)
maestro = Maestro()
maestro.rotate(stepper, -360, 3000)