import math

import numpy
import numpy as np

from tkManager import *


# Types of cells:
#   - Player
#   - Enemy
#   - Wall
#   - Walkable
#   - Free

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
    room = plr.currentRoom
    enemy = room.enemy
    gridFrame = ttk.Frame(frame)
    gridFrame.grid()
    grid = createGrid(room, gridFrame)
    movePlayer(grid, plr, room.width-1, room.height-1)
    moveEnemy(grid, plr, enemy)
    log = tk.Text(frame, height=1.5*room.height, width=40, state="disabled")
    log.grid(column=1, row=0)
    showActionButtons(frame, backButton, grid, room, plr, log, enemy)

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


def movePlayer(grid, plr, x, y):
    if plr.xPos is not None:
        grid[plr.xPos][plr.yPos].setColor("white")
        grid[plr.xPos][plr.yPos].setCommand(None)
        grid[plr.xPos][plr.yPos].states["walkable"] = True
        grid[plr.xPos][plr.yPos].remove(plr)
    plr.xPos = x
    plr.yPos = y
    grid[x][y].setColor("blue")
    grid[x][y].setCommand(lambda: moveAction(grid, plr.currentRoom, plr))
    grid[x][y].states["walkable"] = False
    grid[x][y].append(plr)

def moveAction(grid, room, plr):
    cellsInReach = getCellsInReach(grid, room, plr.movementSpeed, plr.xPos, plr.yPos, "walkable")
    grid[plr.xPos][plr.yPos].setCommand(lambda: cancelMove(grid, plr, cellsInReach))
    for cell in cellsInReach:
        cell.setColor("red")
        cell.setCommand(lambda x=cell.x, y=cell.y: [cancelMove(grid, plr, cellsInReach), movePlayer(grid, plr, x, y)])

def getCellsInReach(grid, room, reach, xStart, yStart, requirement=""):
    cells = []
    for column in grid[np.clip(xStart - math.ceil(reach), 0, None):np.clip(xStart + math.ceil(reach) + 1, None, room.width)]:
        for cell in column[np.clip(yStart - math.ceil(reach), 0, None):np.clip(yStart + math.ceil(reach) + 1, None, room.height)]:
            if ((xStart - cell.x) ** 2 + (yStart - cell.y) ** 2 <= reach ** 2) and cell.states[requirement]:
                cells.append(cell)
    return cells

def cancelMove(grid, plr, cellsInReach):
    for cell in cellsInReach:
        cell.setColor("white")
        cell.setCommand(None)
    grid[plr.xPos][plr.yPos].setCommand(lambda: moveAction(grid, plr.currentRoom, plr))

def showActionButtons(frame, backButton, grid, room, plr, log, enemy):
    actionButtonFrame = ttk.Frame(frame)
    attackButton = Button("Attack", lambda: [attackAction(backButton, grid, room, plr, log, attackButton)], actionButtonFrame)
    attackButton.grid(column=0, row=0, padx=1)
    Button("Enemy Move", lambda: moveEnemy(grid, plr, enemy), actionButtonFrame).grid(column=1, row=0, padx=1)
    actionButtonFrame.grid(column=0, row=room.height)
def moveEnemy(grid, plr, enemy, x=0, y=0):
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

def attackAction(backButton, grid, room, plr, log, button):
    cells = getCellsInReach(grid, room, plr.weapon.reach, plr.xPos, plr.yPos, "walkable")
    enemyCells = getCellsInReach(grid, room, plr.weapon.reach, plr.xPos, plr.yPos, "enemy")
    if len(enemyCells) > 0:
        button.configure(command=lambda: [cancelMove(grid, plr, cells), enemyCells[0].setColor("green"),
                                          enemyCells[0].setCommand(None),
                                          button.configure(command=lambda: attackAction(backButton, grid, room, plr, log, button))])
    else:
        button.configure(command=lambda: [cancelMove(grid, plr, cells), button.configure(
            command=lambda: (attackAction(backButton, grid, room, plr, log, button)))])

    for cell in enemyCells:
        cell.setColor("SeaGreen3")
        cell.setCommand(lambda: attackEnemy(backButton, plr, log))

    for cell in cells:
        cell.setColor("orange")


def attackEnemy(backButton, plr, log):
    enemy = plr.currentRoom.enemy
    attackPower = plr.strength + plr.weapon.strBonus
    enemy.health -= attackPower
    out(log, f"You attack the {enemy.name} for {attackPower} damage. They now have {enemy.health} hp left.")
    if enemy.health <= 0:
        plr.xPos = None
        plr.yPos = None
        backButton.grid()

def out(log, text):
    log.configure(state="normal")
    log.insert(tk.END, text+"\n\n")
    log.see("end")
    log.configure(state="disabled")

