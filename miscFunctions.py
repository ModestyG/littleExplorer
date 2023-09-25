from math import sqrt


def getOrientation(var1, var2):  # Returns 1, 0, or -1
    if var1 < var2:
        return -1
    elif var1 == var2:
        return 0
    else:
        return 1


def getDistance(pos1, pos2):
    return sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)
