import tcod

from components.fighter import Fighter
from components.inventory import Inventory
from entity import Entity
from game_messages import MessageLog
from game_states import GameStates
from map_objects.game_map import GameMap
from map_objects.world_map import WorldMap
from render_functions import RenderOrder

def get_constants():
    window_title = 'Tutorial'

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

    building_max_size = 8
    building_min_size = 6
    #make_map2(): 30
    #make_map(): 3
    max_buildings = 5

    fov_algorithim = 0
    fov_light_walls = True
    fov_radius = 15

    max_monsters_per_room = 3
    max_items_per_building = 2

    colors = {
        'dark_wall': tcod.Color(0, 0, 100),
        'dark_ground': tcod.Color(50, 50, 150),
        'light_wall': tcod.Color(130, 110, 50),
        'light_ground': tcod.Color(200, 180, 50),
        'black' :tcod.Color(0, 0, 0),
        'white' :tcod.Color(255, 255, 255)
    }

    constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'building_max_size': building_max_size,
        'building_min_size': building_min_size,
        'max_buildings': max_buildings,
        'fov_algorithm': fov_algorithim,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'max_monsters_per_room': max_monsters_per_room,
        'max_items_per_building': max_items_per_building,
        'colors': colors
    }

    return constants

def get_game_variables(constants):
    fighter_component = Fighter(hp = 30, defense = 2, power = 5)
    inventory_component = Inventory(26)
    player = Entity(0, 0, '@', tcod.white, 'Player', blocks = True, render_order=RenderOrder.ACTOR, fighter = fighter_component, inventory = inventory_component)
    entities = [player]

    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_map(constants['max_buildings'], constants['building_min_size'], constants['building_max_size'],
        constants['map_width'], constants['map_height'], player, entities,
        constants['max_monsters_per_room'], constants['max_items_per_building'])

    world_map = WorldMap(10, 10, 0, 0, game_map)

    message_log = MessageLog(constants['message_x'], constants['message_width'],
        constants['message_height'])

    game_state = GameStates.PLAYER_TURN

    return player, entities, world_map, message_log, game_state
