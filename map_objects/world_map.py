# SHOULD MOVE GAME_MAP CREATION FROM ENGINE TO THIS FILE TO REDUCE REDUNDANCY

class WorldMap:
    def __init__(self, width, height, x, y, game_map):
        self.maps = [[None for x in range(width)] for y in range(height)]
        self.x = x
        self.y = y
        self.maps[x][y] = game_map

    def move_to(self, x, y, game_map):
        self.x = x
        self.y = y
        if not self.maps[x][y]:
            self.maps[x][y] = game_map
        #current_map = self.maps[x][y]
