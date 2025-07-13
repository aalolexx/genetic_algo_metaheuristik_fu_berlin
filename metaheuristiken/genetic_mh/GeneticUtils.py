import random
from copy import deepcopy
from metaheuristiken.genetic_mh.PossibleSolution import PossibleSolution
from metaheuristiken.genetic_mh.Route import Route
import numpy as np
import math

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


def apply_mutation(possible_solution, all_prs, route_change_rate=0.5, reclustering_rate=0.5):
    """
    Mutation Method
    Applies slight random Mutation on existing solutions
    """
    new_possible_solution = deepcopy(possible_solution)
    new_possible_solution.birth_type = "mutation"

    # ---------
    # Mutation 1: Reorder the cluster distribution
    if random.random() > reclustering_rate: 
        k = random.random()
        if k < 0.4:
            new_possible_solution.cluster_mapper.recluster_population()
        else:
            for ra in new_possible_solution.ra_list:
                if random.random() < 0.3: # todo maybe configurable but its neglectable
                    new_possible_solution.cluster_mapper.random_switch_ra(ra["id"])

    # ---------
    # Mutation 2: Cluster Start Times
    for cluster in new_possible_solution.cluster_mapper.clusters:
        cluster.start_time += random.randrange(-100, 100) * 10 # todo set step size variable
        cluster.start_time = math.floor(max(0, cluster.start_time)) # floor just to have nice starting times

    # ---------
    # Mutation 3: Route PR Goals

    # precompute selection weights
    ra_edge_selection_weights = {}
    for ra in set(route.RA for route in new_possible_solution.routes):
        available_edges = [edge for edge in new_possible_solution.edges_list if edge["from"] == ra]

        weights_distance = np.array([1 / float(edge["distance_km"]) for edge in available_edges])
        normalized_weights_distance = (weights_distance - np.min(weights_distance)) / (np.max(weights_distance) - np.min(weights_distance))

        weights_capacity = np.array([next(pr for pr in all_prs if pr["id"] == edge["to"])["capacity"] for edge in available_edges])
        normalized_weights_capacity = (weights_capacity - np.min(weights_capacity)) / (np.max(weights_capacity) - np.min(weights_capacity))

        ra_edge_selection_weights[ra] = {
            "edges": available_edges,
            "distance_weights": normalized_weights_distance,
            "capacity_weights": normalized_weights_capacity,
        }
        
    # than update route PR based on weights and mutation rate
    for route in new_possible_solution.routes:
        if random.random() < route_change_rate:
            data = ra_edge_selection_weights[route.RA]
            edges = data["edges"]
            weights = 0.2 * data["distance_weights"] + 4 * data["capacity_weights"]

            # Sample new edge based on combined weights
            route.PR = random.choices(edges, weights=weights, k=1)[0]["to"]

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
        ra_cluster = possible_solution.cluster_mapper.find_RA_cluster(ra["id"])
        for human in range(0, ra["population"]):    
            target_pr_id = random.choice(pr_ids)
            distance = next(float(edge["distance_km"]) for edge in edges_list if edge["from"] == ra["id"] and edge["to"] == target_pr_id) * 1000
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