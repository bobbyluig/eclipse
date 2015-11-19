from shared.cerebral.hippocampus import Memory
import time

memory = Memory()

if __name__ == '__main__':
    servo = memory.servos[0]
    memory.maestro.set_speed(servo, int(round(servo.k_vel2mae * 1)))
    servo.target = 90
    memory.maestro.set_target(servo)
    memory.maestro.flush()

    while memory.maestro.get_moving_state():
        time.sleep(0.01)

    servo.target = 0
    memory.maestro.set_target(servo)
    memory.maestro.flush()