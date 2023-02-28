#!/usr/bin/python3

from typing import Dict
from concurrent.futures import ThreadPoolExecutor


class AlignmentResults:
    def __init__(self):
        self.map = {}

    def get_map(self):
        return self.map

    def add_result(self, uid, sim):
        self.map[uid] = sim

    def get_uid_over(self, thr):
        tmp = {}
        for uid, sim in self.map.items():
            if sim >= thr:
                tmp[uid] = sim
        return tmp

    def get_uid_over_concurrent(self, thr):
        tmp = {}
        with ThreadPoolExecutor() as executor:
            for uid, sim in executor.map(lambda x: (x[0], x[1]), self.map.items()):
                if sim >= thr:
                    tmp[uid] = sim
        return tmp

    def get_uid(self):
        return self.map
