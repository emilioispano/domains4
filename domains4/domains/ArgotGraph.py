import os
import math
import random
from typing import List, Set
import subprocess
import networkx as nx
from networkx.readwrite import gml

from utils.Settings import Settings
from utils.RetrieveProteins import RetrieveProteins
import utils.Utilities as util
from parsers.Blast8 import Blast8
from utils.LoadInRam import LoadInRam
from utils.SSNetwork import SSNetwork


class ArgotGraph:
    def __init__(self, uidscore, pid, database, blast_prot, thread_id):
        self.settings = Settings.init()
        self.filein = None
        self.retparam = None
        self.workdir = self.settings.workdir
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

        self.workDir = self.settings.get_work_dir() + "/" + str(thread_id)
        fileInClust = self.workDir + "/" + pid + "_" + self.randomseed + ".fa.tmp"
        self.filein = self.workDir + "/" + pid + "_" + self.randomseed + ".fa"
        fileq = self.filein + "_" + str(thread_id) + ".q"
        filenwscore = self.filein + ".nwscore"
        tmpClust = os.path.join(self.workDir, "mmclust_tmp")
        outClust = self.workDir + "/" + pid + "_output"

        util.create_directory(self.workDir)

        if blast_prot is not None and len(blast_prot) > 0:
            for prot in blast_prot:
                uidscore.pop(prot, None)

        if len(uidscore.keys()) > self.settings.get_max_seqs():
            uids = util.sort_uids(uidscore)
        else:
            uids = list(uidscore.keys())

        self.retparam.write_prot_file(uids, fileInClust, pid, database)

        self.run_mmlin_clust(fileInClust, outClust, tmpClust)
        self.protClusters = util.read_clustering_data(outClust + "_cluster.tsv", self.database, self.settings)

        if len(self.protClusters.keys()) > 0:
            for reprId in self.protClusters.keys():
                self.repr_score[reprId] = uidscore[reprId]

            util.delete_file(fileInClust)

            reprProtIds = list(self.protClusters.keys())
            self.retparam.write_prot_file_repr(reprProtIds, self.filein, pid, database)

            with open(filenwscore, "w") as outputnwscore:
                for p in uids:
                    outputnwscore.write(p + "\t" + str(uidscore[p]) + "\n")

            if not os.path.exists(tmpClust):
                os.makedirs(tmpClust)

            with open(self.settings.get_input_fasta(), "rb") as rafinput, open(fileq, "w") as output:
                self.retparam.write_query(rafinput, output, pid)

            if self.settings.is_rom_used():
                outfile = self.filein + "_" + str(thread_id) + ".aln"
                self.run_glsearch_alignment(fileq, self.filein, outfile)
                b8 = Blast8(outfile, self.settings.get_similarity_thr(), self.sg)
            else:
                lir = LoadInRam()
                self.run_glsearch_alignment_lir(fileq, self.filein, lir)
                b8 = Blast8(lir, self.settings.get_similarity_thr(), self.sg)
                lir.close()

            self.sg = b8.get_graph()
            targets = b8.get_targets()

            if self.settings.get_max_iteration() > 0 and len(targets) > 0:
                dir = os.path.join(self.workdir, str(self.randomseed))
                os.mkdir(dir)
                self.deep_search(dir, targets, self.database, self.settings)
                for uid in self.modularity(pid, self.sg):
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

    def deep_search(self, dir: str, targets: Set[str], database: str, settings) -> Set[str]:
        deeptargets = set()
        global iternum
        iternum += 1

        lir = None
        if not settings.isRomUsed():
            lir = LoadInRam()

        for tid in targets:
            tidq = os.path.join(dir, tid)
            self.retparam.writeSingleProt(tid, tidq, database)
            tmp = os.path.join(self.workDir, "mmseq_tmp")
            if not os.path.exists(tmp):
                os.mkdir(tmp)

            if settings.isRomUsed():
                outfile = os.path.join(dir, tid + ".aln")
                self.run_mmsearch_alignment(tidq, self.filein, outfile, tmp)
                b8 = Blast8(outfile, settings.getSimilarityTHR(), self.sg)
            else:
                self.run_mmsearch_alignment_lir(tidq, self.filein, lir, tmp)
                b8 = Blast8(lir, settings.getSimilarityTHR(), self.sg)
                if lir:
                    lir.reset()

            self.sg = b8.get_graph()

            for uid in b8.get_targets():
                if uid not in self.buffer:
                    deeptargets.add(uid)

            self.buffer.update(deeptargets)

        if iternum <= settings.getMaxITERATION() and deeptargets:
            if settings.isPrintgml():
                self.print_gml(iternum)

            self.deep_search(dir, deeptargets, database, settings)

        if lir:
            lir.close()

        return self.buffer

    def modularity(self, pid: str, sg) -> Set[str]:
        ssn = SSNetwork(pid, sg)
        ids = ssn.get_cluster()
        tmp = set(ids)
        if pid in tmp:
            tmp.remove(pid)
        return tmp

    def to_score(self, evalue: float) -> float:
        if evalue == 0.0:
            return 300

        score = -math.log10(evalue)

        if score > 300:
            return 300

        return score

    def run_cmd(self, listargs: List[str], lir=None) -> bool:
        pb = subprocess.Popen(listargs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        if lir is None:
            log = os.path.join(self.workDir, "log")

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

    def run_glsearch_alignment(self, fileq: str, filein: str, outfile: str, num_threads=1) -> bool:
        selfalignargs = [
            self.settings.getGLSearchAlignmentCMD(),
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

    def run_glsearch_alignment_lir(self, fileq: str, filein: str, lir, num_threads=1) -> bool:
        selfalignargs = [
            self.settings.getGLSearchAlignmentCMD(),
            "-m",
            "8",
            "-T",
            str(num_threads),
            fileq,
            filein
        ]
        return self.run_cmd(selfalignargs, lir)

    def run_mmsearch_alignment(self, fileq: str, filein: str, outfile: str, tmp_dir: str, num_threads=1) -> bool:
        selfalignargs = [
            self.settings.getMMSearchAlignmentCMD(),
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

    def run_mmsearch_alignment_lir(self, fileq: str, filein: str, lir, tmp_dir: str, num_threads=1) -> bool:
        selfalignargs = [
            self.settings.getMMSearchAlignmentCMD(),
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

    def run_mmlin_clust(self, filein: str, outfile: str, tmp_dir: str, num_threads=1) -> bool:
        selfalignargs = [
            self.settings.getMMSearchAlignmentCMD(),
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

    def get_random_seed(self) -> str:
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
        return self.protClusters
