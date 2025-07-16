from basis.metaheuristik import Metaheuristik
import random
from metaheuristiken.genetic_mh.Route import Route
from metaheuristiken.genetic_mh.Generation import Generation
from metaheuristiken.genetic_mh import GeneticUtils
from metaheuristiken.genetic_mh import RepairUtils
import math
from copy import deepcopy
import time
import os
import numpy as np

class GeneticMetaheuristik(Metaheuristik):
    def __init__(self, instanz_daten, konfiguration, durchlauf_verzeichnis):
        super().__init__(instanz_daten, konfiguration, durchlauf_verzeichnis)

        self.edges_list = None
        self.pr_list = None
        self.ra_list = None
        os.makedirs(durchlauf_verzeichnis, exist_ok=True)

        self.max_street_capacity = None # make public

        # Genetic Algorithm specific properties
        self.generations = []
        self.iteration_counter = 0

        
    def initialisiere(self):
        # read graph data and set some general variable
        self.ra_list = self.eingabe_daten["residential_areas"]
        self.pr_list = self.eingabe_daten["places_of_refuge"]
        self.edges_list = self.eingabe_daten["edges"]

        # Analyze the input data a little bit
        print("-------------------")
        print("Input Data Overview")
        print(f"Number of RAs {len(self.ra_list)}")
        print(f"Number of PRs {len(self.pr_list)}")
        ra_pop_array = [ra["population"] for ra in self.ra_list]
        print(f"City Population: total={sum(ra_pop_array)}, max RA={max(ra_pop_array)}, mean RA={np.mean(ra_pop_array)}, min RA={min(ra_pop_array)}")
        del ra_pop_array
        pr_capacity_array = [pr["capacity"] for pr in self.pr_list]
        print(f"City RAs capacity: total={sum(pr_capacity_array)}, max RA={max(pr_capacity_array)}, mean RA={np.mean(pr_capacity_array)}, min RA={min(pr_capacity_array)}")
        del pr_capacity_array

        print("-------------------")

        city_population = sum([ra["population"] for ra in self.ra_list])
        self.max_street_capacity = math.ceil(self.konfiguration["street_capacity"] * city_population)

        # check if the problem is solvable with the given amount of clusters
        assert city_population / self.konfiguration["num_clusters"] < self.max_street_capacity, "You need more clusters to stay under the street_overflow bound"

        first_generation = Generation()

        print("Generating Initial Start Population..")
        for i in range(self.konfiguration["population_size"]): #"population_size" as in: population of solutions, not city_population
            possible_solution = GeneticUtils.create_new_possible_solution(self.pr_list, self.ra_list, self.edges_list, self.max_street_capacity, self.konfiguration["num_clusters"], self.konfiguration["route_group_size"])
            print(f"done with init population {i}/{self.konfiguration['population_size']}")
            first_generation.append(possible_solution)

        first_generation.set_losses()

        first_generation.get_best().write_solution_to_file(self.durchlauf_verzeichnis, 1)

        self.generations.append(first_generation)
        self.iteration_counter = 1


    def iteriere(self):
        """
        In the iteration we create a new generation of possible solutions
        """
        latest_generation = self.generations[-1]
        new_generation = Generation()
        
        # TODO maybe put the percentages also in the conf
        num_childs = self.konfiguration["population_size"]
        num_crossovers =  math.floor(num_childs * 0.2)
        num_explorative_mutants = math.floor(num_childs * 0.5)
        #num_new_random_solutions = math.floor(num_childs * 0)
        num_elits = math.floor(num_childs * 0.1)
        num_repairs= math.floor(num_childs * 0.2)

        # ----
        # CROSSOVERS
        print("- Generating Crossovers")
        for i in range(num_crossovers):
            parent1, parent2 = GeneticUtils.select_two_by_roulette(latest_generation)
            child = GeneticUtils.mutation_crossover(parent1, parent2, self.pr_list)
            new_generation.append(child)

        # ----
        # EXPLORATIVE MUTANTS
        print("- Explorative Mutants")
        for i in range(num_explorative_mutants):
            parent1, _ = GeneticUtils.select_two_by_roulette(latest_generation)
            child = GeneticUtils.apply_mutation(parent1, self.pr_list)
            new_generation.append(child)

        # Removed this one due to performance and not really bringing benefits
        # ----
        # RANDOM NEW SOLUTIONS
        #for i in range(num_new_random_solutions):
        #    child = GeneticUtils.create_new_possible_solution(self.pr_list, self.ra_list, self.edges_list, self.max_street_capacity, self.konfiguration["num_clusters"])
        #    new_generation.append(child)

        # ----
        # ELITS
        print("- Getting Elits")
        elits = sorted(latest_generation, key=lambda p: p.loss)[:num_elits]
        for elit in elits:
            elit.birth_type = "elit"
        new_generation += elits

        # ----
        # REPAIRS -> get the best solutions and repair them (no PR overflows ) # TODO also fix Street capacity here
        print("- Generating Repairs")
        repair_candidates = sorted(latest_generation, key=lambda p: p.loss)[:num_repairs]
        for repair_candidate in repair_candidates:
            repaired = RepairUtils.repair_possible_solution(deepcopy(repair_candidate))
            repaired.birth_type = "repaired"
            new_generation.append(repaired)

        # Set losses
        print("Calculating Losses")
        new_generation.set_losses()

        self.generations.append(new_generation)
        self.iteration_counter += 1

        # clean old generations to save storage
        if len(self.generations) > 3:
            self.generations.pop(0)


    def bewerte_loesung(self):
        return self.generations[-1].get_best().loss


    def speichere_zwischenergebnis(self):
        """
        Print/save and analyse the current generation
        """
        avg_loss = self.generations[-1].average_loss()
        best_solution = self.generations[-1].get_best()

        avg_path = os.path.join(self.durchlauf_verzeichnis, "average_losses.csv")
        best_path = os.path.join(self.durchlauf_verzeichnis, "best_losses.csv")
        best_solution_path = os.path.join(self.durchlauf_verzeichnis, "best_solution_loss_dict.csv")
        detailed_generation_loss_path = os.path.join(self.durchlauf_verzeichnis, f"detailed_generation_loss.csv")

        with open(avg_path, 'a') as f_avg:
            f_avg.write(f"{avg_loss}\n")

        with open(best_path, 'a') as f_best:
            f_best.write(f"{best_solution.loss}\n")

        with open(best_solution_path, 'a') as f_best:
            f_best.write(f"{best_solution.get_loss_dict()}\n")

        with open(detailed_generation_loss_path, 'a') as f_best:
            f_best.write(f"{self.generations[-1].dict_all_inds_loss()}\n")

        print(f"Logged average: {avg_loss}, best: {best_solution.loss}")

        # save in ouput directory
        best_solution.write_solution_to_file(self.durchlauf_verzeichnis, self.iteration_counter)

    def gebe_endloesung_aus(self):
        best_solution = self.generations[-1].get_best()

        return best_solution.convert_to_desired_format(number_of_iterations=len(self.generations)) , self.bewerte_loesung()

