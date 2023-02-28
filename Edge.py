class Edge:
    def __init__(self, node, rel):
        self.node = node
        self.rel = rel

    def get_relationship_type(self):
        return self.rel

    def __str__(self):
        return str(self.rel)

    def get_node(self):
        return self.node
