import math

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

    def setup(self):
        gridFrame = ttk.Frame(self.frame)
        gridFrame.grid()
        self.grid = createGrid(self.room, gridFrame)
        self.log.grid(column=1, row=0)
        self.actionButtonFrame.grid(column=0, row=self.room.height, columnspan=2)
        self.backButtonArgs += (self.actionButtonFrame,)
        self.state = "playerTurn"

    def updateActionButtons(self, newState=None):
        """
        Possible battle states:
              - "starting"     -> The fight is setting up
              - "playerTurn"   -> It's the player's turn and they are not in the middle of an action (all actions should be enabled)
              - "playerMoving" -> It's the player's turn and they are choosing where to move (only cancel move should be enabled)
              - "playerAiming" -> It's the player's turn and they are choosing where to aim (only cancel attack should be enabled)
              - "enemyTurn"    -> It's the player's turn (no actions should be enabled)
              - "battleWon"    -> The battle is won and only the continue button should be visible
        """
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
            attackButton.grid(column=0, row=0, padx=1)

            moveButton = Button("Move", lambda: moveAction(self), self.actionButtonFrame)
            if self.plr.movement < 1:
                moveButton["state"] = tk.DISABLED
            moveButton.grid(column=1, row=0, padx=1)

            Button("End Turn", lambda: enemyTurn(self), self.actionButtonFrame).grid(column=2, row=0, padx=1)
        elif state == "playerMoving":
            Button("Cancel Move", lambda: [cancelMove(self, getCellsInReach(self, self.plr.movementSpeed, self.plr.xPos,
                                                                            self.plr.yPos, "walkable"))], self.actionButtonFrame).grid()
        elif state == "playerAiming":
            Button("Cancel Attack", lambda: [cancelAttack(self)], self.actionButtonFrame).grid()
        elif state == "enemyTurn":
            pass
        elif state == "battleWon":
            Button(*self.backButtonArgs).grid()
        elif state == "gameOver":
            Label(self.frame, "Game Over!").grid()
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
        self.grid(column=self.x, row=self.y)

    def setCommand(self, command):
        super().__init__(self.parent, background=self.cget("background"), command=command, **self.kwargs)
        self.grid(column=self.x, row=self.y)


def main(frame, backButton, plr):
    fight = Fight(frame, backButton, plr)
    fight.setup()
    movePlayer(fight, fight.room.width - 1, fight.room.height - 1)
    moveEnemy(fight, 0, 0)
    plr.actions = 1
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
    fight.updateActionButtons("enemyTurn")
    moveTowardsPlayer(fight, *getDesiredPos(fight))
    for i in getCellsInReach(fight, enemy.reach, enemy.xPos, enemy.yPos, "player"):
        attackPlayer(fight)
    fight.plr.actions = 1
    fight.plr.movement = fight.plr.movementSpeed
    fight.updateActionButtons("playerTurn")


def attackPlayer(fight):
    plr = fight.plr
    log = fight.log
    enemy = fight.enemy
    plr.hp -= np.clip(enemy.strength, None, plr.hp)
    out(log, f"The {enemy.name} attack you for {enemy.strength} damage. You now have {plr.hp} hp left.")
    if plr.hp == 0:
        gameOver(fight)


def getDesiredPos(fight):
    x = 0
    y = 0
    enemy = fight.enemy
    plr = fight.plr
    closestCell = fight.grid[enemy.xPos][enemy.yPos]
    for cell in getCellsInReach(fight, enemy.reach, enemy.xPos, enemy.yPos):
        if cell.states["player"]:
            closestCells = [fight.grid[plr.xPos][plr.yPos]]
            for c in getCellsInReach(fight, enemy.reach, plr.xPos, plr.yPos):
                if (plr.xPos - c.x) ** 2 + (plr.yPos - c.y) ** 2 > (plr.xPos - closestCells[0].x) ** 2 + (
                        plr.yPos - closestCells[0].y) ** 2:
                    closestCells.clear()
                    closestCells.append(c)
                if (plr.xPos - c.x) ** 2 + (plr.yPos - c.y) ** 2 == (plr.xPos - closestCells[0].x) ** 2 + (
                        plr.yPos - closestCells[0].y) ** 2:
                    closestCells.append(c)
            closestCell = closestCells[0]
            for c in closestCells:
                if (enemy.xPos - c.x) ** 2 + (enemy.yPos - c.y) ** 2 < (enemy.xPos - closestCell.x) ** 2 + (
                        enemy.yPos - closestCell.y) ** 2:
                    closestCell = c
                x = closestCell.x
                y = closestCell.y
            break
        if cell.states["walkable"] or cell.states["enemy"]:
            if (plr.xPos - cell.x) ** 2 + (plr.yPos - cell.y) ** 2 < (plr.xPos - closestCell.x) ** 2 + (plr.yPos - closestCell.y) ** 2:
                closestCell = cell
            xDiff = enemy.xPos - closestCell.x
            yDiff = enemy.yPos - closestCell.y
            x = plr.xPos + xDiff
            y = plr.yPos + yDiff
    return x, y


def getOrientation(var1, var2):  # Returns 1, 0, or -1
    if var1 < var2:
        return -1
    elif var1 == var2:
        return 0
    else:
        return 1


def movePlayer(fight, x, y):
    grid = fight.grid
    plr = fight.plr
    if plr.xPos is not None:
        grid[plr.xPos][plr.yPos].setColor("white")
        grid[plr.xPos][plr.yPos].setCommand(None)
        grid[plr.xPos][plr.yPos].states["walkable"] = True
        grid[plr.xPos][plr.yPos].states["player"] = False
        grid[plr.xPos][plr.yPos].remove(plr)
    plr.xPos = x
    plr.yPos = y
    grid[x][y].setColor("blue")
    grid[x][y].setCommand(lambda: moveAction(fight))
    grid[x][y].states["walkable"] = False
    grid[x][y].states["player"] = True
    grid[x][y].append(plr)


def moveAction(fight):
    if fight.state == "playerAiming":
        cancelAttack(fight)
    fight.updateActionButtons("playerMoving")
    grid = fight.grid
    plr = fight.plr
    cellsInReach = getCellsInReach(fight, plr.movement, plr.xPos, plr.yPos, "walkable")
    grid[plr.xPos][plr.yPos].setCommand(lambda: cancelMove(fight, cellsInReach))
    for cell in cellsInReach:
        cell.setColor("red")
        cell.setCommand(lambda x=cell.x, y=cell.y: [plr.setMovement(plr.movement - ((plr.xPos - x) ** 2 + (plr.yPos - y) ** 2)),
                                                    cancelMove(fight, cellsInReach), movePlayer(fight, x, y)])


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


def moveTowardsPlayer(fight, x=0, y=0):
    grid = fight.grid
    enemy = fight.enemy
    if (x, y) != (enemy.xPos, enemy.yPos):
        grid[enemy.xPos][enemy.yPos].setColor("white")
        grid[enemy.xPos][enemy.yPos].setCommand(None)
        grid[enemy.xPos][enemy.yPos].states["walkable"] = True
        grid[enemy.xPos][enemy.yPos].states["enemy"] = False

        targetCell = grid[0][0]
        for cell in getCellsInReach(fight, enemy.movementSpeed, enemy.xPos, enemy.yPos, "walkable"):
            if (x - cell.x) ** 2 + (y - cell.y) ** 2 < (x - targetCell.x) ** 2 + (y - targetCell.y) ** 2:
                targetCell = cell

        moveEnemy(fight, targetCell.x, targetCell.y)


def moveEnemy(fight, x, y):
    enemy = fight.enemy
    grid = fight.grid
    enemy.xPos = x
    enemy.yPos = y
    grid[x][y].setColor("green")
    grid[x][y].states["walkable"] = False
    grid[x][y].states["enemy"] = True


def showAttackSquares(fight):
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
    plr.actions -= 1
    cancelAttack(fight)
    enemy = plr.currentRoom.enemy
    attackPower = plr.strength + plr.weapon.strBonus
    enemy.health -= np.clip(attackPower, None, enemy.health)
    out(log, f"You attack the {enemy.name} for {attackPower} damage. They now have {enemy.health} hp left.")
    if enemy.health == 0:
        plr.xPos = None
        plr.yPos = None
        fight.updateActionButtons("battleWon")
        out(log, "You Won!")


def out(log, text):
    log.configure(state="normal")
    log.insert(tk.END, text + "\n\n")
    log.see("end")
    log.configure(state="disabled")


def gameOver(fight):
    plr = fight.plr
    out(fight.log, "You died! Game Over")
    fight.grid[plr.xPos][plr.yPos].setCommand(None)
    fight.updateActionButtons("gameOver")
