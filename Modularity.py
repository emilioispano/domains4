from typing import TypeVar, List, Dict, Any, Set, Type
from jgrapht.alg.interfaces import SpanningTreeAlgorithm
from jgrapht.graph import DefaultWeightedEdge, SimpleWeightedGraph, AsWeightedGraph
import numpy as np
import MakeClusters

T = TypeVar('T')


class Modularity:
    def __init__(self, graph: AsWeightedGraph[T, DefaultWeightedEdge], c: Type[T]) -> None:
        self.map: Dict[T, int] = {}
        self.buffer: List[SimpleWeightedGraph[T, DefaultWeightedEdge]] = []
        edges = np.zeros(graph.edge_set().size() * 2, dtype=int)
        index = np.zeros(graph.vertex_set().size(), dtype=c)

        i = 0
        n = 0
        edgeset = graph.edge_set()
        for e in edgeset:
            node = graph.get_edge_source(e)
            if node not in self.map:
                index[i] = node
                self.map[node] = i
                i += 1
            edges[n] = self.map[node]
            n += 1
            node = graph.get_edge_target(e)
            if node not in self.map:
                index[i] = node
                self.map[node] = i
                i += 1
            edges[n] = self.map[node]
            n += 1
        self.map = {}  # deleting
        ss = MakeClusters.MakeClusters()
        cluster = ss.get_fast_greedy_res(edges, index.size)
        memberships: Dict[int, Set[T]] = {}
        for i in range(cluster.size):
            if cluster[i] in memberships:
                memberships[cluster[i]].add(index[i])
            else:
                hs = set()
                hs.add(index[i])
                memberships[cluster[i]] = hs
        alledges = graph.edge_set()

        for hs in memberships.values():
            g = SimpleWeightedGraph(DefaultWeightedEdge)
            for e in alledges:
                k = graph.get_edge_source(e)
                m = graph.get_edge_target(e)
                if k in hs and m in hs:
                    if k not in g:
                        g.add_vertex(k)
                    if m not in g:
                        g.add_vertex(m)
                    dwe = g.add_edge(k, m)
                    g.set_edge_weight(dwe, graph.get_edge_weight(e))
            self.buffer.append(g)

    def get_clusters(self) -> List[SimpleWeightedGraph[T, DefaultWeightedEdge]]:
        return self.buffer
