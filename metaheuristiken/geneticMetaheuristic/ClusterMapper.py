import math
from copy import deepcopy
import random
from metaheuristiken.geneticMetaheuristic.Cluster import Cluster

class ClusterMapper():
    """
    ClusterMapper maps RAs into Clusters and manages their starting times etc
    """
    def __init__(self, ra_list, num_clusters, max_start_time):
        self.ra_list = ra_list
        self.max_start_time = max_start_time
        self.num_clusters = num_clusters
        self.clusters = self.get_random_cluster_distribution(max_start_time)

    
    def get_random_cluster_distribution(self, max_start_time):
        """
        Randomly distribute all RAs into the given amount of clusters
        """
        # Shuffle to add randomness and avoid bias
        shuffled_ras = random.sample(self.ra_list, len(self.ra_list))

        # Init containers
        clusters = [[] for _ in range(self.num_clusters)]
        cluster_populations = [0] * self.num_clusters

        # Assign RAs to cluster with currently lowest population
        for ra in shuffled_ras:
            idx = cluster_populations.index(min(cluster_populations))
            clusters[idx].append(ra)
            cluster_populations[idx] += ra["population"]

        # Build Cluster objects
        result = []
        for i, ra_group in enumerate(clusters):
            new_cluster = Cluster(
                start_time=random.randrange(0, int(max_start_time)),
                cluster_mapper=self,
                ra_ids=[ra["id"] for ra in ra_group],
                size=sum(ra["population"] for ra in ra_group)
            )
            result.append(new_cluster)

        return result
    

    def reassign_random_ra(self, ra_id):
        """
        Finds the cluster with a given RA ID and adds it to another random cluster
        """
        cluster_with_ra = next((c for c in self.clusters if ra_id in c.ra_ids), None)
        if cluster_with_ra is None:
            return # can happen if it's been removed in the same mutation

        weights = [1 / (c.size + 0.001) for c in self.clusters]
        random_cluster = random.choices(self.clusters, weights=weights, k=1)[0]
        
        cluster_with_ra.ra_ids.remove(ra_id)
        random_cluster.ra_ids.append(ra_id)


    def recluster_population(self):
        """
        Keeps the cluster start_times but reorders the RAs in it
        """
        # TODO this method can be somhow combined with the get_random_cluster_distribution function (duplicated code fragments)
        cluster_size = math.ceil(len(self.ra_list) / self.num_clusters)
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