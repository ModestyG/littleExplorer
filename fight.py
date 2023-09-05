import math
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
        self.inPlayerWalkRange = False
        self.inEnemyWalkRange = False
        self.inPlayerReachRange = False
        self.inEnemyReachRange = False
        self.command = None
        self.contents = []
        self.states = {
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


def main(frame, plr):
    room = plr.currentRoom
    enemy = room.enemy
    gridFrame = ttk.Frame(frame)
    gridFrame.grid()
    grid = createGrid(room, gridFrame)
    movePlayer(grid, plr, 4, 4)
    # enemy.xPos = 7
    # enemy.yPos = 9
    # grid[enemy.xPos][enemy.yPos].append("Enemy")
    # showBattleScreen(grid, frame, plr, enemy)


#
# def showBattleScreen(grid, frame, plr, enemy):
#     renderGrid(grid, frame, plr, enemy)
#     showActionButtons(grid, frame, plr, enemy)


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
        cell.inPlayerWalkRange = True
        cell.setCommand(lambda x=cell.x, y=cell.y: [cancelMove(grid, plr, cellsInReach), movePlayer(grid, plr, x, y)])

def getCellsInReach(grid, room, reach, xStart, yStart, requirement=""):
    cells = []
    for column in grid[np.clip(xStart - reach, 0, None):np.clip(xStart + reach + 1, None, room.width)]:
        for cell in column[np.clip(yStart - reach, 0, None):np.clip(yStart + reach + 1, None, room.height)]:
            if ((xStart - cell.x) ** 2 + (yStart - cell.y) ** 2 <= reach ** 2) and cell.states[requirement]:
                cells.append(cell)
    return cells


def cancelMove(grid, plr, cellsInReach):
    for cell in cellsInReach:
        cell.setColor("white")
        cell.setCommand(None)
        cell.inPlayerWalkRange = False
    grid[plr.xPos][plr.yPos].setCommand(lambda: moveAction(grid, plr.currentRoom, plr))

# def showGrid(grid, frame, plr, enemy):
#     gridFrame = ttk.Frame(frame)
#     x = 0
#     for row in grid:
#         rowFrame = ttk.Frame(gridFrame)
#         y = 0
#         for cell in row:
#             cellButton = GridButton(rowFrame, x, y)
#             if cell == "Player":
#                 cellButton.configure(style="Player.TButton",
#                                      command=lambda: [countWalkable(grid, plr),
#                                                       showBattleScreen(grid, frame, plr, enemy)])
#             elif cell == "Walkable":
#                 cellButton.configure(style="Walkable.TButton",
#                                      command=lambda xPos=x, yPos=y: movePlayer(grid, frame, plr, enemy, xPos, yPos))
#             elif cell == "Enemy":
#                 cellButton.configure(style="Enemy.TButton")
#             else:
#                 cellButton.configure(style="Free.TButton")
#                 cellButton["state"] = tk.DISABLED
#             cellButton.pack()
#             y += 1
#         x += 1
#
#         rowFrame.pack(side=tk.LEFT)
#     gridFrame.pack()


# def showActionButtons(grid, frame, plr, enemy):
#     Button("Move", lambda: [countWalkable(grid, plr), showBattleScreen(grid, frame, plr, enemy)], frame).pack()
#     Button("Enemy Move", lambda: moveEnemy(grid, frame, plr, enemy), frame).pack()
#
#
# def countWalkable(grid, plr):
#     for x in range(len(grid)):
#         for y in range(len(grid[x])):
#             if grid[x][y] == "Walkable":
#                 grid[x][y] = "Free"
#
#             if abs(plr.xPos - x) ** 2 + abs(plr.yPos - y) ** 2 <= plr.movementSpeed ** 2 and grid[x][y] == "Free":
#                 grid[x][y] = "Walkable"
#
#
# def movePlayer(grid, frame, plr, enemy, x, y):
#     grid[plr.xPos][plr.yPos] = "Free"
#     plr.xPos = x
#     plr.yPos = y
#     grid[plr.xPos][plr.yPos] = "Player"
#
#     for x in range(len(grid)):
#         for y in range(len(grid[x])):
#             if grid[x][y] == "Walkable":
#                 grid[x][y] = "Free"
#
#     showBattleScreen(grid, frame, plr, enemy)
#
#
# def moveEnemy(grid, frame, plr, enemy):
#     grid[enemy.xPos][enemy.yPos] = "Free"
#     if abs(plr.xPos - enemy.xPos) ** 2 + abs(plr.yPos - enemy.yPos) ** 2 > enemy.movementSpeed ** 2:
#         try:
#             direction = numpy.arctan(abs(plr.xPos - enemy.xPos) / abs(plr.yPos - enemy.yPos))
#
#             moveX = math.floor(enemy.movementSpeed * numpy.sin(direction))
#             if enemy.xPos > plr.xPos:
#                 enemy.xPos -= moveX
#             else:
#                 enemy.xPos += moveX
#
#             moveY = math.floor(enemy.movementSpeed * numpy.cos(direction))
#             if enemy.yPos > plr.yPos:
#                 enemy.yPos -= moveY
#             else:
#                 enemy.yPos += moveY
#         except ZeroDivisionError:
#             if enemy.xPos > plr.xPos:
#                 enemy.xPos -= enemy.movementSpeed
#             else:
#                 enemy.xPos += enemy.movementSpeed
#     else:
#         if enemy.xPos > plr.xPos:
#             enemy.xPos = plr.xPos + 1
#         elif enemy.xPos == plr.xPos:
#             enemy.xPos = plr.xPos
#         else:
#             enemy.xPos = plr.xPos - 1
#
#         if enemy.yPos > plr.yPos:
#             enemy.yPos = plr.yPos + 1
#         elif enemy.yPos == plr.yPos:
#             enemy.yPos = plr.yPos
#         else:
#             enemy.yPos = plr.yPos - 1
#
#     grid[enemy.xPos][enemy.yPos] = "Enemy"
#     showBattleScreen(grid, frame, plr, enemy)
#
#
# def printPos(x, y):
#     print(f"({x},{y})")
