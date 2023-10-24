import numpy as np

from miscFunctions import Vector2


class Room:
    def __init__(self, desc="", enemy=None):
        self.desc = desc
        self.enemy = enemy
        self.chestContents = []
        self.width = 10
        self.height = 10


class Enemy:
    def __init__(self, name, strength, article, health, cr=0, reach=3):
        self.name = name
        self.strength = strength
        self.article = article  # The article that precedes the enemy's name (ex: {A} rat approaches you)
        self.pos = Vector2(None, None)
        self.movementSpeed = 3
        self.health = health
        self.cr = cr
        self.reach = reach

    def loseHealth(self, fight, amount=1, printWin=True):
        plr = fight.plr
        self.health -= np.clip(amount, None, self.health)
        if self.health == 0 and printWin:
            plr.xPos = None
            plr.yPos = None
            fight.updateActionButtons("battleWon")

    def __repr__(self):
        return "{" + self.name + "}"


class Weapon:
    def __init__(self, name, strBonus, article, itemRating=0, reach=1, desc=""):
        self.name = name
        self.strBonus = strBonus
        self.article = article  # The article that precedes the weapon's name (ex: You found {a} dagger)
        self.ir = itemRating
        self.desc = desc
        self.reach = reach


class Rune:
    def __init__(self, name, runeId, itemRating=0, image="placeholder.png"):
        self.name = name
        self.id = runeId
        self.ir = itemRating
        self.image = image
        self.desc = "A stone tablet with a glowing engraving."


class Spell:
    def __init__(self, desc, spellFunction, useNormalDescInFight=True):
        self.desc = desc
        self.spellFunction = spellFunction
        self.useDesc = useNormalDescInFight

    def execute(self, args):
        return self.spellFunction(args)
