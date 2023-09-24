class Room:
    def __init__(self, desc="", enemy=None):
        self.desc = desc
        self.enemy = enemy
        self.chestContents = []
        self.width = 10
        self.height = 10


class Enemy:
    def __init__(self, name, strength, article, health, reach=3):
        self.name = name
        self.strength = strength
        self.article = article  # The article that precedes the enemy's name (ex: {A} rat approaches you)
        self.xPos = None
        self.yPos = None
        self.movementSpeed = 3
        self.health = health
        self.reach = reach


class Weapon:
    def __init__(self, name, strBonus, article, reach=1, desc=""):
        self.name = name
        self.strBonus = strBonus
        self.article = article  # The article that precedes the weapon's name (ex: You found {a} dagger)
        self.desc = desc
        self.reach = reach


class Rune:
    def __init__(self, name, runeId, image="placeholder.png"):
        self.name = name
        self.id = runeId
        self.image = image
        self.desc = "A stone tablet with a glowing engraving."


class Spell:
    def __init__(self, desc, spellFunction, fightDesc="", args=0):
        self.desc = desc
        self.spellFunction = spellFunction
        if fightDesc == "":
            fightDesc = desc
        self.fightDesc = fightDesc
        self.args = args

    def execute(self, args):
        return self.spellFunction(args)
