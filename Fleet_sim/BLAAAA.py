from Fleet_sim.Zone import Zone
from Fleet_sim.trip import Trip


def new_trip(zone: Zone):
    return Trip()

class TripQueue:

    def __init__(self, env):
        self.env = env
        self.trips = []

    def addTrip(self, trip: Trip):
        self.trips.append(trip)
        env.event()
