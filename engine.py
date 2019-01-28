import tcod as libtcod

from entity import Entity
from input_handlers import handle_keys
from render_functions import clear_all, render_all

def main():
    #sets varaibles for screen width and height (used later on)
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45

    player = Entity(int(screen_width / 2), int(screen_height / 2), '@', libtcod.white)
    npc = Entity(int(screen_width / 2 - 5), int(screen_height / 2), '@', libtcod.yellow)
    entities = [npc, player]

    #sets the font of the console to arial10x10.png
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE
        | libtcod.FONT_LAYOUT_TCOD)

    #creates a non-fullscreen window with the width and height defined earlier
    #and the title of "Tutorial"
    libtcod.console_init_root(screen_width, screen_height, "Tutorial", False)

    con = libtcod.console_new(screen_width, screen_height)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    #main game loop
    while not libtcod.console_is_window_closed():
        #updates the key and mouse variables with any key or mouse events
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        render_all(con, entities, screen_width, screen_height)

        libtcod.console_flush()

        clear_all(con, entities)

        action = handle_keys(key)

        move = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move:
            dx, dy = move
            player.move(dx, dy)

        if exit:
            return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())





if __name__ == '__main__':
    main()
