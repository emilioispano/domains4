#!/usr/bin/python3

import os
import math
import random
import subprocess
import networkx as nx
from networkx.readwrite import gml

from Settings import Settings
from RetrieveProteins import RetrieveProteins
import Utilities as util
import Blast8
import LoadInRam
import SSNetwork


class ArgotGraph:
    def __init__(self, uidscore, pid, database, blast_prot, thread_id):
        self.settings = Settings.init()
        self.filein = None
        self.retparam = None
        self.work_dir = self.settings.work_dir
        self.iternum = 0
        self.sg = None
        self.database = database
        self.buffer = set()
        self.randomseed = None
        self.cluster = {}
        self.prot_clusters = {}

        self.uids = []
        self.cluster = {}
        self.randomseed = self.get_random_seed()
        self.retparam = RetrieveProteins.init(True)
        self.repr_prot_ids = []
        self.repr_score = {}

        self.outfile = None

        self.work_dir = self.settings.get_work_dir() + "/" + str(thread_id)
        file_in_clust = self.work_dir + "/" + pid + "_" + self.randomseed + ".fa.tmp"
        self.filein = self.work_dir + "/" + pid + "_" + self.randomseed + ".fa"
        fileq = self.filein + "_" + str(thread_id) + ".q"
        filenwscore = self.filein + ".nwscore"
        tmp_clust = os.path.join(self.work_dir, "mmclust_tmp")
        out_clust = self.work_dir + "/" + pid + "_output"

        util.create_directory(self.work_dir)

        if blast_prot is not None and len(blast_prot) > 0:
            for prot in blast_prot:
                uidscore.pop(prot, None)

        if len(uidscore.keys()) > self.settings.get_max_seqs():
            uids = util.sort_uids(uidscore)
        else:
            uids = list(uidscore.keys())

        self.retparam.write_prot_file(uids, file_in_clust, pid, database)

        self.run_mmlin_clust(file_in_clust, out_clust, tmp_clust)
        self.prot_clusters = util.read_clustering_data(out_clust + "_cluster.tsv", self.database, self.settings)

        if len(self.prot_clusters.keys()) > 0:
            for reprId in self.prot_clusters.keys():
                self.repr_score[reprId] = uidscore[reprId]

            util.delete_file(file_in_clust)

            repr_rot_ids = list(self.prot_clusters.keys())
            self.retparam.write_prot_file_repr(repr_rot_ids, self.filein, pid, database)

            with open(filenwscore, "w") as outputnwscore:
                for p in uids:
                    outputnwscore.write(p + "\t" + str(uidscore[p]) + "\n")

            if not os.path.exists(tmp_clust):
                os.makedirs(tmp_clust)

            with open(self.settings.get_input_fasta(), "rb") as rafinput, open(fileq, "w") as output:
                self.retparam.write_query(rafinput, output, pid)

            if self.settings.is_rom_used():
                outfile = self.filein + "_" + str(thread_id) + ".aln"
                self.run_glsearch_alignment(fileq, self.filein, outfile)
                b8 = Blast8.Blast8(outfile, self.settings.get_similarity_thr(), self.sg)
            else:
                lir = LoadInRam.LoadInRam()
                self.run_glsearch_alignment_lir(fileq, self.filein, lir)
                b8 = Blast8.Blast8(lir, self.settings.get_similarity_thr(), self.sg)
                lir.close()

            self.sg = b8.get_graph()
            targets = b8.get_targets()

            if self.settings.get_max_iteration() > 0 and len(targets) > 0:
                dirr = os.path.join(self.work_dir, str(self.randomseed))
                os.mkdir(dirr)
                self.deep_search(dirr, targets, self.database, self.settings)
                for uid in self.modularity(self.sg):
                    score = 0.0
                    graphpath = nx.shortest_path(self.sg, source=uid, target=pid, weight='weight')
                    ledge = [self.sg[u][v]['weight'] for u, v in zip(graphpath, graphpath[1:])]
                    for edge in ledge:
                        score += self.to_score(edge)
                    score /= pow(2, len(ledge) - 1)
                    self.cluster[uid] = score
            else:
                if pid in self.sg:
                    for edge in self.sg.edges(pid):
                        self.cluster[self.sg[edge[1]]] = self.to_score((self.sg[edge]))

        if not self.settings.is_rom_used():
            os.remove(fileq)

            if self.outfile is not None:
                os.remove(self.outfile)

            os.remove(self.filein)

    def deep_search(self, dirr, targets, database, settings):
        deeptargets = set()
        global iternum
        iternum += 1

        lir = None
        if not settings.is_rom_used():
            lir = LoadInRam.LoadInRam()

        for tid in targets:
            tidq = os.path.join(dirr, tid)
            self.retparam.write_single_prot(tid, tidq, database)
            tmp = os.path.join(self.work_dir, "mmseq_tmp")
            if not os.path.exists(tmp):
                os.mkdir(tmp)

            if settings.is_rom_used():
                outfile = os.path.join(dirr, tid + ".aln")
                self.run_mmsearch_alignment(tidq, self.filein, outfile, tmp)
                b8 = Blast8.Blast8(outfile, settings.get_similarity_thr(), self.sg)
            else:
                self.run_mmsearch_alignment_lir(tidq, self.filein, lir, tmp)
                b8 = Blast8.Blast8(lir, settings.get_similarity_thr(), self.sg)
                if lir:
                    lir.reset()

            self.sg = b8.get_graph()

            for uid in b8.get_targets():
                if uid not in self.buffer:
                    deeptargets.add(uid)

            self.buffer.update(deeptargets)

        if iternum <= settings.get_max_iteration() and deeptargets:
            if settings.isPrintgml():
                self.print_gml(iternum)

            self.deep_search(dirr, deeptargets, database, settings)

        if lir:
            lir.close()

        return self.buffer

    @staticmethod
    def modularity(pid, sg):
        ssn = SSNetwork.SSNetwork(pid, sg)
        ids = ssn.get_cluster()
        tmp = set(ids)
        if pid in tmp:
            tmp.remove(pid)
        return tmp

    @staticmethod
    def to_score(evalue):
        if evalue == 0.0:
            return 300

        score = -math.log10(evalue)

        if score > 300:
            return 300

        return score

    def run_cmd(self, listargs, lir=None):
        pb = subprocess.Popen(listargs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        if lir is None:
            log = os.path.join(self.work_dir, "log")

            with open(log, "wb") as f:
                for line in pb.stdout:
                    f.write(line)
        else:
            builder = []

            while True:
                line = pb.stdout.readline().decode()
                if not line:
                    break
                builder.append(line)

            lir.writeBytes(''.join(builder).encode())

        exitvalue = pb.wait()

        return exitvalue == 0

    def run_glsearch_alignment(self, fileq, filein, outfile, num_threads=1):
        selfalignargs = [
            self.settings.get_glsearch_alignment_cmd(),
            fileq,
            filein,
            "-m",
            "8",
            "-T",
            str(num_threads),
            "-O",
            outfile
        ]
        return self.run_cmd(selfalignargs)

    def run_glsearch_alignment_lir(self, fileq, filein, lir, num_threads=1):
        selfalignargs = [
            self.settings.get_glsearch_alignment_cmd(),
            "-m",
            "8",
            "-T",
            str(num_threads),
            fileq,
            filein
        ]
        return self.run_cmd(selfalignargs, lir)

    def run_mmsearch_alignment(self, fileq, filein, outfile, tmp_dir, num_threads=1):
        selfalignargs = [
            self.settings.get_mmsearch_alignment_cmd(),
            "easy-search",
            "--search-type",
            "1",
            "--threads",
            str(num_threads),
            fileq,
            filein,
            outfile,
            tmp_dir
        ]
        b = self.run_cmd(selfalignargs)
        if b:
            util.delete_directory(tmp_dir)
        return b

    def run_mmsearch_alignment_lir(self, fileq, filein, lir, tmp_dir, num_threads=1):
        selfalignargs = [
            self.settings.get_mmsearch_alignment_cmd(),
            "easy-search",
            "--search-type",
            "1",
            "--threads",
            str(num_threads),
            fileq,
            filein,
            tmp_dir
        ]
        b = self.run_cmd(selfalignargs, lir)
        if b:
            util.delete_directory(tmp_dir)
        return b

    def run_mmlin_clust(self, filein, outfile, tmp_dir, num_threads=1):
        selfalignargs = [
            self.settings.get_mmsearch_alignment_cmd(),
            "easy-linclust",
            "--min-seq-id",
            "0.90",
            "--threads",
            str(num_threads),
            filein,
            outfile,
            tmp_dir
        ]
        b = self.run_cmd(selfalignargs)
        if b:
            util.delete_directory(tmp_dir)
        return b

    def get_random_seed(self):
        saltchars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        salt = "".join(random.choice(saltchars) for _ in range(18))
        return salt

    def get_graph(self):
        return self.sg

    def print_gml(self, count):
        with open(f"{self.randomseed}_{count}.gml", "w") as out:
            gmlexp = gml.GmlExporter()
            gmlexp.add_graph(self.sg)
            out.write(gmlexp.dumps())

    def get_cluster(self):
        return self.cluster

    def get_prot_clusters(self):
        return self.prot_clusters
