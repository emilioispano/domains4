import NodeFreq


class GraphNode(NodeFreq):
    def __init__(self):
        super().__init__()
        self.weight = 0.0

    def set_weight(self, w):
        self.weight = w

    def get_weight(self):
        return self.weight

    def clean(self):
        super().clean()
        self.weight = 0.0
