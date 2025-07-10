class Cluster(object):
    def __init__(self, routes, start_time=0):
        self.routes = routes
        self.start_time = 0

    def __repr__(self):
        return f"{self.__class__.__name__}({len(self.routes)} routes starting at t={self.start_time})"