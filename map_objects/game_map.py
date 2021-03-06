import tcod
from entity import Entity
from map_objects.tile import Tile
from map_objects.rectangle import Rect
from random import randint
from components.ai import BasicMonster
from components.fighter import Fighter
from components.breakable import Breakable
from render_functions import RenderOrder
from components.item import Item
from item_functions import heal, cast_lightning, cast_fireball, throw_grenade
from game_messages import Message

#TO CHANGE TO NEW MAP GEN:
# 1. line 23 initialize_tiles replace Tile(True) with Tile(False)
# 2. initialize_new_game change max_rooms to a low number (3)


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.entities = []

    def initialize_tiles(self):
        tiles = [[Tile(False) for y in range(self.height)] for x in range(self.width)]
        return tiles

    #needs to choose type of map and set it up
    def make_map(self, max_buildings, building_min_size, building_max_size, map_width, map_height, player, entities, max_enemies, max_items_per_building):


        #ADD TO FUNCTION CALL LATER
        max_trees = 200
        for r in range(max_trees):
            x = randint(0, map_width - 1)
            y = randint(0, map_height - 1)
            breakable_component = Breakable(hp = 20)
            tree = Entity(x, y, '*', tcod.desaturated_green, 'Tree', blocks = True, render_order = RenderOrder.ACTOR, breakable = breakable_component)
            entities.append(tree)

        #self.set_up_wilderness(entities, map_width, map_height)
        #map type:
        type_id = randint(0,2)
        if type_id == 0:
            self.set_up_outpost(entities, map_width, map_height, player, max_buildings, building_min_size, building_max_size, max_enemies)
        else:
            self.set_up_wilderness(entities, map_width, map_height)


        entities.append(player)
        #
        # breakable_component = Breakable(hp = 20)
        # crate = Entity(20, 20, '*', tcod.dark_sepia, 'Crate', blocks = True, render_order = RenderOrder.ACTOR, breakable = breakable_component)
        # entities.append(crate)

    def make_map2(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room, max_items_per_room):
        rooms = []
        num_rooms = 0
        for r in range(max_rooms):
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            new_room = Rect(x, y, w, h)

            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                self.create_room(new_room)

                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    player.x = new_x
                    player.y = new_y
                else:
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    if randint(0, 1) == 1:
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.place_entities(new_room, entities, max_monsters_per_room, max_items_per_room)

            rooms.append(new_room)
            num_rooms += 1

    def set_up_wilderness(self, entities, map_width, map_height):
        for i in range(randint(1, 5)):
            #later change to a getCreature call to randomly add animals
            fighter_component = Fighter(hp = 10, defense = 0, power = 3)
            ai_component = BasicMonster()
            x = randint(0, map_width - 1)
            y = randint(0, map_height - 1)
            if not any([entity for entity in entities if entity.x == x and entity.y == y]) and not self.is_blocked(x, y):
                enemy = Entity(x, y, 'T', tcod.orange, 'Tiger', blocks = True, render_order=RenderOrder.ACTOR, fighter = fighter_component, ai = ai_component)
                entities.append(enemy)

    #notes:
    # -make it so outpost zone can't touch the edge of the screen
    # -add enemies
    # -add barriers, crates, items, etc.
    def set_up_outpost(self, entities, map_width, map_height, player, max_buildings, building_min_size, building_max_size, max_enemies):
        zone_w = randint(int(map_width*2/3), int(map_width*3/4))
        zone_h = randint(int(map_height*2/3), int(map_height*3/4))
        zone_x = randint(0, map_width - zone_w - 1)
        zone_y = randint(0, map_height - zone_h - 1)

        breakable_component = Breakable(hp = 40)
        sandbag = Entity(0, 0, '#', tcod.dark_sepia, 'sandbag', blocks = True, render_order = RenderOrder.ACTOR, breakable = breakable_component)



        for x in range(zone_x, zone_x + zone_w):
            for y in range(zone_y, zone_y + zone_h):
                for entity in entities:
                    if not entity == player and entity.x == x and entity.y == y:
                        entities.remove(entity)

        buildings = []
        num_buildings = 0
        for r in range(max_buildings):
            w = randint(building_min_size, building_max_size)
            h = randint(building_min_size, building_max_size)
            x = randint(zone_x, zone_x + zone_w - 1 - w)
            y = randint(zone_y, zone_y + zone_h - 1 - h)

            new_building = Rect(x, y, w, h)

            for other_building in buildings:
                if new_building.intersect(other_building):
                    break
            else:
                self.create_building(new_building)

                (new_x, new_y) = new_building.center()

                if num_buildings == 0:
                    player.x = new_x
                    player.y = new_y

                for x in range(x, x+w):
                    for y in range(y, y + h):
                        for entity in entities:
                            if not entity == player and entity.x == x and entity.y == y:
                                entities.remove(entity)

                buildings.append(new_building)

            #place_entities(entities, etc.) should be added

        for r in range(0, 5):#CHANGE TO A CONSTANT
            x = randint(zone_x + 1, zone_x + zone_w - 1)
            y = randint(zone_y + 1, zone_y + zone_h - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item_chance = randint(0, 100)
                if item_chance > 50:
                    item_component = Item(use_function = throw_grenade,
                        targeting=True, targeting_message=Message('Select the target of your grenade', tcod.light_cyan),
                        damage=20, radius=3)
                    item = Entity(x, y, '6', tcod.darker_green, 'Grenade', render_order=RenderOrder.ITEM, item=item_component)
                else:
                    item_component = Item(use_function = heal, amount = 4)
                    item = Entity(x, y, '=', tcod.white, 'Bandage', render_order = RenderOrder.ITEM, item=item_component)

                entities.append(item)

        for r in range(0, max_enemies):
            x = randint(zone_x + 1, zone_x + zone_w - 1)
            y = randint(zone_y + 1, zone_y + zone_h - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                spawn_chance = randint(0, 100)
                if spawn_chance > 0:
                    fighter_component = Fighter(hp = 10, defense = 0, power = 3)
                    ai_component = BasicMonster()
                    enemy = Entity(x, y, '@', tcod.red, 'Enemy solider', blocks = True, render_order=RenderOrder.ACTOR, fighter = fighter_component, ai = ai_component, sight_passes = True)
                    entities.append(enemy)



    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_building(self, building):
        self.create_v_wall(building.y1, building.y2, building.x1)
        self.create_v_wall(building.y1, building.y2, building.x2)
        self.create_h_wall(building.x1, building.x2, building.y1)
        self.create_h_wall(building.x1, building.x2, building.y2)
        if randint(0, 1) == 0:
            if randint(0, 1) == 0:
                y = building.y1
            else:
                y = building.y2
            x = randint(building.x1 + 1, building.x2 - 1)
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
        else:
            if randint(0, 1) == 0:
                x = building.x1
            else:
                x = building.x2
            y = randint(building.y1 + 1, building.y2 - 1)
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_h_wall(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = True
            self.tiles[x][y].block_sight = True

    def create_v_wall(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = True
            self.tiles[x][y].block_sight = True

    def place_entities(self, room, entities, max_monsters_per_room, max_items_per_room):
        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)

        for i in range(number_of_monsters):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                if randint(0, 100) < 80:
                    fighter_component = Fighter(hp = 10, defense = 0, power = 3)
                    ai_component = BasicMonster()
                    monster = Entity(x, y, 'o', tcod.desaturated_green, 'Orc', blocks = True, render_order=RenderOrder.ACTOR, fighter = fighter_component, ai = ai_component)
                else:
                    fighter_component = Fighter(hp = 16, defense = 1, power = 4)
                    ai_component = BasicMonster()
                    monster = Entity(x, y, 'T', tcod.darker_green, 'Troll', blocks = True, render_order=RenderOrder.ACTOR, fighter = fighter_component, ai = ai_component)

                entities.append(monster)

        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item_chance = randint(0, 100)
                if item_chance < 70:
                    item_component = Item(use_function = heal, amount = 4)
                    item = Entity(x, y, '!', tcod.violet, 'Healing Potion', render_order = RenderOrder.ITEM, item=item_component)
                elif item_chance < 85:
                    item_component = Item(use_function = cast_fireball,
                        targeting=True, targeting_message=Message('Select the target of your fireball', tcod.light_cyan),
                        damage=12, radius=3)
                    item = Entity(x, y, '#', tcod.red, 'Fireball Scroll', render_order=RenderOrder.ITEM, item=item_component)
                else:
                    item_component = Item(use_function = cast_lightning, damage = 20, maximum_range = 5)
                    item = Entity(x, y, '#', tcod.yellow, 'Lightning Scroll', render_order = RenderOrder.ITEM, item=item_component)
                entities.append(item)

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False
