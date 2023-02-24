from rdflib import Graph, Namespace, OWL
from typing import TypeVar, List, Tuple, Set, Dict
import NodeNotFoundException
import Relation
import NodeFactory
import GONode
import Node
import OntNamespace
import Direction
import NodeExt
import Edge
import logging

T = TypeVar('T')


class GOGraphOWL:
    def __init__(self, owl_file, g, e):
        self.typeg = g
        self.typee = e
        self.node_map = {}
        self.relation = Relation.Relation().instance()
        self.load_from_file(owl_file)
        self.model = None
        self.descendantb = None
        self.ancestorb = None
        self.visited = set()
        self.id = 0
        self.gonode = None

    def load_from_file(self, file):
        self.model = Graph()
        self.model.parse(file, format="xml")
        for subject, predicate, obj in self.model.triples((None, OWL.Class, None)):
            self.browse_class(subject)

    def browse_class(self, ontclass):
        localname = ontclass.get_local_name()
        localname = localname.replace('_', ':')
        if localname.startswith("GO:"):
            ontpr = self.model.getOntProperty("http://www.geneontology.org/formats/oboInOwl#hasOBONamespace")
            namespace = ontclass.getPropertyValue(ontpr)
            if namespace is not None:
                if localname in self.node_map:
                    self.gonode = self.node_map[localname]
                else:
                    self.gonode = self.create_gonode(localname)
                self.gonode.setNamespace(str(namespace))
                ontpr = self.model.getOntProperty("http://www.w3.org/2000/01/rdf-schema#label")
                label = ontclass.getPropertyValue(ontpr)
                self.gonode.setComment(str(label))
                iterst = ontclass.listProperties()

                while iterst.hasNext():
                    stmt = iterst.nextStatement()
                    predicate = stmt.getPredicate()
                    if predicate.hasURI("http://www.w3.org/2000/01/rdf-schema#subClassOf"):
                        rdfnode = stmt.getObject()
                        if rdfnode.isURIResource():
                            ontid = stmt.getObject().asResource().getLocalName()
                            ontid = ontid.replace('_', ':')
                            self.add_node(ontid, Relation.RelationshipType.is_a)
                        else:
                            oc = rdfnode.asOntClass()
                            if oc.isRestriction():
                                r = oc.asRestriction()
                                if r.isSomeValuesFromRestriction():
                                    av = r.asSomeValuesFromRestriction()
                                    ontid = av.getSomeValuesFrom().getLocalName()
                                    ontid = ontid.replace('_', ':')
                                    if av.getOnProperty().getLocalName() in Relation.Relation:
                                        rel = Relation.RelationshipType[av.getOnProperty().getLocalName()]
                                        self.add_node(ontid, rel)
                    elif predicate.hasURI("http://www.w3.org/2002/07/owl#equivalentClass"):
                        itr = ontclass.listEquivalentClasses()
                        while itr.hasNext():
                            ontc = itr.next()
                            inc = ontc.asIntersectionClass()
                            rdflist = inc.getOperands()
                            for ii in rdflist.iterator():
                                n = ii.next()
                                if n.isResource():
                                    res = n.asResource()
                                    oc = res.asOntClass()
                                    if oc.isRestriction():
                                        r = oc.asRestriction()
                                        if r.isSomeValuesFromRestriction():
                                            av = r.asSomeValuesFromRestriction()
                                            ontid = av.getSomeValuesFrom().getLocalName()
                                            ontid = ontid.replace('_', ':')
                                            if av.getOnProperty().getLocalName() in Relation.Relation:
                                                rel = Relation.RelationshipType[av.getOnProperty().getLocalName()]
                                                self.add_node(ontid, rel)
                    elif predicate.hasURI("http://www.w3.org/2002/07/owl#disjointWith"):
                        ontid = stmt.getObject().asResource().getLocalName()
                        if ontid is not None:
                            ontid = ontid.replace('_', ':')
                            if ontid in self.node_map:
                                n = self.node_map[ontid]
                                n.addDisjoint(self.gonode.get_ont_id())
                            else:
                                assert ontid.startswith("GO:")
                                self.create_gonode(ontid.addDisjoint(self.gonode.get_ont_id()))
                            self.gonode.addDisjoint(ontid)
        elif localname.startswith("CHEBI:") or localname.startswith("PR:"):
            if localname in self.node_map:
                extnode = self.node_map[localname]
            else:
                extnode = NodeFactory.NodeFactory().get_node(self.typee)
                extnode.set_id(self.id + 1)
                ns = localname.split(":")
                extnode.set_name_space(ns[0])
                self.node_map[localname] = extnode
            extnode.set_ont_id(localname)

    def add_node(self, ontid, rel):
        if ontid.startswith("GO:"):
            if ontid in self.node_map:
                gn = self.node_map[ontid]
            else:
                gn = self.create_gonode(ontid)
            self.set_node(gn, self.gonode, rel)
        elif ontid.startswith("CHEBI:") or ontid.startswith("PR:"):
            if ontid in self.node_map:
                extn = self.node_map[ontid]
            else:
                extn = NodeFactory.NodeFactory().get_node(self.typee)
                extn.set_ont_id(ontid)
                self.id += 1
                extn.set_id(self.id)
                ns = ontid.split(":")
                extn.set_namespace(ns[0])
                self.node_map[ontid] = extn
            self.set_node(self.gonode, extn, rel)

    def set_node(self, parent, child, rel):
        if parent.contains_child(child) and child.contains_parent(parent):
            return

        edgep = Edge.Edge(parent, rel)
        edgec = Edge.Edge(child, rel)
        parent.add_child(edgec)
        child.add_parent(edgep)
        parent.add_child_node(child, edgec)
        child.add_parent_node(parent, edgep)

    def create_gonode(self, goid):
        n = NodeFactory.NodeFactory().get_node(self.typeg)
        n.set_ont_id(goid)
        self.id += 1
        n.set_id(self.id)
        self.node_map[goid] = n
        return n

    def get_node_map(self):
        return self.node_map

    def get_parents(self, node):
        return node.get_parents()

    def get_children(self, node):
        return node.get_children()

    def get_go_children(self, node):
        listt = []
        for e in node.get_children():
            if Relation.Relation().get_relation(e.get_relationship_type()) != Direction.Direction.propagationUp:
                if isinstance(e.get_node(), GONode.GONode()):
                    listt.append(e)
        return listt

    def get_go_parents(self, node):
        listt = []
        for e in node.get_parents():
            if Relation.Relation().get_relation(e.get_relationship_type()) != Direction.Direction.propagationDown:
                if isinstance(e.get_node(), GONode.GONode()):
                    listt.append(e)
        return listt

    def is_ancestor_of(self, ancestor, node):
        self.browse_ancestor(ancestor, node)
        if self.ancestorb:
            self.ancestorb = False
            return True
        return False

    def browse_ancestor(self, ancestor, node):
        for e in node.get_parents():
            if Relation.Relation().get_relation(e.get_relationship_type()) != Direction.Direction.propagationDown:
                if e.get_node() == ancestor:
                    self.ancestorb = True
                    return
                self.browse_ancestor(ancestor, e.get_node())

    def is_descendant_of(self, descendant, node):
        self.browse_descendant(descendant, node)
        self.visited.clear()
        if self.descendantb:
            self.descendantb = False
            return True
        return False

    def browse_descendant(self, descendant, node):
        if node not in self.visited:
            self.visited.add(node)
            for e in node.get_children():
                if Relation.Relation().get_relation(e.get_relationship_type()) != Direction.Direction.propagationUp:
                    if e.get_node() == descendant:
                        self.descendantb = True
                        return
                    self.browse_descendant(descendant, e.get_node())

    @staticmethod
    def process_id():
        return "GO:0008150"

    @staticmethod
    def function_id():
        return "GO:0003674"

    @staticmethod
    def component_id():
        return "GO:0005575"

    def clean_all(self):
        for key in self.node_map.keys():
            n = self.node_map[key]
            if n.is_flagged():
                n.clean()

    def read_disjoint(self, disj_file):
        try:
            with open(disj_file, "r") as f:
                for line in f:
                    if line.startswith("#"):
                        continue
                    line = line.strip()
                    if self.exists(line):
                        try:
                            n = self.get_go_node(line)
                            n.setIntDisjoint(True)
                        except NodeNotFoundException as ex:
                            logging.getLogger(GOGraphOWL.__name__).log(logging.Level.SEVERE, None, ex)
        except (FileNotFoundError, IOError) as ex:
            logging.getLogger(GOGraphOWL.__name__).log(logging.Level.SEVERE, None, ex)

    def dump_sif(self):
        buffer = set()
        try:
            with open("map.sif", "w") as fw:
                for ontid in self.node_map.keys():
                    n = self.node_map[ontid]
                    buffer.add(ontid)
                    for edge in n.get_parents():
                        if edge.get_node().get_ont_id() not in buffer:
                            fw.write(f"{ontid}\t{edge.getRelationshipType()}\t{edge.get_node().get_ont_id()}\n")
                    for edge in n.get_children():
                        if edge.get_node().get_ont_id() not in buffer:
                            fw.write(f"{edge.get_node().get_ont_id()}\t{edge.getRelationshipType()}\t{ontid}\n")
        except IOError as ex:
            logging.getLogger(GOGraphOWL.__name__).log(logging.Level.SEVERE, None, ex)

    def dump_edge(self):
        try:
            with open("dataEdge.txt", "w") as fw:
                for ontid in self.node_map.keys():
                    n = self.node_map[ontid]
                    if isinstance(n, NodeExt.NodeExt()) and len(n.getParents()) > 1:
                        fw.write(n.getOntID())
                        for edge in n.getParents():
                            fw.write(f"\t{edge.get_node().get_ont_id()}")
                        fw.write("\n")
        except IOError as ex:
            logging.getLogger(GOGraphOWL.__name__).log(logging.Level.SEVERE, None, ex)

    def remove_cross_path(self):
        for ontid in self.node_map.keys():
            if self.node_map[ontid].is_go_node():
                node = self.node_map[ontid]
                buffer = []
                for e in node.get_parents():
                    if e.get_node().is_go_node():
                        n = e.get_node()
                        if node.get_name_space() != n.get_name_space():
                            buffer.append(e)
                            n.remove_child_node(node)
                            print(f"{node.get_ont_id()} -- {n.get_ont_id()}")
                for e in buffer:
                    node.remove_parent(e)

    def get_node(self, ontid: str) -> T:
        n = None
        if ontid in self.node_map:
            n = self.node_map[ontid]
        else:
            raise NodeNotFoundException.NodeNotFoundException("The Ontology ID " + ontid + " is not present in the current ontology.")
        return n

    def get_go_node(self, goid: str) -> T:
        n = None
        if goid in self.node_map:
            n = self.node_map[goid]
            if isinstance(n, GONode.GONode()):
                return n
        else:
            raise NodeNotFoundException.NodeNotFoundException("The GO ID " + goid + " is not present in the current ontology.")
        return None

    def get_ancestors_of(self, node) -> List[T]:
        anc = []
        # anc.append(node)
        self.browse_ancestors(anc, node)
        return anc

    def browse_ancestors(self, anc: List[T], node: Node):
        if not node.is_root():
            for e in node.get_parents():
                if self.relation.getRelation(e.getRelationshipType()) != Direction.Direction.propagationDown:
                    if isinstance(e.get_node(), GONode.GONode()):
                        anc.append(e.get_node())
                    self.browse_ancestors(anc, e.get_node())

    def get_all_go_descendants(self, n: T) -> Set[T]:
        listt = set()
        if not n.isLeaf():
            for e in n.getChildren():
                if isinstance(e.get_node(), GONode.GONode()):
                    self.walk_descendants(e.get_node(), listt)
        return listt

    def walk_descendants(self, n: T, listt: Set[T]):
        listt.add(n)
        if not n.isLeaf():
            for e in n.getChildren():
                if isinstance(e.get_node(), GONode.GONode()):
                    if self.relation.getRelation(e.getRelationshipType()) != Direction.Direction.propagationUp:
                        self.walk_descendants(e.get_node(), listt)

    def get_all_go_ancestors(self, n: T) -> Set[T]:
        listt = set()
        if not n.isRoot():
            for e in n.getParents():
                if isinstance(e.get_node(), GONode.GONode()):
                    self.walk_ancestors(e.get_node(), listt)
        return listt

    def walk_ancestors(self, n: T, listt: Set[T]):
        listt.add(n)
        # print(n.getOntID())
        if not n.isRoot():
            for e in n.getParents():
                if isinstance(e.get_node(), GONode.GONode()):
                    if self.relation.getRelation(e.getRelationshipType()) != Direction.Direction.propagationDown:
                        self.walk_ancestors(e.get_node(), listt)

    def exists(self, ontid: str) -> bool:
        return ontid in self.node_map

    def get_root(self, namespace: OntNamespace) -> T:
        gid = ""
        root = None
        if namespace == OntNamespace.OntNamespace.molecular_function:
            gid = self.function_id()
        elif namespace == OntNamespace.OntNamespace.biological_process:
            gid = self.process_id()
        elif namespace == OntNamespace.OntNamespace.cellular_component:
            gid = self.component_id()

        try:
            root = self.node_map[gid]
        except NodeNotFoundException as ex:
            logging.getLogger(GOGraphOWL.__name__).log(logging.Level.SEVERE, None, ex)
        return root
