import tcod

from game_states import GameStates

def handle_keys(key, game_state):
    if game_state == GameStates.PLAYER_TURN:
        return handle_player_turn_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory_keys(key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)
    elif game_state == GameStates.LOOKING:
        return handle_looking_keys(key)

    return {}

def handle_player_turn_keys(key):
    key_char = chr(key.c)
    #movement keys
    if key.vk == tcod.KEY_KP8:
        return {'move' : (0, -1)}
    elif key.vk == tcod.KEY_KP9:
        return {'move' : (1, -1)}
    elif key.vk == tcod.KEY_KP6:
        return {'move' : (1, 0)}
    elif key.vk == tcod.KEY_KP3:
        return {'move' : (1, 1)}
    elif key.vk == tcod.KEY_KP2:
        return {'move' : (0, 1)}
    elif key.vk == tcod.KEY_KP1:
        return {'move' : (-1, 1)}
    elif key.vk == tcod.KEY_KP4:
        return {'move' : (-1, 0)}
    elif key.vk == tcod.KEY_KP7:
        return {'move' : (-1, -1)}

    #pick up item
    if key_char == 'g':
        return {'pickup' : True}

    #open inventory
    if key_char == 'i':
        return {'show_inventory': True}

    #drop item from inventory
    if key_char == 'd':
        return {'drop_inventory': True}

    #look
    if key_char == 'l':
        return {'look': True}

    #toggle fullscreen
    if key.vk == tcod.KEY_ENTER and key.lalt:
        return {'fullscreen' : True}

    if key.vk == tcod.KEY_ESCAPE:
        return {'exit' : True}

    return {}

def handle_player_dead_keys(key):
    key_char = chr(key.c)

    #open inventory
    if key_char == 'i':
        return {'show_inventory': True}

    #toggle fullscreen
    if key.vk == tcod.KEY_ENTER and key.lalt:
        return {'fullscreen' : True}

    if key.vk == tcod.KEY_ESCAPE:
        return {'exit' : True}

    return {}

def handle_inventory_keys(key):
    index = key.c - ord('a')

    if index >= 0:
        return {'inventory_index': index}

    if key.vk == tcod.KEY_ENTER and key.lalt:
        return {'fullscreen' : True}

    if key.vk == tcod.KEY_ESCAPE:
        return {'exit' : True}

    return {}

def handle_targeting_keys(key):
    if key.vk == tcod.KEY_KP8:
        return {'move_target' : (0, -1)}
    elif key.vk == tcod.KEY_KP9:
        return {'move_target' : (1, -1)}
    elif key.vk == tcod.KEY_KP6:
        return {'move_target' : (1, 0)}
    elif key.vk == tcod.KEY_KP3:
        return {'move_target' : (1, 1)}
    elif key.vk == tcod.KEY_KP2:
        return {'move_target' : (0, 1)}
    elif key.vk == tcod.KEY_KP1:
        return {'move_target' : (-1, 1)}
    elif key.vk == tcod.KEY_KP4:
        return {'move_target' : (-1, 0)}
    elif key.vk == tcod.KEY_KP7:
        return {'move_target' : (-1, -1)}

    if key.vk == tcod.KEY_ENTER:
        return {'target_selected': True}

    if key.vk == tcod.KEY_ESCAPE:
        return {'exit' : True}

    return {}

def handle_looking_keys(key):
    if key.vk == tcod.KEY_KP8:
        return {'move_target' : (0, -1)}
    elif key.vk == tcod.KEY_KP9:
        return {'move_target' : (1, -1)}
    elif key.vk == tcod.KEY_KP6:
        return {'move_target' : (1, 0)}
    elif key.vk == tcod.KEY_KP3:
        return {'move_target' : (1, 1)}
    elif key.vk == tcod.KEY_KP2:
        return {'move_target' : (0, 1)}
    elif key.vk == tcod.KEY_KP1:
        return {'move_target' : (-1, 1)}
    elif key.vk == tcod.KEY_KP4:
        return {'move_target' : (-1, 0)}
    elif key.vk == tcod.KEY_KP7:
        return {'move_target' : (-1, -1)}

    if key.vk == tcod.KEY_ESCAPE:
        return {'exit' : True}

    return{}

def handle_main_menu(key):
    key_char = chr(key.c)

    if key_char == 'n':
        return {'new_game': True}
    elif key_char == 'l':
        return {'load_game': True}
    elif key_char == 'e' or  key.vk == tcod.KEY_ESCAPE:
        return {'exit_game': True}

    return {}
