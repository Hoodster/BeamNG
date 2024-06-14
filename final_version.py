import time
from beamngpy import BeamNGpy, Scenario, Vehicle, StaticObject, angle_to_quat
from beamngpy.sensors import Ultrasonic
import csv

# This file spawns pickup vehicle on a smallgrid map and places small drywall 10 m in the front of the car.
# The car has two ultrasonic sensors attached to the front bumper. 
# Every 0.5 s, data from sensors is polled and saved to a .csv file. 
# After 50 s, the simulation is closed.

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
    beamng = BeamNGpy('localhost', 64256, home=r"C:\Gry\BeamNG.tech.v0.31.3.0", user=r"C:\Gry\BeamNG.tech.v0.31.3.0")
    scenario = Scenario('smallgrid', 'tech_test123', description='Random driving for research')
    vehicle = Vehicle('vehicle1', model='pickup')
    wall = StaticObject(
        name='wall', 
        pos=(0, 10, 0),
        rot_quat=angle_to_quat((90, 0, 90)), scale=(1, 1, 1),
        shape='/art/shapes/objects/s_drywall.dae')

    with beamng.open(launch=True) as bng:
        scenario.add_object(wall)
        scenario.add_vehicle(vehicle, pos=(0, 0, 0.3), rot_quat=(0, 0, 1, 0))
        scenario.make(bng)
        
        setup_beamng(bng, scenario, vehicle)

        sensors = {
            "front left": Ultrasonic('ultrasonic Front', beamng, vehicle, pos=(0.6, -2.2, 0.6), dir=(0, -1, 0)),
            "front right": Ultrasonic('ultrasonic Front', beamng, vehicle, pos=(-0.6, -2.2, 0.6), dir=(0, -1, 0)),
        }
        

        with open('sensor_data.csv', 'w', newline='') as csvfile:
            fieldnames = sensors.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for i in range(100):
                measurements = get_new_data(sensors)
                writer.writerow(measurements)
                time.sleep(0.5)

            csvfile.close()
        
        beamng.close()

if __name__ == '__main__':
    main()
