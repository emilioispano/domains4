import Node
import OntNamespace


class NodeExt(Node.Node()):
    def __init__(self):
        super().__init__()
        self.namespace = None

    def set_name_space(self, namespace):
        self.namespace = OntNamespace.OntNamespace.valueOf(namespace)

    def get_name_space(self):
        return self.namespace
