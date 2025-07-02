from metaheuristiken.genetic_mh.Route import Route
from metaheuristiken.genetic_mh.GlobalTracker import GlobalTracker
from copy import deepcopy

class PossibleSolution:
    def __init__(self, routes, max_street_capacity):
        self.routes = routes
        self.loss = float("inf") # goal: loss = 0
        self.max_street_capacity = max_street_capacity

    def __repr__(self):
        return f"{self.__class__.__name__}(#routes={len(self.routes)}, loss={self.loss}, street_cap={self.max_street_capacity})"


    def set_loss(self, all_prs):
        # loss = a * street_overflow + b * pr_overflow + steps
        # todo better balanced loss function (this is just for a first debugging)
        amount_street_overflows, street_overflow_sum, current_step = self.get_street_overflows()
        self.loss = amount_street_overflows + self.get_amount_pr_overflows(all_prs) + current_step

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

        routes_to_scan = deepcopy(self.routes) # create a copy and delete its routes when person reached PR to optimize performance

        persons_on_street = 0
        persons_in_shelter = 0

        while (True):
            # take a step on each route
            for route in routes_to_scan:
                # if the route has started and is not done, indicate that a person is on the street
                if route.start_time < current_step < route.start_time + route.distance:
                    persons_on_street += 1

                # A person has reached its shelter
                if route.start_time + route.distance < current_step:
                    persons_in_shelter += 1
                    routes_to_scan.remove(route)

                if persons_on_street > self.max_street_capacity:
                    amount_street_overflows += 1
                    street_overflow_sum += persons_on_street - self.max_street_capacity

            current_step += step_size

            #print(f"step: {current_step}, in_s: {persons_in_shelter}, rts left: {len(routes_to_scan)}")

            if persons_in_shelter >= len(self.routes):
                break # Everybody is in the shelter
            
        return amount_street_overflows, street_overflow_sum, current_step


    # gets the amount of PR overflows
    # -> Should be used to optimize PR selection
    def get_amount_pr_overflows(self, all_prs):
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