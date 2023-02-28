class BMMDistance:
    def __init__(self, distance_method):
        self.distance_method = distance_method

    def semantic_similarity(self, list1, list2):
        simat = [[0.0 for _ in range(len(list2))] for _ in range(len(list1))]

        for i in range(len(list1)):
            n = list1[i]
            for j in range(len(list2)):
                simat[i][j] = self.distance_method.compute_distance(n, list2[j])

        k = 0
        tmp = 0.0
        totsim = 0.0
        m = min(len(list1), len(list2))
        for n in range(m):
            for i in range(k, len(list1)):
                tmp = max(simat[i][k], tmp)
            for j in range(k + 1, len(list2)):
                tmp = max(simat[k][j], tmp)
            k += 1
            totsim += tmp
            tmp = 0.0

        sim = totsim / max(len(list1), len(list2))
        return sim
