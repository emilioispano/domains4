#!/usr/bin/python3

import Settings


class NW:
    def __init__(self, x, y, weightscore):
        setting = Settings.Settings().init()
        self.x = x
        self.y = y
        self.weight_score = weightscore
        self.gap_score = setting.get_gap_score()
        self.match_score = setting.get_match_score()
        self.mismatch_score = setting.get_mismatch_score()
        self.x_len = len(x)
        self.y_len = len(y)
        self.score_array = [[0.0] * (self.x_len + 1) for _ in range(self.y_len + 1)]
        self.fill_score_array()

    def fill_score_array(self):
        # Fill the top row and left column:
        for col in range(self.x_len + 1):
            self.score_array[0][col] = self.gap_score * col
        for row in range(self.y_len + 1):
            self.score_array[row][0] = self.gap_score * row

        # Now fill in the rest of the array:
        for row in range(1, self.y_len + 1):
            for col in range(1, self.x_len + 1):
                if self.x[col - 1] == self.y[row - 1]:
                    northwest = self.score_array[row - 1][col - 1] + self.match_score * (2 * self.weight_score[self.x[col - 1]])
                else:
                    northwest = self.score_array[row - 1][col - 1] + self.mismatch_score * (self.weight_score[self.y[row - 1]] + self.weight_score[self.x[col - 1]])
                west = self.score_array[row][col - 1] + self.gap_score
                north = self.score_array[row - 1][col] + self.gap_score
                best = northwest
                if north > best:
                    best = north
                if west > best:
                    best = west
                self.score_array[row][col] = best

    def get_similarity(self):
        sim = 0.0
        if self.y_len == 0 and self.x_len == 0:
            return sim

        score = self.score_array[self.y_len][self.x_len]
        smn = self.x_len * self.gap_score + self.y_len * self.gap_score
        selfx = 0.0
        for dom in self.x:
            selfx += self.match_score * self.weight_score[dom] * 2
        selfy = 0.0
        for dom in self.y:
            selfy += self.match_score * self.weight_score[dom] * 2
        sim = min((score - smn)/(selfx - smn), (score - smn)/(selfy - smn))
        return sim
