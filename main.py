from beamngpy import BeamNGpy, Vehicle, Scenario
from beamngpy.sensors import Ultrasonic

import time

# Max allowed distance between obstacle and closest sensor
THRESHOLD_DISTANCE = 1


def initialize(
        scenario_config: Scenario = None,
        vehicle_config: Vehicle = None,
        init_pos: tuple[float, float, float] = (100, 100, 100),
        init_rotation: tuple[float, float, float, float] = (0, 0, 0, 0)):
    beam_instance = BeamNGpy('localhost', port=50977, home=HOME)
    beam_instance.open(launch=True)
    beam_instance.hide_hud()

    scenario = scenario_config or Scenario('gridmap_v2', 'ultrasonic_analysis')
    vehicle = vehicle_config or Vehicle('ego_vehicle', 'etk800', license='Maciej Hojda')
    scenario.add_vehicle(vehicle, pos=(-426.68, -43.59, 31.11), rot_quat=(0, 0, 1, 0))

    # left_rear = Ultrasonic('left_rear', beam_instance, vehicle, pos=(0, 0, 0), up=(0, 0, 0))
    # center_rear = Ultrasonic('center_rear', beam_instance, vehicle, pos=(0, 0, 0), up=(0, 0, 0))
    # right_rear = Ultrasonic('right_rear', beam_instance, vehicle, pos=(0, 0, 0), up=(0, 0, 0))

    # sensors = {
    #     'left_rear': left_rear,
    #     'center_rar': center_rear,
    #     'right_rear': right_rear
    # }
    #
    # for name, sensor in sensors.items():
    #     vehicle.attach_sensor(name, sensor)

    scenario.make(beam_instance)
    beam_instance.scenario.load(scenario)
    beam_instance.scenario.start()

    return {
        'bng': beam_instance,
        'scenario': scenario,
        'vehicle': vehicle,
        # 'sensors': sensors
    }


def main():
    instance = initialize()
    current_vehicle = instance['vehicle']

    def move_vehicle(pos, rot_quat):
        print('move')
        assert current_vehicle.is_connected()
        current_vehicle.teleport(pos, rot_quat)
        time.sleep(2)

        def ride(direction):
            current_vehicle.poll_sensors()
            start_pos = current_vehicle.state['pos'][1]
            gear = direction['gear']
            throttle = direction['throttle']

            # Move forward or backward
            current_vehicle.control(throttle=throttle, gear=gear, brake=0)
            print('ride')
            time.sleep(0.1)  # Small delay to allow for initial movement

            # Wait until the vehicle has moved approximately 4 meters
            while abs(current_vehicle.state['pos'][1] - start_pos) <= 5.0:
                current_vehicle.poll_ensors()
                print('reverse' if gear == -1 else 'follow')
                time.sleep(0.1)  # Adjust the delay as needed

            # Stop the vehicle
            current_vehicle.control(throttle=0, brake=1, gear=0)
            print('brake')

            # Wait until the vehicle velocity drops below 0.08 m/s to ensure it has stopped
            while current_vehicle.state['vel'][1] > 0.08:
                current_vehicle.poll_sensors()
                time.sleep(0.1)  # Adjust the delay as needed

            print(f'distance:  {abs(current_vehicle.state['pos'][1] - start_pos)}')
            print('end')

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
        print('FOLLOW=>REVERSE')
        ride(reverse_direction)

    move_vehicle(pos=(28, -150.59, 100.8), rot_quat=(0, 0, 1, 0))


    # # Data collection initialization
    # data = []
    #
    # # LET'S GOOOO
    # while True:
    #     time.sleep(1)
    #     sensors = current_vehicle.sensors.poll()
    #     stop_flag = False
    #
    #     # Do-while enforcement; when car stops then exit loop
    #     if sensors['electrics']['throttle'] == 0:
    #         break
    #
    #     # Data chunk from all ultrasonic sensors
    #     chunk = {}
    #
    #     # Read data from sensors
    #     for name, sensor in instance['sensors'].items():
    #         sensor_distance = sensors[name]['distance']
    #         chunk[name] = sensor_distance
    #
    #         # If any of sensors value reaches equal or lower to distance threshold set flag to start braking
    #         if sensor_distance <= THRESHOLD_DISTANCE:
    #             stop_flag = True
    #
    #     if stop_flag:
    #         current_vehicle.control(throttle=0, brake=1)

   #     data.append(chunk)




    # Data part here


if __name__ == '__main__':
    main()
