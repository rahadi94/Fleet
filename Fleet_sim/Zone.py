import random


class Zone:
    def __init__(self, id, centre):
        self.id = id
        self.centre = centre
        self.list_of_vehicles = []
        self.demand = random.uniform(0.010, 0.015)

    def update(self, vehicles):
        self.list_of_vehicles = [vehicle for vehicle in vehicles
                                 if vehicle.position == self.id and vehicle.mode == 'idle']