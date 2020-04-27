import random
import pandas as pd
import simpy
from Fleet_sim.trip import Trip


# This function give us the available vehicles for a trip
def available_vehicle(vehicles, trip):
    available_vehicles = list()
    for vehicle in vehicles:
        distance_to_pickup = vehicle.location.distance(trip.origin)
        distance_to_dropoff = vehicle.location.distance(trip.destination)
        charge_consumption = (distance_to_pickup + distance_to_dropoff) * \
                             vehicle.fuel_consumption * 100.0 / vehicle.battery_capacity
        # Add idle vehicles that have enough energy to respond the trip into available vehicles
        if charge_consumption + 20 <= vehicle.charge_state and vehicle.mode == 'idle':
            available_vehicles.append(vehicle)
    return available_vehicles


class Model:

    def __init__(self, env):
        self.waiting_list = []
        self.simulation_time = 300
        self.env = env
        self.trip_end = env.event()
        self.trip_start = env.event()
        self.charge_start = env.event()
        self.charging_end = env.event()
        self.charging_interrupt = env.event()
        self.relocation_start = env.event()
        self.relocation_end = env.event()

    def relocate(self, vehicle, target_zone):
        vehicle.relocate(target_zone)
        yield self.env.timeout(vehicle.time_to_relocate)
        vehicle.finsih_relocating(target_zone)

    def relocate_task(self, zones, vehicles):
        for zone in zones:
            zone.update(vehicles)
        origin_zones = [z for z in zones if len(z.list_of_vehicles) > 1]
        target_zones = [z for z in zones if len(z.list_of_vehicles) == 0]
        if len(origin_zones) > 1 and len(target_zones) > 1:
            origin_zone = random.choice(origin_zones)
            vehicle = random.choice(origin_zone.list_of_vehicles)
            target_zone = random.choice(target_zones)
            if vehicle.charge_state >= 60 and vehicle.mode == 'idle':
                self.env.process(self.relocate(vehicle, target_zone))

    def start_charge(self, charging_station, vehicle):
        vehicle.send_charge(charging_station)
        yield self.env.timeout(vehicle.time_to_CS)
        self.t_start_charging = self.env.now
        vehicle.charging(charging_station)
        self.charge_start.succeed()
        self.charge_start = self.env.event()

    def finish_charge(self, charging_station, vehicle):

        try:
            yield self.env.timeout(vehicle.charge_duration)
            vehicle.finish_charging(charging_station)
            self.charging_end.succeed()
            self.charging_end = self.env.event()
        except simpy.Interrupt:
            vehicle.charge_state += (charging_station.power * (
                    self.env.now - self.t_start_charging) * 100) / vehicle.battery_capacity
            vehicle.mode = 'idle'
            self.charging_interrupt.succeed()
            self.charging_interrupt = self.env.event()
            print(f'Warning!!!Charging state of vehicle {vehicle.id} is {vehicle.charge_state} at {self.env.now} ')

    # Checking charge status for vehicles and send them to charge if necessary
    def charge_task(self, vehicle, charging_stations):
        if vehicle.charge_state <= 50 and vehicle.mode == 'idle':
            # Finding the closest charging station
            distances_to_CSs = [vehicle.location.distance(CS.location) for CS in charging_stations]
            charging_station = [x for x in charging_stations
                                if x.location.distance(vehicle.location) == min(distances_to_CSs)][0]
            with charging_station.plugs.request() as req:
                yield req
                yield self.env.process(self.start_charge(charging_station, vehicle))
                charging = self.env.process(self.finish_charge(charging_station, vehicle))
                yield charging | self.env.timeout(10)
                if not charging.triggered:
                    charging.interrupt()
                    print(f'Vehicle {vehicle.id} stop charging at {self.env.now}')

    def take_trip(self, trip, vehicle):
        vehicle.send(trip)
        trip.mode = 'assigned'
        yield self.env.timeout(vehicle.time_to_pickup)
        vehicle.pick_up(trip)
        trip.mode = 'in vehicle'
        yield self.env.timeout(trip.duration)
        vehicle.drop_off(trip)
        self.trip_end.succeed()
        self.trip_end = self.env.event()
        self.vehicle_id = vehicle.id
        trip.mode = 'finished'

    def trip_task(self, vehicles, trip):
        available_vehicles = available_vehicle(vehicles, trip)
        distances = [vehicle.location.distance(trip.origin) for vehicle in available_vehicles]
        # If there is no available vehicle, add the trip to the waiting list
        if len(available_vehicles) == 0:
            trip.mode = 'unassigned'
        # Assigning the closest available vehicle to the trip
        else:
            print(f'There is/are {len(available_vehicles)} available vehicle(s) for trip {trip.id}')
            vehicle = [x for x in available_vehicles
                       if x.location.distance(trip.origin) == min(distances)][0]
            self.env.process(self.take_trip(trip, vehicle))

    def trip_generation(self, zone):
        j = 0
        # Trips are being generated randomly and cannot be rejected
        while True:
            j += 1
            trip = Trip(self.env, [zone.id, j], zone)
            yield self.env.timeout(trip.start_time)
            self.trip_start.succeed()
            self.trip_start = self.env.event()
            trip.info['arrival_time'] = self.env.now
            self.waiting_list.append(trip)
            print(f'Trip {trip.id} is received at {self.env.now}')

    def run(self, vehicles, charging_stations, zones):
        while True:
            event_1 = self.trip_start
            event_2 = self.trip_end
            event_3 = self.charging_end
            event_4 = self.charging_interrupt
            events = yield event_1 | event_2 | event_3 | event_4
            if event_1 in events:
                for trip in self.waiting_list:
                    if trip.mode == 'unassigned':
                        self.trip_task(vehicles, trip)
                        yield self.env.timeout(0)
            if event_2 in events:
                print(f'A vehicle get idle at {self.env.now}')
                vehicle = [v for v in vehicles if v.id == self.vehicle_id][0]
                self.env.process(self.charge_task(vehicle, charging_stations))
                yield self.env.timeout(0.1)
                self.relocate_task(zones, vehicles)
                for trip in self.waiting_list:
                    if trip.mode == 'unassigned':
                        self.trip_task(vehicles, trip)
                        yield self.env.timeout(0)

            if event_3 in events:
                print(f'A vehicle get charged at {self.env.now}')
                self.relocate_task(zones, vehicles)
                for trip in self.waiting_list:
                    if trip.mode == 'unassigned':
                        self.trip_task(vehicles, trip)
                        yield self.env.timeout(0)

            if event_4 in events:
                print(f'Charging get interrupted at {self.env.now}')
                for trip in self.waiting_list:
                    if trip.mode == 'unassigned':
                        self.trip_task(vehicles, trip)
                        yield self.env.timeout(0)

    def obs_Ve(self, vehicle):
        self.t = []
        while True:
            t_now = self.env.now
            self.t.append(t_now)
            vehicle.info['SOC'].append(vehicle.charge_state)
            vehicle.info['location'].append([vehicle.location.lat, vehicle.location.long])
            vehicle.info['position'].append(vehicle.position)
            vehicle.info['mode'].append(vehicle.mode)
            yield self.env.timeout(1)

    def obs_CS(self, charging_station):
        while True:
            charging_station.queue.append(charging_station.plugs.count)
            yield self.env.timeout(1)

    def save_results(self, vehicles, charging_stations):
        trips_info = []
        for i in self.waiting_list:
            trips_info.append(i.info)
        results = pd.DataFrame(trips_info)
        with pd.ExcelWriter("results.xlsx") as writer:
            results.to_excel(writer, sheet_name='Trips')
            for j in vehicles:
                pd.DataFrame([j.info["SOC"], j.info["location"], j.info["position"], j.info["mode"]])\
                    .to_excel(writer, sheet_name='Vehicle_%s' % j.id)

            for c in charging_stations:
                pd.DataFrame([c.queue]).to_excel(writer, sheet_name='CS_%s' % c.id)
