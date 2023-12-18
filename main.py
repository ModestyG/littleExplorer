# Adventure game about a travelling artificer

import random
from copy import deepcopy

import fight
import resources
from gameClasses import *
from logManager import entryExists, addEntry, createLogbookPage
from miscFunctions import Vector2, BiDict
from tkManager import *

#   Import resources
ENEMIES = resources.ENEMIES

WEAPONS = resources.WEAPONS

ROOM_DESCRIPTIONS = resources.ROOM_DESCRIPTIONS

RUNES = resources.RUNES

POTIONS = resources.POTIONS

SPELLS = resources.SPELLS

ITEMS = BiDict({**WEAPONS, **RUNES, **POTIONS})
del ITEMS[30]  # Removes empty rune from list of items you can get in chests.

#   Setup game UI
w = createGameWindow()

notebook = createGameNotebook(w)
mainPage = createNotebookPage(notebook, " Main ")
characterPage = createNotebookPage(notebook, " Character ")
inventoryPage = createNotebookPage(notebook, " Inventory ")
magicPage = createNotebookPage(notebook, " Magic ")
logbookPage = createNotebookPage(notebook, " Logbook ")

runeSlots = [RUNES[30], RUNES[30], RUNES[30]]


class Player:
    def __init__(self, strength=0, lv=1, name="", maxHP=10):
        self.hp = maxHP
        self.strength = strength
        self.lv = lv
        self.inv = []
        self.runeInv = []
        self.invSize = 5
        self.weapon = Weapon("Hand-wraps", 0, 1, "", 0, 1, "Flimsy bandages that protect your fists while boxing. Not very "
                                                           "useful.")
        self.name = name
        self.maxHP = maxHP
        self.hasChestOpen = False
        self.currentRoom = Room("Starting Room")
        self.actionsPerTurn = 1
        self.movementSpeed = 3.5
        self.pos = Vector2(None, None)
        self.effects = []

        self.actions = 0
        self.movement = self.movementSpeed
        self.runeSlots = [RUNES[30], RUNES[30], RUNES[30]]

        self.levelingSpeed = 2

        self.gatheredEntries = [Option([], "Monsters"), Option([Option([], "Weapons"), Option([], "Potions"), Option([], "Runes")],
                                                               "Items"), Option([], "Spells")]
        self.reachBoost = 0

        self.bindFuncs = [bindTabs, unbindTabs]
        #  Borde denna ligga här? Absolut inte men det är alldeles för sent på natten för att jag
        #  ska orka bry mig så konstiga funktioner som inte har någonting med spelaren att göra får hamna i spelar objektet. Fight me.

    def changeHealth(self, amount):
        self.hp += amount
        updateCharacterPage()
        if self.hp <= 0:
            gameOver()

    def setMovement(self, amount):
        self.movement = amount

    def setPos(self, x, y):
        self.pos.x = x
        self.pos.y = y


# Room functions

def describeRoom():
    w.bind("<Control-f>", "break")
    bindMain()
    updateMagicPage()
    clear(mainPage)
    Label(mainPage, text=plr.currentRoom.desc).grid()
    Button("Chest", openChest, mainPage).grid()
    Button("Door 1", buildRoom, mainPage).grid()
    Button("Door 2", buildRoom, mainPage).grid()
    Button("Door 3", buildRoom, mainPage).grid()


def buildRoom():
    unbindMain()
    room = Room(desc=ROOM_DESCRIPTIONS[random.randint(1, len(ROOM_DESCRIPTIONS))])
    room.width = random.randint(3, 15)
    room.height = random.randint(5, 15)
    summonEnemy(room)
    fillChest(room)
    plr.currentRoom = room
    plr.lv += plr.levelingSpeed

    if random.randint(0, 20) == 1:
        encounterTrap()
    else:
        clear(mainPage)
        clear(magicPage)
        Label(magicPage, "Cannot experiment while in battle.").grid()
        backButton = ("Continue", describeRoom)
        fight.main(w, mainPage, backButton, plr, logbookPage)


# Fight functions

def summonEnemy(room):
    weights = []
    for enemy in ENEMIES.invert():
        weight = 100 / ((enemy.cr - plr.lv) ** 2 + 1)
        if enemy.cr > plr.lv:
            weight /= 2
        weights.append(weight)
    room.enemy = deepcopy(*random.choices(ENEMIES.getList(), weights))
    if not entryExists(ENEMIES[room.enemy.id], plr):
        addEntry(ENEMIES[room.enemy.id], plr, logbookPage, "Monsters")


def encounterTrap():
    clear(mainPage)
    Label(mainPage, text="You run into a trap and lose 1 health!").grid()
    plr.changeHealth(-1)
    Button("Continue", describeRoom, mainPage).grid()


# Inventory/Chest functions

def fillChest(room):
    points = plr.lv
    while points >= 2:
        item = ITEMS.getRandomItem()
        if item.ir <= points:
            points -= item.ir
            room.chestContents.append(item)


def openChest():
    plr.hasChestOpen = True
    w.bind("<Control-f>", lambda event: [describeRoom(), updateInventoryPage()])
    clear(mainPage)
    if len(plr.currentRoom.chestContents) > 0:
        for item in plr.currentRoom.chestContents:
            Button("- " + item.name, lambda i=item: [takeItem(i), openChest()], mainPage).grid()
    else:
        Label(mainPage, "This chest is empty").grid()
    w.bind("<space>", lambda event: takeAll())
    Button("Back", lambda: [describeRoom(), updateInventoryPage()], mainPage).grid()


def takeAll():
    for i in range(len(plr.currentRoom.chestContents)):
        takeItem(plr.currentRoom.chestContents[0])
    openChest()


def takeItem(item):
    if not entryExists(item, plr):
        if type(item) == Potion:
            addEntry(item, plr, logbookPage, "Items/Potions")
        elif type(item) == Weapon:
            addEntry(item, plr, logbookPage, "Items/Weapons")
        elif type(item) == Rune:
            addEntry(item, plr, logbookPage, "Items/Runes")
    if plr.invSize > len(plr.inv):
        if type(item) == Rune:
            plr.runeInv.append(item)
            updateMagicPage()
        else:
            plr.inv.append(item)
            updateInventoryPage()
        plr.currentRoom.chestContents.remove(item)


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
    Label(inventoryPage, item.desc).grid()
    if type(item) == Weapon:
        Label(inventoryPage, f"Attack bonus: {item.strBonus}").grid()
        Label(inventoryPage, f"Range: {item.reach}").grid()
        Button("Equip", lambda: [updateInventoryPage(), equipItem(item)], inventoryPage).grid()
    if type(item) == Potion:
        Label(inventoryPage, f"Effect: {item.effectDesc}")
        Button("Drink", lambda: [item.drink(plr), plr.inv.remove(item), updateInventoryPage()], inventoryPage).grid()
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


def updateMagicPage():
    clear(magicPage)
    magicFrame = ttk.Frame(magicPage)
    magicFrame.grid()
    i = 0
    for rune in runeSlots:
        RuneSlotImage(magicFrame, lambda index=i: removeRune(index), rune.image).grid(row=0, column=i)
        i += 1
    Button("Activate", activateExperiment, magicFrame).grid(row=1, column=0, columnspan=len(runeSlots))
    Label(magicFrame, "Your runes:").grid(row=2, column=0, columnspan=len(runeSlots))
    if plr.runeInv:
        for rune in plr.runeInv:
            Button(rune.name, lambda r=rune: addRune(r), magicFrame).grid()
    else:
        Label(magicFrame, "You don't have any runes at the moment. Keep exploring to find some!").grid(row=3, column=0,
                                                                                                       columnspan=len(runeSlots))


# Magic functions
def activateExperiment():
    runeSlotIds = ""
    for rune in runeSlots:
        if rune != RUNES[30]:
            runeSlotIds += str(rune.id) + ";"
    try:
        spell = SPELLS[runeSlotIds]
        title = spell.name
        outcome = spell.desc
        spell.hasExperimented = True
        if not entryExists(spell, plr):
            addEntry(spell, plr, logbookPage, "Spells")
    except KeyError:
        outcome = "The runes glow for a second before the power fizzles out with a slight hissing sound."
        title = "Fail"

    clear(magicPage)
    Label(magicPage, title).grid()
    Label(magicPage, outcome).grid()
    Button("Continue", updateMagicPage, magicPage).grid()


def addRune(rune):
    for i in range(len(runeSlots)):
        if runeSlots[i].id == 30:
            runeSlots[i] = rune
            break
    updateMagicPage()


def removeRune(index):
    runeSlots[index] = RUNES[30]
    updateMagicPage()


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


#   Keybinds
def bindTabs():
    w.bind("q", lambda event: notebook.select(mainPage))
    w.bind("w", lambda event: notebook.select(characterPage))
    w.bind("c", lambda event: notebook.select(characterPage))
    w.bind("e", lambda event: notebook.select(inventoryPage))
    w.bind("i", lambda event: notebook.select(inventoryPage))
    w.bind("r", lambda event: notebook.select(magicPage))
    w.bind("m", lambda event: notebook.select(magicPage))
    w.bind("t", lambda event: notebook.select(logbookPage))
    w.bind("l", lambda event: notebook.select(logbookPage))


def unbindTabs():
    w.bind("q", "break")
    w.bind("w", "break")
    w.bind("c", "break")
    w.bind("e", "break")
    w.bind("i", "break")
    w.bind("r", "break")
    w.bind("m", "break")
    w.bind("t", "break")
    w.bind("l", "break")


def bindMain():
    w.bind("<Control-f>", lambda event: openChest())
    w.bind("<Control-Key-1>", lambda event: buildRoom())
    w.bind("<Control-Key-2>", lambda event: buildRoom())
    w.bind("<Control-Key-3>", lambda event: buildRoom())
    w.bind("<Escape>", lambda event: w.destroy())


def unbindMain():
    w.bind("<Control-f>", "break")
    w.bind("<space>", "break")
    w.bind("<Control-Key-1>", "break")
    w.bind("<Control-Key-2>", "break")
    w.bind("<Control-Key-3>", "break")


#   Start

def debug():
    plr.weapon = Weapon("Ultra Mega Cheater Sword", 666, strBonus=999, article="a", reach=8,
                        desc="This sword is only to be wielded by cheaters and debuggers")
    plr.movementSpeed = 5
    plr.maxHP = 999
    plr.hp = plr.maxHP
    plr.currentRoom.chestContents.append(random.choice(list(WEAPONS.values())))
    plr.currentRoom.chestContents.append(random.choice(list(RUNES.values())))
    plr.currentRoom.chestContents.append(RUNES[31])
    plr.currentRoom.chestContents.append(POTIONS[28])


def main():
    bindTabs()
    bindMain()
    updateInventoryPage()
    updateCharacterPage()
    createLogbookPage(logbookPage, plr)
    describeRoom()
    w.wait_window()


plr = Player()
#  debug()
main()
