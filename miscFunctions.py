from math import sqrt


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
    :param pos1: tuple(x, y)
    :param pos2: tuple(x, y)
    :return: distance: float
    """
    return sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)
