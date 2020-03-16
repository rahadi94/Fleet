import datetime
from Fleet_sim.charging_station import ChargingStation


class Vehicle:

    # remove everything env related and put it into VehicleSimulation
    def __init__(self, id, env, initial_location, capacity, charge_state, mode):
        self.location = initial_location
        self.id = id
        self.env = env
        self.mode = mode
        self.time_to_pickup = datetime.timedelta(seconds=0)
        """Allowed modes are:
             active - car is currently driving a passenger from pickup to destination
             locked - car is currently going to pickup location to pick up customer
             idle - car is currently idle and waiting for request
             relocating - car is moving to a different comb
             charging - car is currently charging
             en_route_to_charge - car is on its way to a charging station"""
        self.battery_capacity = capacity
        self.charge_state = charge_state
        self.count_request_accepted = 0
        self.rental_time = 0.0
        self.fuel_consumption = 0.15  # in kWh/km
        self.speed = 5  # km/min
        self.count_times = dict()
        self.count_times['active'] = 0
        self.count_times['locked'] = 0
        self.count_times['idle'] = 1
        self.count_times['relocating'] = 0
        self.count_times['charging'] = 0
        self.count_times['ertc'] = 0
        self.count_seconds = dict()
        self.count_seconds['active'] = 0.0
        self.count_seconds['locked'] = 0.0
        self.count_seconds['idle'] = 0.0
        self.count_seconds['relocating'] = 0.0
        self.count_seconds['charging'] = 0.0
        self.count_seconds['ertc'] = 0.0
        self.last_count_seconds_idle = 0.0
        self.last_count_seconds_relocating = 0.0
        self.count_km = dict()
        self.count_km['active'] = 0.0
        self.count_km['locked'] = 0.0
        self.count_km['relocating'] = 0.0
        self.count_km['ertc'] = 0.0
        self.task_list = list()

    def take_trip(self, trip):
        yield self.env.timeout(trip.start_time)
        print('A request is received at %d' % self.env.now)
        distance_to_pickup = self.location.distance(trip.origin)
        distance_to_dropoff = self.location.distance(trip.destination)
        # distance divided by speed to calculate pick up time
        self.time_to_pickup = round(distance_to_pickup / self.speed)
        charge_consumption = (distance_to_pickup + distance_to_dropoff) \
                             * self.fuel_consumption * 100.0 / self.battery_capacity
        self.rental_time = trip.duration

        print(f'Vehicle {self.id} is sent to the request {self.env.now}')
        self.count_request_accepted += 1
        self.mode = 'locked'

        self.task_list.append({'mode': 'locked',
                               'duration': self.time_to_pickup,
                               'start time': trip.start_time,
                               'end time': self.env.now + self.time_to_pickup})
        self.task_list.append({'mode': 'active',
                               'duration': self.rental_time,
                               'start time': self.time_to_pickup,
                               'end time': trip.start_time + self.time_to_pickup + self.rental_time})

        self.count_seconds['idle'] += trip.start_time
        self.count_seconds['locked'] += self.task_list[-2]['duration']
        self.count_seconds['active'] += self.task_list[-1]['duration']
        self.count_times['locked'] += 1
        self.count_times['active'] += 1
        self.count_km['locked'] += distance_to_pickup
        self.count_km['active'] += distance_to_dropoff
        yield self.env.timeout(self.time_to_pickup)
        print(f'Vehicle {self.id} pick up the user at {self.env.now}')
        self.location = trip.origin
        self.mode = 'active'

        yield self.env.timeout(trip.duration)
        self.charge_state -= charge_consumption
        self.location = trip.destination

        # I am not sure about it
        self.mode = 'idle'
        self.count_times['idle'] += 1
        print(f'Vehicle {self.id} drop off the user at {self.env.now}')

    def charge(self, charging_station):
        print(f'Charging state of vehicle {self.id} is {self.charge_state}')
        print(f'Vehicle {self.id} is going to be charged at {self.env.now}')
        distance_to_CS = self.location.distance(charging_station.location)
        time_to_CS = round(distance_to_CS / self.speed)
        self.mode = 'ertc'
        charge_consumption_to_charging = distance_to_CS \
                                         * self.fuel_consumption * 100.0 / self.battery_capacity
        self.charge_state -= charge_consumption_to_charging
        self.count_times['ertc'] += 1
        self.task_list.append({'mode': 'ertc',
                               'duration': time_to_CS,
                               'start time': self.env.now,
                               'end time': self.env.now + time_to_CS})
        yield self.env.timeout(time_to_CS)
        charge_duration = round(
            ((100 - self.charge_state) * self.battery_capacity) / (100.0 * charging_station.power))
        self.count_times['charging'] += 1
        self.task_list.append({'mode': 'charging',
                               'duration': charge_duration,
                               'start time': self.env.now,
                               'end time': self.env.now + charge_duration})
        self.location = charging_station.location
        print(f'Vehicle {self.id} start charging at {self.env.now}')
        self.mode = 'charging'
        yield self.env.timeout(charge_duration)
        print(f'Vehicle {self.id} is fully charged at {self.env.now} ')
        self.charge_state += charging_station.power * charge_duration
        self.count_seconds['ertc'] += self.task_list[-2]['duration']
        self.count_seconds['charging'] += self.task_list[-1]['duration']
        self.count_km['ertc'] += distance_to_CS
        self.mode = 'idle'


