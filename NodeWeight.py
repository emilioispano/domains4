import NodeFreq
from decimal import Decimal


class NodeWeight(NodeFreq.NodeFreq()):
    def __init__(self):
        super().__init__()
        self.weight = 0
        self.zscore = -10

    def set_weight(self, weight):
        self.weight = weight

    def get_weight(self):
        return self.weight

    def get_round_weight(self, round_to):
        if round_to < 0:
            round_to = 0

        bd = Decimal(self.weight)
        bd = bd.quantize(Decimal('1.' + '0' * round_to), rounding='ROUND_HALF_UP')
        w = bd.to_eng_string()
        return float(w)

    def add_weight(self, w):
        self.weight += w

    def get_round_zscore(self, round_to):
        if round_to < 0:
            round_to = 0

        bd = Decimal(self.zscore)
        bd = bd.quantize(Decimal('1.' + '0' * round_to), rounding='ROUND_HALF_UP')
        z = bd.to_eng_string()
        return float(z)

    def clean(self):
        super().clean()
        self.weight = 0
        self.zscore = -10
