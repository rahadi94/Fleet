from Fleet_sim.charging_station import ChargingStation
from Fleet_sim.location import Location
from Fleet_sim.model import Model
import simpy
import random
from Fleet_sim.read import zones
from Fleet_sim.vehicle import Vehicle

env = simpy.Environment()


# Initialize Vehicles

def generate_location():
    return Location(random.uniform(13.00, 13.80), random.uniform(52.00, 53.00))


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
vehicles = vehicles[:200]
# Initializing charging stations

CS_data = [

    dict(id=1, env=env, location=Location(13.85, 52.90), power=5, Number_of_chargers=2),
    dict(id=2, env=env, location=Location(13.10, 52.00), power=5, Number_of_chargers=2),
    dict(id=3, env=env, location=Location(13.20, 52.95), power=5, Number_of_chargers=2),
    dict(id=4, env=env, location=Location(13.95, 52.05), power=5, Number_of_chargers=2),
    dict(id=5, env=env, location=Location(13.05, 52.90), power=5, Number_of_chargers=2),
    dict(id=6, env=env, location=Location(13.40, 52.30), power=5, Number_of_chargers=2),
    dict(id=7, env=env, location=Location(13.10, 52.00), power=5, Number_of_chargers=2),
    dict(id=8, env=env, location=Location(13.35, 52.50), power=5, Number_of_chargers=2),
    dict(id=9, env=env, location=Location(13.95, 52.60), power=5, Number_of_chargers=2),
    dict(id=10, env=env, location=Location(13.55, 52.75), power=5, Number_of_chargers=2),

]

# Initialize Charging Stations
charging_stations = list()

for data in CS_data:
    charging_station = (ChargingStation(
        data['id'],
        data['env'],
        data['location'],
        data['power'],
        data['Number_of_chargers']

    ))
    charging_stations.append(charging_station)
charging_stations = charging_stations[:5]

# Run simulation
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
    print(vehicle.costs)
    print(vehicle.count_times)
    print(vehicle.count_seconds)
sim.save_results(vehicles, charging_stations)
"""
Extension and debugs:
. Should vehicles wait for travelers?
. Use driving distances between two points (i.g. Google Map)
. Consider a waiting time tolerance for each trip after which the trip is missed
. Count missed trips
. Consider public and owned CSs
. Calculate charging cost and revenue 
. We can consider different size of vehicles
. We can consider different trips (pooling, multi-destination)
. V2G connection 
. We should measure waiting time, impact on the grid and REG utilization (First, we need to add REG to the model)
. In this scenario we just assign idle vehicles to trips. In further, we could consider active vehicles too, because 
    maybe one of these active vehicles would be the best choice.
"""
