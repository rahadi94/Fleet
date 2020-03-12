from geopy.distance import geodesic


class Location:

    def __init__(self, long, lat):
        self.long = long
        self.lat = lat

    def distance(self, loc):
        origin = [self.long, self.lat]
        destination = [loc.long, loc.lat]
        return geodesic(origin, destination).kilometers
