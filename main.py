# Adventure game about a travelling artificer

import random
from copy import deepcopy

import fight
import resources
from gameClasses import *
from tkManager import *

w = createGameWindow()

notebook = createGameNotebook(w)
mainPage = createNotebookPage(notebook, " Main ")
characterPage = createNotebookPage(notebook, " Character ")
inventoryPage = createNotebookPage(notebook, " Inventory ")

#   Import resources
ENEMIES = resources.ENEMIES
WEAPONS = resources.WEAPONS
ROOM_DESCRIPTIONS = resources.ROOM_DESCRIPTIONS


class Player:
    def __init__(self, strength=1, lv=1, name="", maxHP=5):
        self.hp = maxHP
        self.strength = strength
        self.lv = lv
        self.inv = []
        self.invSize = 5
        self.weapon = Weapon("Hand-wraps", 0, "", 1, "Flimsy bandages that protect your fists while boxing. Not very "
                                                     "useful.")
        self.name = name
        self.maxHP = maxHP
        self.hasChestOpen = False
        self.currentRoom = Room("Starting Room")
        self.movementSpeed = 3.5
        self.xPos = None
        self.yPos = None

    def loseHealth(self, amount=1):
        self.hp -= amount
        updateCharacterPage()
        if self.hp <= 0:
            gameOver()


# Room functions

def describeRoom():
    clear(mainPage)
    Label(mainPage, text=plr.currentRoom.desc).grid()
    Button("Chest", openChest, mainPage).grid()
    Button("Door 1", buildRoom, mainPage).grid()
    Button("Door 2", buildRoom, mainPage).grid()
    Button("Door 3", buildRoom, mainPage).grid()


def buildRoom():
    room = Room(desc=ROOM_DESCRIPTIONS[random.randint(0, len(ROOM_DESCRIPTIONS) - 1)])
    room.enemy = deepcopy(ENEMIES[random.randint(0, len(ENEMIES) - 1)])
    room.chestContents.append(WEAPONS[random.randint(0, len(WEAPONS) - 1)])
    room.width = random.randint(3, 15)
    room.height = random.randint(5, 15)
    plr.currentRoom = room

    if random.randint(0, 5) == 1:
        encounterTrap()
    else:
        clear(mainPage)
        backButton = ("Continue", describeRoom)
        fight.main(mainPage, backButton, plr)


# Fight functions

def encounterTrap():
    clear(mainPage)
    Label(mainPage, text="You run into a trap and lose 1 health!").grid()
    plr.loseHealth(1)
    Button("Continue", describeRoom, mainPage).grid()


def fightEnemy():
    enemy = plr.currentRoom.enemy
    attackStrength = plr.strength + plr.weapon.strBonus
    clear(mainPage)
    Label(mainPage, text=f"You encounter {enemy.article} {enemy.name}!").grid()
    if attackStrength > enemy.strength:
        Label(mainPage,
              text=f"The {enemy.name} is weaker than you and you successfully defeat it!\nLevel up!").grid()
        plr.lv += 1
        updateCharacterPage()
        if plr.lv >= 10:
            win()

    elif attackStrength < enemy.strength:
        Label(mainPage,
              text=f"The {enemy.name} is stronger than you and you are thoroughly thrashed by it!").grid()
        plr.loseHealth(1)

    else:
        Label(mainPage,
              text=f"You and the {enemy.name} are equally strong and decide to call it a draw.").grid()

    Button("Details", lambda: battleDetails(enemy, attackStrength), mainPage).grid()
    Button("Continue", describeRoom, mainPage).grid()


def battleDetails(enemy, attackStrength):
    Label(mainPage,
          text=f"Your total attack power was {attackStrength} while you enemy's was {enemy.strength}.").grid()


# Inventory/Chest functions

def openChest():
    plr.hasChestOpen = True
    clear(mainPage)
    if len(plr.currentRoom.chestContents) > 0:
        for item in plr.currentRoom.chestContents:
            Button("- " + item.name, lambda i=item: [takeItem(i), openChest()], mainPage).grid()
    else:
        Label(mainPage, "This chest is empty").grid()
    Button("Back", lambda: [describeRoom(), updateInventoryPage()], mainPage).grid()


def takeItem(item):
    if plr.invSize > len(plr.inv):
        plr.inv.append(item)
        plr.currentRoom.chestContents.remove(item)
        updateInventoryPage()


def moveItem(item):
    if plr.hasChestOpen:
        plr.currentRoom.chestContents.append(item)
        plr.inv.remove(item)
        updateInventoryPage()
        openChest()
    else:
        clear(inventoryPage)
        Label(inventoryPage, "You don't seem to have a chest open. Do you want to throw away this item? (Note: Items "
                             "cannot be recovered once thrown away)").grid()
        f = ttk.Frame(inventoryPage)
        Button("Yes", lambda: throwItem(item), f).grid()
        Button("No", lambda: inspectItem(item), f).grid()
        f.grid()


def throwItem(item):
    plr.inv.remove(item)
    updateInventoryPage()


def inspectItem(item):
    clear(inventoryPage)
    Label(inventoryPage, item.name).grid()
    Label(inventoryPage, f"Attack bonus: {item.strBonus}").grid()
    Label(inventoryPage, item.desc).grid()
    Button("Equip", lambda: [updateInventoryPage(), equipItem(item)], inventoryPage).grid()
    Button("Put Away", lambda: moveItem(item), inventoryPage).grid()
    Button("Back", lambda: updateInventoryPage(), inventoryPage).grid()


def equipItem(item):
    plr.inv.remove(item)
    plr.inv.append(deepcopy(plr.weapon))
    plr.weapon = item
    updateCharacterPage()
    updateInventoryPage()


#   Page management functions

def updateCharacterPage():
    clear(characterPage)
    Label(characterPage, f"""
            {plr.name}
    ---------------------------
    Level:     {plr.lv}
    Weapon: {plr.weapon.name} (+{plr.weapon.strBonus})
    Hp:         {plr.hp}/{plr.maxHP}
    Str:        {plr.strength}
""", justify=tk.LEFT).grid()


def updateInventoryPage():
    clear(inventoryPage)
    plr.hasChestOpen = False
    Label(inventoryPage, text=f"{len(plr.inv)}/{plr.invSize}").grid()
    for item in plr.inv:
        Button(item.name, lambda i=item: inspectItem(i), inventoryPage).grid()


#   Win and Lose placeholder functions

def gameOver():
    notebook.hide(mainPage)
    notebook.hide(characterPage)
    notebook.hide(inventoryPage)
    Label(notebook, text="Game Over").grid()


def win():
    notebook.hide(mainPage)
    notebook.hide(characterPage)
    notebook.hide(inventoryPage)
    Label(w, text="You Win!").grid()


#   Start

def debug():
    plr.weapon = Weapon("Ultra Mega Cheater Sword", 9999, "a", 8, "This sword is only to be wielded by cheaters and debuggers")
    plr.movementSpeed = 10


def main():
    updateInventoryPage()
    updateCharacterPage()
    describeRoom()
    w.wait_window()


plr = Player()
debug()
main()