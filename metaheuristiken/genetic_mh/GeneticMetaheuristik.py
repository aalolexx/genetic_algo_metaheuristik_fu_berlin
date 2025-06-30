from basis.metaheuristik import Metaheuristik
import random
from metaheuristiken.genetic_mh.Route import Route
from metaheuristiken.genetic_mh.PossibleSolution import PossibleSolution
import math


class GeneticMetaheuristik(Metaheuristik):
    def initialisiere(self):
        # read graph data and set some general variable

        ra_list = self.eingabe_daten["residential_areas"]
        pr_list = self.eingabe_daten["places_of_refuge"]
        edges_list = self.eingabe_daten["edges"]

        pr_ids = [por["id"] for por in pr_list]

        city_population = sum([ra["population"] for ra in ra_list])
        # set upper boarder for start time by (population (city population size * longest edge)
        upper_start_time_border = max([e["distance_km"] for e in edges_list]) * city_population
        max_street_capacity = math.ceil(self.konfiguration["street_capacity"] * city_population)

        solutions = []
        for _ in range(self.konfiguration["population_size"]): #"population_size" as in: population of solutions, not city_population
            #create a random initial solution
            rescue_routes = []
            for ra in ra_list:
                for human in range(0,ra["population"]):
                    target_rp_id = random.choice(pr_ids)
                    distance = [edge["distance_km"] for edge in edges_list if edge["from"]==ra["id"] and edge["to"]==target_rp_id][0]
                    rescue_routes.append(
                        Route(ra["id"], target_rp_id, random.randrange(upper_start_time_border), distance)
                    )
            #todo: try to close gaps where noone is moving
            solutions.append(
                PossibleSolution(
                    routes = rescue_routes,
                    max_street_capacity = max_street_capacity
                )
            )


    def iteriere(self):
        pass

    def bewerte_loesung(self):
        pass

    def speichere_zwischenergebnis(self):
        pass