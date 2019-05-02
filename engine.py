#TO DO (beyond the scope of the tutorial):
# (DONE) 1. Implement "look" action without mouse controls
# 2. Implement ranged combat without mouse controls
    #(should be able to change targeting game state to accomplish this easily)
# (DONE) 3. Make lightning not target corpses
# 4. Show fireball radius during targeting
# 5. Get tech department to install shelve2
# 6. Add list of common items to quickly add in game

#Current state of world map:
# -Only moving off right side is currently implemented
# -Player is placed at a location defined by the game map
# -Entities are not deleted. They cant simply be deleted because the player must be able to return to maps
#   -Each GameMap needs a list of entities for itself

#Loading errors:
# Loading a game, exiting the map that was loaded on to, and then returning it causes the player to be invisible
# Error is related to entities = current_map.entities

import tcod

from entity import get_blocking_entities_at_location, get_fighting_entities_at_location
from input_handlers import handle_keys, handle_main_menu
from render_functions import clear_all, render_all
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from death_functions import kill_player, kill_monster, destroy_object
from game_messages import Message
from target import Target
from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import load_game, save_game
from menus import main_menu, message_box
from map_objects.world_map import WorldMap
from map_objects.game_map import GameMap

def main():
    constants = get_constants()

    #sets the font of the console to arial10x10.png
    tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE
        | tcod.FONT_LAYOUT_TCOD)

    #creates a non-fullscreen window with the width and height defined earlier
    #and the title of "Tutorial"
    tcod.console_init_root(constants['screen_width'], constants['screen_height'],
        constants['window_title'], False)

    con = tcod.console_new(constants['screen_width'], constants['screen_height'])
    panel = tcod.console_new(constants['screen_width'], constants['panel_height'])

    player = None
    entities = []
    world_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = tcod.image_load('menu_background.png')

    key = tcod.Key()
    mouse = tcod.Mouse()

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)

        if show_main_menu:
            main_menu(con, main_menu_background_image, constants['screen_width'], constants['screen_height'])

            if show_load_error_message:
                message_box(con, 'No save game to load', 50, constants['screen_width'], constants['screen_height'])

            tcod.console_flush()

            action = handle_main_menu(key)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit_game')

            #get better method for main menu item selection

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
            elif new_game:
                player, entities, world_map, message_log, game_state = get_game_variables(constants)
                game_state = GameStates.PLAYER_TURN

                show_main_menu = False
            elif load_saved_game:
                try:
                    player, entities, world_map, message_log, game_state = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif exit_game:
                break

        else:
            tcod.console_clear(con)
            play_game(player, entities, world_map, message_log, game_state, con, panel, constants)

            show_main_menu = True

def play_game(player, entities, world_map, message_log, game_state, con, panel, constants):
    # print("entities: ")
    # for entity in entities:
    #     print(entity.name)
    current_map = world_map.maps[world_map.x][world_map.y]
    # entities = current_map.entities
    # print("entities: ")
    # for entity in entities:
    #     print(entity.name)

    fov_recompute = True

    fov_map = initialize_fov(current_map)

    key = tcod.Key()
    mouse = tcod.Mouse()

    previous_game_state = game_state

    targeting_item = None
    player_target = Target(0,0)

    #main game loop
    while not tcod.console_is_window_closed():
        #updates the key and mouse variables with any key or mouse events
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)

        if fov_recompute:
            fov_map = initialize_fov(current_map)
            recompute_fov(fov_map, player, constants['fov_radius'], entities,
                constants['fov_light_walls'], constants['fov_algorithm'])

        render_all(con, panel, entities, player, current_map, fov_map, fov_recompute,
            message_log,  constants['screen_width'], constants['screen_height'], constants['bar_width'],
            constants['panel_height'], constants['panel_y'], constants['colors'], game_state, player_target)

        tcod.console_flush()

        clear_all(con, entities)

        action = handle_keys(key, game_state)

        move = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        inventory_index = action.get('inventory_index')
        drop_inventory = action.get('drop_inventory')
        look = action.get('look')
        move_target = action.get('move_target')
        target_selected = action.get('target_selected')

        player_turn_results = []

        #Current errors:
        # (FIXED) x and y are being set to default make_map values in opposite moves
        # diagonal moves off the edge of the map cause a crash
        # !!!FOCUS!!! entity lists are not attached to maps, so buildings remain while entities refresh

        # Need to readd player to returning maps

        #!!!!!!!!!
        #WHEN A USER SAVES AND LOADS ON A GAME_MAP, A PERMANENT "DUMB" COPY OF
        #THEIR BODY IS LEFT AT THE POSITION THEY SAVED AND LOADED
        #UPON SUBSEQUENT RETURNS TO THE MAP
        #
        #THE GLITCH ONLY OCCURS WHEN THE USER LEAVES THE MAP
        #SOMEHOW, PLAYER IS KEPT IN ENTITIES OVER TRANSITIONS
        #!!!!!!!!!
        if move and game_state == GameStates.PLAYER_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if destination_x == current_map.width:
                if world_map.x < 9:
                    world_map.move_to(world_map.x+1, world_map.y, constants, player)
                    current_map = world_map.maps[world_map.x][world_map.y]
                    entities = current_map.entities
                    destination_x = 0
                    dx = 0
                    player.x = 0
                    player.y = destination_y
                else:
                    destination_x = player.x
                    destination_y = player.y
                    message_log.add_message(Message('You can\'t go that way', tcod.blue))
                print(str(world_map.x)+" ,"+str(world_map.y))
            elif destination_y == current_map.height:
                if world_map.y > 0:
                    world_map.move_to(world_map.x, world_map.y-1, constants, player)
                    current_map = world_map.maps[world_map.x][world_map.y]
                    entities = current_map.entities
                    destination_y = 0
                    dy = 0
                    player.y = 0
                    player.x = destination_x
                else:
                    destination_x = player.x
                    destination_y = player.y
                    message_log.add_message(Message('You can\'t go that way', tcod.blue))
                print(str(world_map.x)+" ,"+str(world_map.y))
            elif destination_x == -1:
                if world_map.x > 0:
                    world_map.move_to(world_map.x-1, world_map.y, constants, player)
                    current_map = world_map.maps[world_map.x][world_map.y]
                    entities = current_map.entities
                    destination_x = current_map.width-1
                    dx = 0
                    player.x = current_map.width-1
                    player.y = destination_y
                else:
                    destination_x = player.x
                    destination_y = player.y
                    message_log.add_message(Message('You can\'t go that way', tcod.blue))
                print(str(world_map.x)+" ,"+str(world_map.y))
            elif destination_y == -1:
                if world_map.y < 9:
                    world_map.move_to(world_map.x, world_map.y+1, constants, player)
                    current_map = world_map.maps[world_map.x][world_map.y]
                    entities = current_map.entities
                    destination_y = current_map.height-1
                    dy = 0
                    player.y = current_map.height-1
                    player.x = destination_x
                else:
                    destination_x = player.x
                    destination_y = player.y
                    message_log.add_message(Message('You can\'t go that way', tcod.blue))
                print(str(world_map.x)+" ,"+str(world_map.y))

            if not current_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)
                if target:
                    if target.fighter and target != player:
                        attack_results = player.fighter.attack(target)
                        player_turn_results.extend(attack_results)
                    elif target.breakable:
                        attack_results = player.fighter.attack(target)
                        player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)
                    fov_recompute = True

            game_state = GameStates.ENEMY_TURN

        elif pickup and game_state == GameStates.PLAYER_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)
                    break
            else:
                message_log.add_message(Message('There is nothing here to pick up', tcod.yellow))

        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if look:
            previous_game_state = game_state
            player_target.set(player.x, player.y)
            game_state = GameStates.LOOKING

        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
            item = player.inventory.items[inventory_index]
            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities = entities, fov_map = fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.LOOKING):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                save_game(player, entities, world_map, message_log, game_state)

                return True

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        if game_state == GameStates.TARGETING:
            if move_target:
                dx, dy = move_target
                player_target.move(dx, dy)
            if target_selected:
                item_use_results = player.inventory.use(targeting_item,
                    entities=entities, fov_map=fov_map, target_x=player_target.x,
                        target_y=player_target.y)
                player_turn_results.extend(item_use_results)


        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            destroyed_entity = player_turn_result.get('destroyed')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')

            if message:
                message_log.add_message(message)

            if targeting_cancelled:
                game_state = previous_game_state
                message_log.add_message(Message('Targeting cancelled'))

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            if destroyed_entity:
                message = destroy_object(destroyed_entity)
                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)

                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = GameStates.PLAYER_TURN
                game_state = GameStates.TARGETING
                player_target.set(player.x, player.y)

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

            if item_dropped:
                entities.append(item_dropped)
                game_state = GameStates.ENEMY_TURN

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, current_map, entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

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

                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:
                game_state = GameStates.PLAYER_TURN

        if game_state == GameStates.LOOKING and move_target:
            dx, dy = move_target
            player_target.move(dx, dy)


if __name__ == '__main__':
    main()
