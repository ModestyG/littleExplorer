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
    def __init__(self, name, id, strength, article, health, reach=3, movement=3, cr=1):
        self.name = name
        self.id = id
        self.strength = strength
        self.article = article  # The article that precedes the enemy's name (ex: {A} rat approaches you)
        self.pos = Vector2(None, None)
        self.movementSpeed = movement
        self.health = health
        self.cr = cr
        self.reach = reach
        self.content = []  # For logbook

    def loseHealth(self, fight, amount=1, printWin=True):
        plr = fight.plr
        self.health -= np.clip(amount, None, self.health)
        if self.health == 0 and printWin:
            plr.xPos = None
            plr.yPos = None
            fight.updateActionButtons("battleWon")

    def __repr__(self):
        return "{" + self.name + "}"


class Entry:
    def __init__(self):
        self.name = "New Entry"
        self.path = "/"
        self.content = [TextBox, TextBox]


class TextBox:
    def __init__(self):
        self.content = "New Text"


class Item:
    def __init__(self, name, article, itemRating, desc, id):
        self.name = name
        self.article = article
        self.ir = itemRating
        self.desc = desc
        self.id = id
        self.content = []  # For logbook

    def __repr__(self):
        return "{" + self.name + "}"


class Weapon(Item):
    def __init__(self, name, id, strBonus, article, itemRating=0, reach=1, desc=""):
        self.strBonus = strBonus
        self.reach = reach
        super().__init__(name, article, itemRating, desc, id)


class Rune(Item):
    def __init__(self, name, id, itemRating=0, image="placeholder.png"):
        self.id = id
        self.image = image
        super().__init__(name, "a", itemRating, "A stone tablet with a glowing engraving.", id)


class Effect:
    def __init__(self, name, function, duration):
        self.name = name
        self.duration = duration
        self.function = function


class Potion(Item):
    def __init__(self, name, id, article, effectName, function, itemRating, desc, effectDesc, duration=None, strength=1):
        self.effect = Effect(effectName, function, duration)
        self.effectDesc = effectDesc
        super().__init__(name, article, itemRating, desc, id)

    def drink(self, plr):
        if self.effect.duration is not None:
            plr.effects.append(self.effect)
        self.effect.function(plr)


class Spell:
    def __init__(self, id, desc, spellFunction, useNormalDescInFight=True):
        self.name = "Unnamed Spell"
        self.desc = desc
        self.spellFunction = spellFunction
        self.useDesc = useNormalDescInFight
        self.history = []
        self.hasExperimented = False
        self.id = id
        self.content = []  # For logbook

    def execute(self, args):
        return self.spellFunction(args)


class spellHistoryInstance:
    def __init__(self, target, resultDesc, distance):
        self.target = target
        self.desc = resultDesc
        self.distance = distance


class Option:
    def __init__(self, thing, name=None, opened=False):
        self.thing = thing
        self.opened = opened
        self.name = name
        self.path = "/"
        self.content = []  # Specifically content for front page. Not the same as "thing" which is where child tabs are placed
