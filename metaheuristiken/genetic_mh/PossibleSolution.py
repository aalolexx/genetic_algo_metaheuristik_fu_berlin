from metaheuristiken.genetic_mh.Route import Route
from metaheuristiken.genetic_mh.ClusterMapper import ClusterMapper
from copy import deepcopy
import numpy as np
import json
import os

class PossibleSolution:
    def __init__(self, pr_list, ra_list, edges_list, num_clusters, max_street_capacity, routes=[], birth_type=""):
        self.routes = routes
        self.loss = float("inf") # goal: loss = 0
        self.max_street_capacity = max_street_capacity
        self.pr_list = pr_list
        self.ra_list = ra_list
        self.edges_list = edges_list
        self.num_clusters = num_clusters
        
        # initialize cluster
        max_start_time = max([edge["distance_km"] for edge in self.edges_list]) * self.num_clusters # heuristic - TODO can be optimized
        self.cluster_mapper = ClusterMapper(self.ra_list, self.num_clusters, max_start_time)

        # For Analysis / Debugging
        self.birth_type = birth_type


    def __repr__(self):
        return f"{self.__class__.__name__}(#routes={len(self.routes)}, loss={self.loss}, street_cap={self.max_street_capacity})"        
        

    def set_routes(self, routes):
        self.routes = routes


    def set_loss(self):
        street_cap_loss, pr_overflow_loss, time_loss = self.get_loss_dict()
        self.loss = street_cap_loss + pr_overflow_loss + time_loss
        #print(f"LOSS: {street_overflow_sum / self.max_street_capacity}, {sum_pr_overflows}, {normalized_time} ")

    
    def get_loss_dict(self):
        amount_street_overflows, street_overflow_sum, normalized_time, steps_took = self.get_street_overflows()

        population_size = np.sum([r.group_size for r in self.routes])
        normalized_street_overflow = street_overflow_sum / self.max_street_capacity / population_size

        sum_pr_overflows = self.get_sum_pr_overflows()
        normalized_pr_overflow = sum_pr_overflows / population_size

        weighted_time = normalized_time
        # make sure these two are always maximum penalized
        weighted_street_overflow = 0 if normalized_street_overflow == 0 else  normalized_street_overflow * 10 + weighted_time * 2
        weighted_pr_overflow = 0 if normalized_pr_overflow == 0 else normalized_pr_overflow * 5 + weighted_time

        return weighted_street_overflow, weighted_pr_overflow, weighted_time

    #
    # Analysis Functions
    #

    # gets the amount of street overflows
    # -> Should be used to optimize start_time
    def get_street_overflows(self):
        events = []  # (time, delta_people), delta +1 for enter, -1 for exit
        longest_distance = 0

        for route in self.routes:
            enter_time = route.cluster.start_time
            exit_time = route.cluster.start_time + route.distance

            events.append((enter_time, route.group_size))   # person enters street
            events.append((exit_time, -1 * route.group_size))  # person leaves street

            if route.distance > longest_distance:
                longest_distance = route.distance

        # Sort events by time
        events.sort()

        persons_on_street = 0
        amount_street_overflows = 0
        street_overflow_sum = 0
        last_event_time = 0

        for time, delta in events:
            persons_on_street += delta
            if persons_on_street > self.max_street_capacity:
                amount_street_overflows += 1
                street_overflow_sum += persons_on_street - self.max_street_capacity
            last_event_time = time
    
        # Normalize last_event_time
        normalized_time = last_event_time / longest_distance -1 # 0 would be the optimal solution
        #print(f"STREET OVERFLOW: {amount_street_overflows}, {street_overflow_sum}, {normalized_time}, {last_event_time}")
        return amount_street_overflows, street_overflow_sum, normalized_time, last_event_time


    # gets the amount of PR overflows
    # -> Should be used to optimize PR selection
    def get_sum_pr_overflows(self):
        sum_pr_overflows = 0

        prs_with_usage = self.pr_list.copy()
        for pr in prs_with_usage:
            pr['current_usage'] = 0

        for route in self.routes:
            next(pr for pr in prs_with_usage if pr['id'] == route.PR)['current_usage'] += route.group_size

        for pr in prs_with_usage:
            if pr['current_usage'] > pr['capacity']:
                sum_pr_overflows += pr['current_usage'] - pr['capacity']

        return sum_pr_overflows
    

    #
    # Export
    #
    def export_as_json(self, output_folder, filename="best_solution_export.json"):
        """
        Export a PossibleSolution object as a JSON file.
        """
        def route_to_dict(route):
            return {
                "ra_id": route.RA,
                "pr_id": route.PR,
                "distance": route.distance,
                "cluster_start_time": route.cluster.start_time
            }

        def cluster_to_dict(cluster):
            return {
                "start_time": cluster.start_time,
                "ra_ids": cluster.ra_ids,
                "size": cluster.size
            }

        export_data = {
            "loss": self.loss,
            "routes": [route_to_dict(route) for route in self.routes],
            "pr_list": self.pr_list,
            "ra_list": self.ra_list,
            "edges_list": self.edges_list,
            "clusters": [cluster_to_dict(c) for c in self.cluster_mapper.clusters]
        }

        export_path = os.path.join(output_folder, filename)
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        with open(export_path, "w") as f:
            json.dump(export_data, f, indent=2)

        print(f"Possible solution exported to {export_path}")

    def convert_to_desired_format(self, number_of_iterations):

        # get flows
        flows = []

        for ra in self.ra_list:
            for pr in self.pr_list:
                persons = len([r for r in self.routes if r.RA == ra['id'] and r.PR == pr['id']])
                if persons==0:
                    continue

                flows.append({
                    "from": ra['id'],
                    "to": pr['id'],
                    "persons": persons,
                })
        # get clusters
        clusters = []

        i = 0
        for c in self.cluster_mapper.clusters:
            if len(c.ra_ids)==0:
                continue

            clusters.append({
                "id": i,
                "start_sec": self.convert_to_time(c.start_time),
                "RAs": c.ra_ids,
            })
            i+=1

        return {
            "ZFW": self.loss,
            "num_iterations": number_of_iterations,
            "total_runtime": self.convert_to_time(max([(r.cluster.start_time + r.distance) for r in self.routes])),
            "metaheuristik": "GeneticMetaheuristic",
            "flows": flows,
            "clusters": clusters
        }

    def write_solution_to_file(self, directory, iteration):
        export_path = os.path.join(directory, f"evacuation_result_iteration_{iteration}.json")
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        with open(export_path, "w") as f:
            json.dump(self.convert_to_desired_format(iteration), f, indent=2)

    # converto to min (s = 4km/h)
    def convert_to_time(self, value):
        return round((value/1000)/4*60)