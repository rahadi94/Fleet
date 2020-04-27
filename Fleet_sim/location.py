from geopy.distance import geodesic


class Location:

    def __init__(self, lat, long):
        self.long = long
        self.lat = lat

    def distance(self, loc):
        origin = [self.lat, self.long]
        destination = [loc.lat, loc.long]
        return geodesic(origin, destination).kilometers

    def find_zone(self, zones):
        distances_to_centers = [self.distance(zone.centre) for zone in zones]
        position = [x for x in zones
                         if x.centre.distance(self) == min(distances_to_centers)][0].id
        return position

