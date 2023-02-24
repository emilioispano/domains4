from typing import List, Set
from modularity.Modularity import Modularity
from collections import defaultdict
from jgrapht.alg.connectivity import ConnectivityInspector
from jgrapht.graph import AsSubgraph, DefaultWeightedEdge, SimpleWeightedGraph, AsWeightedGraph

class SSNetwork:
    def __init__(self, query: str, sg: SimpleWeightedGraph[str, DefaultWeightedEdge]):
        self.query = query
        self.modularity = None
        insp = ConnectivityInspector(sg)
        vertexconnected = insp.connected_sets()

        for vertices in vertexconnected:
            subg = AsSubgraph(sg, vertices)
            map = defaultdict(float)
            for e in subg.edge_set():
                map[e] = sg.get_edge_weight(e)
            tG = AsWeightedGraph(subg, map)

            if tG.contains_vertex(query):
                self.modularity = Modularity(tG, str)
                break

    def get_all_clusters(self) -> List[Set[str]]:
        clusters = []
        if self.modularity:
            for g in self.modularity.get_clusters():
                clusters.append(g.vertex_set())
        return clusters

    def get_cluster(self) -> Set[str]:
        cluster = set()
        if self.modularity:
            for g in self.modularity.get_clusters():
                if g.contains_vertex(self.query):
                    cluster = g.vertex_set()
                    break
        return cluster
