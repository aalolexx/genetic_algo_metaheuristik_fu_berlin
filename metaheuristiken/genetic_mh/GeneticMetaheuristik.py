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

class GeneticMetaheuristik(Metaheuristik):
    def __init__(self, instanz_daten, konfiguration, durchlauf_verzeichnis):
        super().__init__(instanz_daten, konfiguration, durchlauf_verzeichnis)

        os.makedirs(durchlauf_verzeichnis, exist_ok=True)

        self.max_street_capacity = None # make public

        # Genetic Algorithm specific properties
        self.generations = []

        
    def initialisiere(self):
        # read graph data and set some general variable

        self.ra_list = self.eingabe_daten["residential_areas"]
        self.pr_list = self.eingabe_daten["places_of_refuge"]
        self.edges_list = self.eingabe_daten["edges"]

        city_population = sum([ra["population"] for ra in self.ra_list])
        self.max_street_capacity = math.ceil(self.konfiguration["street_capacity"] * city_population)

        # check if the problem is solvable with the given amount of clusters
        assert city_population / self.konfiguration["num_clusters"] < self.max_street_capacity, "You need more clusters to stay under the street_overflow bound"

        first_generation = Generation()
        for i in range(self.konfiguration["population_size"]): #"population_size" as in: population of solutions, not city_population
            possible_solution = GeneticUtils.create_new_possible_solution(self.pr_list, self.ra_list, self.edges_list, self.max_street_capacity, self.konfiguration["num_clusters"])
            first_generation.append(possible_solution)
            
        first_generation.set_losses()
        self.generations.append(first_generation)


    def iteriere(self):
        """
        In the iteration we create a new generation of possible solutions
        """
        latest_generation = self.generations[-1]
        new_generation = Generation()
        
        # TODO maybe put the percentages also in the conf
        num_childs = self.konfiguration["population_size"]
        num_crossovers =  math.floor(num_childs * 0.25)
        num_explorative_mutants = math.floor(num_childs * 0.5)
        num_new_random_solutions = math.floor(num_childs * 0.05)
        num_elits = math.floor(num_childs * 0.1)
        num_repairs= math.floor(num_childs * 0.1)

        # CROSSOVERS
        for i in range(num_crossovers):
            parent1, parent2 = GeneticUtils.select_two_by_roulette(latest_generation)
            child = GeneticUtils.mutation_crossover(parent1, parent2, self.pr_list)
            new_generation.append(child)

        # EXPLORATIVE MUTANTS
        for i in range(num_explorative_mutants):
            parent1, _ = GeneticUtils.select_two_by_roulette(latest_generation)
            child = GeneticUtils.apply_mutation(parent1, self.pr_list)
            new_generation.append(child)

        # RANDOM NEW SOLUTIONS
        for i in range(num_new_random_solutions):
            child = GeneticUtils.create_new_possible_solution(self.pr_list, self.ra_list, self.edges_list, self.max_street_capacity, self.konfiguration["num_clusters"])
            new_generation.append(child)

        # ELITS
        elits = sorted(latest_generation, key=lambda p: p.loss)[:num_elits]
        for elit in elits:
            elit.birth_type = "elit"
        new_generation += elits

        # REPAIRS -> get the best solutions and repair them (no PR overflows ) # TODO also fix Street capacity here
        repair_candidates = sorted(latest_generation, key=lambda p: p.loss)[:num_repairs]
        for repair_candidate in repair_candidates:
            repaired = RepairUtils.repair_possible_solution(deepcopy(repair_candidate))
            repaired.birth_type = "repaired"
            new_generation.append(repaired)

        # Set losses
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