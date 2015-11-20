from shared.agility.maestro import *
import time

if __name__ == '__main__':
    maestro = Maestro()

    s1 = Servo(0, 0, 270, 500, 2500, 160)
    s2 = Servo(1, 0, 270, 500, 2500, 160)

    def run():
        maestro.set_speed(s1, 200)
        maestro.set_speed(s2, 400)
        maestro.flush()

    import timeit

    t = timeit.Timer(lambda: run())
    print(t.timeit(number=1000))

