class Route:
    def __init__(self, ra_id, pr_id, start_time, distance):
        self.RA = ra_id  
        self.PR = pr_id
        self.start_time = start_time
        self.distance = distance # distance in meters (not km like in json)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.RA} -> {self.PR}, t={self.start_time}, m={self.distance})"

    def set_pr(self, pr_id, distance):
        self.PR = pr_id
        self.distance = distance

    def set_start_time(self, start_time):
        self.start_time = start_time

    def increment_start_time(self, increment=1):
        self.start_time += increment