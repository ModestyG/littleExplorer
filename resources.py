from gameClasses import*
ENEMIES = [
    Enemy("Spider", 1, "a", 1),
    Enemy("Rat", 1, "a", 2),
    Enemy("Goblin", 2, "a", 5),
    Enemy("Dragon", 100, "a", 500)
]

WEAPONS = [
    Weapon("Dagger", 1, "a", 1.5, "A small but sharp dagger."),
    Weapon("Sword", 3, "a", 2, "A large sword to swing at your enemies."),
    Weapon("Bow", 3, "a", 8, "A basic bow.")
]

ROOM_DESCRIPTIONS = [
    "You're in a large and humid cavern. There are large, dripping stalactites hanging from the ceiling and you can "
    "hear a waterfall in the distance. Opposite you are three dark openings.",
    "You have entered a long corridor with multiple numbered doors on both sides. The floor is covered in red carpet "
    "and the lights are turned down. You can hear faint lobby music. Only three of the doors seem unlocked."
]