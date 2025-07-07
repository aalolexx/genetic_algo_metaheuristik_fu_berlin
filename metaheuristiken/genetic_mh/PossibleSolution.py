from metaheuristiken.genetic_mh.Route import Route
from metaheuristiken.genetic_mh.GlobalTracker import GlobalTracker
from copy import deepcopy
import numpy as np

class PossibleSolution:
    def __init__(self, routes, max_street_capacity, all_prs):
        self.routes = routes
        self.loss = float("inf") # goal: loss = 0
        self.max_street_capacity = max_street_capacity
        self.all_prs = all_prs


    def __repr__(self):
        return f"{self.__class__.__name__}(#routes={len(self.routes)}, loss={self.loss}, street_cap={self.max_street_capacity})"


    def set_loss(self):
        street_cap_loss, pr_overflow_loss, time_loss = self.get_loss_dict()
        self.loss = street_cap_loss + pr_overflow_loss + time_loss
        #print(f"LOSS: {street_overflow_sum / self.max_street_capacity}, {sum_pr_overflows}, {normalized_time} ")

    
    def get_loss_dict(self):
        amount_street_overflows, street_overflow_sum, normalized_time, steps_took = self.get_street_overflows()

        population_size = len(self.routes)
        normalized_street_overflow = street_overflow_sum / self.max_street_capacity / population_size

        sum_pr_overflows = self.get_sum_pr_overflows(self.all_prs)
        normalized_pr_overflow = sum_pr_overflows / population_size

        return 10 * normalized_street_overflow, 10 * normalized_pr_overflow, normalized_time

    #
    # Analysis Functions
    #

    # gets the amount of street overflows
    # -> Should be used to optimize start_time
    def get_street_overflows(self):
        events = []  # (time, delta_people), delta +1 for enter, -1 for exit
        longest_distance = 0

        for route in self.routes:
            enter_time = route.start_time
            exit_time = route.start_time + route.distance

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
    def get_sum_pr_overflows(self, all_prs):
        sum_pr_overflows = 0

        prs_with_usage = all_prs.copy()
        for pr in prs_with_usage:
            pr['current_usage'] = 0

        for route in self.routes:
            next(pr for pr in prs_with_usage if pr['id'] == route.PR)['current_usage'] += 1

        for pr in prs_with_usage:
            if pr['current_usage'] > pr['capacity']:
                sum_pr_overflows += pr['current_usage'] - pr['capacity']

        return sum_pr_overflows