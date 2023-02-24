#!/usr/bin/python3

from typing import List, Set, Tuple, Dict
from multiprocessing import Manager, Process
import logging
from ArgotGraph import ArgotGraph
from DataDomains import DataDomains
from ThreadData import ThreadData


class DomainsThread(Process):
    def __init__(self, domains_map: Dict[str, Dict[int, Set[str]]], blast_prot_map: Dict[str, Set[str]],
                 templates: List[str], database, nwth: float):
        super().__init__()
        self.domains_map = domains_map
        self.blast_prot_map = blast_prot_map
        self.templates = templates
        self.database = database
        self.nwth = nwth
        self.output = Manager().dict()

    def run(self):
        for template in self.templates:
            if self.blast_prot_map.get(template) is not None:
                self.get_neighbors(self.domains_map.get(template), template, self.blast_prot_map.get(template))

    def get_neighbors(self, map: Dict[int, Set[str]], pid: str, blast_prot: Set[str]):
        try:
            doms = self.get_domains(map)
            dd = DataDomains(self.database, doms)
            if not dd.get_exit():
                uidscore = dd.get_results().getUidOver(self.nwth)
                if uidscore:
                    at = ArgotGraph(uidscore, pid, self.database, blast_prot, self.ident)
                    if pid not in self.output:
                        self.output[pid] = ThreadData(at.get_prot_clusters(), at.get_cluster())
            else:
                logging.error(f"ERROR: suck: {pid}")
        except Exception as e:
            logging.error(f"ERROR: {e}, {pid}")

    def get_domains(self, map: Dict[int, Set[str]]) -> List[str]:
        buffer = []
        for p in sorted(map.keys()):
            if len(map[p]) > 1:
                for ipr in sorted(list(map[p])):
                    buffer.append(ipr)
            else:
                buffer.extend(list(map[p]))
        return buffer
