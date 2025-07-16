# GeneticMetaheuristik

This repository contains an implementation of a genetic algorithm used in metaheuristics. It is adapted to solve the 
problems of finding a satisfying solution for an evacuation problem taking into account maximum street capacities 
and maximum rescue area capacities.

## Installation

Clone the repository with

```python
git clone https://github.com/aalolexx/genetic_algo_metaheuristik_fu_berlin.git
```

Install python dependencies (preferably in a local environment) with

```
pip install -r requirements.txt
```

## Classes and modules

This part will briefly summarize the used classes in this project.

### Cluster(object):

The _[Cluster](./metaheuristiken/genetic_mh/Cluster.py)_ class represents a group of people who start evacuation from a specific residential area at the same 
time and head towards a specific rescue area.

### ClusterMapper(object):

The _[ClusterMapper](./metaheuristiken/genetic_mh/ClusterMapper.py)_ class is responsible for organizing a list of residential areas into a specified number of clusters.

This module provides essential functionality for managing clusters of rescue areas. It supports random  
initialization, where RAs are distributed across clusters in a balanced way based on their population, promoting  
diversity in the solution space. Individual RAs can be reassigned to different clusters, with a preference for  
smaller clusters to maintain balance. Additionally, the module allows for complete reclustering, redistributing all 
RAs while preserving the original cluster start times.


### Generation(list):

The _[Generation](./metaheuristiken/genetic_mh/Generation.py)_ class represents a population of possible solutions 
for the evacuation problem at a specific 
iteration. It extends a standard list with additional methods to evaluate and analyze the solutions. It can compute 
the loss for each individual, identify the best solution and calculate the 
average loss across the generation. Additionally, _dict_all_inds_loss() provides a summary of 
loss values and additional information for all individuals, which is useful for logging and visualization.


### GeneticMetaheuristik(Metaheuristik)
The _[GeneticMetaheuristik](./metaheuristiken/genetic_mh/GeneticMetaheuristik.py)_ class implements a genetic algorithm to solve evacuation planning problems by evolving 
routing and clustering solutions over multiple generations.

Key features:

Initialization:
_initialisiere(self)_ enerates an initial population of possible evacuation plans based on input data (RAs, PRs, edges).

Iteration (iteriere):
_iteriere(self)_ creates new generations through crossovers, mutations, elite preservation, and solution repair.

Evaluation:
_bewerte_loesung(self)_ returns the loss value for the best solution of that iteration. Todo realize in code

Final Output:
_speichere_zwischenergebnis(self)_ returns the best evolved solution in the required output format given in [.../example_mh_beispiel/evacuation_result.json](./data/output/example_mh_beispiel/evacuation_result.json).
todo: realize in code

It builds on a base Metaheuristik class and uses utilities for solution creation, mutation, crossover, and repair.


### GeneticUtils

The _[GeneticUtils](./metaheuristiken/genetic_mh/GeneticUtils.py)_ module provides core utility functions for genetic algorithm operations used in 
GeneticMetaheuristik,  including selection, crossover, mutation, and generation of initial solutions.

### PlotUtils.py

The _[PlotUtils](./metaheuristiken/genetic_mh/PlotUtils.py)_ module provides a variety of visualising the progress and final solution of the problem, which can 
be exoirted into the ouput directory.

### PossibleSolution

The _[PossibleSolution](./metaheuristiken/genetic_mh/PossibleSolution.py)_ class models a solution for the 
evacuation problem, 
assigning rescue 
routes from RAs to 
PRs 
while managing clustering, capacity, and timing. It calculates a loss based on street overload, PR overflow, and overall 
duration. The class supports outputting the solution as JSON or in a custom format given in 
[.../example_mh_beispiel/evacuation_result.json](data/output/example_mh_beispiel/evacuation_result.json).

### RepairUtils.py

The _[RepairUtils](./metaheuristiken/genetic_mh/RepairUtils.py)_ module tries to improve/repair solutions by redistributing routes to underutilized PRs with 
available capacity and randomizing starting times to counter overflown street capacities.

### Route

The _[Route](./metaheuristiken/genetic_mh/Route.py)_ class symbolized an edge between residential area and rescue area. It carries information about the 
edge's length and to which cluster the route belongs to.
