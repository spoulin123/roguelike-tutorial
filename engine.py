#TO DO (beyond the scope of the tutorial):
# (DONE) 1. Implement "look" action without mouse controls
# 2. Implement ranged combat without mouse controls
    #(should be able to change targeting game state to accomplish this easily)
# (DONE) 3. Make lightning not target corpses
# 4. Show fireball radius during targeting
# 5. Get tech department to install shelve2

#Current state of world map:
# -Only moving off right side is currently implemented
# -Player is placed at a location defined by the game map
# -Entities are not deleted. They cant simply be deleted because the player must be able to return to maps
#   -Each GameMap needs a list of entities for itself

import tcod

from entity import get_blocking_entities_at_location, get_fighting_entities_at_location
from input_handlers import handle_keys
from render_functions import clear_all, render_all
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from death_functions import kill_player, kill_monster, destroy_object
from game_messages import Message
from target import Target
from loader_functions.initialize_new_game import get_constants, get_game_variables
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

    player, entities, world_map, message_log, game_state = get_game_variables(constants)

    current_map = world_map.maps[world_map.x][world_map.y]

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
        if move and game_state == GameStates.PLAYER_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if destination_x == current_map.width:
                entities = [player]
                game_map = GameMap(constants['map_width'], constants['map_height'])
                game_map.make_map2(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                    constants['map_width'], constants['map_height'], player, entities,
                    constants['max_monsters_per_room'], constants['max_items_per_room'])
                world_map.move_to(world_map.x+1, world_map.y, game_map)
                current_map = world_map.maps[world_map.x][world_map.y]
                destination_x = 0
                dx = 0
                player.x = 0
                player.y = destination_y
                print(str(world_map.x)+" ,"+str(world_map.y))
            elif destination_y == current_map.height:
                entities = [player]
                game_map = GameMap(constants['map_width'], constants['map_height'])
                game_map.make_map2(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                    constants['map_width'], constants['map_height'], player, entities,
                    constants['max_monsters_per_room'], constants['max_items_per_room'])
                world_map.move_to(world_map.x, world_map.y-1, game_map)
                current_map = world_map.maps[world_map.x][world_map.y]
                destination_y = 0
                dy = 0
                player.y = 0
                player.x = destination_x
                print(str(world_map.x)+" ,"+str(world_map.y))
            elif destination_x == -1:
                entities = [player]
                game_map = GameMap(constants['map_width'], constants['map_height'])
                game_map.make_map2(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                    constants['map_width'], constants['map_height'], player, entities,
                    constants['max_monsters_per_room'], constants['max_items_per_room'])
                world_map.move_to(world_map.x-1, world_map.y, game_map)
                current_map = world_map.maps[world_map.x][world_map.y]
                destination_x = current_map.width-1
                dx = 0
                player.x = current_map.width-1
                player.y = destination_y
                print(str(world_map.x)+" ,"+str(world_map.y))
            elif destination_y == -1:
                entities = [player]
                game_map = GameMap(constants['map_width'], constants['map_height'])
                game_map.make_map2(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                    constants['map_width'], constants['map_height'], player, entities,
                    constants['max_monsters_per_room'], constants['max_items_per_room'])
                world_map.move_to(world_map.x, world_map.y+1, game_map)
                current_map = world_map.maps[world_map.x][world_map.y]
                destination_y = current_map.height-1
                dy = 0
                player.y = current_map.height-1
                player.x = destination_x
                print(str(world_map.x)+" ,"+str(world_map.y))

            if not current_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)
                if target:
                    if target.fighter:
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
