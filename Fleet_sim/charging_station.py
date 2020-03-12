from Fleet_sim.location import Location


class ChargingStation:

    def __init__(self, env):
        self.env = env
        self.location = Location(5.4, 5.0)
        self.power = 0.5  # kwh/min
