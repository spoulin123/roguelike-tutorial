import tcod
from enum import Enum
from game_states import GameStates
from menus import inventory_menu
#from target import Target

class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3

def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    tcod.console_set_default_background(panel, back_color)
    tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_foreground(panel, tcod.white)
    tcod.console_print_ex(panel, int(x + total_width/2), y, tcod.BKGND_NONE, tcod.CENTER, "{0}: {1}/{2}".format(name, value, maximum))


def render_all(con, panel, entities, player, game_map, fov_map, fov_recompute,
    message_log, screen_width, screen_height, bar_width, panel_height, panel_y,
    colors, game_state, current_enemy, player_target):
    if fov_recompute:
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = tcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        tcod.console_set_char_background(con, x, y, colors.get('light_wall'), tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(con, x, y, colors.get('light_ground'), tcod.BKGND_SET)

                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    if wall:
                        tcod.console_set_char_background(con, x, y, colors.get('dark_wall'), tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(con, x, y, colors.get('dark_ground'), tcod.BKGND_SET)
                elif game_state != GameStates.SHOW_INVENTORY:
                    tcod.console_set_char_background(con, x, y, colors.get('black'), tcod.BKGND_SET)
                    tcod.console_put_char(con, x, y, ' ', tcod.BKGND_NONE)


    entities_in_render_order = sorted(entities, key = lambda x: x.render_order.value)

    for entity in entities_in_render_order:
        draw_entity(con, entity, fov_map)

    tcod.console_set_default_background(panel, tcod.black)
    tcod.console_clear(panel)

    y = 1
    for message in message_log.messages:
        tcod.console_set_default_foreground(panel, message.color)
        tcod.console_print_ex(panel, message_log.x, y, tcod.BKGND_NONE, tcod.LEFT, message.text)
        y += 1

    render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp, tcod.light_red, tcod.darker_red)
    if current_enemy:
        render_bar(con, int(screen_width/2)-int(bar_width/2), 1, bar_width, 'HP', player.current_enemy.hp, player.current_enemy.max_hp, tcod.light_red, tcod.darker_red)

    if game_state in (GameStates.LOOKING, GameStates.TARGETING):
        tcod.console_set_char_background(con, player_target.x, player_target.y, tcod.light_gray, tcod.BKGND_SET)
        tcod.console_set_default_foreground(panel, tcod.light_gray)
        tcod.console_print_ex(panel, 1, 0, tcod.BKGND_NONE, tcod.LEFT,
            get_names_at_target(entities, fov_map, player_target))

    tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    tcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = 'Press the key next to an item to use it, or use Esc to cancel.\n'
        elif game_state == GameStates.DROP_INVENTORY:
            inventory_title = 'Press the key next to an item to drop it, or use Esc to cancel.\n'

        inventory_menu(con, inventory_title, player.inventory, 50, screen_width, screen_height)

def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)

def draw_entity(con, entity, fov_map):
    if tcod.map_is_in_fov(fov_map, entity.x, entity.y):
        tcod.console_set_default_foreground(con, entity.color)
        tcod.console_put_char(con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)

def clear_entity(con, entity):
    tcod.console_put_char(con, entity.x, entity.y, ' ', tcod.BKGND_NONE)

def get_names_at_target(entities, fov_map, target):
    names = [entity.name for entity in entities if entity.x == target.x and
        entity.y == target.y and tcod.map_is_in_fov(fov_map, entity.x, entity.y)]
    names = ', '.join(names)
    return names.capitalize()
