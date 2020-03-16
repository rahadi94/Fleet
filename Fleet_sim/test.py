"""import simpy

env = simpy.Environment


# resource
class SuperComputer:

    def __init__(self, env):
        self.nodes = simpy.Resource(env, capacity=2)


# users of resource
class Job:
    # enter: time the job enters the system
    # timeout is how long the job occupies a resource for
    # resources is how many resources a job needs in order to run
    def __init__(self, env, name, enter, timeout, resources):
        self.env = env
        self.name = name
        self.enter = enter
        self.timeout = timeout
        self.resources = resources


# system
def system(env, job, super_computer):
    with super_computer.nodes.request() as req:
        print('%s arrives at %s' % (job.name, job.enter))
        yield req
        yield env.timeout(job.enter)
        print('%s starts running with %s resources at %s' % (job.name, job.resources, env.now))
        yield env.timeout(job.timeout)
        print('%s completed job at %s' % (job.name, env.now))


env = simpy.Environment()
super_computer = SuperComputer(env)

jobs = [
    Job(env, 'a', 1, 4, 1),
    Job(env, 'b', 1, 4, 1),
    Job(env, 'c', 1, 4, 1),
    Job(env, 'd', 1, 4, 1),
]

for job in jobs:
    env.process(system(env, job, super_computer))

env.run(50)"""
import multiprocessing as mp
import simpy
import random


NUM_MACHINES = 2  # Number of machines in the carwash
WASHTIME = 5      # Minutes it takes to clean a car
T_INTER = 7       # Create a car every ~7 minutes
SIM_TIME = 20     # Simulation time in minutes


class Carwash(object):
    """A carwash has a limited number of machines (``NUM_MACHINES``) to
    clean cars in parallel.

    Cars have to request one of the machines. When they got one, they
    can start the washing processes and wait for it to finish (which
    takes ``washtime`` minutes).

    """
    def __init__(self, env, num_machines, washtime):
        self.env = env
        self.machine = simpy.Resource(env, num_machines)
        self.washtime = washtime

    def wash(self, car):
        """The washing processes. It takes a ``car`` processes and tries
        to clean it."""
        yield self.env.timeout(WASHTIME)


def car(env, name, cw):
    """The car process (each car has a ``name``) arrives at the carwash
    (``cw``) and requests a cleaning machine.

    It then starts the washing process, waits for it to finish and
    leaves to never come back ...

    """
    with cw.machine.request() as request:
        yield request
        yield env.process(cw.wash(name))


def setup(env, num_machines, washtime, t_inter):
    """Create a carwash, a number of initial cars and keep creating cars
    approx. every ``t_inter`` minutes."""
    # Create the carwash
    carwash = Carwash(env, num_machines, washtime)

    # Create 4 initial cars
    for i in range(4):
        env.process(car(env, 'Car %d' % i, carwash))

    # Create more cars while the simulation is running
    while True:
        yield env.timeout(random.randint(t_inter - 5, t_inter + 5))
        i += 1
        env.i = i
        env.process(car(env, 'Car %d' % i, carwash))


# additional wrapping function to be executed by the pool
def do_simulation_with_seed(rs):

    random.seed(rs)  # This influences only the specific process being run
    env = simpy.Environment()  # THE ENVIRONMENT IS CREATED HERE, IN THE CHILD PROCESS
    env.process(setup(env, NUM_MACHINES, WASHTIME, T_INTER))

    env.run(until=SIM_TIME)

    return env.i


if __name__ == '__main__':
    seeds = range(4)
    carwash_pool = mp.Pool(4)
    ncars_by_seed = carwash_pool.map(do_simulation_with_seed, seeds)
    for s, ncars in zip(seeds, ncars_by_seed):
        print('seed={} --> {} cars washed'.format(s, ncars))
