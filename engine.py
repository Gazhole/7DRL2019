import tdl
from map_system_2 import GameMap, generate_map
from entities import Actor, Item, get_blocking_entities_at_location
from game_states import GameStates
from render import render_all, clear_all
from input_functions import handle_keys
from message_log import MessageLog
from death_functions import kill_monster, kill_player
from components import Fighter, Weapon

def main():
    tdl.set_font('terminal16x16.png', greyscale=True, altLayout=False)  # Load the font from a png.
    tdl.set_fps(100)

    map_width = 20
    map_height = 20

    room_width = 30
    room_height = 30

    screen_width = room_width + 22
    screen_height = room_height + 22

    root_console = tdl.init(screen_width, screen_height, title='7DRL 2019')
    top_panel_console = tdl.Console(screen_width, 10)
    view_port_console = tdl.Console(room_width, room_height)
    bottom_panel_console = tdl.Console(screen_width, 10)
    message_log = MessageLog(0, 0, screen_width, 9)

    entities = []

    game_map = GameMap(map_width, map_height)

    sword_stats = Weapon(2, 10)
    player_weapon = Item(game_map, "0x0", 0, 0, "Sword", "|", (255, 255, 255), weapon=sword_stats)
    player_stats = Fighter(hits=10, left_hand=player_weapon)
    player = Actor(game_map, "2x2", 15, 10, "Player", "@", (255, 255, 255), fighter=player_stats)
    entities.append(player)

    generate_map(game_map, entities, player)

    all_consoles = [root_console, view_port_console, bottom_panel_console, top_panel_console]

    fov_algorithm = "BASIC"
    fov_light_walls = True
    fov_radius = 50
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
        select_hand = action.get('select_hand')
        drop_item = action.get('drop_item')
        pickup_item = action.get('pickup_item')
        shuffle_rooms = action.get('shuffle_rooms')

        player_turn_results = []

        if shuffle_rooms:
            message = game_map.shuffle_rooms(player, entities)
            message_log.add_message(message)
            fov_recompute = True

        # TODO at the moment these functions are doing all the leg work and player_turn_results isn't used. Rectify.

        if select_hand and game_state == GameStates.PLAYER_TURN:
            player.fighter.selected_hand = select_hand
            fov_recompute = True

        if drop_item and game_state == GameStates.PLAYER_TURN:
            message = player.fighter.drop_item(game_map, entities)
            message_log.add_message(message)
            game_state = GameStates.ENEMY_TURN
            fov_recompute = True

        if pickup_item and game_state == GameStates.PLAYER_TURN:
            message = player.fighter.pickup_item(entities)
            message_log.add_message(message)
            game_state = GameStates.ENEMY_TURN
            fov_recompute = True

        if move and game_state == GameStates.PLAYER_TURN:
            dx, dy = move
            destination_room_x = player.room_x + dx
            destination_room_y = player.room_y + dy

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
                target = get_blocking_entities_at_location(entities, player.map_x, player.map_y, destination_room_x, destination_room_y)

                if target:  # Combat here
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)  # Add the result of the last turn to the list
                    fov_recompute = True

                else:
                    player.move(dx, dy)  # Or just move
                    player.set_current_room(game_map)

                    # TODO: Bug with the new room layouts - some cause change of room to break.
                    print("MapPos: ", player.map_x, ",", player.map_y, end=" / ")
                    print("RoomPos: ", player.room_x, ",", player.room_y)
                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN  # Switch over the enemy's turn.

        if exit_game:
            return True

        for player_turn_result in player_turn_results:
            message = player_turn_result.get("message")  # Pull any messages
            dead_entity = player_turn_result.get("dead")  # Or anything that died

            if message:
                message_log.add_message(message)  # Add the message (if any) to the message log to print on screen.

            if dead_entity:  # If anything died...
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)  # Game over
                else:
                    message = kill_monster(dead_entity)  # Print a death message for monster, add exp

                message_log.add_message(message)  # Print messages to screen.

        player_turn_results.clear()  # Clear ready for next turn.

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.map_x == player.map_x and entity.map_y == player.map_y:
                    if entity.ai:  # If the entity has some intelligence (monsters, npc)
                        enemy_turn_results = entity.ai.take_turn(player, game_map, entities)

                        for enemy_turn_result in enemy_turn_results:  # Same deal as the player turns
                            message = enemy_turn_result.get("message")
                            dead_entity = enemy_turn_result.get("dead")

                            if message:
                                message_log.add_message(message)

                            if dead_entity:
                                if dead_entity == player:
                                    message, game_state = kill_player(dead_entity)
                                else:
                                    message = kill_monster(dead_entity)

                                message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                        enemy_turn_results.clear()

                    if game_state == GameStates.PLAYER_DEAD:
                        break

            else:
                game_state = GameStates.PLAYER_TURN


if __name__ == "__main__":
    main()
