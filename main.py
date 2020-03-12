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

trip = Trip(env)

sim = Model(env)
# for vehicle in vehicles:
#sim = Model(env, vehicles, trip)
env.process(sim.run(vehicles, trip))
env.run(until=1000)

for vehicle in vehicles:
    print(vehicle.charge_state)
    print(vehicle.location.lat, vehicle.location.long)
    print(vehicle.count_times)
    print(vehicle.count_seconds)
# print(vehicles[1].__dict__)
