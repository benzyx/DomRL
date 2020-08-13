import pytest
from ..game import Game
from ..agent import Agent
from ..state import Player
from ..cards.base import *
from .utils import *


class TestCards:
    def test_throne_room(self):
        agents = [ThroneRoomAgent(), Agent()]
        player1 = Player(
            'Player 1',
            0,
            hand=[ThroneRoom for _ in range(3)] + [Village for _ in range(3)],
            agent=agents[0],
        )
        player2 = Player('Player 2', 1, agent=agents[1])
        players = [player1, player2]
        game = Game(
            agents,
            players=players,
        )
        game.run()

