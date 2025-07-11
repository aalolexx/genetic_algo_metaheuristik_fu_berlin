from metaheuristiken.genetic_mh.Route import Route
from metaheuristiken.genetic_mh.GlobalTracker import GlobalTracker
from metaheuristiken.genetic_mh.ClusterMapper import ClusterMapper
from copy import deepcopy
import numpy as np

class PossibleSolution:
    def __init__(self, pr_list, ra_list, num_clusters, max_street_capacity, routes=[]):
        self.routes = routes
        self.loss = float("inf") # goal: loss = 0
        self.max_street_capacity = max_street_capacity
        self.pr_list = pr_list
        self.ra_list = ra_list
        self.num_clusters = num_clusters
        self.cluster_mapper = ClusterMapper(self.ra_list, num_clusters)


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

        population_size = len(self.routes)
        normalized_street_overflow = street_overflow_sum / self.max_street_capacity / population_size

        sum_pr_overflows = self.get_sum_pr_overflows()
        normalized_pr_overflow = sum_pr_overflows / population_size

        weighted_time = normalized_time

        # make sure these two are never lower than the time loss since they are a survival must have
        weighted_street_overflow = max((10 * normalized_street_overflow), weighted_time) + 1
        weighted_pr_overflow = max(10 * normalized_pr_overflow, weighted_time) + 1

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

            events.append((enter_time, 1))   # person enters street
            events.append((exit_time, -1))  # person leaves street

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
        normalized_time = last_event_time / longest_distance - 1 # 0 would be the optimal solution (unrealistic to reach due to max street cap)

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
            next(pr for pr in prs_with_usage if pr['id'] == route.PR)['current_usage'] += 1

        for pr in prs_with_usage:
            if pr['current_usage'] > pr['capacity']:
                sum_pr_overflows += pr['current_usage'] - pr['capacity']

        return sum_pr_overflows