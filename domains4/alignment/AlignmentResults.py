from typing import Dict
from concurrent.futures import ThreadPoolExecutor


class AlignmentResults:
    def __init__(self):
        self.map: Dict[str, float] = {}

    def get_map(self) -> Dict[str, float]:
        return self.map

    def add_result(self, uid: str, sim: float) -> None:
        self.map[uid] = sim

    def get_uid_over(self, thr: float) -> Dict[str, float]:
        tmp: Dict[str, float] = {}
        for uid, sim in self.map.items():
            if sim >= thr:
                tmp[uid] = sim
        return tmp

    def get_uid_over_concurrent(self, thr: float) -> Dict[str, float]:
        tmp: Dict[str, float] = {}
        with ThreadPoolExecutor() as executor:
            for uid, sim in executor.map(lambda x: (x[0], x[1]), self.map.items()):
                if sim >= thr:
                    tmp[uid] = sim
        return tmp

    def get_uid(self) -> Dict[str, float]:
        return self.map
