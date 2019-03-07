from collections import namedtuple

# Weapons
weapon = namedtuple("weapon", ["name", "char", "colour", "power", "uses"])

dagger = weapon("Dagger", "d", (255, 255, 255), 1, 5)

weapons_list = [dagger]


# Monsters
monster = namedtuple("monster", ["name", "char", "colour", "hits", "weapon"])

lunatic = monster("Lunatic", "l", (255, 255, 255), 5, dagger)

monsters_list = [lunatic]

