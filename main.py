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

# FIXME : this is an unnecessary step; just directly create the Vehicle instances ;)
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

# TODO : same as above: just directly create instances
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
model = Model(env, zones, vehicles, charging_stations)
model.init()

for zone in zones:
    env.process(model.trip_generation(zone))

env.process(model.run(vehicles, charging_stations, zones))

for vehicle in vehicles:
    env.process(model.obs_Ve(vehicle))

for charging_station in charging_stations:
    env.process(model.obs_CS(charging_station))

env.run(until=model.simulation_time)

for vehicle in vehicles:
    print(vehicle.charge_state)
    print(vehicle.id)
    print(vehicle.costs)
    print(vehicle.count_times)
    print(vehicle.count_seconds)
model.save_results(vehicles, charging_stations)

