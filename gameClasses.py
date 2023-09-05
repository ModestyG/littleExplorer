
class Room:
    def __init__(self, desc="", enemy=None):
        self.desc = desc
        self.enemy = enemy
        self.chestContents = []
        self.width = 10
        self.height = 10


class Enemy:
    def __init__(self, name, strength, article):
        self.name = name
        self.strength = strength
        self.article = article  # The article that precedes the enemy's name (ex: {A} rat approaches you)
        self.xPos = None
        self.yPos = None
        self.movementSpeed = 3


class Weapon:
    def __init__(self, name, strBonus, article, desc=""):
        self.name = name
        self.strBonus = strBonus
        self.article = article  # The article that precedes the weapon's name (ex: You found {a} dagger)
        self.desc = desc
