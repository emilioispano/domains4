from typing import Set
import GONode
import math


class NodeFreq(GONode.GONode()):
    def __init__(self):
        super().__init__()
        self.absValue = 0
        self.freq = -1
        self.realFreq = 0.0
        self.realCount = 0
        self.intpid: Set[int] = set()

    def add_abs_value(self, n):
        self.absValue += n

    def get_abs_value(self):
        return self.absValue

    def set_frequency(self, freq):
        self.freq = freq

    def get_frequency(self):
        return self.freq

    def get_ic(self):
        if self.absValue == 0:
            return 0
        return -math.log(self.freq)

    def set_real_frequency(self, freq):
        self.realFreq = freq

    def get_real_frequency(self):
        return self.realFreq

    def set_real_count(self, real_count):
        self.realCount = real_count

    def get_real_count(self):
        return self.realCount

    def add_protein_id(self, prot_id):
        self.intpid.add(prot_id)

    def get_protein_id_list(self):
        return self.intpid

    def has_gos(self):
        return len(self.intpid) > 0

    def clean(self):
        super().clean()
