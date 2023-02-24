#!/usr/bin/python3

from typing import List, Dict
from Settings import Settings


class NW:
    def __init__(self, x: List[str], y: List[str], weigthscore: Dict[str, float]):
        setting = Settings.init()
        self.x = x
        self.y = y
        self.weigthscore = weigthscore
        self.gapscore = setting.get_gap_SCORE()
        self.matchscore = setting.get_match_SCORE()
        self.mismatchscore = setting.get_mismatch_SCORE()
        self.xlen = len(x)
        self.ylen = len(y)
        self.score_array = [[0.0] * (self.xlen + 1) for _ in range(self.ylen + 1)]
        self.fill_score_array()

    def fill_score_array(self) -> None:
        # Fill the top row and left column:
        for col in range(self.xlen + 1):
            self.score_array[0][col] = self.gapscore * col
        for row in range(self.ylen + 1):
            self.score_array[row][0] = self.gapscore * row

        # Now fill in the rest of the array:
        for row in range(1, self.ylen + 1):
            for col in range(1, self.xlen + 1):
                if self.x[col - 1] == self.y[row - 1]:
                    northwest = self.score_array[row - 1][col - 1] + self.matchscore * (2 * self.weigthscore[self.x[col - 1]])
                else:
                    northwest = self.score_array[row - 1][col - 1] + self.mismatchscore * (self.weigthscore[self.y[row - 1]] + self.weigthscore[self.x[col - 1]])
                west = self.score_array[row][col - 1] + self.gapscore
                north = self.score_array[row - 1][col] + self.gapscore
                best = northwest
                if north > best:
                    best = north
                if west > best:
                    best = west
                self.score_array[row][col] = best

    def get_similarity(self) -> float:
        sim = 0.0
        if self.ylen == 0 and self.xlen == 0:
            return sim

        score = self.score_array[self.ylen][self.xlen]
        smn = self.xlen * self.gapscore + self.ylen * self.gapscore
        selfx = 0.0
        for dom in self.x:
            selfx += self.matchscore * self.weigthscore[dom] * 2
        selfy = 0.0
        for dom in self.y:
            selfy += self.matchscore * self.weigthscore[dom] * 2
        sim = min((score - smn)/(selfx - smn), (score - smn)/(selfy - smn))
        return sim
