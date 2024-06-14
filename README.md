

## API Reference

#### Setup BeamNG environment

```python
  setup_beamng(bng, scenario, vehicle, obstacles)
```

| Parameter   | Type     | Description                |
|:------------| :------- | :------------------------- |
| `bng`       | [BeamNGpy](https://beamngpy.readthedocs.io/en/latest/beamngpy.html#beamngpy) | **Required**. BeamNG instance |
| `scenario`  | [Scenario](https://beamngpy.readthedocs.io/en/latest/beamngpy.html#beamngpy.Scenario) | **Required**. Scenario instance |
| `vehicle`   | [Vehicle](https://beamngpy.readthedocs.io/en/latest/beamngpy.html#beamngpy.Vehicle) | **Required**. Vehicle instance |
| `obstacles` | `[ScenarioObject]` | Additional elements like walls, curbs or poles. See [ScenarioObject](https://beamngpy.readthedocs.io/en/latest/beamngpy.html#beamngpy.ScenarioObject). |

Orchiestrates vehicle, scenario, all other objects into `BeamNGpy` instance.

#### Run simulation

```python
  simulate_motion(simulation_name, pos, quat_rot, opt_forward, opt_backward)
```

| Parameter | Type     | Description                       | Default value |
| :-------- | :------- | :------ |:-------------------------------- |
| `simulation_name`      | `str` | **Required**. Name of simulation |
| `pos`      | `Float3` | **Required**.  Position (x,y,z) of vehicle |
| `quat_rot`      | `(double, double, double, double)` | **Required**. Vehicle rotation |
| `opt_forward`      | `dict[]` | Drive forward settings | {'throttle': `THROTTLE`, 'distance': `DISTANCE`, 'gear': 2}
| `opt_backward`    |   `dict[]` | Drive backward settings | {'throttle': `THROTTLE`, 'distance': `DISTANCE` * 2, 'gear':-1}


Teleports map of given pos and rotation by given distance with speed (throttle). Later saves and exports results from ultrasonic sensors to "sensor_data_{simulation_name}.csv" file.


