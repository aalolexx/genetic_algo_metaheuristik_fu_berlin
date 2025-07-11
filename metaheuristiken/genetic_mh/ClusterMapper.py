import math
from copy import deepcopy
import random
from metaheuristiken.genetic_mh.Cluster import Cluster
import numpy as np

class ClusterMapper():
    """
    ClusterMapper maps RAs into Clusters and manages their starting times etc
    """
    def __init__(self, ra_list, num_clusters, max_start_time):
        self.ra_list = ra_list
        self.num_clusters = num_clusters
        self.clusters = self.get_random_cluster_distribution(max_start_time)

    
    def get_random_cluster_distribution(self, max_start_time):
        """
        Randomly distribute all RAs into the given amount of clusters
        """
        cluster_size = math.ceil(len(self.ra_list) / self.num_clusters)
        clusters = []
        areas_to_evacuate = deepcopy(self.ra_list)

        for _ in range(self.num_clusters):
            selected = random.sample(areas_to_evacuate, cluster_size if len(areas_to_evacuate) >= cluster_size else len(areas_to_evacuate))
            new_cluster = Cluster(
                start_time = max_start_time, 
                cluster_mapper = self,
                ra_ids = [ra["id"] for ra in selected],
                size = np.sum([ra["population"] for ra in selected])
            )
            clusters.append(new_cluster)
            areas_to_evacuate = [o for o in areas_to_evacuate if o not in selected]

        return clusters
    

    def recluster_population(self):
        """
        Keeps the cluster start_times but reorders the RAs in it
        """
        # TODO this method can be somhow combined with the get_random_cluster_distribution function (duplicated code fragments)
        cluster_size = math.floor(len(self.ra_list) / self.num_clusters)
        areas_to_evacuate = deepcopy(self.ra_list)

        for cluster in self.clusters:
            selected = random.sample(areas_to_evacuate, cluster_size if len(areas_to_evacuate) >= cluster_size else len(areas_to_evacuate))
            cluster.ra_ids = [ra["id"] for ra in selected]
            areas_to_evacuate = [o for o in areas_to_evacuate if o not in selected]


    def find_RA_cluster(self, ra_id):
        """
        Given an RA ID, find the cluster it belongs to and return the cluster.
        """
        for cluster in self.clusters:
            if ra_id in cluster.ra_ids:
                return cluster
        raise ValueError(f"RA ID {ra_id} not found in any cluster.")