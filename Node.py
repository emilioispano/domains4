class Node:
    def __init__(self):
        self.ontid = ''
        self.parents = set()
        self.children = set()
        self.parent_nodes = {}
        self.child_nodes = {}
        self.id = 0
        self.flag = False

    def set_ont_id(self, ontid):
        self.ontid = ontid

    def get_ont_id(self):
        return self.ontid

    def equals(self, node):
        return self.ontid == node.get_ont_id()

    def add_parent(self, edge):
        self.parents.add(edge)

    def add_child(self, edge):
        self.children.add(edge)

    def add_parent_node(self, n, e):
        self.parent_nodes[n] = e

    def add_child_node(self, n, e):
        self.child_nodes[n] = e

    def get_parents(self):
        return self.parents

    def get_children(self):
        return self.children

    def contain_parent(self, n):
        return n in self.parent_nodes

    def contain_child(self, n):
        return n in self.child_nodes

    def is_leaf(self):
        return len(self.children) == 0

    def set_flag(self, flag):
        self.flag = flag

    def is_flagged(self):
        return self.flag

    def remove_child(self, e):
        self.children.remove(e)

    def remove_parent(self, e):
        self.parents.remove(e)

    def remove_parent_node(self, n):
        p = self.parent_nodes[n]
        self.remove_parent(p)
        self.parent_nodes.pop(n)

    def remove_child_node(self, n):
        c = self.child_nodes[n]
        self.remove_child(c)
        self.child_nodes.pop(n)

    def is_root(self):
        return len(self.parents) == 0

    def clean(self):
        self.flag = False

    def get_id(self):
        return self.id

    def set_id(self, idd):
        self.id = idd
