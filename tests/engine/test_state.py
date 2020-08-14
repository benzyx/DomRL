import unittest

from domrl.engine.state import Player, GameState
from domrl.engine.card import *

class TestPlayer(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_player(self):
        player = Player(
                "Lord Rattington", 0, None,
        )
        self.assertEqual(player.total_vp(), 3)
        self.assertEqual(len(player.all_cards), 10)


class TestGameState(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass