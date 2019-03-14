from tdl.map import Map
from collections import namedtuple
from enum import Enum
from entities import Actor, Item
from components import Fighter, BasicMonster, Weapon
from templates import monsters_list
import random

PRNG = random.Random()
seed = random.Random()
PRNG.seed(seed)
choice = PRNG.choice
shuffle = PRNG.shuffle
randint = PRNG.randint

# Colours
colours = namedtuple("colours", ["light_wall", "dark_wall", "light_ground", "dark_ground"])
white = colours((250, 250, 250), (160, 160, 160), (110, 110, 110), (40, 40, 40))
red = colours((250, 65, 65), (160, 35, 35), (110, 30, 30), (40, 10, 10))
blue = colours((65, 125, 250), (35, 75, 160), (30, 60, 110), (10, 20, 40))
green = colours((0, 250, 0), (0, 160, 0), (0, 110, 0), (0, 40, 0))
yellow = colours((250, 180, 0), (160, 110, 0), (110, 70, 0), (40, 10, 0))


class RoomComponentTypes(Enum):
    main_area = 0
    north_exit = 1
    west_exit = 2
    south_exit = 3
    east_exit = 4


class Schematic(Enum):
    """
    This contains static variables to delimit each possible room schematic.
    """
    FOUR_WAY = 0
    NORTH_TEE = 1
    EAST_TEE = 2
    SOUTH_TEE = 3
    WEST_TEE = 4
    NORTH_SOUTH_TUNNEL = 5
    WEST_EAST_TUNNEL = 6
    NORTH_EAST_CORNER = 7
    NORTH_WEST_CORNER = 8
    SOUTH_EAST_CORNER = 9
    SOUTH_WEST_CORNER = 10
    NORTH_DEAD = 11
    EAST_DEAD = 12
    SOUTH_DEAD = 13
    WEST_DEAD = 14


class Rect:
    """
    Rect class takes an initial x,y coordinate as the top left of a rectangle, and using width and height
    generates all coordinates in that area.
    """
    def __init__(self, room_x, room_y, rect_width, rect_height):
        self.x1 = room_x
        self.y1 = room_y
        self.x2 = self.x1 + rect_width
        self.y2 = self.y1 + rect_height

    def carve_rect(self, room):  # Create a walkable area in the room object the shape of this Rect, return coords.
        carved_coordinates = []
        for x in range(self.x1, self.x2):
            for y in range(self.y1, self.y2):
                room.walkable[x, y] = True
                room.transparent[x, y] = True
                carved_coordinates.append((x, y))
        return carved_coordinates

    def fill_rect(self, room):  # Create a solid area in the room object the shape of this Rect, return coords.
        filled_coordinates = []
        for x in range(self.x1, self.x2):
            for y in range(self.y1, self.y2):
                room.walkable[x, y] = False
                room.transparent[x, y] = False
                filled_coordinates.append((x, y))
        return filled_coordinates

    def ghost_rect(self):  # Only coordinates returned, no interaction with room object.
        coordinates = []
        for x in range(self.x1, self.x2):
            for y in range(self.y1, self.y2):
                coordinates.append((x, y))
        return coordinates


class RoomComponent:
    """
    A room component is a unit which stores it's coordinates, and can create itself in a room.
    In practice this could be either a walkable area or a blocked off area.
    This is usually either the main room, an exit location, or walls inside a room.
    """
    def __init__(self, x, y, w, h, walkable=True):
        self.rect = Rect(x, y, w, h)
        self.coordinates = self.rect.ghost_rect()

        if walkable:
            self.create = self.rect.carve_rect
        else:
            self.create = self.rect.fill_rect


def create_room_component(component_type):
    if component_type == RoomComponentTypes.main_area:
        room_component = RoomComponent(4, 4, 22, 22, walkable=True)

    elif component_type == RoomComponentTypes.north_exit:
        room_component = RoomComponent(4, 0, 22, 4, walkable=True)

    elif component_type == RoomComponentTypes.east_exit:
        room_component = RoomComponent(26, 4, 4, 22, walkable=True)

    elif component_type == RoomComponentTypes.south_exit:
        room_component = RoomComponent(4, 26, 22, 4, walkable=True)

    elif component_type == RoomComponentTypes.west_exit:
        room_component = RoomComponent(0, 4, 4, 22, walkable=True)
    else:
        room_component = RoomComponent(0, 0, 0, 0, walkable=False)

    return room_component


class RoomLayout:
    """
    The room layout is a holding class for multiple room components.
    Arguments are the four cardinal exit locations (optional) and the main central area.
    Later on this could also include an iterable of features within the room.
    The room layout can create itself within a room via a function taking the room as an argument.
    """
    def __init__(self, main_area, north_exit=False, east_exit=False, west_exit=False, south_exit=False):
        self.north_exit = north_exit
        self.west_exit = west_exit
        self.south_exit = south_exit
        self.east_exit = east_exit
        self.main_area = main_area


class GameMap:
    def __init__(self, map_width, map_height):
        self.map_width = map_width
        self.map_height = map_height
        self.rooms = self.initialise_rooms()

        self.rooms_index = {}  # This is a dictionary to keep track of where each room is in the GameMap object.
        self.update_rooms_index()

        self.create_room_layouts()

    def initialise_rooms(self):
        rooms = [[Room(30, 30, room_id=str(map_x) + "x" + str(map_y), room_layout=False)
                  for map_y in range(self.map_height)] for map_x in range(self.map_width)]

        return rooms

    def update_rooms_index(self):
        for y in range(self.map_height):
            for x in range(self.map_width):
                self.rooms_index[self.rooms[x][y].room_id] = {"map_x": x, "map_y": y, "room_layout": None}

    def create_room_layouts(self):
        for y in range(self.map_height):
            for x in range(self.map_width):
                self.rooms_index[self.rooms[x][y].room_id]["room_layout"] = RoomLayout(create_room_component(RoomComponentTypes.main_area))
                self.rooms[x][y].room_layout = self.rooms_index[self.rooms[x][y].room_id]["room_layout"]

    def print_map(self):
        for y in range(self.map_height):
            print("")
            for x in range(self.map_width):
                if not self.rooms[x][y].room_layout:
                    print(" ", end="")
                else:
                    if self.rooms[x][y].branch_level == 0:
                        print(".", end=' ')
                    else:
                        print(self.rooms[x][y].branch_level, end=" ")
        print("\n")


class Room(Map):
    def __init__(self, room_width, room_height, room_id, room_layout=False):
        super().__init__(room_width, room_height)
        self.room_id = room_id

        self.room_width = room_width
        self.room_height = room_height

        self.explored = [[False for room_y in range(self.room_height)] for room_x in range(self.room_width)]
        self.colours = white

        self.room_layout = room_layout
        self.schematic = None
        self.branch_level = 0


def generate_map(game_map, entities, player):
    all_rooms = {}

    for key in all_rooms:
        print(key, " : ", end='')
        for item in all_rooms[key]:
            print(item.room_id, end=", ")
        print("")

    main_path = create_path(game_map, path_length=10, source_x=10, source_y=10, all_rooms=all_rooms)
    create_branched_rooms(game_map, iterations=5, all_rooms=all_rooms)
    game_map.print_map()

    player.current_room = main_path[0].room_id
    player.set_map_position(game_map)

    # TODO : take all the rooms created, and figure out how to create loops between branches (nearby rooms).
    # TODO : apply room "decorators"
    # TODO : apply room types (combat, puzzle, etc)


# TODO: could we re-use this in the branches section and nest this in each branch?
def create_path(game_map, path_length, source_x, source_y, all_rooms):
    branch_level = 1
    rooms_in_path = []  # This will be returned by this function to be used creating branches off the main path.
    room_count = 0  # Track how many rooms have been made.

    # Choose whether the path will walk north or south and east or west (1 for south east, -1 for northwest)
    # The value assigned will be used as a modifier to the coordinates of the map array position with each room step.
    horizontal_direction = choice([-1, 1])
    vertical_direction = choice([-1, 1])

    vertical_movement = (0, vertical_direction)
    horizontal_movement = (horizontal_direction, 0)

    current_x = source_x
    current_y = source_y

    while room_count < path_length:
        movement_direction = choice([vertical_movement, horizontal_movement])
        dx, dy = movement_direction

        rooms_in_path.append(create_linked_room(game_map, current_x, current_y, dx, dy, branch_level))
        room_count += 1

        current_x, current_y = validate_coords(current_x, current_y, dx, dy, game_map.map_height, game_map.map_width)

    all_rooms[branch_level] = rooms_in_path
    return rooms_in_path


# TODO: fix bug where a room is created without a main area.
# TODO: why is branch level 6 running twice?
# TODO: figure out how the branching works...can we spread it out more?
def create_branched_rooms(game_map, iterations, all_rooms):
    for i in range(iterations):
        branch_level = i + 2
        rooms_in_this_branch = []

        if branch_level == 2:
            rooms_to_branch = all_rooms[branch_level - 1][1:-1:int(iterations/2)]
        else:
            rooms_to_branch = all_rooms[branch_level - 1]

        for room in rooms_to_branch:
            current_map_x = game_map.rooms_index[room.room_id]["map_x"]
            current_map_y = game_map.rooms_index[room.room_id]["map_y"]

            unused_exits = get_unused_exits(room)

            if not unused_exits:
                continue
            else:
                new_exit = choice(unused_exits)
                add_component_to_room(room, new_exit)
                add_component_to_room(room, RoomComponentTypes.main_area)
                room.branch_level = branch_level

            adjacent_room = get_adjacent_room(game_map, current_map_x, current_map_y, new_exit)

            add_component_to_room(adjacent_room, RoomComponentTypes.main_area)
            add_component_to_room(adjacent_room, get_opposite_exit(new_exit))

            adjacent_room.branch_level = branch_level
            rooms_in_this_branch.append(adjacent_room)

        all_rooms[branch_level] = []
        all_rooms[branch_level].extend(rooms_in_this_branch)
        branch_level += 1


def validate_coords(current_x, current_y, dx, dy, map_width, map_height):
    new_x = current_x + dx
    new_y = current_y + dy

    if new_x != current_x:
        if new_x < 0:
            new_x = map_width - 1

        elif new_x == map_width:
            new_x = 0

    if new_y != current_y:
        if new_y < 0:
            new_y = map_height - 1

        elif new_y == map_height:
            new_y = 0

    return new_x, new_y


def create_linked_room(game_map, current_x, current_y, dx, dy, branch_level):
    linked_x, linked_y = validate_coords(current_x, current_y, dx, dy, game_map.map_width, game_map.map_height)

    current_room = game_map.rooms[current_x][current_y]
    linked_room = game_map.rooms[linked_x][linked_y]

    if dx == 1:
        current_exit = RoomComponentTypes.east_exit
        linked_exit = RoomComponentTypes.west_exit
    elif dx == -1:
        current_exit = RoomComponentTypes.west_exit
        linked_exit = RoomComponentTypes.east_exit
    else:
        pass

    if dy == 1:
        current_exit = RoomComponentTypes.south_exit
        linked_exit = RoomComponentTypes.north_exit
    elif dy == -1:
        current_exit = RoomComponentTypes.north_exit
        linked_exit = RoomComponentTypes.south_exit
    else:
        pass

    add_component_to_room(current_room, RoomComponentTypes.main_area)
    add_component_to_room(current_room, current_exit)
    add_component_to_room(linked_room, linked_exit)

    current_room.branch_level = branch_level

    return current_room


def add_component_to_room(room, component_type):
    if component_type == RoomComponentTypes.north_exit:
        room.room_layout.north_exit = create_room_component(component_type)
        room.room_layout.north_exit.create(room)

    elif component_type == RoomComponentTypes.east_exit:
        room.room_layout.east_exit = create_room_component(component_type)
        room.room_layout.east_exit.create(room)

    elif component_type == RoomComponentTypes.south_exit:
        room.room_layout.south_exit = create_room_component(component_type)
        room.room_layout.south_exit.create(room)

    elif component_type == RoomComponentTypes.west_exit:
        room.room_layout.west_exit = create_room_component(component_type)
        room.room_layout.west_exit.create(room)

    elif component_type == RoomComponentTypes.main_area:
        room.room_layout.main_area = create_room_component(component_type)
        room.room_layout.main_area.create(room)


def get_unused_exits(room):
    unused_exits = []

    if not room.room_layout.north_exit:
        unused_exits.append(RoomComponentTypes.north_exit)

    if not room.room_layout.east_exit:
        unused_exits.append(RoomComponentTypes.east_exit)

    if not room.room_layout.south_exit:
        unused_exits.append(RoomComponentTypes.south_exit)

    if not room.room_layout.west_exit:
        unused_exits.append(RoomComponentTypes.west_exit)

    return unused_exits


def get_adjacent_room(game_map, current_map_x, current_map_y, new_exit):

    if new_exit == RoomComponentTypes.north_exit:
        dx = 0
        dy = -1

    elif new_exit == RoomComponentTypes.east_exit:
        dx = 1
        dy = 0

    elif new_exit == RoomComponentTypes.south_exit:
        dx = 0
        dy = 1

    elif new_exit == RoomComponentTypes.west_exit:
        dx = -1
        dy = 0

    adjacent_x, adjacent_y = validate_coords(current_map_x, current_map_y, dx, dy, game_map.map_width, game_map.map_height)
    adjacent_room = game_map.rooms[adjacent_x][adjacent_y]

    return adjacent_room


def get_opposite_exit(exit_component_type):
    if exit_component_type == RoomComponentTypes.north_exit:
        opposite_exit = RoomComponentTypes.south_exit

    elif exit_component_type == RoomComponentTypes.east_exit:
        opposite_exit = RoomComponentTypes.west_exit

    elif exit_component_type == RoomComponentTypes.south_exit:
        opposite_exit = RoomComponentTypes.north_exit

    elif exit_component_type == RoomComponentTypes.west_exit:
        opposite_exit = RoomComponentTypes.east_exit

    return opposite_exit


def place_entities(game_map, room, entities, max_monsters_per_room, max_items_per_room):
    for i in range(randint(1, max_monsters_per_room)):
        room_x, room_y = choice(room.coordinates)

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
