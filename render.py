from enum import Enum


class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3


def render_status_blocks(panel, x, y, current_value, maximum_value, fg_colour, bg_colour):
    x = x
    for i in range(maximum_value):
        panel.draw_str(x, y, " ", None, bg_colour)
        if current_value - 1 >= i:
            panel.draw_str(x, y, " ", None, fg_colour)
        x += 2


def render_status_characters(panel, x, y, current_value, maximum_value, char_code, fg_colour, bg_colour):
    x = x
    for i in range(maximum_value):
        panel.draw_char(x, y, char_code, bg_colour, None)
        if current_value - 1 >= i:
            panel.draw_char(x, y, char_code, fg_colour, None)
        x += 2


def render_status_bar(panel, x, y, width, current_value, maximum_value, bar_colour, back_colour):
    if maximum_value == 0:
        bar_width = width
    else:
        bar_width = int(float(current_value) / maximum_value * width)

        if bar_width == 0 and current_value > 0:  # This avoids rounding errors where the bar is indicating 0 but the value isnt
            bar_width = 1

    # draw background
    panel.draw_rect(x , y, width, 1, None, bg=back_colour)

    # draw the remaining total bar on top
    if bar_width > 0:
        panel.draw_rect(x, y, bar_width, 1, None, bg=bar_colour)


def render_all(consoles, game_map, entities, player, fov_recompute, message_log):

    # Unpack consoles
    root_console, view_port_console, bottom_panel_console, top_panel_console = consoles

    # Single cross = 197, double cross = 206
    # texblock = 177

    ground_char = 197
    wall_char = None

    # Draw all the tiles in the game map
    if fov_recompute:
        # Make sure the player is always centered in the view port - but stop when we get to the edge of the map.
        for x, y in game_map.rooms[player.map_x][player.map_y]:

            # Load room colours
            light_wall, dark_wall, light_ground, dark_ground = game_map.rooms[player.map_x][player.map_y].colours

            wall = not game_map.rooms[player.map_x][player.map_y].transparent[x][y]

            # In FOV
            if game_map.rooms[player.map_x][player.map_y].fov[x, y]:
                if wall:
                    view_port_console.draw_char(x, y, wall_char, bg=light_wall, fg=None)
                else:
                    view_port_console.draw_char(x, y, ground_char, bg=None, fg=light_ground)

                game_map.rooms[player.map_x][player.map_y].explored[x][y] = True

            # Outside FOV, explored already
            elif game_map.rooms[player.map_x][player.map_y].explored[x][y]:
                if wall:
                    view_port_console.draw_char(x, y, wall_char, bg=dark_wall, fg=None)
                else:
                    view_port_console.draw_char(x, y, ground_char, bg=None, fg=dark_ground)

    # Draw all entities in the list
    entities_in_this_room = []
    for entity in entities:
        if entity.map_x == player.map_x and entity.map_y == player.map_y:
            entities_in_this_room.append(entity)

    entities_in_render_order = sorted(entities_in_this_room, key=lambda x: x.render_order.value)

    for entity in entities_in_render_order:
        draw_entity(view_port_console, entity, game_map.rooms[player.map_x][player.map_y].fov)

    # Now blit the view port console onto the root console.
    root_console.blit(view_port_console, 11, 11, 30, 30, 0, 0)
    view_port_console.clear()

    # Draw stuff on top panel
    top_panel_console.clear(fg=(255, 255, 255), bg=(0, 0, 0))

    top_panel_console.draw_str(0, 0, player.name, fg=(255, 255, 255), bg=None)

    top_panel_console.draw_str(0, 2, "Hits: ", fg=(255, 255, 255), bg=None)
    render_status_characters(top_panel_console, 6, 2, player.fighter.hits, player.fighter.max_hits, 3, (200, 0, 0), (255, 255, 255))

    # Equipment
    if player.fighter.right_hand:
        rh_name = player.fighter.right_hand.name
        if player.fighter.right_hand.weapon:
            rh_uses = player.fighter.right_hand.weapon.uses
            rh_max_uses = player.fighter.right_hand.weapon.max_uses
            render_status_bar(top_panel_console, 13, 5, 5, rh_uses, rh_max_uses, (255, 255, 255), (0, 0, 0))
    else:
        rh_name = ""

    if player.fighter.left_hand:
        lh_name = player.fighter.left_hand.name
        if player.fighter.left_hand.weapon:
            lh_uses = player.fighter.left_hand.weapon.uses
            lh_max_uses = player.fighter.left_hand.weapon.max_uses
            render_status_bar(top_panel_console, 13, 4, 5, lh_uses, lh_max_uses, (255, 255, 255), (0, 0, 0))
    else:
        lh_name = ""

    if player.fighter.selected_hand == "right":
        top_panel_console.draw_str(0, 4, "Left Hand : ", fg=(255, 255, 255), bg=None)
        top_panel_console.draw_str(19, 4, lh_name, fg=(255, 255, 255), bg=(0, 0, 0))
        top_panel_console.draw_str(0, 5, "Right Hand: ", fg=(0, 0, 0), bg=(0, 200, 0))
        top_panel_console.draw_str(19, 5, rh_name, fg=(0, 0, 0), bg=(0, 200, 0))

    elif player.fighter.selected_hand == "left":
        top_panel_console.draw_str(0, 4, "Left Hand : ", fg=(0, 0, 0), bg=(0, 200, 0))
        top_panel_console.draw_str(19, 4, lh_name, fg=(0, 0, 0), bg=(0, 200, 0))
        top_panel_console.draw_str(0, 5, "Right Hand: ", fg=(255, 255, 255), bg=None)
        top_panel_console.draw_str(19, 5, rh_name, fg=(255, 255, 255), bg=(0, 0, 0))

    # blit top panel to root
    root_console.blit(top_panel_console, 1, 1, 42, 10, 0, 0)

    # Draw stuff on bottom panel
    bottom_panel_console.clear(fg=(255, 255, 255), bg=(0, 0, 0))

    # Print the game messages, one line at a time
    y = message_log.y
    for message in message_log.messages:
        bottom_panel_console.draw_str(message_log.x, y, message.text, bg=None, fg=message.colour)
        y += 1

    # Blit the bottom panel onto the root console.
    root_console.blit(bottom_panel_console, 1, 42, 50, 10, 0, 0)


def clear_all(view_port_console, entities):  # This is dirty...
    for entity in entities:
        clear_entity(view_port_console, entity)


def draw_entity(view_port_console, entity, fov):
    if fov[entity.room_x, entity.room_y]:
        view_port_console.draw_char(entity.room_x, entity.room_y, entity.char, entity.colour, bg=None)


def clear_entity(view_port_console, entity):
    # erase the character that represents this object
    view_port_console.draw_char(entity.room_x, entity.room_y, ' ', entity.colour, bg=None)
