import tcod

def handle_keys(key):
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

    #toggle fullscreen
    if key.vk == tcod.KEY_ENTER and key.lalt:
        return {'fullscreen' : True}

    if key.vk == tcod.KEY_ESCAPE:
        return {'exit' : True}

    return {}
