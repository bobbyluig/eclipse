from agility.maestro import *
import time

if __name__ == '__main__':
    maestro = Maestro()

    s1 = Servo(0, 0, 270, 500, 2500, 160)
    s2 = Servo(1, 0, 270, 500, 2500, 160)

    def run():
        maestro.get_position(s1)

    import timeit

    t = timeit.Timer(lambda: run())
    print(t.timeit(number=5000))

