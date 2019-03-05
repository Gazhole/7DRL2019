import tdl
from map_functions import GameMap
from entities import Actor, get_blocking_entities_at_location
from game_states import GameStates
from render import render_all, clear_all
from input_functions import handle_keys
from message_log import MessageLog


def main():
    tdl.set_font('lucida12x12.png', greyscale=True, altLayout=True)  # Load the font from a png.
    tdl.set_fps(100)

    map_width = 5
    map_height = 5

    room_width = 30
    room_height = 30

    screen_width = room_width + 2
    screen_height = room_height + 22

    root_console = tdl.init(screen_width, screen_height, title='7DRL 2019')
    top_panel_console = tdl.Console(room_width, 10)
    view_port_console = tdl.Console(room_width, room_height)
    bottom_panel_console = tdl.Console(room_width, 10)
    message_log = MessageLog(0, 0, room_width, 10)

    game_map = GameMap(map_width, map_height)
    player = Actor(game_map, "22", 15, 15, "Bolly", "@", (255, 255, 255))

    all_consoles = [root_console, view_port_console, bottom_panel_console, top_panel_console]
    entities = [player]

    fov_algorithm = "BASIC"
    fov_light_walls = True
    fov_radius = 10
    fov_recompute = True

    game_state = GameStates.PLAYER_TURN

    while not tdl.event.is_window_closed():
        if fov_recompute:  # Compute the field of view to show changes.
            game_map.rooms[player.map_x][player.map_y]\
                .compute_fov(player.room_x, player.room_y,
                             fov=fov_algorithm, radius=fov_radius, light_walls=fov_light_walls, sphere=True)

            render_all(all_consoles, game_map, entities, player, fov_recompute, message_log)
            tdl.flush()
            clear_all(view_port_console, entities)
            fov_recompute = False

        for event in tdl.event.get():
            if event.type == 'KEYUP':
                user_input = event
                break

        else:
            user_input = None

        if not user_input:
            continue

        action = handle_keys(user_input)

        move = action.get('move')
        exit_game = action.get('exit_game')
        shuffle_rooms = action.get('shuffle_rooms')

        if shuffle_rooms:
            message = game_map.shuffle_rooms(player)
            message_log.add_message(message)
            fov_recompute = True

        if move and game_state == GameStates.PLAYER_TURN:
            dx, dy = move
            destination_room_x = player.room_x + dx
            destination_room_y = player.room_y + dy

            # Check whether we need to transition between rooms.
            # TODO build this into the move method for Actors.
            if destination_room_x < 0:
                dx = 0

                if player.map_x - 1 < 0:
                    player.map_x = map_width - 1
                else:
                    player.map_x -= 1

                player.room_x = room_width - 1

            if destination_room_x == room_width:
                destination_room_x -= 1
                dx = 0

                if player.map_x + 1 > map_width - 1:
                    player.map_x = 0
                else:
                    player.map_x += 1

                player.room_x = 0

            if destination_room_y < 0:
                dy = 0

                if player.map_y - 1 < 0:
                    player.map_y = map_height - 1
                else:
                    player.map_y -= 1

                player.room_y = room_height - 1

            if destination_room_y == room_height:
                destination_room_y -= 1
                dy = 0

                if player.map_y + 1 > map_height - 1:
                    player.map_y = 0
                else:
                    player.map_y += 1

                player.room_y = 0

            if game_map.rooms[player.map_x][player.map_y].walkable[destination_room_x, destination_room_y]:
                target = get_blocking_entities_at_location(entities, destination_room_x, destination_room_y)

                if target:  # Combat here
                    pass

                else:
                    player.move(dx, dy)  # Or just move
                    fov_recompute = True

        if exit_game:
            return True


if __name__ == "__main__":
    main()
