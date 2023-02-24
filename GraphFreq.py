from typing import TypeVar
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from math import log
import NodeNotFoundException
import Direction
import GOGraphOWL
import NodeExt
import NodeFreq
import OntNamespace
import Relation

from typing import Dict

W = TypeVar('W', bound=NodeFreq.NodeFreq())
E = TypeVar('E', bound=NodeExt.NodeExt())


class GraphFreq:
    _instance = None

    def __init__(self):
        self.total_terms = None
        self.id2freq = {}
        self.graph = None
        self.max_bp_ic = 0.0
        self.max_mf_ic = 0.0
        self.max_cc_ic = 0.0
        self.relation = Relation.Relation()
        self._instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.relation = Relation.Relation.instance()
            cls.id2freq = {}
        return cls._instance

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def init(self, graph, database: MongoClient, collection: str):
        self.graph = graph
        try:
            self.load_freq_from_mongo(database, collection)
            for goid, freq in self.id2freq.items():
                if graph.exists(goid):
                    self.add_abs_value(graph.getGONode(goid), freq)

            self.calc_freq()
        except NodeNotFoundException as ex:
            print('o forse era qui?')

    def add_abs_value(self, node: W, w: int):
        node.addAbsValue(w)
        for e in self.graph.get_go_parents(node):
            if self.relation.get_relation(e.getRelationshipType()) != Direction.Direction.propagationDown:
                self.add_abs_value(e.get_node(), w)

    def calc_freq(self):
        mapnode = self.graph.get_node_map()
        maxw = max(self.graph.get_root(OntNamespace.OntNamespace.biological_process).getAbsValue(), self.graph.get_root(OntNamespace.OntNamespace.molecular_function).getAbsValue())
        maxw = max(maxw, self.graph.get_root(OntNamespace.OntNamespace.cellular_component).getAbsValue())
        for ontid, node in mapnode.items():
            if isinstance(node, NodeFreq.NodeFreq()):
                if node.getOntID() in self.id2freq:
                    node.setRealCount(self.id2freq[node.getOntID()])
                    absfreq = node.getRealCount() / self.total_terms
                    node.setRealFrequency(absfreq)

                freq = node.getAbsValue() / maxw

                if freq > 0:
                    ic = -log(freq)
                    if node.getNameSpace() == OntNamespace.OntNamespace.biological_process:
                        if ic > self.max_bp_ic:
                            self.max_bp_ic = ic
                    elif node.getNameSpace() == OntNamespace.OntNamespace.molecular_function:
                        if ic > self.max_mf_ic:
                            self.max_mf_ic = ic
                    elif node.getNameSpace() == OntNamespace.OntNamespace.cellular_component:
                        if ic > self.max_cc_ic:
                            self.max_cc_ic = ic
                node.setFrequency(freq)

    def load_freq_from_mongo(self, database: MongoClient, collection: str):
        coll: Collection = database[collection]
        cursor: Cursor = coll.find(projection={'_id': False})
        for doc in cursor:
            t = doc["freq"]
            self.id2freq[doc["goid"]] = t
            self.total_terms += t

    def max_bp_ic(self) -> float:
        return self.max_bp_ic

    def max_mf_ic(self):
        return self.max_mf_ic

    def max_cc_ic(self):
        return self.max_cc_ic

    def max_ic(self, namespace):
        if namespace == OntNamespace.OntNamespace.biological_process:
            return self.max_bp_ic
        elif namespace == OntNamespace.OntNamespace.molecular_function:
            return self.max_mf_ic
        elif namespace == OntNamespace.OntNamespace.cellular_component:
            return self.max_cc_ic
        else:
            return 0

    def get_total_term_number(self):
        return self.total_terms
