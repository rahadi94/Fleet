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
        self.waiting_list = []
        self.env = env
        self.trip_end = env.event()
        self.trip_start = env.event()
        self.charging_end = env.event()

    def charge(self, charging_station, vehicle):
        vehicle.send_charge(charging_station)
        yield self.env.timeout(vehicle.time_to_CS)
        vehicle.charging(charging_station)
        yield self.env.timeout(vehicle.charge_duration)
        vehicle.finish_charging(charging_station)
        self.charging_end.succeed()
        self.charging_end = self.env.event()

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

        self.trip_start.succeed()
        self.trip_start = self.env.event()
        vehicle.send(trip)
        trip.mode = 'assigned'
        yield self.env.timeout(vehicle.time_to_pickup)
        vehicle.pick_up(trip)
        trip.mode = 'in vehicle'
        yield self.env.timeout(trip.duration)
        vehicle.drop_off(trip)
        self.trip_end.succeed()
        self.trip_end = self.env.event()
        trip.mode = 'finished'

    def trip_task(self, vehicles, trip):
        available_vehicles = available_vehicle(vehicles, trip)
        distances = [vehicle.location.distance(trip.origin) for vehicle in available_vehicles]
        # If there is no available vehicle, add the trip to the waiting list
        if len(available_vehicles) == 0:
            print(f'There is no available vehicle to respond trip {trip.id}')
            trip.mode = 'unassigned'
            #self.waiting_list.append(trip)
        # Assigning the closest available vehicle to the trip
        else:
            print(f'There is/are {len(available_vehicles)} available vehicle(s) for trip {trip.id}')
            for vehicle in available_vehicles:
                if vehicle.location.distance(trip.origin) == min(distances):
                    self.env.process(self.take_trip(trip, vehicle))

    def run_1(self, vehicles, charging_stations):
        j = 0
        # Trips are being generated randomly and cannot be rejected
        while True:
            j += 1
            trip = Trip(j)
            event_1 = self.env.timeout(trip.start_time)
            yield event_1
            self.waiting_list.append(trip)
            self.env.process(self.charge_task(vehicles, charging_stations))
            print(f'Trip {trip.id} is received at {self.env.now}')
            for trip in self.waiting_list:
                if trip.mode == 'unassigned':
                    self.trip_task(vehicles, trip)
                    yield self.env.timeout(0)



    def run_2(self, vehicles, charging_stations):
        while True:
            event_2 = self.trip_end
            event_3 = self.charging_end
            events = yield event_2 | event_3
            if event_2 in events:
                print(f'A vehicle get idle at {self.env.now}')
                self.env.process(self.charge_task(vehicles, charging_stations))
                for trip in self.waiting_list:
                    if trip.mode == 'unassigned':
                        self.trip_task(vehicles, trip)
                        yield self.env.timeout(0)


            if event_3 in events:
                print(f'A vehicle get charged at {self.env.now}')
                for trip in self.waiting_list:
                    if trip.mode == 'unassigned':
                        self.trip_task(vehicles, trip)
                        yield self.env.timeout(0)
