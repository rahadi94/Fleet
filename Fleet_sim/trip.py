import random
from Fleet_sim.location import Location
import numpy as np
from Fleet_sim.vehicle import Vehicle


def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))


class Trip:

    def __init__(self, env, id, zone):
        self.env = env
        self.id = id
        self.zone = zone
        np.random.seed(0)

        # We generate origin and destination of trips randomly
        self.origin = Location(random.uniform(zone.centre.lat - 0.05, zone.centre.lat + 0.05),
                               random.uniform(zone.centre.long - 0.05, zone.centre.long + 0.05))
        self.destination = Location(random.uniform(6.70, 7.20), random.uniform(50.80, 51.10))
        # time = self.env.now

        # We generate time-varying trips (i.e. trips are being generated exponentially, in which
        # arrival-rate is a gaussian function of time during the day)
        # arrival_rate = gaussian(time, 100, 50)

        self.start_time = random.expovariate(zone.demand)

        distance = self.origin.distance(self.destination)
        self.duration = distance / Vehicle.speed
        self.end_time = self.start_time + self.duration

        self.mode = 'unassigned'
        self.pickup_time = None
        self.waiting_time = None
        self.info = dict()
        self.info['id'] = self.id
        self.info['origin'] = [self.origin.lat, self.origin.long]
        self.info['destination'] = [self.destination.lat, self.destination.long]
        self.info['arrival_time'] = None
        self.info['pickup_time'] = None
        self.info['waiting_time'] = None

    """
    Allowed modes are:
    unassigned - no vehicle is assigned to it
    assigned - a vehicle is assigned and sent
    in vehicle - it is being served
    finished - it is finished   """