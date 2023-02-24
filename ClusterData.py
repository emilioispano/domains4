#!/usr/bin/python3

class ClusterData:
    def __init__(self, representative, proteins, gos=None):
        self.representative = representative
        self.proteins = set(proteins)
        self.gos = set(gos) if gos else set()

    def get_representative(self):
        return self.representative

    def set_representative(self, representative):
        self.representative = representative

    def get_proteins(self):
        return self.proteins

    def set_proteins(self, proteins):
        self.proteins = set(proteins)

    def get_gos(self):
        return self.gos

    def set_gos(self, gos):
        self.gos = set(gos)

    def add_protein(self, prot_id):
        self.proteins.add(prot_id)

    def add_all_proteins(self, prot_ids):
        self.proteins.update(prot_ids)

    def add_go(self, go):
        self.gos.add(go)

    def add_all_gos(self, gos):
        self.gos.update(gos)
