import time
from beamngpy import BeamNGpy, Scenario, Vehicle, StaticObject, angle_to_quat
from beamngpy.sensors import Ultrasonic
import csv

# This file spawns pickup vehicle on a smallgrid map and places small drywall 10 m in the front of the car.
# The car has two ultrasonic sensors attached to the front bumper. 
# Every 0.5 s, data from sensors is polled and saved to a .csv file. 
# After 50 s, the simulation is closed.

THROTTLE = .2 # in meters per second
DISTANCE = 4.5 # in meters
DATA_SPAN = .5 # in seconds

def setup_beamng(bng, scenario, vehicle):
    bng.settings.change('GraphicDisplayResolutions', '1280 720')
    bng.settings.change('GraphicDisplayModes', 'Window')
    bng.settings.apply_graphics()
    bng.settings.set_deterministic(60)
    bng.ui.hide_hud()
    bng.scenario.load(scenario)
    bng.scenario.start()
    assert vehicle.is_connected()

def get_new_data(sensors):
    distances = {}
    for sensor_name in sensors.keys():
        distance = sensors[sensor_name].poll()['distance']
        distances[sensor_name] = distance
        print(f"{sensor_name} distance: {distance}")
    return distances

def main():
    beamng = BeamNGpy('localhost', 50977, home=r'C:\Users\kubap\Desktop\BeamNG\BeamNG.tech.v0.32.2.0',
                      user=r'C:\Users\kubap\Desktop\BeamNG\BeamNG.tech.v0.32.2.0')
    scenario = Scenario('smallgrid', 'tech_test123', description='Random driving for research')
    vehicle = Vehicle('vehicle1', model='pickup')
    wall = StaticObject(
        name='wall', 
        pos=(0, 8, 0),
        rot_quat=angle_to_quat((90, 0, 90)), scale=(1, 1, 1),
        shape='/art/shapes/objects/s_drywall.dae')

    sensor_data = []

    def print_results(scenario_name):
        with open(f'sensor_data_{scenario_name}.csv', 'w', newline='') as csvfile:
            fieldnames = sensors.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for item in sensor_data:
                writer.writerow(item)

            csvfile.close()
            sensor_data.clear()

    def simulate_movement(simulation_name, pos, rot_quat, forward_opts = None, backward_opts = None):
        vehicle.teleport(pos=pos, rot_quat=rot_quat)
        assert vehicle.is_connected()
        time.sleep(.2)

        forward = forward_opts or {
            'throttle': THROTTLE,
            'distance': DISTANCE,
            'gear': 2,
        }

        backward = backward_opts or {
            'throttle': THROTTLE,
            'distance': DISTANCE * 2,
            'gear': -1
        }

        def ride(direction):
            def get_current_position():
                vehicle.poll_sensors()
                return vehicle.state['pos'][1]

            def get_current_speed():
                vehicle.poll_sensors()
                return abs(vehicle.state['vel'][1])

            is_braking = False
            start_pos = get_current_position()

            while get_current_speed() > 0.2 or not is_braking:

                if is_braking:
                    vehicle.control(throttle=0, brake=1, parkingbrake=1, gear=0)
                else:
                    vehicle.control(throttle=direction['throttle'], gear=direction['gear'], brake=0, parkingbrake=0)
                    is_braking = abs(get_current_position() - start_pos) >= direction['distance']

                measure = get_new_data(sensors)
                sensor_data.append(measure)

            print(f'Stopped at position Y:   {get_current_position()}')

        ride(forward)
        ride(backward)
        print_results(simulation_name)
        time.sleep(5)

    with beamng.open(launch=True) as bng:
        scenario.add_object(wall)
        scenario.add_vehicle(vehicle, pos=(0, 0, 0.3), rot_quat=(0, 0, 1, 0))
        scenario.make(bng)
        setup_beamng(bng, scenario, vehicle)

        sensors = {
            "front left": Ultrasonic('ultrasonic Front', beamng, vehicle, pos=(0.6, -2.2, 0.6), dir=(0, -1, 0)),
            "front right": Ultrasonic('ultrasonic Front', beamng, vehicle, pos=(-0.6, -2.2, 0.6), dir=(0, -1, 0)),
        }

        simulate_movement('sample_name', pos=(0, 0, 0.3), rot_quat=(0, 0, -1, 0))
        




if __name__ == '__main__':
    main()
