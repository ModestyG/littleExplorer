from math import sqrt


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if (self.x, self.y) == other:
            return True
        elif type(other) == Vector2:
            if (other.x, other.y) == (self.x, self.y):
                return True
        return False

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __add__(self, other):
        if type(other) == Vector2:
            return Vector2(other.x + self.x, other.y + self.y)
        elif type(other) == tuple and len(other) == 2:
            return Vector2(other[0] + self.x, other[1] + self.y)
        else:
            error(f"Cannot add {other} to Vector2")

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if type(other) == Vector2:
            return Vector2(other.x - self.x, other.y - self.y)
        elif type(other) == tuple and len(other) == 2:
            return Vector2(self.x - other[0], self.y - other[1])
        else:
            error(f"Cannot subtract {other} from Vector2")

    def __rsub__(self, other):
        return -(self - other)

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def set(self, x, y):
        self.x = x
        self.y = y


class BiDict(dict):
    def __init__(self, content):
        inv_content = {v: k for k, v in content.items()}
        super().__init__({**content, **inv_content})

    def __invert__(self):


def getOrientation(var1, var2):  # Returns 1, 0, or -1
    """
    Checks whether var1 is larger or smaller than var2\n
    -1: smaller\n
    0: equal\n
    1: larger\n
    :param var1: float
    :param var2: float
    :return: -1, 0, or 1
    """
    if var1 < var2:
        return -1
    elif var1 == var2:
        return 0
    else:
        return 1


def getDistance(pos1, pos2):
    """
    Calculates the distance between two points
    :param pos1: Vector2(x, y)
    :param pos2: Vector2(x, y)
    :return: distance: float
    """
    if type(pos1) == tuple:
        return sqrt((pos1[0] - pos2[0] ** 2) + (pos1[1] - pos2[1] ** 2))
    else:
        return sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2)


def error(text):
    print(f"\033[91m{text}\033[0m")
