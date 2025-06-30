from metaheuristiken.genetic_mh.Route import Route
from metaheuristiken.genetic_mh.GlobalTracker import GlobalTracker

class PossibleSolution:
    def __init__(self, max_street_capacity):
        self.routes = []
        self.loss = float.infinity # goal: loss = 0
    def __init__(self, routes, max_street_capacity):
        self.routes = routes
        self.loss = float("inf") # goal: loss = 0
        self.max_street_capacity = max_street_capacity

    def __repr__(self):
        return f"{self.__class__.__name__}(#routes={len(self.routes)}, loss={self.loss}, street_cap={self.max_street_capacity})"


    def get_loss(self):
        # loss = a * street_overflow + b * pr_overflow + steps
        return 0

    #
    # Analysis Functions
    #

    # gets the amount of street overflows
    # -> Should be used to optimize start_time
    def get_street_overflows(self):
        amount_street_overflows = 0
        street_overflow_sum = 0

        current_step = 0
        step_size = 10

        while (True):
            persons_on_street = 0
            persons_in_shelter = 0

            for route in self.routes:
                if route.start_time < current_step < route.start_time + route.distance:
                    persons_on_street += 1

                if route.starte_time + route.distance < current_step:
                    persons_in_shelter += 1

                if persons_on_street > self.max_street_capacity:
                    amount_street_overflows += 1
                    street_overflow_sum += persons_on_street - self.max_street_capacity

            current_step += step_size 

            if persons_in_shelter == len(route):
                break # Everybody is in the shelter
            
        return amount_street_overflows, street_overflow_sum, current_step


    # gets the amount of PR overflows
    # -> Should be used to optimize PR selection
    def get_amount_pr_overflows(self, all_prs):
        sum_pr_overflows = 0

        prs_with_usage = all_prs.copy()
        prs_with_usage['current_usage'] = 0

        for route in self.routes:
            prs_with_usage[route.PR]['current_usage'] += 1

        for pr_id in prs_with_usage:
            if prs_with_usage[pr_id]["current_usage"] > prs_with_usage[pr_id]["capacity"]:
                sum_pr_overflows += prs_with_usage[pr_id]["current_usage"] - prs_with_usage[pr_id]["capacity"]