import math
import tkinter

import numpy

from tkManager import *


# Types of cells:
#   - Player
#   - Enemy
#   - Wall
#   - Walkable
#   - Free

class Grid:
    def __init__(self):
        self.contents = []

        def getCell(x, y):
            return self[x].winfo_children()[y]

    def __getitem__(self, item):
        return self.contents[item]

    def __setitem__(self, key, value):
        self.contents[key] = value

    def __add__(self, other):
        self.contents.append(other)


class GridButton(ttk.Button):

    def __init__(self, parent, x, y):
        self.width = 2
        self.x = x
        self.y = y
        self.inPlayerWalkRange = False
        self.inEnemyWalkRange = False
        self.inPlayerReachRange = False
        self.inEnemyReachRange = False
        self.walkable = True
        self.contains = []
        kwargs = {
            "width": self.width,
        }
        super().__init__(parent, **kwargs)


def main(frame, plr):
    room = plr.currentRoom
    enemy = room.enemy
    grid = createGrid(room, frame)
    grid.getCell(0, 0)
    # movePlayer(grid, frame, plr, enemy, 5, 0)
    enemy.xPos = 7
    enemy.yPos = 9
    getCell(enemy.xPos, enemy.yPos)  # = "Enemy"
    # showBattleScreen(grid, frame, plr, enemy)


def showBattleScreen(grid, frame, plr, enemy):
    clear(frame)
    showGrid(grid, frame, plr, enemy)
    showActionButtons(grid, frame, plr, enemy)


def createGrid(room, frame):
    clear(frame)
    grid = Grid()
    for i in range(room.height):
        row = ttk.Frame()
        for j in range(room.width):
            cell = GridButton(row, i, j)
            cell.pack()
        grid.append(row)
        row.pack()
    return grid


def showGrid(grid, frame, plr, enemy):
    gridFrame = ttk.Frame(frame)
    x = 0
    for row in grid:
        rowFrame = ttk.Frame(gridFrame)
        y = 0
        for cell in row:
            cellButton = GridButton(rowFrame, x, y)
            if cell == "Player":
                cellButton.configure(style="Player.TButton",
                                     command=lambda: [countWalkable(grid, plr),
                                                      showBattleScreen(grid, frame, plr, enemy)])
            elif cell == "Walkable":
                cellButton.configure(style="Walkable.TButton",
                                     command=lambda xPos=x, yPos=y: movePlayer(grid, frame, plr, enemy, xPos, yPos))
            elif cell == "Enemy":
                cellButton.configure(style="Enemy.TButton")
            else:
                cellButton.configure(style="Free.TButton")
                cellButton["state"] = tk.DISABLED
            cellButton.pack()
            y += 1
        x += 1

        rowFrame.pack(side=tk.LEFT)
    gridFrame.pack()


def showActionButtons(grid, frame, plr, enemy):
    Button("Move", lambda: [countWalkable(grid, plr), showBattleScreen(grid, frame, plr, enemy)], frame).pack()
    Button("Enemy Move", lambda: moveEnemy(grid, frame, plr, enemy), frame).pack()


def countWalkable(grid, plr):
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            if grid[x][y] == "Walkable":
                grid[x][y] = "Free"

            if abs(plr.xPos - x) ** 2 + abs(plr.yPos - y) ** 2 <= plr.movementSpeed ** 2 and grid[x][y] == "Free":
                grid[x][y] = "Walkable"


def movePlayer(grid, frame, plr, enemy, x, y):
    grid[plr.xPos][plr.yPos] = "Free"
    plr.xPos = x
    plr.yPos = y
    grid[plr.xPos][plr.yPos] = "Player"

    for x in range(len(grid)):
        for y in range(len(grid[x])):
            if grid[x][y] == "Walkable":
                grid[x][y] = "Free"

    showBattleScreen(grid, frame, plr, enemy)


def moveEnemy(grid, frame, plr, enemy):
    grid[enemy.xPos][enemy.yPos] = "Free"
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

    grid[enemy.xPos][enemy.yPos] = "Enemy"
    showBattleScreen(grid, frame, plr, enemy)


def printPos(x, y):
    print(f"({x},{y})")
