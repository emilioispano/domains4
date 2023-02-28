import Modularity
from py4j import java_gateway

gateway = java_gateway.JavaGateway().launch_gateway(port=0, classpath='jgrapht-core-1.3.0.jar')
ConnectivityInspector = gateway.jvm.org.jgrapht.alg.connettivity.ConnectivityInspector
GraphTypeBuilder = gateway.jvm.org.jgrapht.graph.builder.GraphTypeBuilder
DefaultWeightedEdge = gateway.jvm.org.jgrapht.graph.DefaultWeightedEdge
SimpleWeightedGraph = gateway.jvm.org.jgrapht.graph.SimpleWeightedGraph
AsSubgraph = gateway.jvm.org.jgrapht.graph.AsSubgraph
AsWeightedGraph = gateway.jvm.org.jgrapht.graph.AsWeightedGraph


class SSNetwork:
    def __init__(self, query, sg):
        self.query = query
        self.modularity = None

        insp = ConnectivityInspector(sg)
        vertexconnected = insp.connected_sets()
        for vertices in vertexconnected:
            subg = AsSubgraph(sg, vertices)
            map = {e: sg.get_edge_weight(e) for e in subg.edge_set()}
            tG = AsWeightedGraph(GraphTypeBuilder().weighted(True).undirected().build(), subg, map)
            if tG.contains_vertex(query):
                self.modularity = Modularity.Modularity(tG, str)
                break
        else:
            self.modularity = None

    def get_all_clusters(self):
        clusters = []
        if self.modularity:
            for g in self.modularity.get_clusters():
                clusters.append(g.vertex_set())
        return clusters

    def get_cluster(self):
        cluster = set()
        if self.modularity:
            for g in self.modularity.get_clusters():
                if g.contains_vertex(self.query):
                    cluster = g.vertex_set()
                    break
        return cluster
