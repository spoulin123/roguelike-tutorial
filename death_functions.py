import tcod

from render_functions import RenderOrder
from game_states import GameStates
from game_messages import Message

def kill_player(player):
    player.char = '%'
    player.color = tcod.dark_red

    return Message('You died!', tcod.red), GameStates.PLAYER_DEAD

def kill_monster(monster):
    death_message = Message('{0} is dead!'.format(monster.name.capitalize()), tcod.orange)

    monster.char = '%'
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.render_order = RenderOrder.CORPSE

    return death_message

def destroy_object(object):
    destroy_message = Message('{0} has been destroyed!'.format(object.name.capitalize()), tcod.white)

    object.char = '.'
    object.color = tcod.black
    object.blocks = False
    object.breakable = None
    object.name = 'destroyed ' + object.name
    object.render_order = RenderOrder.CORPSE

    return destroy_message
