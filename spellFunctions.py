import numpy as np

from miscFunctions import getDistance


def uselessSpell(args):
    return ""


def spell_1(args):
    plr = args["fight"].plr
    plr.loseHealth()
    return f"Your fingers are numb and you take 1 damage. You now have {plr.hp} hp left."


def spell_2(args):
    fight = args["fight"]
    plr = fight.plr
    enemy = fight.enemy
    if getDistance((plr.xPos, plr.yPos), (enemy.xPos, enemy.yPos)) <= 3:
        enemy.loseHealth(fight, np.clip(3, None, enemy.health), False)
        return f"You blast the {enemy.name} with a ball of fire for 3 damage. They now have {enemy.health} left."
    else:
        return f"A ball of fire flies off towards the {enemy.name} but tapers off before it can reach them."
