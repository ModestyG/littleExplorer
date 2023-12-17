from gameClasses import *
from miscFunctions import BiDict
from spellFunctions import *

ENEMIES = BiDict({
    1: Enemy("Spider", 1, strength=1, article="a", health=1, reach=2, cr=2),
    2: Enemy("Rat", 2, strength=1, article="a", health=2, reach=1.5, movement=4, cr=4),
    3: Enemy("Boar", 3, strength=1.5, article="a wild", health=3, reach=2, movement=4, cr=18),
    4: Enemy("Goblin", 4, strength=1.5, article="a", health=5, reach=3, cr=20),
    5: Enemy("Bees", 5, strength=0.5, article="a swarm of", health=10, reach=1, movement=6, cr=30),
    6: Enemy("Slime", 6, strength=0.5, article="a", health=5, reach=2, movement=7, cr=30),
    7: Enemy("Rogue", 7, strength=3, article="a knife-wielding", health=8, reach=1.5, cr=50),
    8: Enemy("Knight", 8, strength=4, article="a", health=15, reach=2, cr=70),
    9: Enemy("Rogue", 9, strength=3, article="a bow-wielding", health=8, reach=8, cr=80),
    10: Enemy("Possessed Armour", 10, strength=4, article="a", health=25, reach=2, cr=80),
    11: Enemy("Undead Mage", 11, strength=6, article="an", health=8, reach=5, cr=80),
    12: Enemy("Possessed Armour", 12, strength=4, article="a bow-wielding", health=15, reach=8, cr=100),
    13: Enemy("Ice Dragon", 13, strength=80, article="an", health=600, reach=5, cr=500),
    14: Enemy("Fire Dragon", 14, strength=100, article="a", health=500, reach=5, cr=550),
    15: Enemy("God", 15, strength=1000, article="", health=10000, reach=10, cr=1000),
})

WEAPONS = BiDict({
    16: Weapon("Stick", 16, strBonus=1, article="a", reach=1.5,
               desc="A stick. Maybe if you hit the enemy REALLY hard it will leave a mark", itemRating=3),
    17: Weapon("Dagger", 17, strBonus=2, article="a", reach=1.5, desc="A small but sharp dagger.", itemRating=3),
    18: Weapon("Wooden Club", 18, strBonus=3, article="a", reach=2, desc="A glorified stick.", itemRating=5),
    19: Weapon("Shortsword", 19, strBonus=3.5, article="a", reach=2,
               desc="Truly the inferior type of sword. Good for people with noodle arms.", itemRating=20),
    20: Weapon("Silver warhammer", 20, strBonus=4, article="a", reach=2, desc="A silver warhammer with copper decour.", itemRating=30),
    21: Weapon("Longsword", 21, strBonus=4.5, article="a", reach=3, desc="A large sword to swing at your enemies.", itemRating=45),
    22: Weapon("Bow", 22, strBonus=4, article="a", reach=8, desc="A basic bow.", itemRating=75),
    23: Weapon("Gun", 23, strBonus=100, article="a", reach=8, desc="'You're a fool. No weapon forged can stop me.' 'That was then... this "
                                                                   "is now.' I swear this is just a very high-level enchanted artefact.",
               itemRating=400),
})

# Duration=None -> Effect is permanent
# Duration=0    -> Effect lasts for the whole battle
# Duration>0    -> Effect lasts for set amount of turns

POTIONS = BiDict({

    24: Potion("Lesser Health Potion", 24, article="a",
               effectName="Heal", function=lesserHealthPotion, duration=None, itemRating=2,
               desc="A bottle filled with shiny pink liquid.", effectDesc="Restores 2 HP"),

    25: Potion("Health Potion", 25, article="a",
               effectName="Heal", function=healthPotion, duration=None,
               itemRating=10, desc="A bottle filled with shiny pink liquid.", effectDesc="Restores 5 HP"),

    26: Potion("Greater Health Potion", 26, article="a",
               effectName="Heal", function=healthPotion, duration=None,
               itemRating=50, desc="A bottle filled with shiny pink liquid.", effectDesc="Restores 25 HP"),

    27: Potion("Superior Health Potion", 27, article="a",
               effectName="Heal", function=healthPotion, duration=None,
               itemRating=200, desc="A bottle filled with shiny pink liquid.", effectDesc="Restores 100 HP"),

    28: Potion("Growth Elixir", 28, article="a", effectName="Growth", function=growthElixir, itemRating=15,
               desc="A jar of thick, red, muck with small multicolored chunks. It reminds you of chunky salsa.",
               effectDesc="Makes you grow to the size of a troll. You gain +1.5 reach.", duration=0),

    29: Potion("Elixir of Haste", 29, article="an", effectName="Haste", function=hasteElixir, itemRating=20,
               desc="A crystal bottle filled with what looks like liquid silver. It is much less viscous than the metallic color suggests.",
               effectDesc="Gives you +1 action and +2 movement for the remainder of the battle.", duration=5),

})
ROOM_DESCRIPTIONS = BiDict({
    1: "You're in a large and humid cavern. There are large, dripping stalactites hanging from the ceiling and you can "
       "hear a waterfall in the distance. Opposite you are three dark openings.",
    2: "You have entered a long corridor with multiple numbered doors on both sides. The floor is covered in red carpet "
       "and the lights are turned down. You can hear faint lobby music. Only three of the doors seem unlocked."
})

RUNES = BiDict({
    30: Rune("None", 30, itemRating=0),
    31: Rune("Frost Rune", 31, itemRating=10, image="ice.png"),
    32: Rune("Fire Rune", 32, itemRating=10, image="fire.png")
})

SPELLS = BiDict({
    "": Spell("You haven't chosen any runes. Nothing happens.", uselessSpell),

    "1;": Spell("The rune slowly grows colder until you are forced to drop it. As soon as you stop touching it, the rune's glow fades "
                "out. Your fingertips are covered in frost.", spell_1),
    "2;": Spell("A small ball of fire forms in your hand before launching off towards a wall", spell_2, False)
})
