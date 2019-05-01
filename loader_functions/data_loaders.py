import os
import shelve

def save_game(player, entities, world_map, message_log, game_state):
    with shelve.open('savegame.dat', 'n') as data_file:
        data_file['player_index'] = entities.index(player)
        data_file['entities'] = entities
        for entity in entities:
            print(entity.name)
        print("______________________")
        #print(entities[entities.index(player)])
        data_file['world_map'] = world_map
        data_file['message_log'] = message_log
        data_file['game_state'] = game_state

def load_game():
    if not os.path.isfile('savegame.dat.db'):
        raise FileNotFoundError

    with shelve.open('savegame.dat') as data_file:
        player_index = data_file['player_index']
        entities = data_file['entities']
        world_map = data_file['world_map']
        message_log = data_file['message_log']
        game_state = data_file['game_state']

    player = entities[player_index]
    print(player.name)
    #entities.remove(player)

    return player, entities, world_map, message_log, game_state
