class Model:

    def __init__(self, env):
        self.env = env

    def charge_task(self, vehicle, charging_stations):
        # Checking state of charge for all vehicles

        # for vehicle in vehicles:
            if vehicle.charge_state <= 70:
                distances_to_CSs = [vehicle.location.distance(CS.location) for CS in charging_stations]
                # Finding the closest charging station
                charging_station = [x for x in charging_stations
                                    if x.location.distance(vehicle.location) == min(distances_to_CSs)][0]
                print(f'Vehicle {vehicle.id} is sent to the charging station {charging_station.id}')
                with charging_station.plugs.request() as req:
                    yield req
                yield self.env.process(vehicle.charge(charging_station))

    def available_vehicles(self, vehicles, trip):
        available_vehicles = list()
        for vehicle in vehicles:
            distance_to_pickup = vehicle.location.distance(trip.origin)
            distance_to_dropoff = vehicle.location.distance(trip.destination)
            charge_consumption = (distance_to_pickup + distance_to_dropoff) \
                                 * vehicle.fuel_consumption * 100.0 / vehicle.battery_capacity
            if charge_consumption + 20 <= vehicle.charge_state and vehicle.mode == 'idle':
                available_vehicles.append(vehicle)
        return available_vehicles

    def trip_task(self, vehicles, trip):
        distances = [vehicle.location.distance(trip.origin) for vehicle in vehicles]
        available_vehicles = self.available_vehicles(vehicles, trip)
        # If there is no available vehicle, reject the trip
        if len(available_vehicles) == 0:
            print('There is no available vehicle to respond the trip')
        # Assigning the closest available vehicle to the trip
        for vehicle in available_vehicles:
            if vehicle.location.distance(trip.origin) == min(distances):
                yield self.env.process(vehicle.take_trip(trip))

    def run(self, vehicles, charging_stations, trips):
        while True:
            for vehicle in vehicles:
                yield self.env.process(self.charge_task(vehicle, charging_stations))
            for trip in trips:
                yield self.env.process(self.trip_task(vehicles, trip))
