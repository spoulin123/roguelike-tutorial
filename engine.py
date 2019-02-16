#TO DO (beyond the scope of the tutorial):
# (DONE) 1. Implement "look" action without mouse controls
# 2. Implement ranged combat without mouse controls
    #(should be able to change targeting game state to accomplish this easily)
# (DONE) 3. Make lightning not target corpses
import tcod


from entity import Entity, get_blocking_entities_at_location
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from render_functions import clear_all, render_all, RenderOrder
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from components.fighter import Fighter
from death_functions import kill_player, kill_monster
from game_messages import Message, MessageLog
from components.inventory import Inventory
from target import Target

def main():
    #sets varaibles for screen width and height (used later on)
    screen_width = 80
    screen_height = 50

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithim = 0
    fov_light_walls = True
    fov_radius = 10

    max_monsters_per_room = 3
    max_items_per_room = 2

    colors = {
        'dark_wall': tcod.Color(0, 0, 100),
        'dark_ground': tcod.Color(50, 50, 150),
        'light_wall': tcod.Color(130, 110, 50),
        'light_ground': tcod.Color(200, 180, 50),
        'black' :tcod.Color(0, 0, 0),
        'white' :tcod.Color(255, 255, 255)
    }

    fighter_component = Fighter(hp = 30, defense = 2, power = 5)
    inventory_component = Inventory(26)
    player = Entity(0, 0, '@', tcod.white, 'Player', blocks = True, render_order=RenderOrder.ACTOR, fighter = fighter_component, inventory = inventory_component)
    entities = [player]

    #sets the font of the console to arial10x10.png
    tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE
        | tcod.FONT_LAYOUT_TCOD)

    #creates a non-fullscreen window with the width and height defined earlier
    #and the title of "Tutorial"
    tcod.console_init_root(screen_width, screen_height, "Tutorial", False)

    con = tcod.console_new(screen_width, screen_height - panel_height)
    panel = tcod.console_new(screen_width, panel_height)

    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room, max_items_per_room)

    fov_recompute = True

    fov_map = initialize_fov(game_map)

    message_log = MessageLog(message_x, message_width, message_height)

    key = tcod.Key()
    mouse = tcod.Mouse()

    game_state = GameStates.PLAYER_TURN
    previous_game_state = game_state

    player_target = Target(0,0)

    #main game loop
    while not tcod.console_is_window_closed():
        #updates the key and mouse variables with any key or mouse events
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithim)

        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute,
            message_log, screen_width, screen_height, bar_width, panel_height,
            panel_y, colors, game_state, player_target)

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


        player_turn_results = []

        if move and game_state == GameStates.PLAYER_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)
                if target:
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
            else:
                return True

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            targeting = player_turn_result.get('targeting')

            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)

                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if item_dropped:
                entities.append(item_dropped)

                game_state = GameStates.ENEMY_TURN

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

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
