#!/usr/bin/python3

from multiprocessing import Manager, Process
import logging
import ArgotGraph
import DataDomains
import ThreadData


class DomainsThread(Process):
    def __init__(self, domains_map, blast_prot_map, templates, database, nwth):
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

    def get_neighbors(self, mapp, pid, blast_prot):
        try:
            doms = self.get_domains(mapp)
            dd = DataDomains.DataDomains(self.database, doms)
            if not dd.get_exit():
                uidscore = dd.get_results().get_uid_over(self.nwth)
                if uidscore:
                    at = ArgotGraph.ArgotGraph(uidscore, pid, self.database, blast_prot, self.ident)
                    if pid not in self.output:
                        self.output[pid] = ThreadData.ThreadData(at.get_prot_clusters(), at.get_cluster())
            else:
                logging.error(f"ERROR: suck: {pid}")
        except Exception as e:
            logging.error(f"ERROR: {e}, {pid}")

    @staticmethod
    def get_domains(mapp):
        buffer = []
        for p in sorted(mapp.keys()):
            if len(mapp[p]) > 1:
                for ipr in sorted(list(mapp[p])):
                    buffer.append(ipr)
            else:
                buffer.extend(list(mapp[p]))
        return buffer
