from beamngpy import BeamNGpy, Vehicle, Scenario
from beamngpy.sensors import Ultrasonic
import time

# Max allowed distance between obstacle and closest sensor
THRESHOLD_DISTANCE = 1

PORT = 2137
HOME = '/dir'
USER = '/dir'


def initialize(scenario_config: Scenario = None, vehicle_config: Vehicle = None):
    beam_instance = BeamNGpy('localhost', port=PORT, home=HOME, user=USER)
    beam_instance.open(launch=True)
    beam_instance.hide_hud()

    scenario = scenario_config or Scenario('west_coast_usa', 'ultrasonic_analysis')
    vehicle = vehicle_config or Vehicle('ego_vehicle', 'etk800', license='Maciej Hojda')

    sensors = {
        'left_rear': Ultrasonic('left_rear', beam_instance, pos=(0, 0, 0), up=(0, 0, 0)),
        'center_rear': Ultrasonic('center_rear', beam_instance, pos=(0, 0, 0), up=(0, 0, 0)),
        'right_rear': Ultrasonic('right_rear', beam_instance, pos=(0, 0, 0), up=(0, 0, 0))
    }

    for name, sensor in sensors.items():
        vehicle.attach_sensor(name, sensor)

    scenario.add_vehicle(vehicle, pos=(0, 0, 0))
    scenario.make(beam_instance)
    beam_instance.scenario.load(scenario)
    beam_instance.scenario.start()

    return {
        'bng': beam_instance,
        'scenario': scenario,
        'vehicle': vehicle,
        'sensors': sensors
    }


def main():
    instance = initialize()
    current_vehicle = instance['vehicle']

    # Drive reverse with around 5km/h (~0.2
    current_vehicle.control(throttle=.2, gear=-1)

    # Data collection initialization
    data = []

    # LET'S GOOOO
    while True:
        time.sleep(1)
        sensors = current_vehicle.sensors.poll()
        stop_flag = False

        # Do-while enforcement; when car stops then exit loop
        if sensors['electrics']['throttle'] == 0:
            break

        # Data chunk from all ultrasonic sensors
        chunk = {}

        # Read data from sensors
        for name, sensor in instance['sensors'].items():
            sensor_distance = sensors[name]['distance']
            chunk[name] = sensor_distance

            # If any of sensors value reaches equal or lower to distance threshold set flag to start braking
            if sensor_distance <= THRESHOLD_DISTANCE:
                stop_flag = True

        if stop_flag:
            current_vehicle.control(throttle=0, brake=1)

        data.append(chunk)

    instance['bng'].close()

    # Data part here


if __name__ == '__main__':
    main()
