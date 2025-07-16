# GeneticMetaheuristik

This repository contains an implementation of a genetic algorithm used in metaheuristics. It is adapted to solve the 
problems of finding a satisfying solution for an evacuation problem taking into account maximum street capacities, 
maximum rescue point capacities and evacuation time.

## Installation

Clone the repository with

```python
git clone https://github.com/aalolexx/genetic_algo_metaheuristik_fu_berlin.git
```

Install python dependencies (preferably in a local environment) with

```
pip install -r requirements.txt
```

## Basic principles

### Genetic Algorithms

Genetic algorithms are optimization methods inspired by natural evolution. They can solve complex problems by 
evolving a population of possible solutions over time to find better ones. A solution's fittness is rated by a loss 
function and during runtime of the algorithm, those loss values will (mostly) continuously be lowered while better 
solutions are approached. At the same time, one of the biggest advantages of genetic algorithms are randomized 
procedures, namely crossover and mutation, to explore a wider range of solutions and to not get stuck in local minima. 

Futher explanation of genetic algorithms can be found in [S. Ólafsson (2006)](https://www.sciencedirect.com/science/article/abs/pii/S0927050706130212?via%3Dihub) 

### Crossover Mechanism

The crossover operation is responsible for combining two parent solutions to generate a new child solution. A random 
crossover point is selected, and the rescue points (RPs) from both parents are combined - the first segment  
coming from parent 1 and the second from parent 2.

Only the RP assignments are mixed; the rest of the route structure remains unchanged. This strategy ensures 
that the 
overall evacuation timing (tied to the clusters) stays valid while exploring new combinations of assignments.

Additionally, there's a chance of applying a mutation to the child after crossover, slightly altering its RP 
assignments to introduce diversity.

### Mutation Mechanism

Mutation introduces diversity into a possible solution by applying small, randomized changes. It creates a mutated 
copy of the input solution to preserve the original.

Three kinds of mutation are applied:

Cluster Reordering:  
With a certain probability, the assignment of RPs to clusters is modified. This is done either by 
redistributing all RPs among existing clusters (reclustering) or by randomly reassigning individual residential areas 
RAs to different clusters, helping to explore new clustering configurations.

Cluster Start Time Adjustment:  
Some clusters have their start time shifted slightly (by up to ±5000 seconds). This helps in fine-tuning the  
evacuation timing to reduce street congestion and overlaps.

Route Reassignment:  
With a certain chance for each route, the target RP is changed. New RPs are selected based on a 
weighted combination of proximity (shorter distance) and available capacity.  This ensures that more suitable RPs 
are chosen without overloading them.

By applying these three types of mutations, the function improves the exploration of the  solution space and helps 
the algorithm escape local optima.

### Repair Mechanism

The repair functionality improves the feasibility of a solution by addressing two main issues: 
overloaded RPs and street capacity overflow.

First, it checks how many people are currently assigned to each RP and compares this with the RP’s capacity. 
If a RP is overloaded, the function tries to reassign some of its routes to nearby underutilized RPs. 
It does this by prioritizing RPs that are closer to the route’s origin (RA) to keep travel distances short.

Second, the function checks for streets that are over their capacity. If such overflows exist, 
it attempts to reduce congestion by slightly delaying the start times of larger clusters. 
This adjustment is repeated for up to five iterations or until the overflows are resolved.


## Classes and modules

This part will briefly summarize the used classes in this project.

### Cluster(object):

The _[Cluster](./metaheuristiken/genetic_mh/Cluster.py)_ class represents a group of people who start evacuation 
from a specific residential area (RA) at the same time and head towards a specific rescue point (RP).

### ClusterMapper(object):

The _[ClusterMapper](./metaheuristiken/genetic_mh/ClusterMapper.py)_ class is responsible for organizing a list of 
RAs into a specified number of clusters.

This module provides essential functionality for managing clusters of RPs. It supports random  
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
_initialisiere()_ enerates an initial population of possible evacuation plans based on input data (RAs, RPs, edges).

Iteration:  
_iteriere()_ creates new generations through crossovers, mutations, elite preservation, and solution repair.

Evaluation:  
_bewerte_loesung()_ returns the loss value for the best solution of that iteration. The loss function in this 
implementation is a combination of weighted street overflow, RP overflow and time of the evacuation.

Final Output:  
_speichere_zwischenergebnis()_ returns the best evolved solution in the required output format given in [.../example_mh_beispiel/evacuation_result.json](./data/output/example_mh_beispiel/evacuation_result.json).


It builds on a base Metaheuristik class and uses utilities for solution creation, mutation, crossover, and repair.


### GeneticUtils

The _[GeneticUtils](./metaheuristiken/genetic_mh/GeneticUtils.py)_ module provides core utility functions for genetic algorithm operations used in 
GeneticMetaheuristik,  including selection, crossover, mutation, and generation of initial solutions.

### PlotUtils.py

The _[PlotUtils](./metaheuristiken/genetic_mh/PlotUtils.py)_ module provides a variety of visualising the progress and final solution of the problem, which can 
be exoirted into the ouput directory.

### PossibleSolution

The _[PossibleSolution](./metaheuristiken/genetic_mh/PossibleSolution.py)_ class models a solution for the 
evacuation problem, assigning rescue routes from RAs to RPs 
while managing clustering, capacity, and timing. It calculates a loss based on street overload, RP overflow, and overall 
duration. The class supports outputting the solution as JSON or in a custom format given in 
[.../example_mh_beispiel/evacuation_result.json](data/output/example_mh_beispiel/evacuation_result.json).

### RepairUtils.py

The _[RepairUtils](./metaheuristiken/genetic_mh/RepairUtils.py)_ module tries to improve/repair solutions by redistributing routes to underutilized RPs with 
available capacity and randomizing starting times to counter overflown street capacities.

### Route

The _[Route](./metaheuristiken/genetic_mh/Route.py)_ class symbolized an edge between RA and RP. It carries 
information about the 
edge's length and to which cluster the route belongs to. The class also provides the funcionality to groupe individual 
people into small groups. This can reduce the computation time significantly but also reduce the result quality if 
chosen poorly, because individuals are more efficiently to manage than groups regarding street capacity and RP 
capacity.
