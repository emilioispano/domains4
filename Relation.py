from enum import Enum


class Direction(Enum):
    propagationUp = 1
    propagationDown = 2
    transitive = 3
    symmetric = 4


class RelationshipType(Enum):
    is_a = 1
    BFO_0000050 = 2
    BFO_0000051 = 3
    BFO_0000066 = 4
    RO_0002211 = 5
    RO_0002212 = 6
    RO_0002213 = 7
    RO_0002215 = 8
    RO_0002216 = 9
    RO_0002091 = 10
    RO_0002092 = 11
    RO_0002093 = 12


class Relation:
    relation = None
    rel = None
    relations = None

    def __init__(self):
        self.relation = {}
        self.relations = set()
        self.relation[RelationshipType.is_a] = Direction.transitive
        self.relation[RelationshipType.BFO_0000050] = Direction.transitive
        self.relation[RelationshipType.BFO_0000051] = Direction.propagationDown  # non usare has_part
        self.relation[RelationshipType.BFO_0000066] = Direction.transitive
        self.relation[RelationshipType.RO_0002211] = Direction.transitive
        self.relation[RelationshipType.RO_0002212] = Direction.transitive
        self.relation[RelationshipType.RO_0002213] = Direction.transitive
        self.relation[RelationshipType.RO_0002215] = Direction.transitive
        self.relation[RelationshipType.RO_0002216] = Direction.transitive
        self.relation[RelationshipType.RO_0002091] = Direction.transitive
        self.relation[RelationshipType.RO_0002092] = Direction.transitive
        self.relation[RelationshipType.RO_0002093] = Direction.transitive
        self.relations.add("is_a")
        self.relations.add("BFO_0000050")  # part_of
        self.relations.add("BFO_0000066")  # occurs_in
        self.relations.add("RO_0002211")  # regulates
        self.relations.add("RO_0002212")  # negatively regulates
        self.relations.add("RO_0002213")  # positively regulates
        self.relations.add("RO_0002215")  # capable of
        self.relations.add("RO_0002216")  # capable of part of
        self.relations.add("RO_0002091")
        self.relations.add("RO_0002092")
        self.relations.add("RO_0002093")

    @staticmethod
    def instance():
        if not Relation.rel:
            Relation.rel = Relation()
        return Relation.rel

    def get_relation(self, reltype):
        return self.relation[reltype]

    def contains(self, rel):
        return rel in self.relations
