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


def mutation_crossover(parent1, parent2, all_prs, mutation_rate=0.1):
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

    # Apply mutation to each route with a small chance
    for route in child_routes:
        if random.random() < mutation_rate:
            # Mutate start_time slightly (±1)
            route.start_time += random.randrange(-100, 100) * 10 # todo set step size variable
            route.start_time = max(0, route.start_time)  # clamp to zero

        if random.random() < mutation_rate and all_prs:
            # Mutate PR assignment randomly from allowed PRs for this RA
                route.pr_id = random.choice(all_prs)

    return PossibleSolution(
         routes=child_routes,
         max_street_capacity=parent1.max_street_capacity,
         all_prs=parent1.all_prs
    ) #todo maybe store the max_street_capacity somewhere else?


def apply_explorative_mutation(possible_solution, all_prs):
    new_possible_solution = deepcopy(possible_solution)
    for route in new_possible_solution.routes:
        # Mutate start_time slightly (±1)
        route.start_time += random.randrange(-100, 100) * 10 # todo set step size variable
        route.start_time = max(0, route.start_time)
        route.pr_id = random.choice(all_prs)
    return new_possible_solution
     