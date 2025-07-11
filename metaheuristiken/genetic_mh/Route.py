class Route:
    def __init__(self, ra_id, pr_id, distance, cluster):
        self.RA = ra_id  
        self.PR = pr_id
        self.distance = distance # distance in meters (not km like in json)
        self.cluster = cluster

    def __repr__(self):
        return f"{self.__class__.__name__}({self.RA} -> {self.PR}, m={self.distance})"

    def set_pr(self, pr_id, distance):
        self.PR = pr_id
        self.distance = distance