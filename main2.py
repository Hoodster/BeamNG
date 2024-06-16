from beamngpy import BeamNGpy, Scenario, Vehicle, StaticObject, angle_to_quat
from beamngpy.sensors import Ultrasonic
from environs import Env
import csv, time

# BeamNG instance settings
# EDIT THESE IN .env FILE
env = Env()
env.read_env()
PATH = env('PROJ_PATH')
PORT = int(env('PORT'))

print(PATH)

# EDITABLE (but not recommended)
THROTTLE = .2   # in meters per second
DISTANCE = 4.5  # in meters (mind some braking distance)


def setup_beamng(bng, scenario, vehicle, obstacles):
    bng.settings.change('GraphicDisplayResolutions', '1280 720')
    bng.settings.change('GraphicDisplayModes', 'Window')
    bng.settings.apply_graphics()
    bng.settings.set_deterministic(60)
    bng.ui.hide_hud()

    scenario.add_vehicle(vehicle, pos=(0, 0, 0.3), rot_quat=(0, 0, 1, 0))
    for obstacle in obstacles:
        scenario.add_object(obstacle)
    scenario.make(bng)

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
    # change in .env file
    beamng = BeamNGpy('localhost', PORT, home=HOME, user=PATH)
    scenario = Scenario('smallgrid', 'tech_test123', description='Random driving for research')
    vehicle = Vehicle('vehicle1', model='pickup')

    objects = []
    names = []
    wall = StaticObject(
        name='wall', 
        pos=(0, 8, 0),
        rot_quat=angle_to_quat((90, 0, 90)), scale=(3, 1, 1),
        shape='/art/shapes/objects/s_drywall.dae')
    objects.append(wall)
    names.append('wall')
    curbstone = StaticObject(
        name='curbstone',
        pos=(10, 8, 0),
        rot_quat=angle_to_quat((90, 0, 90)), scale=(0.2, 1, 1),
        shape='/art/shapes/objects/s_drywall.dae')
    objects.append(curbstone)
    names.append('curbstone')
    fakesign = StaticObject(
        name='fakesign',
        pos=(20, 8, 0),
        rot_quat=angle_to_quat((0, 90, 90)), scale=(0.050, 2.500, 0.050),
        shape='/art/shapes/objects/s_spool_wire.dae')
    objects.append(fakesign)
    names.append('fakesign')
    verticalpipe = StaticObject(
        name='verticalpipe',
        pos=(30, 8, 1.5),
        rot_quat=angle_to_quat((90, 0, 90)), scale=(0.050, 2.500, 0.050),
        shape='/art/shapes/objects/s_spool_wire.dae')
    objects.append(verticalpipe)
    names.append('verticalpipe')
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
        setup_beamng(bng, scenario, vehicle,objects)
        pos = (0,0,0.3)
        for i in range(len(objects)):
            sensors = {
                "front left": Ultrasonic('ultrasonic Front', beamng, vehicle, pos=(0.6, -2.2, 0.6), dir=(0, -1, 0)),
                "front right": Ultrasonic('ultrasonic Front', beamng, vehicle, pos=(-0.6, -2.2, 0.6), dir=(0, -1, 0)),
            }

            simulate_movement(names[i], pos=pos, rot_quat=(0, 0, -1, 0))
            pos = (pos[0] + 10, 0, 0.3)
        

if __name__ == '__main__':
    main()
