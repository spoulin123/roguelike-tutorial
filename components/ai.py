class BasicMonster:
    def take_turn(self, target, fov_ma, game_map, entities):
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(target) >= 2:
                monster.move_towards(target.x, target.y, game_map, entities)
            elif target.fighter.hp > 0:
                print("The {0} wants to attack the player!".format(monster.name))
