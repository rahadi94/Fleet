import random
from Fleet_sim.location import Location
import simpy
#event = simpy.Environment.event()

class Trip:

    def __init__(self, env):
        self.env = env
        self.origin = Location(random.normalvariate(5, 0.5), random.normalvariate(5, 0.5))
        self.destination = Location(random.normalvariate(5, 0.5), random.normalvariate(5, 0.5))
        self.start_time = random.randint(3, 10)
        distance_1 = self.origin.distance(self.destination)
        self.duration = round(distance_1 / 10)
        self.end_time = self.start_time + self.duration
