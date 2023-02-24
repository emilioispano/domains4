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

    def add_abs_value(self, n: int) -> None:
        self.absValue += n

    def get_abs_value(self) -> int:
        return self.absValue

    def set_frequency(self, freq: float) -> None:
        self.freq = freq

    def get_frequency(self) -> float:
        return self.freq

    def get_ic(self) -> float:
        if self.absValue == 0:
            return 0
        return -math.log(self.freq)

    def set_real_frequency(self, freq: float) -> None:
        self.realFreq = freq

    def get_real_frequency(self) -> float:
        return self.realFreq

    def set_real_count(self, real_count: int) -> None:
        self.realCount = real_count

    def get_real_count(self) -> int:
        return self.realCount

    def add_protein_id(self, prot_id: int) -> None:
        self.intpid.add(prot_id)

    def get_protein_id_list(self) -> Set[int]:
        return self.intpid

    def has_gos(self) -> bool:
        return len(self.intpid) > 0

    def clean(self) -> None:
        super().clean()
