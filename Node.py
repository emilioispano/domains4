from typing import Set
import NodeInterface


class Node(NodeInterface.NodeInterface()):
    def __init__(self):
        self.ontid = ''
        self.parents = set()
        self.children = set()
        self.parentNodes = {}
        self.childNodes = {}
        self.id = 0
        self.flag = False

    def set_ont_id(self, ontid: str) -> None:
        self.ontid = ontid

    def get_ont_id(self) -> str:
        return self.ontid

    def equals(self, node) -> bool:
        return self.ontid == node.get_ont_id()

    def add_parent(self, edge) -> None:
        self.parents.add(edge)

    def add_child(self, edge) -> None:
        self.children.add(edge)

    def add_parent_node(self, n, e) -> None:
        self.parentNodes[n] = e

    def add_child_node(self, n, e) -> None:
        self.childNodes[n] = e

    def get_parents(self):
        return self.parents

    def get_children(self):
        return self.children

    def contain_parent(self, n):
        return n in self.parentNodes

    def contain_child(self, n):
        return n in self.childNodes

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def set_flag(self, flag: bool) -> None:
        self.flag = flag

    def is_flagged(self) -> bool:
        return self.flag

    def remove_child(self, e) -> None:
        self.children.remove(e)

    def remove_parent(self, e) -> None:
        self.parents.remove(e)

    def remove_parent_node(self, n) -> None:
        p = self.parentNodes[n]
        self.remove_parent(p)
        self.parentNodes.pop(n)

    def remove_child_node(self, n) -> None:
        c = self.childNodes[n]
        self.remove_child(c)
        self.childNodes.pop(n)

    def is_root(self) -> bool:
        return len(self.parents) == 0

    def clean(self) -> None:
        self.flag = False

    def get_id(self) -> int:
        return self.id

    def set_id(self, idd) -> None:
        self.id = idd
