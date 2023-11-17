import math

import numpy as np

from miscFunctions import error, getDistance, Vector2
from resources import RUNES, SPELLS
from tkManager import *


class Fight:
    def __init__(self, w, frame, backCommand, plr):
        self.w = w
        self.frame = frame
        self.backButtonArgs = backCommand
        self.grid = []
        self.plr = plr
        self.room = plr.currentRoom
        self.enemy = self.room.enemy
        self.log = tk.Text(frame, height=1.5 * self.room.height, width=40, state="disabled")
        self.actionButtonFrame = ttk.Frame(frame)
        self.state = "starting"
        self.runeSlots = [RUNES[0], RUNES[0], RUNES[0]]
        self.temporaryFrame = None

    def setup(self):
        gridFrame = ttk.Frame(self.frame)
        gridFrame.grid(column=0, row=0)
        self.grid = createGrid(self.room, gridFrame)
        self.log.grid(column=1, row=0)
        self.actionButtonFrame.grid(column=0, row=1, columnspan=2)
        self.backButtonArgs += (self.actionButtonFrame,)
        self.state = "playerTurn"

    def getCell(self, pos):
        return self.grid[pos.x][pos.y]

    def updateActionButtons(self, newState=None, temporaryFrame=None):
        """
        Possible battle states:
              - "starting"     -> The fight is setting up
              - "playerTurn"   -> It's the player's turn and they are not in the middle of an action (all actions should be enabled)
              - "playerMoving" -> It's the player's turn and they are choosing where to move (only cancel move should be enabled)
              - "playerAiming" -> It's the player's turn and they are choosing where to aim (only cancel attack should be enabled)
              - "playerCasting"-> It's the player's turn and they are choosing what spell to cast (only cancel cast should be enabled)
              - "enemyTurn"    -> It's the player's turn (no actions should be enabled)
              - "battleWon"    -> The battle is won and only the continue button should be visible
        """

        #  Unbind keys
        w = self.w
        w.bind("<Control-a>", "break")
        w.bind("<Control-q>", "break")
        w.bind("<Control-w>", "break")
        w.bind("<Control-m>", "break")
        w.bind("<Control-e>", "break")
        w.bind("<space>", "break")

        if newState is not None and self.state != "gameOver":
            self.state = newState
        state = self.state
        clear(self.actionButtonFrame)
        if state == "starting":
            pass
        elif state == "playerTurn":
            attackButton = Button("Attack", lambda: showAttackSquares(self),
                                  self.actionButtonFrame)
            if self.plr.actions == 0:
                attackButton["state"] = tk.DISABLED
            else:
                w.bind("<Control-a>", lambda event: showAttackSquares(self))
                w.bind("<Control-q>", lambda event: showAttackSquares(self))
            attackButton.grid(column=0, row=0, padx=1)

            moveButton = Button("Move", lambda: moveAction(self), self.actionButtonFrame)
            if self.plr.movement < 1:
                moveButton["state"] = tk.DISABLED
            else:
                w.bind("<Control-w>", lambda event: moveAction(self))
            moveButton.grid(column=1, row=0, padx=1)

            magicButton = Button("Magic", lambda: magicAction(self), self.actionButtonFrame)
            if self.plr.actions == 0:
                magicButton["state"] = tk.DISABLED
            else:
                w.bind("<Control-m>", lambda event: magicAction(self))
                w.bind("<Control-e>", lambda event: magicAction(self))
            magicButton.grid(column=2, row=0, padx=1)

            Button("End Turn", lambda: enemyTurn(self), self.actionButtonFrame).grid(column=3, row=0, padx=1)
            w.bind("<space>", lambda event: enemyTurn(self))

        elif state == "playerMoving":
            Button("Cancel Move", lambda: [cancelMove(self, getCellsInReach(self, self.plr.movementSpeed, self.plr.pos, "walkable"))],
                   self.actionButtonFrame).grid()
            w.bind("<Control-w>", lambda event: [cancelMove(self, getCellsInReach(self, self.plr.movementSpeed, self.plr.pos, "walkable"))])
        elif state == "playerAiming":
            Button("Cancel Attack", lambda: [cancelAttack(self)], self.actionButtonFrame).grid()
            w.bind("<Control-a>", lambda event: cancelAttack(self))
            w.bind("<Control-q>", lambda event: cancelAttack(self))

        elif state == "playerCasting":
            Button("Cancel Cast", lambda: self.updateActionButtons("playerTurn"), self.actionButtonFrame).grid()
            w.bind("<Control-m>", lambda event: self.updateActionButtons("playerTurn"))
        elif state == "enemyTurn":
            pass
        elif state == "battleWon":
            out(self.log, "You Won!")
            checkEffects(self.plr, True)
            Button(*self.backButtonArgs).grid()
            self.plr.pos = Vector2(None, None)
        elif state == "gameOver":
            Label(self.frame, "Game Over!").grid()
        else:
            error(f"Error: Battle state ({state}) does not exist")
        if self.temporaryFrame is not None:
            clear(self.temporaryFrame)
        self.temporaryFrame = temporaryFrame


class GridButton(tk.Button):

    def __init__(self, parent, x, y):
        self.parent = parent
        self.pos = Vector2(x, y)
        self.width = 2
        self.inPlayerReachRange = False
        self.inEnemyReachRange = False
        self.command = None
        self.contents = []
        self.states = {
            "enemy": False,
            "walkable": True,
            "player": False,
            "": True
        }
        self.kwargs = {
            "width": self.width,
        }
        super().__init__(self.parent, **self.kwargs)

    def append(self, item):
        self.contents.append(item)

    def remove(self, item):
        self.contents.remove(item)

    def setColor(self, text):
        super().__init__(self.parent, background=text, command=self.cget("command"), **self.kwargs)
        self.grid(column=self.pos.x, row=self.pos.y)

    def setCommand(self, command):
        super().__init__(self.parent, background=self.cget("background"), command=command, **self.kwargs)
        self.grid(column=self.pos.x, row=self.pos.y)


def main(w, frame, backButton, plr):
    fight = Fight(w, frame, backButton, plr)
    fight.setup()
    movePlayer(fight, Vector2(fight.room.width - 1, fight.room.height - 1))
    moveEnemy(fight, Vector2(0, 0))
    plr.actions = plr.actionsPerTurn
    plr.movement = plr.movementSpeed
    out(fight.log, f"You encounter {fight.enemy.article} {fight.enemy.name}!")
    fight.updateActionButtons()


def createGrid(room, frame):
    grid = []
    for x in range(room.width):
        column = []
        for y in range(room.height):
            cell = GridButton(frame, x, y)
            cell.setColor("white")
            column.append(cell)
        grid.append(column)
    return grid


def enemyTurn(fight):
    enemy = fight.enemy
    plr = fight.plr
    fight.updateActionButtons("enemyTurn")
    moveTowardsPlayer(fight, getDesiredPos(fight))
    for _ in getCellsInReach(fight, enemy.reach, enemy.pos, "player"):
        attackPlayer(fight)
    checkEffects(fight)
    plr.actions = plr.actionsPerTurn
    plr.movement = plr.movementSpeed
    fight.updateActionButtons("playerTurn")


def checkEffects(fight, endBattle=False):
    plr = fight.plr
    for effect in plr.effects:
        if endBattle:
            out(fight.log, f"Your {effect.name} effect ends as the adrenaline leaves your veins.")
            effect.function(plr, False)
            plr.effects.remove(effect)
        if effect.duration > 0:
            effect.duration -= 1
            if not effect.duration:
                out(fight.log, effect.name + " fades.")
                effect.function(plr, False)
                plr.effects.remove(effect)


def attackPlayer(fight):
    plr = fight.plr
    log = fight.log
    enemy = fight.enemy
    plr.changeHealth(-np.clip(enemy.strength, None, plr.hp))
    out(log, f"The {enemy.name} attack you for {enemy.strength} damage. You now have {plr.hp} hp left.")


def getDesiredPos(fight):
    output = Vector2(0, 0)
    enemy = fight.enemy
    plr = fight.plr
    closestCell = fight.getCell(enemy.pos)
    for cell in getCellsInReach(fight, enemy.reach, enemy.pos):
        if cell.states["player"]:
            closestCells = [fight.getCell(plr.pos)]
            for c in getCellsInReach(fight, enemy.reach, plr.pos):
                if getDistance(plr.pos, c.pos) > getDistance(plr.pos, closestCells[0].pos):
                    closestCells.clear()
                    closestCells.append(c)
                elif getDistance(plr.pos, c.pos) == getDistance(plr.pos, closestCells[0].pos):
                    closestCells.append(c)
            closestCell = closestCells[0]

            for c in closestCells:
                if getDistance(enemy.pos, c.pos) < getDistance(enemy.pos, closestCell.pos):
                    closestCell = c
                output = closestCell.pos
            break
        if cell.states["walkable"] or cell.states["enemy"]:
            if getDistance(plr.pos, cell.pos) < getDistance(plr.pos, closestCell.pos):
                closestCell = cell
            diff = enemy.pos - closestCell.pos
            output = plr.pos + diff
    return output


def addRune(fight, rune):
    for i in range(len(fight.runeSlots)):
        if not fight.runeSlots[i].id:
            fight.runeSlots[i] = rune
            break
    magicAction(fight)


def removeRune(fight, index):
    fight.runeSlots[index] = RUNES[0]
    magicAction(fight)


def magicAction(fight):
    plr = fight.plr
    magicFrame = ttk.Frame(fight.frame)
    magicFrame.grid(column=0, row=2, columnspan=2)
    clear(magicFrame)
    fight.updateActionButtons("playerCasting", magicFrame)
    i = 0
    for rune in fight.runeSlots:
        RuneSlotImage(magicFrame, lambda index=i: removeRune(fight, index), rune.image, (75, 100)).grid(row=0, column=i)
        i += 1
    Button("Activate", lambda: castSpell(fight, magicFrame), magicFrame).grid(row=1, column=0, columnspan=len(fight.runeSlots))
    Label(magicFrame, "Your runes:").grid(row=2, column=0, columnspan=len(fight.runeSlots))
    if plr.runeInv:
        runesFrame = ttk.Frame(magicFrame)
        runesFrame.grid(column=0, row=2, columnspan=len(fight.runeSlots))
        for rune in plr.runeInv:
            Button(rune.name, lambda r=rune: addRune(fight, r), runesFrame).grid()
    else:
        Label(magicFrame, "You don't have any runes at the moment. Keep exploring to find some!").grid(row=3, column=0,
                                                                                                       columnspan=len(fight.runeSlots))


def castSpell(fight, magicFrame):
    fight.plr.actions -= 1
    fight.updateActionButtons("playerTurn")
    runeSlotIds = ""
    for rune in fight.runeSlots:
        if rune != RUNES[0]:
            runeSlotIds += str(rune.id) + ";"
    try:
        spell = SPELLS[runeSlotIds]
        outcome = spell.desc
    except KeyError:
        spell = SPELLS[""]
        outcome = "The runes glow for a second before the power fizzles out with a slight hissing sound."
    args = {
        "spell": spell,
        "fight": fight
    }
    if spell.useDesc:
        out(fight.log, outcome)
    executionOutput = spell.execute(args)
    if executionOutput:
        out(fight.log, executionOutput)
    if fight.enemy.health == 0:
        fight.plr.setPos(None, None)
        fight.updateActionButtons("battleWon")
    else:
        fight.updateActionButtons()
    clear(magicFrame)


def movePlayer(fight, pos):
    plr = fight.plr
    if plr.pos.x is not None:
        fight.getCell(plr.pos).setColor("white")
        fight.getCell(plr.pos).setCommand(None)
        fight.getCell(plr.pos).states["walkable"] = True
        fight.getCell(plr.pos).states["player"] = False
        # fight.getCell(plr.pos).remove(plr)
    plr.pos = pos
    fight.getCell(pos).setColor("blue")
    fight.getCell(pos).setCommand(lambda: moveAction(fight))
    fight.getCell(pos).states["walkable"] = False
    fight.getCell(pos).states["player"] = True
    fight.getCell(pos).append(plr)


def moveAction(fight):
    if fight.state == "playerAiming":
        cancelAttack(fight)
    fight.updateActionButtons("playerMoving")
    grid = fight.grid
    plr = fight.plr
    cellsInReach = getCellsInReach(fight, plr.movement, plr.pos, "walkable")
    fight.getCell(plr.pos).setCommand(lambda: cancelMove(fight, cellsInReach))
    for cell in cellsInReach:
        cell.setColor("red")
        cell.setCommand(lambda cellPos=cell.pos: [plr.setMovement(plr.movement - getDistance(plr.pos, cellPos)),
                                                  cancelMove(fight, cellsInReach), movePlayer(fight, cellPos)])
    if plr.pos.x:
        fight.w.bind("<Left>",
                     lambda event: [plr.setMovement(plr.movement - 1), cancelMove(fight, cellsInReach),
                                    movePlayer(fight, plr.pos - (1, 0))])
    if len(grid) > plr.pos.x + 1:
        fight.w.bind("<Right>",
                     lambda event: [plr.setMovement(plr.movement - 1), cancelMove(fight, cellsInReach),
                                    movePlayer(fight, plr.pos + (1, 0))])
    if plr.pos.y:
        fight.w.bind("<Up>",
                     lambda event: [plr.setMovement(plr.movement - 1), cancelMove(fight, cellsInReach),
                                    movePlayer(fight, plr.pos - (0, 1))])
    if len(grid[0]) > plr.pos.y + 1:
        fight.w.bind("<Down>",
                     lambda event: [plr.setMovement(plr.movement - 1), cancelMove(fight, cellsInReach),
                                    movePlayer(fight, plr.pos + (0, 1))])


def getCellsInReach(fight, reach, startPos, requirement=""):
    grid = fight.grid
    room = fight.room
    cells = []
    for column in grid[np.clip(startPos.x - math.ceil(reach), 0, None):np.clip(startPos.x + math.ceil(reach) + 1, None, room.width)]:
        for cell in column[np.clip(startPos.y - math.ceil(reach), 0, None):np.clip(startPos.y + math.ceil(reach) + 1, None, room.height)]:
            if (getDistance(startPos, cell.pos) <= reach) and cell.states[requirement]:
                cells.append(cell)
    return cells


def cancelMove(fight, cellsInReach):
    plr = fight.plr
    fight.updateActionButtons("playerTurn")
    fight.w.bind("<Left>", "break")
    fight.w.bind("<Right>", "break")
    fight.w.bind("<Up>", "break")
    fight.w.bind("<Down>", "break")
    for cell in cellsInReach:
        cell.setColor("white")
        cell.setCommand(None)
    fight.getCell(plr.pos).setCommand(lambda: moveAction(fight))


def cancelAttack(fight):
    plr = fight.plr
    fight.updateActionButtons("playerTurn")
    emptyAttackSquares = getCellsInReach(fight, fight.plr.weapon.reach, plr.pos, "walkable")
    attackSquaresWithEnemy = getCellsInReach(fight, fight.plr.weapon.reach, fight.plr.pos, "enemy")
    for cell in emptyAttackSquares:
        cell.setColor("white")
        cell.setCommand(None)
    for cell in attackSquaresWithEnemy:
        cell.setColor("green")
        cell.setCommand(None)
    fight.getCell(plr.pos).setCommand(lambda: moveAction(fight))


def moveTowardsPlayer(fight, targetPos):
    grid = fight.grid
    enemy = fight.enemy
    if targetPos != enemy.pos:
        fight.getCell(enemy.pos).setColor("white")
        fight.getCell(enemy.pos).setCommand(None)
        fight.getCell(enemy.pos).states["walkable"] = True
        fight.getCell(enemy.pos).states["enemy"] = False

        targetCell = grid[0][0]
        for cell in getCellsInReach(fight, enemy.movementSpeed, enemy.pos, "walkable"):
            if getDistance(targetPos, cell.pos) < getDistance(targetPos, targetCell.pos):
                targetCell = cell

        moveEnemy(fight, targetCell.pos)


def moveEnemy(fight, pos):
    enemy = fight.enemy
    grid = fight.grid
    enemy.pos = pos
    fight.getCell(pos).setColor("green")
    fight.getCell(pos).states["walkable"] = False
    fight.getCell(pos).states["enemy"] = True


def showAttackSquares(fight):
    fight.updateActionButtons("playerAiming")
    plr = fight.plr
    cells = getCellsInReach(fight, plr.weapon.reach, plr.pos, "walkable")
    enemyCells = getCellsInReach(fight, plr.weapon.reach, plr.pos, "enemy")
    for cell in enemyCells:
        cell.setColor("SeaGreen3")
        cell.setCommand(lambda: [attackEnemy(fight)])

    for cell in cells:
        cell.setColor("orange")


def attackEnemy(fight):
    plr = fight.plr
    log = fight.log
    plr.actions -= 1
    cancelAttack(fight)
    enemy = plr.currentRoom.enemy
    attackPower = plr.strength + plr.weapon.strBonus
    damage = np.clip(attackPower, None, enemy.health)
    out(log,
        f"You attack the {enemy.name} for {attackPower} damage. They now have {enemy.health - damage} hp left.")
    enemy.loseHealth(fight, damage)


def out(log, text):
    log.configure(state="normal")
    log.insert(tk.END, text + "\n\n")
    log.see("end")
    log.configure(state="disabled")

# def gameOver(fight):
#     plr = fight.plr
#     out(fight.log, "You died! Game Over")
#     fight.grid[plr.xPos][plr.yPos].setCommand(None)
#     fight.updateActionButtons("gameOver")
