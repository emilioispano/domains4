class Tuple:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        if other is None:
            return False
        if other is self:
            return True
        if not isinstance(other, Tuple):
            return False
        return other.x == self.x and other.y == self.y

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + (0 if self.x is None else hash(self.x))
        result = prime * result + (0 if self.y is None else hash(self.y))
        return result
