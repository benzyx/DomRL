import pytest
from ..game import Game
from ..agent import Agent
from ..state import Player
from ..cards.base import *
from .utils import *


class TestCards:
    def test_throne_room(self):
        pass
        '''
        player1 = Player(
            'Player 1',
            0,
            hand=[ThroneRoom for _ in range(3)] + [Village for _ in range(3)],
        )
        player2 = Player('Player 2', 1)
        players = [player1, player2]
        game = Game([ThroneRoomAgent(), Agent()], players=players)
        game.run()
        '''

