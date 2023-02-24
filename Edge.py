import RelationshipType
import Node


class Edge:
    def __init__(self, node: Node, rel: RelationshipType):
        self.node = node
        self.rel = rel

    def get_relationship_type(self) -> RelationshipType:
        return self.rel

    def __str__(self) -> str:
        return str(self.rel)

    def get_node(self) -> Node:
        return self.node
