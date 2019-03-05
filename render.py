from enum import Enum


class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3


def render_all(consoles, game_map, entities, player, fov_recompute, message_log):

    # Unpack consoles
    root_console, view_port_console, bottom_panel_console, top_panel_console = consoles

    # Load tile characters from map file:
    ground_char = "+"
    wall_char = "#"

    # Draw all the tiles in the game map
    if fov_recompute:
        # Make sure the player is always centered in the view port - but stop when we get to the edge of the map.
        for x, y in game_map.rooms[player.map_x][player.map_y]:

            # Load room colours
            light_wall, dark_wall, light_ground, dark_ground = game_map.rooms[player.map_x][player.map_y].colours

            wall = not game_map.rooms[player.map_x][player.map_y].transparent[x][y]

            if game_map.rooms[player.map_x][player.map_y].fov[x, y]:
                if wall:
                    view_port_console.draw_char(x, y, wall_char, bg=None, fg=light_wall)
                else:
                    view_port_console.draw_char(x, y, ground_char, bg=None, fg=light_ground)

                game_map.rooms[player.map_x][player.map_y].explored[x][y] = True

            elif game_map.rooms[player.map_x][player.map_y].explored[x][y]:
                if wall:
                    view_port_console.draw_char(x, y, wall_char, bg=None, fg=dark_wall)
                else:
                    view_port_console.draw_char(x, y, ground_char, bg=None, fg=dark_ground)

    # Draw all entities in the list
    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    for entity in entities_in_render_order:
        draw_entity(view_port_console, entity, game_map.rooms[player.map_x][player.map_y].fov)

    # Now blit the view port console onto the root console.
    root_console.blit(view_port_console, 1, 11, 30, 30, 0, 0)
    view_port_console.clear()

    # Draw stuff on top panel
    top_panel_console.clear(fg=(255, 255, 255), bg=(0, 0, 0))
    room_coordinates = "(" + str(player.map_x) + "," + str(player.map_y) + ")"
    room_id = game_map.rooms[player.map_x][player.map_y].room_id

    top_panel_console.draw_str(0, 5, room_coordinates, fg=(255, 255, 255), bg=None)
    top_panel_console.draw_str(0, 6, room_id, fg=(255, 255, 255), bg=None)

    # blit top panel to root
    root_console.blit(top_panel_console, 1, 1, 30, 10, 0, 0)

    # Draw stuff on bottom panel
    bottom_panel_console.clear(fg=(255, 255, 255), bg=(0, 0, 0))

    # Print the game messages, one line at a time
    y = message_log.y
    for message in message_log.messages:
        bottom_panel_console.draw_str(message_log.x, y, message.text, bg=None, fg=message.colour)
        y += 1

    # Blit the bottom panel onto the root console.
    root_console.blit(bottom_panel_console, 1, 42, 30, 10, 0, 0)


def clear_all(view_port_console, entities):  # This is dirty...
    for entity in entities:
        clear_entity(view_port_console, entity)


def draw_entity(view_port_console, entity, fov):
    if fov[entity.room_x, entity.room_y]:
        view_port_console.draw_char(entity.room_x, entity.room_y, entity.char, entity.colour, bg=None)


def clear_entity(view_port_console, entity):
    # erase the character that represents this object
    view_port_console.draw_char(entity.room_x, entity.room_y, ' ', entity.colour, bg=None)
