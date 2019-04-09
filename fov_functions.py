import tcod

def initialize_fov(game_map):
    fov_map = tcod.map_new(game_map.width, game_map.height)

    for y in range(game_map.height):
        for x in range (game_map.width):
            tcod.map_set_properties(fov_map, x, y, not game_map.tiles[x][y].block_sight, not game_map.tiles[x][y].blocked)

    return fov_map

def recompute_fov(fov_map, player, radius, entities, light_walls = True, algorithim = 0):
    for entity in entities:
        if entity != player:
            if entity.sight_passes:
                sight_passes = entity.sight_passes
            sight_passes = (not entity.blocks) or sight_passes
            print(sight_blocked)
            tcod.map_set_properties(fov_map, entity.x, entity.y, sight_passes, not entity.blocks)
    tcod.map_compute_fov(fov_map, player.x, player.y, radius, light_walls, algorithim)
