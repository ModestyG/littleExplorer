# Adventure game about a travelling artificer

import random
import tkinter.font
import tkinter.simpledialog
from copy import deepcopy

import fight
import resources
from gameClasses import *
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
del ITEMS[15]  # Removes empty rune from list of items you can get in chests.

#   Setup game UI
w = createGameWindow()

notebook = createGameNotebook(w)
mainPage = createNotebookPage(notebook, " Main ")
characterPage = createNotebookPage(notebook, " Character ")
inventoryPage = createNotebookPage(notebook, " Inventory ")
magicPage = createNotebookPage(notebook, " Magic ")
logbookPage = createNotebookPage(notebook, " Logbook ")

runeSlots = [RUNES[15], RUNES[15], RUNES[15]]


class Player:
    def __init__(self, strength=1, lv=1, name="", maxHP=10):
        self.hp = maxHP
        self.strength = strength
        self.lv = lv
        self.inv = []
        self.runeInv = []
        self.invSize = 5
        self.weapon = Weapon("Hand-wraps", 0, "", 0, 1, "Flimsy bandages that protect your fists while boxing. Not very "
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
        self.runeSlots = [RUNES[15], RUNES[15], RUNES[15]]

        self.levelingSpeed = 2

        self.gatheredEntries = [Option([], "Monsters"), Option([], "Potions")]

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
        fight.main(w, mainPage, backButton, plr)


# Fight functions

def summonEnemy(room):
    weights = []
    for enemy in ENEMIES.invert():
        weight = 100 / ((enemy.cr - plr.lv) ** 2 + 1)
        if enemy.cr > plr.lv:
            weight /= 2
        weights.append(weight)
    room.enemy = deepcopy(*random.choices(ENEMIES.getList(), weights))
    addEntry(ENEMIES[room.enemy.id], "/Monsters/")


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


def createLogbookPage():
    clear(logbookPage)
    topMenu = tk.Frame(logbookPage, pady=5, padx=5, bg="gray85", highlightthickness=2)
    topMenu.grid(column=0, row=0, columnspan=2, sticky="nsew")
    Button("Add Entry", lambda: addEntry(Entry()), topMenu).grid(column=0, row=0)
    tabFrame = tk.Frame(logbookPage, bg="gray85", highlightbackground="gray70", highlightthickness=2, pady=5, padx=5)
    tabFrame.grid(column=0, row=1, sticky="n")
    tabFrame.columnconfigure(0)
    infoFrame = tk.Frame(logbookPage, bg="gray85", highlightbackground="gray70", highlightthickness=2, pady=5, padx=5, height=275,
                         width=350)
    infoFrame.grid_propagate(False)
    infoFrame.grid(column=1, row=1, sticky="n")
    infoFrame.columnconfigure(1, minsize=0)
    myscrollbar = tk.Scrollbar(infoFrame, orient="vertical")
    myscrollbar.grid(sticky="e")
    updateLogbookTabs(tabFrame, infoFrame)
    updateLogbookInfo(tabFrame, infoFrame)


def updateLogbookTabs(frame, infoFrame):
    clear(frame)
    openOption(frame, infoFrame)


def updateLogbookInfo(tabFrame, frame, chosen=None):
    clear(frame)
    if chosen is None:
        testLabel = Label(frame, "Logbook Frontpage", anchor=tk.CENTER, width=30)
        testLabel.columnconfigure(0, weight=1)
        testLabel.grid()
    else:
        Label(frame, chosen.name, width=30, anchor=tk.CENTER).grid()
        if type(chosen) == Enemy:
            Label(frame, f"Strength: {chosen.strength}").grid()
            Label(frame, f"Health: {chosen.health}").grid()
            Label(frame, f"Reach: {chosen.reach}").grid()
        elif type(chosen) == Entry:
            for part in chosen.content:
                if type(part) == str:
                    tk.Label(frame, text=part).grid()
            Button("Add Text", lambda: [chosen.content.append("New Text"), updateLogbookInfo(tabFrame, frame, chosen)], frame).grid()
        Button("Change Name", lambda: changeName(chosen, tabFrame, frame), frame).grid()


# Magic functions
def activateExperiment():
    runeSlotIds = ""
    for rune in runeSlots:
        if rune != RUNES[15]:
            runeSlotIds += str(rune.id) + ";"
    try:
        outcome = SPELLS[runeSlotIds].desc
    except KeyError:
        outcome = "The runes glow for a second before the power fizzles out with a slight hissing sound."

    clear(magicPage)
    Label(magicPage, outcome).grid()
    Button("Continue", updateMagicPage, magicPage).grid()


def addRune(rune):
    for i in range(len(runeSlots)):
        if not runeSlots[i].id:
            runeSlots[i] = rune
            break
    updateMagicPage()


def removeRune(index):
    runeSlots[index] = RUNES[15]
    updateMagicPage()


# Logbook functions

def openOption(frame, infoFrame, parentOption=None):
    if parentOption is None:
        parentOption = Option(plr.gatheredEntries, opened=True)
    for option in parentOption.thing:
        if type(option) == Option:
            tk.Button(text=option.name, command=lambda op=option: openEntry(op, frame, infoFrame), master=frame, bg="gray80",
                      font=tkinter.font.Font(family="Arial", size=14, weight="bold"), width=15).grid(sticky="w")
            if option.opened:
                openOption(frame, infoFrame, option)
        else:
            tk.Button(text=option.name, command=lambda op=option: openEntry(op, frame, infoFrame), master=frame,
                      bg="gray85", font=tkinter.font.Font(
                    family="Arial", size=13), width=18).grid(sticky="w")


def openEntry(option, tabFrame, infoFrame):
    if type(option) == Option:
        option.opened = not bool(option.opened)
        updateLogbookTabs(tabFrame, infoFrame)
    else:
        updateLogbookInfo(tabFrame, infoFrame, option)


def addEntry(entry, target="/"):
    targetList = target.split("/")
    parentThing = plr.gatheredEntries
    for name in targetList:
        for option in parentThing:
            if option.name == name:
                parentThing = option.thing
                break
    parentThing.append(entry)
    createLogbookPage()


def changeName(target, tabFrame, infoFrame):
    target.name = (tkinter.simpledialog.askstring("Change Name", "Please enter the new name"))
    updateLogbookInfo(tabFrame, infoFrame, target)
    updateLogbookTabs(tabFrame, infoFrame)


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

def keyPressed(e):
    if e.char == "q":
        notebook.select(mainPage)
    elif e.char == "w" or e.char == "c":
        notebook.select(characterPage)
    elif e.char == "e" or e.char == "i":
        notebook.select(inventoryPage)
    elif e.char == "r" or e.char == "m":
        notebook.select(magicPage)


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
    plr.weapon = Weapon("Ultra Mega Cheater Sword", strBonus=999, article="a", reach=8,
                        desc="This sword is only to be wielded by cheaters and debuggers")
    plr.movementSpeed = 5
    plr.maxHP = 999
    plr.hp = plr.maxHP
    plr.runeInv.append(RUNES[2])
    plr.currentRoom.chestContents.append(WEAPONS[random.randint(0, len(WEAPONS) - 1)])
    plr.currentRoom.chestContents.append(RUNES[random.randint(1, len(RUNES) - 1)])
    plr.currentRoom.chestContents.append(POTIONS[4])


def main():
    w.bind("<Key>", keyPressed)
    bindMain()
    updateInventoryPage()
    updateCharacterPage()
    createLogbookPage()
    describeRoom()
    w.wait_window()


plr = Player()
# debug()
main()
