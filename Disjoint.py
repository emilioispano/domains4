from typing import Dict, Set
import Relation
import Direction
import GONode
import NodeNotFoundException


class Disjoint:
    def __init__(self):
        self.graph = None
        self.relation = None
        self.visited = set()
        self.mapset = {}

    def add_disjoint(self, graph, bpic: float, ccic: float, mfic: float):
        self.relation = Relation.Relation().instance()
        self.visited = set()
        self.graph = graph

        try:
            print("Process")
            self.mapset = {}
            root = graph.get_gonode(graph.ProcessID())
            self.start(root, bpic)

            print("Function")
            root = graph.get_gonode(graph.FunctionID())
            self.start(root, ccic)

            print("Component")
            root = graph.get_gonode(graph.ComponentID())
            self.start(root, mfic)
        except NodeNotFoundException as ex:
            print('cosa ciera qui?')

    def start(self, root, ic: float) -> None:
        edges = self.graph.get_gochildren(root)
        for e in edges:
            if e.get_node().is_gonode():
                disjoint = self.find_disjoint(e.get_node(), ic)
                for goid, parents in disjoint.items():
                    self.graph.get_gonode(goid).add_disjoint(parents)

    def find_disjoint(self, node, ic: float) -> Dict[str, Set[str]]:
        buffer = {}

        for e in self.graph.get_gochildren(node):
            if e.get_node().is_gonode():
                n = e.get_node()
                if 0 < n.get_ic() <= ic:
                    buffer[n.get_ontid()] = set()
                    self.walk_descendants(n, n.get_ontid(), buffer)

                    self.mapset.clear()
                    self.visited.clear()

        self.mapset.clear()
        self.visited.clear()

        return self.get_disjoint(buffer)

    def walk_descendants(self, n, parent: str, buffer: Dict[str, Set[str]]) -> None:
        if n.get_ontid() in self.mapset:
            for goid in self.mapset[n.get_ontid()]:
                buffer[goid].add(parent)
            self.mapset[n.get_ontid()].add(parent)
        else:
            self.mapset[n.get_ontid()] = {parent}

        self.visited.add(n)

        if not n.is_leaf():
            for e in n.get_children():
                if isinstance(e.get_node(), GONode.GONode):
                    if self.relation.get_relation(e.get_relationship_type()) != Direction.Direction.propagationUp:
                        self.walk_descendants(e.get_node(), parent, buffer)

    @staticmethod
    def get_disjoint(buffer: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
        disjoint = {}

        markers = list(buffer.keys())
        for parent in markers:
            parents = buffer[parent]
            if parents:
                disjoint[parent] = set()
                for marker in markers:
                    if marker not in parents:
                        disjoint[parent].add(marker)
            else:
                disjoint[parent] = set(markers) - {parent}

        return disjoint

    @staticmethod
    def write_disjoint(disjoint):
        for goid, parents in disjoint.items():
            print(goid, end='')
            for marker in parents:
                print('\t' + marker, end='')
            print()
