class Model:

    def __init__(self, env):
        self.env = env

    def run(self, vehicles, trip):
        while True:
            distances = list()
            for vehicle in vehicles:
                if vehicle.charge_state <= 70:
                    yield self.env.process(vehicle.charge())

                distance = vehicle.location.distance(trip.origin)
                distances.append(distance)
                distance_to_pickup = vehicle.location.distance(trip.origin)
                if distance_to_pickup == min(distances):

                    distance_to_pickup = vehicle.location.distance(trip.origin)
                    distance_to_dropoff = vehicle.location.distance(trip.destination)
                    charge_consumption = (distance_to_pickup + distance_to_dropoff) \
                                         * vehicle.fuel_consumption * 100.0 / vehicle.battery_capacity

                    if charge_consumption + 20 <= vehicle.charge_state:
                        yield self.env.process(vehicle.take_trip(trip))
                    else:
                        print('Request is rejected')
                        self.env.process(vehicle.charge())




