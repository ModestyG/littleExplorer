import math

import numpy
import numpy as np

from tkManager import *


class Fight:
    def __init__(self, frame, backCommand, plr):
        self.frame = frame
        self.backButtonArgs = backCommand
        self.grid = []
        self.plr = plr
        self.room = plr.currentRoom
        self.enemy = self.room.enemy
        self.log = tk.Text(frame, height=1.5 * self.room.height, width=40, state="disabled")
        self.actionButtonFrame = ttk.Frame(frame)
        self.state = "starting"

    #       Possible battle states:
    #          - "starting"     -> The fight is setting up
    #          - "playerTurn"   -> It's the player's turn and they are not in the middle of an action (all actions should be enabled)
    #          - "playerMoving" -> It's the player's turn and they are choosing where to move (only cancel move should be enabled)
    #          - "playerAiming" -> It's the player's turn and they are choosing where to aim (only cancel attack should be enabled)
    #          - "enemyTurn"    -> It's the player's turn (no actions should be enabled)
    #          - "battleWon"    -> The battle is won and only the continue button should be visible

    def setup(self):
        gridFrame = ttk.Frame(self.frame)
        gridFrame.grid()
        self.grid = createGrid(self.room, gridFrame)
        self.log.grid(column=1, row=0)
        self.actionButtonFrame.grid(column=0, row=self.room.height, columnspan=2)
        self.backButtonArgs += (self.actionButtonFrame,)
        self.state = "playerTurn"

    def updateActionButtons(self, newState=None):
        if newState is not None:
            self.state = newState
        state = self.state
        clear(self.actionButtonFrame)
        if state == "starting":
            pass
        elif state == "playerTurn":
            attackButton = Button("Attack", lambda: [showAttackSquares(self, self.actionButtonFrame, attackButton)],
                                  self.actionButtonFrame)
            attackButton.grid(column=0, row=0, padx=1)
            Button("Move", lambda: [moveAction(self)], self.actionButtonFrame).grid(column=1, row=0, padx=1)
        elif state == "playerMoving":
            Button("Cancel Move", lambda: [cancelMove(self, getCellsInReach(self, self.plr.movementSpeed, self.plr.xPos,
                                                                            self.plr.yPos, "walkable"))], self.actionButtonFrame).grid()
        elif state == "playerAiming":
            Button("Cancel Attack", lambda: [cancelAttack(self)], self.actionButtonFrame).grid()
        elif state == "enemyTurn":
            moveEnemy(self)
            self.state = "playerTurn"
            self.updateActionButtons()
        elif state == "battleWon":
            Button(*self.backButtonArgs).grid()
        else:
            error(f"Error: Battle state ({state}) does not exist")


class GridButton(tk.Button):

    def __init__(self, parent, x, y):
        self.parent = parent
        self.x = x
        self.y = y
        self.width = 2
        self.inPlayerReachRange = False
        self.inEnemyReachRange = False
        self.command = None
        self.contents = []
        self.states = {
            "enemy": False,
            "walkable": True,
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
        self.grid(column=self.x, row=self.y)

    def setCommand(self, command):
        super().__init__(self.parent, background=self.cget("background"), command=command, **self.kwargs)
        self.grid(column=self.x, row=self.y)


def main(frame, backButton, plr):
    fight = Fight(frame, backButton, plr)
    fight.setup()
    movePlayer(fight, fight.room.width - 1, fight.room.height - 1)
    moveEnemy(fight)
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


def enemyTurn():
    pass


def movePlayer(fight, x, y):
    grid = fight.grid
    plr = fight.plr
    if plr.xPos is not None:
        grid[plr.xPos][plr.yPos].setColor("white")
        grid[plr.xPos][plr.yPos].setCommand(None)
        grid[plr.xPos][plr.yPos].states["walkable"] = True
        grid[plr.xPos][plr.yPos].remove(plr)
    plr.xPos = x
    plr.yPos = y
    grid[x][y].setColor("blue")
    grid[x][y].setCommand(lambda: moveAction(fight))
    grid[x][y].states["walkable"] = False
    grid[x][y].append(plr)


def moveAction(fight):
    fight.updateActionButtons("playerMoving")
    grid = fight.grid
    room = fight.room
    plr = fight.plr
    cellsInReach = getCellsInReach(fight, plr.movementSpeed, plr.xPos, plr.yPos, "walkable")
    grid[plr.xPos][plr.yPos].setCommand(lambda: cancelMove(fight, cellsInReach))
    for cell in cellsInReach:
        cell.setColor("red")
        cell.setCommand(lambda x=cell.x, y=cell.y: [cancelMove(fight, cellsInReach), movePlayer(fight, x, y)])


def getCellsInReach(fight, reach, xStart, yStart, requirement=""):
    grid = fight.grid
    room = fight.room
    cells = []
    for column in grid[np.clip(xStart - math.ceil(reach), 0, None):np.clip(xStart + math.ceil(reach) + 1, None, room.width)]:
        for cell in column[np.clip(yStart - math.ceil(reach), 0, None):np.clip(yStart + math.ceil(reach) + 1, None, room.height)]:
            if ((xStart - cell.x) ** 2 + (yStart - cell.y) ** 2 <= reach ** 2) and cell.states[requirement]:
                cells.append(cell)
    return cells


def cancelMove(fight, cellsInReach):
    grid = fight.grid
    plr = fight.plr
    fight.updateActionButtons("playerTurn")
    for cell in cellsInReach:
        cell.setColor("white")
        cell.setCommand(None)
    grid[plr.xPos][plr.yPos].setCommand(lambda: moveAction(fight))


def cancelAttack(fight):
    grid = fight.grid
    plr = fight.plr
    fight.updateActionButtons("playerTurn")
    emptyAttackSquares = getCellsInReach(fight, fight.plr.weapon.reach, fight.plr.xPos,
                                         fight.plr.yPos, "walkable")
    attackSquaresWithEnemy = getCellsInReach(fight, fight.plr.weapon.reach, fight.plr.xPos,
                                             fight.plr.yPos, "enemy")
    for cell in emptyAttackSquares:
        cell.setColor("white")
        cell.setCommand(None)
    for cell in attackSquaresWithEnemy:
        cell.setColor("green")
        cell.setCommand(None)
    grid[plr.xPos][plr.yPos].setCommand(lambda: moveAction(fight))


def moveEnemy(fight, x=0, y=0):
    grid = fight.grid
    plr = fight.plr
    enemy = fight.enemy
    if enemy.xPos is not None:
        grid[enemy.xPos][enemy.yPos].setColor("white")
        grid[enemy.xPos][enemy.yPos].setCommand(None)
        grid[enemy.xPos][enemy.yPos].states["walkable"] = True
        grid[enemy.xPos][enemy.yPos].states["enemy"] = False
        if abs(plr.xPos - enemy.xPos) ** 2 + abs(plr.yPos - enemy.yPos) ** 2 > enemy.movementSpeed ** 2:
            try:
                direction = numpy.arctan(abs(plr.xPos - enemy.xPos) / abs(plr.yPos - enemy.yPos))

                moveX = math.floor(enemy.movementSpeed * numpy.sin(direction))
                if enemy.xPos > plr.xPos:
                    enemy.xPos -= moveX
                else:
                    enemy.xPos += moveX

                moveY = math.floor(enemy.movementSpeed * numpy.cos(direction))
                if enemy.yPos > plr.yPos:
                    enemy.yPos -= moveY
                else:
                    enemy.yPos += moveY
            except ZeroDivisionError:
                if enemy.xPos > plr.xPos:
                    enemy.xPos -= enemy.movementSpeed
                else:
                    enemy.xPos += enemy.movementSpeed
        else:
            if enemy.xPos > plr.xPos:
                enemy.xPos = plr.xPos + 1
            elif enemy.xPos == plr.xPos:
                enemy.xPos = plr.xPos
            else:
                enemy.xPos = plr.xPos - 1

            if enemy.yPos > plr.yPos:
                enemy.yPos = plr.yPos + 1
            elif enemy.yPos == plr.yPos:
                enemy.yPos = plr.yPos
            else:
                enemy.yPos = plr.yPos - 1
    else:
        enemy.xPos = x
        enemy.yPos = y

    grid[enemy.xPos][enemy.yPos].setColor("green")
    grid[enemy.xPos][enemy.yPos].states["walkable"] = False
    grid[enemy.xPos][enemy.yPos].states["enemy"] = True


def showAttackSquares(fight, actionButtonFrame, button):
    fight.updateActionButtons("playerAiming")
    plr = fight.plr
    cells = getCellsInReach(fight, plr.weapon.reach, plr.xPos, plr.yPos, "walkable")
    enemyCells = getCellsInReach(fight, plr.weapon.reach, plr.xPos, plr.yPos, "enemy")
    for cell in enemyCells:
        cell.setColor("SeaGreen3")
        cell.setCommand(lambda: [attackEnemy(fight)])

    for cell in cells:
        cell.setColor("orange")


def attackEnemy(fight):
    plr = fight.plr
    log = fight.log
    enemy = plr.currentRoom.enemy
    attackPower = plr.strength + plr.weapon.strBonus
    enemy.health -= np.clip(attackPower, None, enemy.health)
    out(log, f"You attack the {enemy.name} for {attackPower} damage. They now have {enemy.health} hp left.")
    if enemy.health == 0:
        plr.xPos = None
        plr.yPos = None
        fight.updateActionButtons("battleWon")


def out(log, text):
    log.configure(state="normal")
    log.insert(tk.END, text + "\n\n")
    log.see("end")
    log.configure(state="disabled")
