import random
from copy import deepcopy
from metaheuristiken.genetic_mh.PossibleSolution import PossibleSolution
from metaheuristiken.genetic_mh.Route import Route

def select_two_by_roulette(population):
    """
    Taking the Roulette Function randomly selecting two solutions. Low less functions makes the solution more likeley to get picked
    """
    EPSILON = 1e-8  # To avoid division by zero
    weights = [1 / (ind.loss + EPSILON) for ind in population]
    selected = random.choices(population, weights=weights, k=2)
    return selected[0], selected[1]


def mutation_crossover(parent1, parent2, all_prs, mutation_rate=0.2):
    """
    Mutation Method
    Uses the "crossover" method to combine existing solutions
    the method makes sure that the clustering stays consistent
    """
    
    # Take the first parent as a base --> clusters can't be mixed randomly but have to stay consistend
    child = deepcopy(parent1)
    child.birth_type = "crossover" 

    # Mix the routes goal PRs
    crossover_point = random.randint(1, len(parent1.routes) - 1)
    mixed_routes = (
        deepcopy(parent1.routes[:crossover_point]) +
        deepcopy(parent2.routes[crossover_point:])
    )
    
    for i, route in enumerate(child.routes):
        route.PR = mixed_routes[i].PR

    # Apply mutation randomly depending on mutation rate in crossover
    if random.random() < mutation_rate:
        child = apply_mutation(child, all_prs)
        child.birth_type = "crossover_mutated" 

    return child


def apply_mutation(possible_solution, all_prs, route_change_rate=0.8, reclustering_rate=0.5):
    """
    Mutation Method
    Applies slight random Mutation on existing solutions
    """
    new_possible_solution = deepcopy(possible_solution)
    new_possible_solution.birth_type = "mutation"

    # Mutation 1: Reorer the cluster distribution
    if random.random() > reclustering_rate:
        new_possible_solution.cluster_mapper.recluster_population()
        new_possible_solution.birth_type = "mutation_reclustered" # todo remove

    # Mutation 1: Cluster Start Times
    for cluster in new_possible_solution.cluster_mapper.clusters:
        cluster.start_time += random.randrange(-100, 100) * 10 # todo set step size variable
        cluster.start_time = max(0, cluster.start_time)

    # Mutation 2: Route PR Goals
    for route in new_possible_solution.routes:
        if random.random() < route_change_rate:
            available_edges = [edge for edge in new_possible_solution.edges_list if edge["from"] == route.RA]
            weights = [1 / float(edge["distance_km"]) for edge in available_edges]
            route.PR = random.choices(available_edges, weights=weights, k=1)[0]["to"]

    return new_possible_solution
     

def create_new_possible_solution(pr_list, ra_list, edges_list, max_street_capacity, num_clusters):
    """
    Generates a completley new random solution.
    Can be used at init and for exploration.
    """
    possible_solution = PossibleSolution(
        max_street_capacity = max_street_capacity,
        pr_list = pr_list,
        ra_list =  ra_list,
        edges_list = edges_list,
        num_clusters = num_clusters,
        birth_type="new_random"
    )

    pr_ids = [por["id"] for por in pr_list]
    rescue_routes = []

    for ra in ra_list:
        for human in range(0, ra["population"]):
            ra_cluster = possible_solution.cluster_mapper.find_RA_cluster(ra["id"])
            target_pr_id = random.choice(pr_ids)
            distance = [int(edge["distance_km"]) for edge in edges_list if edge["from"]==ra["id"] and edge["to"]==target_pr_id][0] * 1000
            rescue_routes.append(
                Route(
                    ra_id = ra["id"],
                    pr_id = target_pr_id,
                    distance = distance,
                    cluster = ra_cluster
                )
            )

    possible_solution.routes = rescue_routes
    return possible_solution