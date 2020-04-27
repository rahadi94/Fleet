from Fleet_sim.Zone import Zone
from Fleet_sim.charging_station import ChargingStation
from Fleet_sim.location import Location
from Fleet_sim.model import Model
import simpy
import random
from Fleet_sim.vehicle import Vehicle

env = simpy.Environment()

zones = list()
stepsize = 5
z = 0
for x in range(670, 720, stepsize):
    for y in range(5080, 5110, stepsize):
        z += 1
        zone = Zone(z, Location(x / 100, y / 100))
        zones.append(zone)


def generate_location():
    return Location(random.uniform(6.70, 7.20), random.uniform(50.80, 51.10))


vehicles_data = []
for i in range(200):
    vehicle_data = dict(id=i, env=env, initial_location=generate_location(), capacity=150, charge_state=100,
                        mode='idle')
    vehicles_data.append(vehicle_data)

vehicles = list()

for data in vehicles_data:
    vehicle = Vehicle(
        data['id'],
        data['env'],
        data['initial_location'],
        data['capacity'],
        data['charge_state'],
        data['mode']
    )
    vehicles.append(vehicle)
vehicles = vehicles[:50]
# Initializing charging stations

CS_data = [

    dict(id=1, env=env, location=Location(6.85, 50.90), power=5),
    dict(id=2, env=env, location=Location(7.10, 51.00), power=5),
    dict(id=3, env=env, location=Location(7.00, 50.95), power=5),
    dict(id=4, env=env, location=Location(6.95, 51.05), power=5),
    dict(id=5, env=env, location=Location(7.05, 50.90), power=5),

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
charging_stations = charging_stations[:5]
sim = Model(env)
for zone in zones:
    env.process(sim.trip_generation(zone))
env.process(sim.run(vehicles, charging_stations, zones))

for vehicle in vehicles:
    env.process(sim.obs_Ve(vehicle))

for charging_station in charging_stations:
    env.process(sim.obs_CS(charging_station))

env.run(until=sim.simulation_time)

for vehicle in vehicles:
    print(vehicle.charge_state)
    print(vehicle.id)
    print(vehicle.count_times)
    print(vehicle.count_seconds)
sim.save_results(vehicles, charging_stations)
"""
Extension and debugs:
. Use rule-based relocation model
. Consider parking cost when a vehicle do not move
. Use logging in your code
. Use real data for trip demands
. Should vehicles wait for travelers?
. Use a real city
. Use driving distances between two points (i.g. Google Map)
. Consider a waiting time tolerance for each trip after which the trip is missed
. Count missed trips
. Calculate charging cost and revenue 
. We can consider different size of vehicles
. We can consider different trips (pooling, multi-destination)
. V2G connection 
. We should measure waiting time, impact on the grid and REG utilization (First, we need to add REG to the model)
. In this scenario we just assign idle vehicles to trips. In further, we could consider active vehicles too, because 
    maybe one of these active vehicles would be the best choice.
. It is better to have 2 70% vehicles rather than a fully charged and a low charge vehicle
. Problem: If more than charging event are being processed, when one stops charging others stop it too.
"""
