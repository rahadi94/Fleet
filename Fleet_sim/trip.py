import random
from Fleet_sim.location import Location
import numpy as np


class Trip:

    def __init__(self, id):
        self.id = id
        np.random.seed(0)
        self.origin = Location(random.normalvariate(5, 0.5), random.normalvariate(5, 0.5))
        self.destination = Location(random.normalvariate(5, 0.5), random.normalvariate(5, 0.5))
        self.start_time = random.randint(3, 10)
        distance_1 = self.origin.distance(self.destination)
        self.duration = round(distance_1 / 10)
        self.end_time = self.start_time + self.duration
        self.mode = 'unassigned'
        self.waiting_time = None



        """
        Allowed modes are:
        unassigned - no vehicle is assigned to it
        assigned - a vehicle is assigned and sent
        in vehicle - it is being served
        finished - it is finished   """
