def uselessSpell(args):
    return ""


def spell_1(args):
    plr = args["plr"]
    plr.loseHealth()
    return f"Your fingers are numb and you take 1 damage. You now have {plr.hp} hp left."
