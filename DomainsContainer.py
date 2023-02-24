#!/usr/bin/python3

import pickle


class DomainsContainer:
    def __init__(self):
        self.map = {}
        self.uidmap = []
        self.tmpuid = ""
        self.position = -1

    def add_values(self, ipr, uid, start):
        if self.tmpuid != uid:
            self.position += 1
            self.uidmap.insert(self.position, uid)
            self.tmpuid = uid

        if ipr in self.map:
            ht = self.map[ipr]
            if self.position in ht:
                ht[self.position].append(start)
            else:
                starts = [start]
                ht[self.position] = starts
        else:
            ht = {}
            starts = [start]
            ht[self.position] = starts
            self.map[ipr] = ht

    def get_uid_with_ipr(self, ipr):
        ht = {}
        iprdata = self.map.get(ipr)

        for i in iprdata.keys():
            ht[self.uidmap[i]] = iprdata[i]

        return ht

    def get_uid(self, i):
        return self.uidmap[i]

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
