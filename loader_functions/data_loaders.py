import os
import shelve

def save_game(player, entities, world_map, message_log, game_state):
    with shelve.open('savegame.dat', 'n') as data_file:
        data_file['player_index'] = entities.index(player)
        data_file['entities'] = entities
        data_file['world_map'] = world_map
        data_file['message_log'] = message_log
        data_file['game_state'] = game_state

def load_game():
    if not os.path.isfile('save_game.dat'):
        raise FileNotFoundError

    with shelve.open('savegame.dat', 'r') as data_file:
        player_index = data_file['player_index']
        entities = data_file['entities']
        world_map = data_file['world_map']
        message_log = data_file['message_log']
        game_state = data_file['game_state']

    player = entities[player_index]

    return player, entities, world_map, message_log, game_state
