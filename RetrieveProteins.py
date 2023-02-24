#!/usr/bin/python3

import sys
from pymongo import MongoClient
from Settings import Settings

class RetrieveProteins:
    instance = None

    def __init__(self, mongo=False):
        self.inputmap = {}
        self.offset = {}
        self.settings = Settings()
        self.db_input = self.settings.get_input_fasta()
        self.db_file = self.settings.get_fasta_db()
        self.read_index()
        if not mongo:
            self.read_uniprot_index()

    @staticmethod
    def init(mongo=False):
        if RetrieveProteins.instance is None:
            RetrieveProteins.instance = RetrieveProteins(mongo)
        return RetrieveProteins.instance

    def read_index(self):
        index_file_input = self.db_input + ".fai"
        with open(index_file_input, "r") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                data = line.split("\t")
                pid = data[0]
                self.inputmap[pid] = int(data[1])

    def read_uniprot_index(self):
        index_file = self.db_file + ".fai"
        with open(index_file, "r") as fr:
            for line in fr:
                if line.startswith("#"):
                    continue
                line = line.strip()
                data = line.split("\t")
                self.offset[data[0]] = int(data[1])

    def write_query(self, rafinput, output, pid):
        lenseq = 0
        if pid not in self.inputmap:
            print("ERROR: no such protein in index: " + pid, file=sys.stderr)
            sys.exit(1)
        offs = self.inputmap[pid]
        rafinput.seek(offs)
        line = rafinput.readline().decode().strip()
        output.write(">" + pid + "\n")
        while line:
            line = line.strip()
            if line.startswith(">"):
                break
            elif len(line) == 0:
                continue
            lenseq += len(line)
            output.write(line + "\n")
            line = rafinput.readline().decode().strip()

        rafinput.seek(self.inputmap[pid])
        line = rafinput.readline()
        output.write(line.decode('utf-8'))

        return lenseq + len(line)

    def write_target(self, raf, output, uid, lenn, offs):
        minlen = 0
        maxlen = 0
        perc = self.settings.get_target_perc_len()
        sb = ""
        if perc > 0:
            minlen = int(lenn - lenn * perc)
            maxlen = int(lenn + lenn * perc)

        if offs != -1:
            raf.seek(offs)
            line = raf.readline()
            if line:
                while not line.startswith(">"):
                    line = raf.readline()
                    if not line:
                        return False
                sb += line.decode('utf-8').strip() + "\n"
                len_line = len(line)
                while len(line) == len_line:
                    line = raf.readline()
                    sb += line.decode('utf-8').strip() + "\n"
                if minlen == 0 or minlen <= len(sb) <= maxlen:
                    output.write(">" + uid + "\n")
                    output.write(sb)
                    return True

        return False

    def write_prot_file(self, uids, outfile, pid, database):
        count = 1
        with open(outfile, 'w') as output, open(self.db_file, 'rb') as raf, open(self.db_input, 'rb') as rafinput:
            len_line = self.write_query(rafinput, output, pid)
            collection = database[Settings.init().getCollectionUNIPROTX()]
            for uid in uids:
                cursor = collection.find({"uid": uid})
                if cursor.count() > 0:
                    doc = cursor.next()
                    if doc:
                        offs = -1
                        res = doc.get("index")
                        if isinstance(res, int):
                            offs = res
                        if count <= self.settings.get_maxseqs():
                            if self.write_target(raf, output, uid, len_line, offs):
                                count += 1
                        else:
                            break

    def write_prot_file_repr(self, uids, outfile, pid, database):
        count = 1

        with open(self.db_file, 'rb') as raf:
            with open(self.db_input, 'rb') as rafinput:
                output = open(outfile, 'w')
                lenn = self.write_query(rafinput, output, pid)
                collection = database.get_collection(Settings.init().getCollectionUNIPROTX())
                for uid in uids:
                    cursor = collection.find({"uid": uid}).limit(1)
                    if cursor.count() > 0:
                        doc = cursor[0]
                        if not doc.empty:
                            offs = -1
                            res = doc.get("index")
                            if isinstance(res, int):
                                offs = res
                            elif isinstance(res, float):
                                offs = int(res)

                            if count <= self.settings.get_max_num_repr():
                                if self.write_target(raf, output, uid, lenn, offs):
                                    count += 1
                            else:
                                break

                output.close()

    def write_single_prot(self, uid, outfile, database):
        with open(self.db_file, 'rb') as raf:
            output = open(outfile, 'w')
            collection = database.get_collection(Settings.init().getCollectionUNIPROTX())
            cursor = collection.find({"uid": uid}).limit(1)
            if cursor.count() > 0:
                doc = cursor[0]
                if not doc.empty:
                    offs = -1
                    res = doc.get("index")
                    if isinstance(res, int):
                        offs = res
                    elif isinstance(res, float):
                        offs = int(res)

                    self.write_target(raf, output, uid, 0, offs)

            output.close()
