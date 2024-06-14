import time
import threading

import matplotlib.pyplot as plt
import matplotlib.animation as animation

from beamngpy import BeamNGpy, Scenario, Vehicle, set_up_simple_logging
from beamngpy.sensors import Ultrasonic

ultrasonic_front_data = []
ultrasonic_rear_data = []
time_steps = []

def update_plot(frame, ultrasonic_front_data, ultrasonic_rear_data, time_steps, line1, line2):
    if len(ultrasonic_front_data) > 0 and len(time_steps) > 0:
        line1.set_data(time_steps, ultrasonic_front_data)

    if len(ultrasonic_rear_data) > 0 and len(time_steps) > 0:
        line2.set_data(time_steps, ultrasonic_rear_data)
    ax.relim()
    ax.autoscale_view()

    return line1, line2


def main():
    global ax

    set_up_simple_logging()

    beamng = BeamNGpy('localhost', 50977, home=r'C:\Users\kubap\Desktop\BeamNG\BeamNG.tech.v0.32.2.0', user=r'C:\Users\kubap\Desktop\BeamNG\BeamNG.tech.v0.32.2.0')
    bng = beamng.open(launch=True)

    bng.settings.change('GraphicDisplayResolutions', '1280 720')
    bng.settings.change('GraphicDisplayModes', 'Window')
    bng.settings.apply_graphics()

    scenario = Scenario('gridmap_v2', 'tech_test123', description='Random driving for research')
    vehicle = Vehicle('vehicle1', model='pickup')

    scenario.add_vehicle(vehicle, pos=(28, -77, 100), rot_quat=(0, 0, 1, 0))
    scenario.make(bng)

    try:
        bng.ui.hide_hud()
        bng.settings.set_deterministic(60)

        bng.scenario.load(scenario)
        bng.scenario.start()

        assert vehicle.is_connected()

        ultrasonic_front = Ultrasonic('ultrasonic Front', beamng, vehicle, pos=(0, -2, 1.7), dir=(0, -1, 0))
        ultrasonic_rear = Ultrasonic('ultrasonic Rear', beamng, vehicle, pos=(0, 3, 1.7), dir=(0, 1, 0))

        fig, ax = plt.subplots()

        ax.set_xlabel('Time Step')
        ax.set_ylabel('Ultrasonic Distance (m)')
        ax.set_title('Ultrasonic Distance vs Time')
        ax.set_ylim(-1, 10)

        line1, = ax.plot([], [], lw=2, label='Front sensor')
        line2, = ax.plot([], [], lw=2, label='Rear sensor')

        ax.legend()

        def init():
            line1.set_data([], [])
            line2.set_data([], [])
            return line1, line2

        def update(frame):
            front_data = ultrasonic_front.poll()
            rear_data = ultrasonic_rear.poll()

            front_distance = front_data['distance']
            rear_distance = rear_data['distance']

            print(f"Front sensor distance: {front_distance}, Rear sensor distance: {rear_distance}")

            ultrasonic_front_data.append(front_distance)
            ultrasonic_rear_data.append(rear_distance)

            time_steps.append(len(ultrasonic_front_data))

            return update_plot(frame, ultrasonic_front_data, ultrasonic_rear_data, time_steps, line1, line2)

        ani = animation.FuncAnimation(fig, update, frames=range(1024), init_func=init, blit=True)

        plt.show()

        def move_vehicle(pos, rot_quat):
            print('move')
            assert vehicle.is_connected()
            vehicle.teleport(pos, rot_quat)
            time.sleep(2)

            def ride(direction):
                vehicle.poll_sensors()
                start_pos = vehicle.state['pos'][1]
                gear = direction['gear']
                throttle = direction['throttle']

                # Move forward or backward
                vehicle.control(throttle=throttle, gear=gear, brake=0)
                time.sleep(0.1)  # Small delay to allow for initial movement

                # Wait until the vehicle has moved approximately 4 meters
                while abs(vehicle.state['pos'][1] - start_pos) <= 5.0:
                    vehicle.poll_sensors()
                    time.sleep(0.1)  # Adjust the delay as needed

                # Stop the vehicle
                vehicle.control(throttle=0, brake=1, gear=0)

                # Wait until the vehicle velocity drops below 0.08 m/s to ensure it has stopped
                while vehicle.state['vel'][1] > 0.08:
                    vehicle.poll_sensors()
                    time.sleep(0.1)  # Adjust the delay as needed

            direction = {
                'gear': 2,
                'throttle': 0.2,
            }

            reverse_direction = {
                'gear': -1,
                'throttle': 0.2,
            }

            ride(direction)
            time.sleep(1)
            ride(reverse_direction)

        time.sleep(12)

        # ########################### TUTAJ WPROWADZAMY POZYCJE SAMOCHODU ######################################### #

        move_vehicle(pos=(28, -149, 101), rot_quat=(0, 0, 1, 0))

        # ########################################################################################################## #


    finally:
        bng.close()


if __name__ == '__main__':
    main()
