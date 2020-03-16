import simpy


class ChargingStation:

    def __init__(self, id, env, location, power):
        self.env = env
        self.plugs = simpy.Resource(self.env, capacity=2)
        self.id = id
        self.location = location
        self.power = power  # kwh/min
