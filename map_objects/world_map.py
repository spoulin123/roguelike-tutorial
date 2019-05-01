from map_objects.game_map import GameMap
#from loader_functions.initialize_new_game import get_constants, get_game_variables

# current issue: world_map importing get_constants is circular

class WorldMap:
    def __init__(self, width, height, x, y, constants, player):
        self.maps = [[None for x in range(width)] for y in range(height)]
        self.x = x
        self.y = y
        game_map = GameMap(constants['map_width'], constants['map_height'])
        game_map.make_map(constants['max_buildings'], constants['building_min_size'], constants['building_max_size'],
            constants['map_width'], constants['map_height'], player, game_map.entities,
            constants['max_monsters_per_room'], constants['max_items_per_building'])
        self.maps[x][y] = game_map

    def move_to(self, x, y, constants, player):
        self.x = x
        self.y = y
        if not self.maps[x][y]:
            game_map = GameMap(constants['map_width'], constants['map_height'])
            game_map.make_map(constants['max_buildings'], constants['building_min_size'], constants['building_max_size'],
                constants['map_width'], constants['map_height'], player, game_map.entities,
                constants['max_monsters_per_room'], constants['max_items_per_building'])
            self.maps[x][y] = game_map
        else:
            self.maps[x][y].entities.append(player)
