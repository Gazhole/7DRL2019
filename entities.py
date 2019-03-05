from render import RenderOrder
import math


class Entity:
    def __init__(self, game_map, room_id, room_x, room_y, name, char, colour, blocks=False, render_order=RenderOrder.CORPSE):
        self.current_room = room_id

        self.map_x, self.map_y = self.set_position_on_map(game_map)
        self.room_x = room_x
        self.room_y = room_y

        self.name = name
        self.char = char
        self.colour = colour

        self.blocks = blocks
        self.render_order = render_order

    def set_position_on_map(self, game_map):
        map_x = game_map.rooms_index[self.current_room]["map_x"]
        map_y = game_map.rooms_index[self.current_room]["map_y"]

        return map_x, map_y



class Actor(Entity):
    def __init__(self, map_x, map_y, room_x, room_y, name, char, colour, blocks=True, render_order=RenderOrder.ACTOR):
        super().__init__(map_x, map_y, room_x, room_y, name, char, colour, blocks=blocks, render_order=render_order)

    def move(self, dx, dy):
        # Move the entity by a given amount
        self.room_x += dx
        self.room_y += dy

    def move_towards(self, target_room_x, target_room_y, game_map, entities):
        path = game_map.compute_path(self.room_x, self.room_y, target_room_x, target_room_y)

        dx = path[0][0] - self.room_x
        dy = path[0][1] - self.room_y

        if game_map.walkable[path[0][0], path[0][1]] and not get_blocking_entities_at_location(entities, self.room_x + dx, self.room_y + dy):
            self.move(dx, dy)

    def distance_to(self, other):
        dx = other.room_x - self.room_x
        dy = other.room_y - self.room_y
        return math.sqrt(dx ** 2 + dy ** 2)


def get_blocking_entities_at_location(entities, destination_room_x, destination_room_y):
    for entity in entities:
        if entity.blocks and entity.room_x == destination_room_x and entity.room_y == destination_room_y:
            return entity
    return None
