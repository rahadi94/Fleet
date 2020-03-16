from typing import List

from simpy import Environment

from Fleet_sim.charging_station import ChargingStation
from Fleet_sim.location import Location
from Fleet_sim.trip import Trip
from Fleet_sim.vehicle import Vehicle
from Fleet_sim.model import Model
import simpy

"""
 1) read data from persistence XXX
 2) create Vehicles based on that data XXX
 3) run simulation with vehicles
    3a) wait for request
    3b) pick up person
    3c) bring person to destination
    3d) go charge up
"""
env = simpy.Environment()
vehicle_data = [

    dict(id=1, env=env, initial_location=Location(5.1, 4.8), capacity=150, charge_state=100, mode='idle'),
    dict(id=2, env=env, initial_location=Location(5.3, 5.0), capacity=150, charge_state=100, mode='idle'),
    dict(id=3, env=env, initial_location=Location(5.0, 5.0), capacity=150, charge_state=100, mode='idle'),
    dict(id=4, env=env, initial_location=Location(4.9, 5.1), capacity=150, charge_state=100, mode='idle'),
    dict(id=5, env=env, initial_location=Location(4.8, 5.0), capacity=150, charge_state=100, mode='idle')

]
CS_data = [

    dict(id=1, env=env, location=Location(5.5, 5.5), power=5),
    dict(id=2, env=env, location=Location(4.8, 4.8), power=5),
    dict(id=3, env=env, location=Location(5.0, 5.0), power=5),
    dict(id=4, env=env, location=Location(5.2, 4.9), power=5),
    dict(id=5, env=env, location=Location(5.1, 4.9), power=5),

]
vehicles = list()

for data in vehicle_data:
    vehicle = (Vehicle(
        data['id'],
        data['env'],
        data['initial_location'],
        data['capacity'],
        data['charge_state'],
        data['mode']
    ))
    vehicles.append(vehicle)

charging_stations = list()

for data in CS_data:
    charging_station = (ChargingStation(
        data['id'],
        data['env'],
        data['location'],
        data['power'],

    ))
    charging_stations.append(charging_station)


sim = Model(env)
# I must define number of trips instead of one!!!!
envs = [env, env]
trips = [Trip(i) for i in envs]

for trip in trips:
    env.process(sim.run(vehicles, charging_stations, trips))

env.run(until=1000)

for vehicle in vehicles:
    print(vehicle.charge_state)
    print(vehicle.location.lat, vehicle.location.long)
    print(vehicle.count_times)
    print(vehicle.count_seconds)
# print(vehicles[1].__dict__)
"""
Extension:
1. Define charging station as a SimPy resource
2. Send the vehicle to the closest CS
3. Processes should be operated in parallel
4. Define a fleet as a class
5.
"""