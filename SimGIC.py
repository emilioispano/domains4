class SimGIC:
    def __init__(self):
        self.graph = None

    def set_graph_owl(self, graph):
        self.graph = graph

    def compute_distance(self, list1, list2, simlimit=None):
        parentset1 = set()
        parentset2 = set()

        if isinstance(list1, list):
            for n in list1:
                parentset1.update(self.graph.get_all_go_ancestors(n))
        else:
            parentset1.update(self.graph.get_all_go_ancestors(list1))

        if isinstance(list2, list):
            for n in list2:
                parentset2.update(self.graph.get_all_go_ancestors(n))
        else:
            parentset2.update(self.graph.get_all_go_ancestors(list2))

        dist = self.similarity(parentset1, parentset2)
        if simlimit is None:
            return dist
        else:
            if dist >= simlimit:
                return dist
            else:
                return 0.0

    @staticmethod
    def get_max_distance():
        return 1.0

    @staticmethod
    def get_min_distance():
        return 0.0

    @staticmethod
    def similarity(parentset1, parentset2):
        union = set()
        sumunion = 0.0
        suminter = 0.0

        union.update(parentset1)
        union.update(parentset2)

        intersection = parentset1.intersection(parentset2)

        if len(intersection) > 0:
            for n in intersection:
                suminter += n.getIC()

            for n in union:
                sumunion += n.getIC()

            # Not true if and only if parents1 and parents2 contain only the root
            if sumunion > 0:
                return suminter / sumunion

        return 0.0
