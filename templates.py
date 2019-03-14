from collections import namedtuple

# Weapons
weapon = namedtuple("weapon", ["name", "char", "colour", "power", "uses"])

# TODO: need to make two weapon variants - one that doesn't break (for the monster to attack with) and one to loot drop
dagger = weapon("Dagger", "d", (255, 255, 255), 1, 1)

weapons_list = [dagger]


# Monsters
monster = namedtuple("monster", ["name", "char", "colour", "hits", "weapon"])

lunatic = monster("Lunatic", "l", (255, 255, 255), 1, dagger)

monsters_list = [lunatic]

