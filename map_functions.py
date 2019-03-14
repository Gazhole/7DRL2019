from tdl.map import Map
from collections import namedtuple
from random import choice, shuffle, randint
from copy import deepcopy
from message_log import Message
from enum import Enum
from entities import Actor, Item
from components import Fighter, BasicMonster, Weapon
from templates import monsters_list

# Colours
colours = namedtuple("colours", ["light_wall", "dark_wall", "light_ground", "dark_ground"])
white = colours((250, 250, 250), (160, 160, 160), (110, 110, 110), (40, 40, 40))
red = colours((250, 65, 65), (160, 35, 35), (110, 30, 30), (40, 10, 10))
blue = colours((65, 125, 250), (35, 75, 160), (30, 60, 110), (10, 20, 40))
green = colours((0, 250, 0), (0, 160, 0), (0, 110, 0), (0, 40, 0))
yellow = colours((250, 180, 0), (160, 110, 0), (110, 70, 0), (40, 10, 0))


class Rect:
    def __init__(self, room_x, room_y, rect_width, rect_height):
        self.x1 = room_x
        self.y1 = room_y
        self.x2 = self.x1 + rect_width
        self.y2 = self.y1 + rect_height

    def fill_rect(self, room):
        filled_coordinates = []
        for x in range(self.x1, self.x2):
            for y in range(self.y1, self.y2):
                room.walkable[x, y] = False
                room.transparent[x, y] = False
                filled_coordinates.append((x,y))
        return filled_coordinates

    def carve_rect(self, room):
        carved_coordinates = []
        for x in range(self.x1, self.x2):
            for y in range(self.y1, self.y2):
                room.walkable[x, y] = True
                room.transparent[x, y] = True
                carved_coordinates.append((x,y))
        return carved_coordinates


class GameMap:
    def __init__(self, map_width, map_height):
        self.map_width = map_width
        self.map_height = map_height
        self.rooms = [[Room(30, 30, map_x, map_y, room_id=str(map_x) + str(map_y)) for map_y in range(self.map_height)] for map_x in range(self.map_width)]
        self.rooms_index = {}  # This is a dictionary to keep track of where each room is in the GameMap object.
        self.update_rooms_index()

    def update_rooms_index(self):
        for y in range(self.map_height):
            for x in range(self.map_width):
                self.rooms_index[self.rooms[x][y].room_id] = {"map_x": x, "map_y": y}

    # This moves the rooms around the map.
    def shuffle_rooms(self, player, entities):
        viable_coordinates = []

        # Append an x,y for each location in the game map.
        for y in range(self.map_height):
            for x in range(self.map_width):
                viable_coordinates.append((x, y))

        # Remove the player's current location or things could get messy. Shuffle the list.
        viable_coordinates.remove((player.map_x, player.map_y))
        shuffle(viable_coordinates)

        # This avoids leaving one room copied and not replaced, ending up with a duplicate.
        final_copy_x, final_copy_y = viable_coordinates[0]
        final_copied_room = deepcopy(self.rooms[final_copy_x][final_copy_y])

        # Pop the first room coords, and set that to be replaced by the next room in the list. Continue in this way.
        while len(viable_coordinates) > 1:
            replace_x, replace_y = viable_coordinates.pop(0)
            copy_x, copy_y = viable_coordinates[0]
            copied_room = deepcopy(self.rooms[copy_x][copy_y])
            self.rooms[replace_x][replace_y] = copied_room

        # There will always be one room left because of this method, so that's why we copied before the while loop
        final_replace_x, final_replace_y = viable_coordinates.pop(0)
        self.rooms[final_replace_x][final_replace_y] = final_copied_room

        self.update_rooms_index()  # Update the room index with the new positions.

        message = Message("You feel an odd sensation of movement...")

        for entity in entities:
            if entity is player:
                continue
            else:
                entity.set_map_position(self)

        return message


class RoomTypes(Enum):
    COMBAT_ROOM = 0
    PUZZLE_ROOM = 1
    TRAP_ROOM = 2
    MYSTERY_ROOM = 3


# TODO: point fov radius to room illumination and vary this by room type.
# TODO: It also might be worth storing floor tile chars in the rooms aswell to aid in decoration
class Room(Map):
    def __init__(self, room_width, room_height, map_x, map_y, room_id,):
        super().__init__(room_width, room_height)
        self.room_id = room_id
        self.position_in_map = (map_x, map_y)

        self.room_width = room_width
        self.room_height = room_height

        self.explored = [[False for room_y in range(self.room_height)] for room_x in range(self.room_width)]
        self.colours = None

        if room_id == "22":
            self.room_type = "exit"
        else:
            self.room_type = choice([RoomTypes.COMBAT_ROOM, RoomTypes.PUZZLE_ROOM, RoomTypes.TRAP_ROOM, RoomTypes.MYSTERY_ROOM])


def create_rooms(game_map, map_width, map_height, entities):
    for map_y in range(map_height):
        for map_x in range(map_width):
            room = game_map.rooms[map_x][map_y]
            create_basic_room_layout(room)

            if room.room_type == "exit":
                create_exit_room(game_map, room, entities)

            elif room.room_type == RoomTypes.TRAP_ROOM:
                create_trap_room(game_map, room, entities)

            elif room.room_type == RoomTypes.PUZZLE_ROOM:
                create_puzzle_room(game_map, room, entities)

            elif room.room_type == RoomTypes.COMBAT_ROOM:
                create_combat_room(game_map, room, entities)

            elif room.room_type == RoomTypes.MYSTERY_ROOM:
                create_mystery_room(game_map, room, entities)


# TODO: different layouts e.g. corners, t-junction, tunnels, dead ends of all four possible alignments.
def create_basic_room_layout(room):
    north_door = Rect(11, 0, 4, 4)
    south_door = Rect(11, 26, 4, 4)
    east_door = Rect(26, 13, 4, 4)
    west_door = Rect(0, 13, 4, 4)
    main_area = Rect(4, 4, 22, 22)

    to_carve = [north_door, east_door, south_door, west_door, main_area]

    room.viable_area = []
    for area in to_carve:
        room.viable_area.extend(area.carve_rect(room))


def create_exit_room(game_map, room, entities):
    room.colours = white
    pillar1 = Rect(7, 7, 6, 6)  # Top Left
    pillar1.fill_rect(room)

    pillar2 = Rect(17, 7, 6, 6)  # Top Right
    pillar2.fill_rect(room)

    pillar3 = Rect(7, 17, 6, 6)  # Bottom Left
    pillar3.fill_rect(room)

    pillar4 = Rect(17, 17, 6, 6)  # Bottom Right
    pillar4.fill_rect(room)

    centre = Rect(11, 11, 8, 8)
    centre.carve_rect(room)

    middle = Rect(13, 13, 4, 4)
    middle.fill_rect(room)


def create_trap_room(game_map, room, entities):
    room.colours = blue


def create_puzzle_room(game_map, room, entities):
    room.colours = green


def create_mystery_room(game_map, room, entities):
    room_to_be = choice([RoomTypes.COMBAT_ROOM, RoomTypes.PUZZLE_ROOM, RoomTypes.TRAP_ROOM])

    if room_to_be == RoomTypes.TRAP_ROOM:
        create_trap_room(game_map, room, entities)

    elif room_to_be == RoomTypes.PUZZLE_ROOM:
        create_puzzle_room(game_map, room, entities)

    elif room_to_be == RoomTypes.COMBAT_ROOM:
        create_combat_room(game_map, room, entities)

    room.colours = yellow


def create_combat_room(game_map, room, entities):
    room.colours = red
    place_entities(game_map, room, entities, 5, 1)


def place_entities(game_map, room, entities, max_monsters_per_room, max_items_per_room):
    for i in range(randint(1, max_monsters_per_room)):
        room_x, room_y = choice(room.viable_area)

        if not any([entity for entity in entities if entity.current_room == room.room_id and entity.room_x == room_x and entity.room_y == room_y]):
            monster_template = choice(monsters_list)
            monster = pick_monster(game_map, room.room_id, room_x, room_y, monster_template)
            entities.append(monster)  # This is that list from engine with just the player in it.

    # TODO: Create pick_item function
    # for j in range(randint(1, max_items_per_room)):
    #     room_x, room_y = choice(room.viable_area)
    #
    #     if not any([entity for entity in entities if entity.current_room == room.room_id and entity.room_x == room_x and entity.room_y == room_y]):
    #         item_template = choice(items_list)
    #         item = pick_item(game_map, room.room_id, room_x, room_y, item_template)
    #         entities.append(item)  # This is that list from engine with just the player in it.


def pick_monster(game_map, room_id, room_x, room_y, monster_template):
        name, char, colour, hits, weapon = monster_template

        weapon_name, weapon_char, weapon_colour, weapon_power, weapon_uses = weapon

        weapon_stats = Weapon(weapon_power, weapon_uses)
        monster_weapon = Item(game_map, room_id, room_x, room_y, weapon_name, weapon_char, weapon_colour, weapon=weapon_stats)

        fighter_component = Fighter(hits, left_hand=monster_weapon)
        ai_component = BasicMonster()
        monster = Actor(game_map, room_id, room_x, room_y, name, char, colour, fighter=fighter_component, ai=ai_component)

        return monster
