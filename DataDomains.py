#!/usr/bin/python3

from AlignmentResults import AlignmentResults
from NW import NW
import Settings
import math


class DataDomains:
    def __init__(self, database, qdoms, uid=None):
        if not uid is None:
            self.database = database
            self.weightscore = {}
            self.aligners = AlignmentResults()
            tdoms = self.get_prot_doms(uid)
            self.weigth_score(tdoms)
            self.weigth_score(qdoms)
            nw = NW(qdoms, tdoms, self.weigthscore)
            self.aligners.add_result(uid, nw.get_similarity())
        else:
            self.database = database
            self.weigthscore = {}
            self.aligners = AlignmentResults()
            self.exit = False
            self.weigth_score(qdoms)
            seedoms = self.select_seed_dom(qdoms)
            inter = self.intersection(seedoms)

            for uid in inter:
                tdoms = self.get_prot_doms(uid)
                self.weigth_score(tdoms)
                sdom = True

                if len(seedoms) == 1:
                    q = qdoms[0]
                    for tdom in tdoms:
                        if q != tdom:
                            sdom = False
                            break

                if sdom and qdoms[0] == tdoms[0]:
                    self.aligners.add_result(uid, 1.0)
                else:
                    nw = NW(qdoms, tdoms, self.weigthscore)
                    self.aligners.add_result(uid, nw.get_similarity())

    def select_seed_dom(self, qdoms):
        numd = 1

        if len(qdoms) > 1:
            numd = len(qdoms) // 2

        seed = []
        map = {}
        domainfreq = []
        collection = self.database[Settings.Settings().init().get_collection_frequences()]

        for ipr in qdoms:
            freq = collection.find_one({"ipr": ipr})["freq"]
            map[freq] = ipr
            seed.append(freq)

        alg = Settings.Settings().init().get_seed_dom()

        if alg == "minfreq":
            seed.sort()
        elif alg == "maxfreq":
            seed.sort(reverse=True)
        elif alg == "all":
            numd = len(seed)

        for d in seed[:numd]:
            domainfreq.append(map[d])
        return domainfreq

    def intersection(self, doms):
        inter = set()
        list_ = []
        collection = self.database[Settings.Settings().init().get_collection_interpro()]

        for ipr in doms:
            buffer = set()
            for doc in collection.find({"ipr": ipr}):
                buffer.add(doc["uid"])
            list_.append(buffer)

        inter = list_[0]

        if len(list_) > 1:
            for i in range(1, len(list_)):
                inter &= list_[i]
        return inter

    def get_prot_doms(self, uid):
        mapp = {}
        collection = self.database.get_collection(Settings.Settings().init().get_collection_interpro())

        for doc in collection.find({"uid": uid}):
            ipr = doc["ipr"]
            pos_list = doc["pos"]

            for p in pos_list:
                if p in mapp:
                    mapp[p].add(ipr)
                else:
                    mapp[p] = {ipr}

        return [",".join(mapp[p]) for p in sorted(mapp.keys())]

    def weigth_score(self, doms):
        collection = self.database[Settings.Settings().init().get_collection_frequences()]

        for ipr in doms:
            if ipr not in self.weightscore:
                cursor = collection.find({"ipr": ipr})
                if cursor.count() > 0:
                    doc = cursor.next()
                    invfreq = 1 / doc["freq"]
                    weight = math.log(invfreq) / math.log(2)
                    self.weightscore[ipr] = weight
                else:
                    self.exit = True

    def get_exit(self):
        return self.exit

    def get_results(self):
        return self.aligners
