def handle_keys(user_input):
    key_char = user_input.char

    # Movement keys wasd for cardinals, qezx for diagonals
    if key_char == 'w':
        return {'move': (0, -1)}
    elif key_char == 's':
        return {'move': (0, 1)}
    elif key_char == 'a':
        return {'move': (-1, 0)}
    elif key_char == 'd':
        return {'move': (1, 0)}
    elif key_char == 'q':
        return {'move': (-1, -1)}
    elif key_char == 'e':
        return {'move': (1, -1)}
    elif key_char == 'z':
        return {'move': (-1, 1)}
    elif key_char == 'x':
        return {'move': (1, 1)}

    elif user_input.key == "LEFT":
        return {'select_hand': "left"}
    elif user_input.key == "RIGHT":
        return {'select_hand': "right"}
    elif user_input.key == "DOWN":
        return {'drop_item': True}
    elif user_input.key == "UP":
        return {'pickup_item': True}

    if user_input.key == 'ESCAPE':
        # Exit the game
        return {'exit_game': True}

    elif user_input.key == "ENTER":
        return {"shuffle_rooms": True}

    # No key was pressed
    return {}
