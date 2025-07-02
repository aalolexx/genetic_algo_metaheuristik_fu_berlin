import random
from copy import deepcopy
from metaheuristiken.genetic_mh.PossibleSolution import PossibleSolution

def select_two_by_roulette(population):
    """
    Taking the Roulette Function randomly selecting two solutions. Low less functions makes the solution more likeley to get picked
    """
    EPSILON = 1e-8  # To avoid division by zero
    weights = [1 / (ind.loss + EPSILON) for ind in population]
    selected = random.choices(population, weights=weights, k=2)
    return selected[0], selected[1]


def mutation_crossover(parent1, parent2):
    """
    Mutation Method
    Uses the "crossover" method (randomly cutting and switching) to create a new solution out of two parents
    """
    # Ensure both parents have the same route count
    assert len(parent1.routes) == len(parent2.routes), "Route lists must be same length"

    crossover_point = random.randint(1, len(parent1.routes) - 1)
    child_routes = (
        deepcopy(parent1.routes[:crossover_point]) +
        deepcopy(parent2.routes[crossover_point:])
    )
    return PossibleSolution(routes=child_routes, max_street_capacity=parent1.max_street_capacity) #todo maybe store the max_street_capacity somewhere else?