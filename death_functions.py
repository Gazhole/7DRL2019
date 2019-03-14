

from game_states import GameStates
from render import RenderOrder
from message_log import Message


def kill_player(player):
    player.char = "%"
    player.colour = (255, 255, 255)

    return Message("You died.", (255, 255, 255)), GameStates.PLAYER_DEAD


# TODO: monsters drop items when they die!
def kill_monster(monster):
    death_message = Message("The {0} dies!".format(monster.name.capitalize()), (255, 255, 255))

    monster.char = "%"
    monster.colour = (255, 255, 255)

    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = "Remains"
    monster.render_order = RenderOrder.CORPSE

    return death_message
