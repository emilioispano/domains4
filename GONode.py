import Node
import OntNamespace


class GONode(Node):
    def __init__(self):
        super().__init__()
        self.defn = None
        self.comment = None
        self.namespace = None
        self.disjoint = set()
        self.intDisjoint = False

    def set_namespace(self, namespace):
        if namespace == "biological_process":
            self.namespace = OntNamespace.OntNamespace.biological_process
        elif namespace == "molecular_function":
            self.namespace = OntNamespace.OntNamespace.molecular_function
        elif namespace == "cellular_component":
            self.namespace = OntNamespace.OntNamespace.cellular_component

    def get_namespace(self):
        return self.namespace

    def set_definition(self, defn):
        self.defn = defn

    def set_comment(self, comment):
        self.comment = comment

    def get_definition(self):
        return self.defn

    def get_comment(self):
        return self.comment

    def add_disjoint(self, goid):
        if isinstance(goid, set):
            self.disjoint.update(goid)
        else:
            self.disjoint.add(goid)

    def has_disjoint(self):
        return bool(self.disjoint)

    def is_disjoint_with(self, goid):
        return goid in self.disjoint

    def set_int_disjoint(self, disj):
        self.intDisjoint = disj

    def is_int_disjoint(self):
        return self.intDisjoint

    def clean(self):
        super().clean()

    @staticmethod
    def is_go_node(node):
        return isinstance(node, GONode)
