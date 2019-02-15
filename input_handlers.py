import tcod

from game_states import GameStates

def handle_keys(key, game_state):
    if game_state == GameStates.PLAYER_TURN:
        return handle_player_turn_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory_keys(key)

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
