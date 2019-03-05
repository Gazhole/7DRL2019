from tdl.map import Map
from collections import namedtuple
from random import choice, shuffle
from copy import deepcopy
from message_log import Message

colours = namedtuple("colours", ["light_wall", "dark_wall", "light_ground", "dark_ground"])
white = colours((250, 250, 250), (180, 180, 180), (110, 110, 110), (40, 40, 40))
red = colours((250, 65, 65), (180, 45, 45), (110, 30, 30), (40, 10, 10))
blue = colours((65, 125, 250), (45, 90, 180), (30, 60, 110), (10, 20, 40))
green = colours((0, 250, 0), (0, 180, 0), (0, 110, 0), (0, 40, 0))

colour_choices = [white, red, blue, green]


class Rect:
    def __init__(self, room_x, room_y, rect_width, rect_height):
        self.x1 = room_x
        self.y1 = room_y
        self.x2 = self.x1 + rect_width
        self.y2 = self.y1 + rect_height

    def carve_rect(self, room):
        for x in range(self.x1, self.x2):
            for y in range(self.y1, self.y2):
                room.walkable[x, y] = True
                room.transparent[x, y] = True


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
    # TODO how is this going to effect entity placement? At the moment location is stored in the entity itself.
    def shuffle_rooms(self, player):
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

        # # This just checks whether all the rooms are unique based on their code.
        # print_rooms = []
        # for y in range(self.map_height):
        #     for x in range(self.map_width):
        #         print_rooms.append(self.rooms[x][y].room_id)
        # print(sorted(print_rooms))

        return message


class Room(Map):
    def __init__(self, room_width, room_height, map_x, map_y, room_id):
        super().__init__(room_width, room_height)
        self.room_id = room_id
        self.position_in_map = (map_x, map_y)

        self.room_width = room_width
        self.room_height = room_height

        self.explored = [[False for room_y in range(self.room_height)] for room_x in range(self.room_width)]

        self.create_basic_room_layout()
        self.colours = choice(colour_choices)

    def create_basic_room_layout(self):
        north_door = Rect(13, 0, 4, 4)
        south_door = Rect(13, 26, 4, 4)
        east_door = Rect(26, 13, 4, 4)
        west_door = Rect(0, 13, 4, 4)
        main_area = Rect(4, 4, 22, 22)

        to_carve = [north_door, east_door, south_door, west_door, main_area]

        for area in to_carve:
            area.carve_rect(self)
