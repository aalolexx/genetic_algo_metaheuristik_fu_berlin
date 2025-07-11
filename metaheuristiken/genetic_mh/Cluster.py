class Cluster(object):
    def __init__(self, cluster_mapper, ra_ids, size, start_time=0):
        self.cluster_mapper = cluster_mapper
        self.start_time = start_time
        self.ra_ids = ra_ids
        self.size = size 


    def __repr__(self):
        return f"{self.__class__.__name__}(starting at t={self.start_time}, ra_ids={', '.join(self.ra_ids)})"