import unittest

from domrl.engine.supply import SupplyPile
from domrl.engine.state import Player, GameState
from domrl.engine.card import *

class TestStateFuncs(unittest.TestCase):
    def setUp(self):
        player1 = Player(
            name="kuroba",
            idx=0,
            agent=None,
            vp=0,
            actions=0,
            coins=3,
            buys=0,
            draw_pile=[Estate, Copper, Province],
            discard_pile=[Silver],
            hand=[Gold, Province, Duchy, Curse],
            play_area=[],
        )

        player2 = Player(
            name="xtruffles",
            idx=0,
            agent=None,
            vp=3,
            actions=0,
            coins=3,
            buys=0,
            draw_pile=[Estate, Copper, Province],
            discard_pile=[Silver],
            hand=[Gold, Province],
            play_area=[],
        )

        self.state = GameState(
            agents=None,
            players=[player1, player2],
            preset_supply={
                "Curse": SupplyPile(Curse, 0),
                "Estate": SupplyPile(Estate, 8),
                "Duchy": SupplyPile(Duchy, 8),
                "Province": SupplyPile(Province, 8),
                "Copper": SupplyPile(Copper, 0),
                "Silver": SupplyPile(Silver, 30),
                "Gold": SupplyPile(Gold, 0),
            }
        )
        pass

    def tearDown(self):
        pass

    def test_draw_cards(self):
        pass