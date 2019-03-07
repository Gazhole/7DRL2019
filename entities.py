from render import RenderOrder
import math


class Entity:
    def __init__(self, game_map, room_id, room_x, room_y, name, char, colour, blocks=False, render_order=RenderOrder.CORPSE, fighter=False, ai=False):
        self.current_room = room_id

        self.map_x = None
        self.map_y = None
        self.set_map_position(game_map)

        self.room_x = room_x
        self.room_y = room_y

        self.name = name
        self.char = char
        self.colour = colour

        self.blocks = blocks
        self.render_order = render_order

        self.fighter = fighter
        self.ai = ai

        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

    def set_map_position(self, game_map):
        self.map_x = game_map.rooms_index[self.current_room]["map_x"]
        self.map_y = game_map.rooms_index[self.current_room]["map_y"]

    def set_current_room(self, game_map):
        for entry in game_map.rooms_index:
            map_x = game_map.rooms_index[entry]["map_x"]
            map_y = game_map.rooms_index[entry]["map_y"]

            if self.map_x == map_x and self.map_y == map_y:
                self.current_room = entry


class Actor(Entity):
    def __init__(self, game_map, room_id, room_x, room_y, name, char, colour, blocks=True, render_order=RenderOrder.ACTOR, fighter=False, ai=False):
        super().__init__(game_map, room_id, room_x, room_y, name, char, colour, blocks=blocks, render_order=render_order, fighter=fighter, ai=ai)

    def move(self, dx, dy):
        # Move the entity by a given amount
        self.room_x += dx
        self.room_y += dy

    def move_towards(self, target_map_x, target_map_y, target_room_x, target_room_y, game_map, entities):
        path = game_map.rooms[target_map_x][target_map_y].compute_path(self.room_x, self.room_y, target_room_x, target_room_y)

        dx = path[0][0] - self.room_x
        dy = path[0][1] - self.room_y

        if game_map.rooms[target_map_x][target_map_y].walkable[path[0][0], path[0][1]] \
                and not get_blocking_entities_at_location(entities, target_map_x, target_map_y, self.room_x + dx, self.room_y + dy):
            self.move(dx, dy)

    def distance_to(self, other):
        dx = other.room_x - self.room_x
        dy = other.room_y - self.room_y
        return math.sqrt(dx ** 2 + dy ** 2)


def get_blocking_entities_at_location(entities, map_x, map_y, destination_room_x, destination_room_y):
    for entity in entities:
        if entity.map_x == map_x and entity.map_y == map_y:
            if entity.blocks and entity.room_x == destination_room_x and entity.room_y == destination_room_y:
                return entity
    return None


class Item(Entity):
    def __init__(self, game_map, room_id, room_x, room_y, name, char, colour, blocks=False, render_order=RenderOrder.ITEM, weapon=False, consumable=False):
        super().__init__(game_map, room_id, room_x, room_y, name, char, colour, blocks=blocks, render_order=render_order)

        if weapon:
            self.weapon = weapon
            self.consumable = False
        else:
            self.consumable = consumable
            self.weapon = False
