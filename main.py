# Adventure game about a travelling artificer

from copy import deepcopy
import random

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
        self.weapon = Weapon("Hand-wraps", 0, "", "Flimsy bandages that protect your fists while boxing. Not very "
                                                  "useful.")
        self.name = name
        self.maxHP = maxHP
        self.hasChestOpen = False
        self.currentRoom = Room("Starting Room")
        self.movementSpeed = 3
        self.xPos = 0
        self.yPos = 0

    def loseHealth(self, amount=1):
        self.hp -= amount
        updateCharacterPage()
        if self.hp <= 0:
            gameOver()


# Room functions

def describeRoom():
    clear(mainPage)
    Label(mainPage, text=plr.currentRoom.desc).pack()
    Button("Chest", openChest, mainPage).pack()
    Button("Door 1", buildRoom, mainPage).pack()
    Button("Door 2", buildRoom, mainPage).pack()
    Button("Door 3", buildRoom, mainPage).pack()


def buildRoom():
    room = Room(desc=ROOM_DESCRIPTIONS[random.randint(0, len(ROOM_DESCRIPTIONS) - 1)])
    room.enemy = deepcopy(ENEMIES[random.randint(0, len(ENEMIES) - 1)])
    room.chestContents.append(WEAPONS[random.randint(0, len(WEAPONS) - 1)])
    room.chestContents.append(WEAPONS[random.randint(0, len(WEAPONS) - 1)])
    plr.currentRoom = room

    if random.randint(0, 999) == 1:
        encounterTrap()
    else:
        fight.main(mainPage, plr)


# Fight functions

def encounterTrap():
    clear(mainPage)
    Label(mainPage, text="You run into a trap and lose 1 health!").pack()
    plr.loseHealth(1)
    Button("Continue", describeRoom, mainPage).pack()


def fightEnemy():
    enemy = plr.currentRoom.enemy
    attackStrength = plr.strength + plr.weapon.strBonus
    clear(mainPage)
    Label(mainPage, text=f"You encounter {enemy.article} {enemy.name}!").pack()
    if attackStrength > enemy.strength:
        Label(mainPage,
              text=f"The {enemy.name} is weaker than you and you successfully defeat it!\nLevel up!").pack()
        plr.lv += 1
        updateCharacterPage()
        if plr.lv >= 10:
            win()

    elif attackStrength < enemy.strength:
        Label(mainPage,
              text=f"The {enemy.name} is stronger than you and you are thoroughly thrashed by it!").pack()
        plr.loseHealth(1)

    else:
        Label(mainPage,
              text=f"You and the {enemy.name} are equally strong and decide to call it a draw.").pack()

    Button("Details", lambda: battleDetails(enemy, attackStrength), mainPage).pack()
    Button("Continue", describeRoom, mainPage).pack()


def battleDetails(enemy, attackStrength):
    Label(mainPage,
          text=f"Your total attack power was {attackStrength} while you enemy's was {enemy.strength}.").pack()


# Inventory/Chest functions

def openChest():
    plr.hasChestOpen = True
    clear(mainPage)
    if len(plr.currentRoom.chestContents) > 0:
        for item in plr.currentRoom.chestContents:
            Button("- " + item.name, lambda i=item: [takeItem(i), openChest()], mainPage).pack()
    else:
        Label(mainPage, "This chest is empty").pack()
    Button("Back", lambda: [describeRoom(), updateInventoryPage()], mainPage).pack()


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
                             "cannot be recovered once thrown away)").pack()
        f = ttk.Frame(inventoryPage)
        Button("Yes", lambda: throwItem(item), f).pack()
        Button("No", lambda: inspectItem(item), f).pack()
        f.pack()


def throwItem(item):
    plr.inv.remove(item)
    updateInventoryPage()


def inspectItem(item):
    clear(inventoryPage)
    Label(inventoryPage, item.name).pack()
    Label(inventoryPage, f"Attack bonus: {item.strBonus}").pack()
    Label(inventoryPage, item.desc).pack()
    Button("Equip", lambda: [updateInventoryPage(), equipItem(item)], inventoryPage).pack()
    Button("Put Away", lambda: moveItem(item), inventoryPage).pack()
    Button("Back", lambda: updateInventoryPage(), inventoryPage).pack()


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
""", justify=tk.LEFT).pack()


def updateInventoryPage():
    clear(inventoryPage)
    plr.hasChestOpen = False
    Label(inventoryPage, text=f"{len(plr.inv)}/{plr.invSize}").pack()
    for item in plr.inv:
        Button(item.name, lambda i=item: inspectItem(i), inventoryPage).pack()


#   Win and Lose placeholder functions

def gameOver():
    notebook.hide(mainPage)
    notebook.hide(characterPage)
    notebook.hide(inventoryPage)
    Label(notebook, text="Game Over").pack()


def win():
    notebook.hide(mainPage)
    notebook.hide(characterPage)
    notebook.hide(inventoryPage)
    Label(w, text="You Win!").pack()


#   Start

def debug():
    plr.currentRoom.chestContents.append(
        Weapon("Ultra Mega Cheater Sword", 100, "a", "This sword is only to be wielded by cheaters and debuggers")
    )


def main():
    updateInventoryPage()
    updateCharacterPage()
    describeRoom()
    w.wait_window()


plr = Player()
debug()
main()
