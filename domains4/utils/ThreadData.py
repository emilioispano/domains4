# ThreadData.py

class ThreadData:
    def __init__(self, prot_custers, neighbor_map):
        self.prot_custers = prot_custers
        self.neighbor_map = neighbor_map

    def get_prot_custers(self):
        return self.prot_custers

    def set_prot_custers(self, prot_custers):
        self.prot_custers = prot_custers

    def get_neighbor_map(self):
        return self.neighbor_map

    def set_neighbor_map(self, neighbor_map):
        self.neighbor_map = neighbor_map
