import numpy as np


class BMADistance:
    def __init__(self, distance_method):
        self.distance_method = distance_method

    def semantic_similarity(self, list1, list2, sim_limit=None) -> float:
        bcol = np.full(len(list2), self.distance_method.get_min_distance())
        brow = np.full(len(list1), self.distance_method.get_min_distance())

        for i, n in enumerate(list1):
            for j, m in enumerate(list2):
                dist = self.distance_method.compute_distance(n, m)
                brow[i] = max(brow[i], dist)
                bcol[j] = max(bcol[j], dist)

        sim_score = (np.sum(brow) + np.sum(bcol)) / (len(list1) + len(list2))

        if sim_limit is not None and sim_score < sim_limit:
            return 0.0
        else:
            return sim_score

