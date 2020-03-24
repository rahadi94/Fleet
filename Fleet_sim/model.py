from Fleet_sim.trip import Trip


# This function give us the available vehicles for a specific trip

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
        self.env = env

    def charge(self, charging_station, vehicle):
        vehicle.send_charge(charging_station)
        yield self.env.timeout(vehicle.time_to_CS)
        vehicle.charging(charging_station)
        yield self.env.timeout(vehicle.charge_duration)
        vehicle.finish_charging(charging_station)

    # Checking charge status for vehicles and send them to charge if necessary

    def charge_task(self, vehicles, charging_stations):
        for vehicle in vehicles:
            if vehicle.charge_state <= 50 and vehicle.mode == 'idle':
                # Finding the closest charging station
                distances_to_CSs = [vehicle.location.distance(CS.location) for CS in charging_stations]
                charging_station = [x for x in charging_stations
                                    if x.location.distance(vehicle.location) == min(distances_to_CSs)][0]
                with charging_station.plugs.request() as req:
                    yield req
                    self.env.process(self.charge(charging_station, vehicle))

    def take_trip(self, trip, vehicle):
        vehicle.send(trip)
        trip.mode = 'assigned'
        yield self.env.timeout(vehicle.time_to_pickup)
        vehicle.pick_up(trip)
        trip.mode = 'in vehicle'
        yield self.env.timeout(trip.duration)
        vehicle.drop_off(trip)
        trip.mode = 'finished'

    def trip_task(self, vehicles, trip):
        distances = [vehicle.location.distance(trip.origin) for vehicle in vehicles]
        available_vehicles = available_vehicle(vehicles, trip)
        # If there is no available vehicle, add the trip to the waiting list
        if len(available_vehicles) == 0:
            print('There is no available vehicle to respond the trip')
            trip.mode = 'unassigned'
        # Assigning the closest available vehicle to the trip
        else:
            for vehicle in available_vehicles:
                if vehicle.location.distance(trip.origin) == min(distances):
                    with vehicle.source.request() as req:
                        yield req
                        self.env.process(self.take_trip(trip, vehicle))

    def run(self, vehicles, charging_stations):
        j = 0
        trips = []
        # Trips are being generated randomly and cannot be rejected
        while True:
            j += 1
            trip = Trip(j)
            yield self.env.timeout(trip.start_time)
            trips.append(trip)
            for trip in trips:
                if trip.mode == 'unassigned':
                    self.env.process(self.trip_task(vehicles, trip))

            self.env.process(self.charge_task(vehicles, charging_stations))

