#!/usr/bin/python3

from typing import Set
import logging
import math
from AlignmentParser import AlignmentParser
from LoadInRam import LoadInRam
from Settings import Settings


class Blast8(AlignmentParser):
    def __init__(self, file_or_lir, thr, sg) -> None:
        self.sg = sg
        self.targets: Set[str] = set()
        self.settings = Settings.init()
        self.counthit = 0
        self.bufferuid: Set[str] = set()

        if isinstance(file_or_lir, str):
            self.read_file(file_or_lir, thr)
        elif isinstance(file_or_lir, LoadInRam):
            self.read_data(file_or_lir, thr)
        else:
            raise ValueError("Expected either a file path or a LoadInRam instance")

    def read_file(self, file: str, thr: float) -> None:
        self.bufferuid = set()
        try:
            with open(file, 'r') as f:
                for line in f:
                    line = line.strip()
                    data = line.split('\t')
                    if data[0] != data[1]:
                        if not self.sg.__contains__(data[0]):
                            self.sg.add_vertex(data[0])

                        if not self.sg.__contains__(data[1]):
                            self.sg.add_vertex(data[1])

                        evalue = float(data[10])
                        score = -math.log(evalue)
                        if score >= thr:
                            if score >= self.settings.get_min_score():
                                self.counthit += 1
                            self.bufferuid.add(data[1])

                            if float(data[2]) <= self.settings.get_deep_thr():
                                self.targets.add(data[1])

                            if not self.sg.__contains_edge__(data[0], data[1]):
                                e = self.sg.add_edge(data[0], data[1])
                                self.sg.set_edge_weight(e, evalue)
                            else:
                                e = self.sg.get_edge(data[0], data[1])
                                if evalue < self.sg.get_edge_weight(e):
                                    self.sg.set_edge_weight(e, evalue)
        except FileNotFoundError as ex:
            logging.getLogger("Blast8").log(0, None, ex)
        except IOError as ie:
            logging.getLogger("Blast8").log(0, None, ie)

    def read_data(self, lir: LoadInRam, thr: float) -> None:
        self.bufferuid = set()
        lines = lir.get_content().split('\n')

        for line in lines:
            data = line.split('\t')

            if len(data) > 1 and data[0] != data[1]:
                if not self.sg.__contains__(data[0]):
                    self.sg.add_vertex(data[0])

                if not self.sg.__contains__(data[1]):
                    self.sg.add_vertex(data[1])

                evalue = float(data[10])
                score = -math.log(evalue)

                if score >= thr:
                    if score >= self.settings.get_min_score():
                        self.counthit += 1
                    self.bufferuid.add(data[1])

                    if float(data[2]) <= self.settings.get_deep_thr():
                        self.targets.add(data[1])

                    if not self.sg.__contains_edge__(data[0], data[1]):
                        e = self.sg.add_edge(data[0], data[1])
                        self.sg.set_edge_weight(e, evalue)
                    else:
                        e = self.sg.get_edge(data[0], data[1])
                        if e is not None and evalue < self.sg.get_edge_weight(e):
                            self.sg.set_edge_weight(e, evalue)

    def get_graph(self):
        return self.sg

    def get_targets(self):
        return self.targets

    def to_go_deep(self):
        return self.counthit <= self.settings.get_hitnum()

    def get_uid(self) -> Set[str]:
        return self.bufferuid
