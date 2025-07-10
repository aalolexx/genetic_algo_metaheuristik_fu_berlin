from basis.metaheuristik import Metaheuristik
import random
from metaheuristiken.genetic_mh.Cluster import Cluster
from metaheuristiken.genetic_mh.Route import Route
from metaheuristiken.genetic_mh.PossibleSolution import PossibleSolution
from metaheuristiken.genetic_mh.Generation import Generation
from metaheuristiken.genetic_mh import GeneticUtils
from copy import deepcopy
import math
import time
import os

class GeneticMetaheuristik(Metaheuristik):
    def __init__(self, instanz_daten, konfiguration, durchlauf_verzeichnis):
        super().__init__(instanz_daten, konfiguration, durchlauf_verzeichnis)

        self.ra_list = None
        self.pr_list = None
        self.edges_list = None

        os.makedirs(durchlauf_verzeichnis, exist_ok=True)

        self.max_street_capacity = None # make public

        # Genetic Algorithm specific properties
        self.generations = []

        
    def initialisiere(self):
        # read graph data and set some general variable

        self.ra_list = self.eingabe_daten["residential_areas"]
        self.pr_list = self.eingabe_daten["places_of_refuge"]
        self.edges_list = self.eingabe_daten["edges"]

        pr_ids = [por["id"] for por in self.pr_list]

        city_population = sum([ra["population"] for ra in self.ra_list])
        # set upper boarder for start time by (population (city population size * longest edge)
        #todo: think about how to set this. Too high: probably increases computation time. Too low: street_capacity is exceeded too often -> low fittness
        upper_start_time_border = max([int(e["distance_km"]) for e in self.edges_list])* 1000 * (city_population - 1) * self.konfiguration["street_capacity"] # " - 1" because only the start time is relevant here
        self.max_street_capacity = math.ceil(self.konfiguration["street_capacity"] * city_population)

        step = 10 #the data is accurate to 10 meters, so we are iterating over looks with step = 10

        first_generation = Generation()
        for i in range(self.konfiguration["population_size"]): #"population_size" as in: population of solutions, not city_population
            #create a random initial solution
            start = time.time()
            rescue_routes = []

            number_of_clusters = 2#()# self.konfiguration["cluster_number"]
            cluster_size = math.floor(len(self.ra_list) / number_of_clusters)
            clusters = []

            areas_to_evacuate = deepcopy(self.ra_list)
            for _ in range(number_of_clusters):

                selected = random.sample(areas_to_evacuate, cluster_size if len(areas_to_evacuate) >= cluster_size else len(areas_to_evacuate))
                areas_to_evacuate = [o for o in areas_to_evacuate if o not in selected]

                routes = []

                for ra in selected:
                    dest = random.choice(self.pr_list)
                    e = next((edge for edge in self.edges_list if edge["from"]==ra["id"] and edge["to"]==dest["id"]), None)

                    distance, group_size = int(e["distance_km"]), next((o["population"] for o in self.ra_list if o["id"] == ra["id"]), None)


                    r = Route(ra["id"], dest["id"], 0, distance, group_size)
                    routes.append(r)

                clusters.append(Cluster(routes))

            end = time.time()
            print(f"time to generate random solution {i + 1}/{self.konfiguration['population_size']}:", end - start)

            ### close gaps where noone is moving
            if False: # it almost takes forever
                # track time for closing gaps...if it takes too long then we need to think about this again
                start = time.time()

                max_t = max([(r.start_time + r.distance) for r in rescue_routes])

                noone_is_on_street_counter = 0
                adjustment_for_shifting = 0

                # iterate through whole timeframe to find gaps
                for t in range(0, max_t, step):
                    t = t - adjustment_for_shifting
                    print("t: ", t, "/", max_t)

                    people_on_street = len([r for r in rescue_routes if r.start_time <= t < (r.start_time + r.distance)])
                    if people_on_street==0:
                        noone_is_on_street_counter += step

                    # if gap end found
                    if people_on_street > 0 and noone_is_on_street_counter!=0:
                        #shift all routes forward that are not in the past
                        move_forward = [r for r in rescue_routes if r.start_time >= t]
                        for m in move_forward:
                            m.set_start_time(m.start_time - noone_is_on_street_counter)

                        adjustment_for_shifting += noone_is_on_street_counter
                        max_t -= noone_is_on_street_counter
                        noone_is_on_street_counter = 0

                end = time.time()
                print(f"time to close gaps for random solution {i + 1}/{self.konfiguration['population_size']}:", end - start)

            first_generation.append(
                PossibleSolution(
                    clusters = clusters,
                    max_street_capacity = self.max_street_capacity,
                    all_prs = self.pr_list
                )
            )
            
        first_generation.set_losses()
        self.generations.append(first_generation)


    def iteriere(self):
        """
        In the iteration we create a new generation of possible solutions
        """
        latest_generation = self.generations[-1]
        new_generation = Generation()

        num_elits = 10
        num_explorative_mutants = 10 # Idea: Use this for explortation
        num_crossovers = len(latest_generation) - (num_elits + num_explorative_mutants)
        
        for i in range(num_crossovers):
            parent1, parent2 = GeneticUtils.select_two_by_roulette(latest_generation)
            child = GeneticUtils.mutation_crossover(parent1, parent2, self.pr_list)
            new_generation.append(child)

        # get and add the single best solution --> elitismus
        elits = sorted(latest_generation, key=lambda p: p.loss)[:10]
        new_generation += elits

        # Add strong random mutations for exploration
        for i in range(num_explorative_mutants):
            random_ind = random.choice(latest_generation)
            new_ind = GeneticUtils.apply_explorative_mutation(random_ind, self.pr_list)
            new_generation.append(new_ind)
        
        new_generation.set_losses()
        self.generations.append(new_generation)

        # clean old generations to save storage
        if len(self.generations) > 3:
            self.generations.pop(0)


    def bewerte_loesung(self):
        best_solution = self.generations[-1].get_best()
        # TODO format the best solution into the given "flows" format
        return best_solution


    def speichere_zwischenergebnis(self):
        """
        Print/save and analyse the current generation
        """
        avg_loss = self.generations[-1].average_loss()
        best_solution = self.generations[-1].get_best()

        # add the losses to our logfiles
        avg_path = os.path.join(self.durchlauf_verzeichnis, "average_losses.csv")
        best_path = os.path.join(self.durchlauf_verzeichnis, "best_losses.csv")
        best_solution_path = os.path.join(self.durchlauf_verzeichnis, "best_solution_loss_dict.csv")

        with open(avg_path, 'a') as f_avg:
            f_avg.write(f"{avg_loss}\n")

        with open(best_path, 'a') as f_best:
            f_best.write(f"{best_solution.loss}\n")

        with open(best_solution_path, 'a') as f_best:
            f_best.write(f"{best_solution.get_loss_dict()}\n")

        print(f"Logged average: {avg_loss}, best: {best_solution.loss}")