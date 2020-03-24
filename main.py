
from Fleet_sim.charging_station import ChargingStation
from Fleet_sim.location import Location
from Fleet_sim.vehicle import Vehicle
from Fleet_sim.model import Model
import simpy

env = simpy.Environment()

# Initializing vehicles

vehicle_data = [

    dict(id=1, env=env, initial_location=Location(5.1, 4.8), capacity=150, charge_state=100, mode='idle'),
    dict(id=2, env=env, initial_location=Location(5.3, 5.0), capacity=150, charge_state=100, mode='idle'),
    dict(id=3, env=env, initial_location=Location(5.0, 5.0), capacity=150, charge_state=100, mode='idle'),
    dict(id=4, env=env, initial_location=Location(4.9, 5.1), capacity=150, charge_state=100, mode='idle'),
    dict(id=13, env=env, initial_location=Location(4.8, 5.0), capacity=150, charge_state=100, mode='idle')

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

# Initializing charging stations

CS_data = [

    dict(id=1, env=env, location=Location(5.5, 5.5), power=5),
    dict(id=2, env=env, location=Location(4.8, 4.8), power=5),
    dict(id=3, env=env, location=Location(5.0, 5.0), power=5),
    dict(id=4, env=env, location=Location(5.2, 4.9), power=5),
    dict(id=5, env=env, location=Location(5.1, 4.9), power=5),

]

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

env.process(sim.run(vehicles, charging_stations))
env.run(until=1000)

for vehicle in vehicles:
    print(vehicle.charge_state)
    print(vehicle.location.lat, vehicle.location.long)
    print(vehicle.count_times)
    print(vehicle.count_seconds)
# print(vehicles[1].__dict__)
"""
Extension:
. Processes should be operated in parallel
. Define a fleet as a class
. Use real data for trip generation
. Use a real city 
. Use driving distances between to points (i.g. Google Map)
. Record waiting time for each trip
. If there is no available car, the earliest option should assign to the trip (If vehicle in CS got enough charge
    or the best option among vehicles in service)
. Consider a waiting time tolerance for each trip after which the trip is missed
. Count missed trips
. Calculate charging cost and revenue 
. We can consider different size of vehicles
. We can consider different trips (pooling, multi-destination)
. V2G connection 
. We should measure waiting time, impact on the grid and REG utilization (First, we need to add REG to the model) 
"""