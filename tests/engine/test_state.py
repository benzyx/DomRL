import unittest

from domrl.engine.supply import SupplyPile
from domrl.engine.state import Player, GameState
from domrl.engine.card import *
from domrl.engine.util import TurnPhase

class TestPlayer(unittest.TestCase):
    def test_create_default_player(self):
        player = Player("Lord Rattington", 0, None)
        self.assertEqual(player.total_vp(), 3)
        self.assertEqual(len(player.all_cards), 10)

    def test_create_complex_player(self):
        player = Player(
            name="Lord Rattington",
            idx=0,
            agent=None,
            vp=4,
            actions=0,
            coins=3,
            buys=0,
            draw_pile=[Estate, Copper, Province],
            discard_pile=[Silver],
            hand=[Gold, Province, Duchy, Curse],
            play_area=[],
            phase=TurnPhase.BUY_PHASE,
        )
        self.assertEqual(player.total_vp(), 19)
        self.assertEqual(len(player.all_cards), 8)

        player.init_turn()
        self.assertEqual(player.actions, 1)
        self.assertEqual(player.buys, 1)
        self.assertEqual(player.coins, 0)
        self.assertEqual(player.phase, TurnPhase.ACTION_PHASE)


class TestGameState(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_basic_state(self):
        state = GameState(
            agents=[None, None],
            preset_supply={"Province": SupplyPile(Province, 0)})

        self.assertEqual(state.current_player_idx, 0)
        self.assertTrue(state.is_game_over())
        self.assertTrue(len(state.get_winners()), 2)

        state.next_player_turn()
        # Handle tiebreak on turns.
        self.assertTrue(len(state.get_winners()), 1)
        self.assertEqual(state.get_winners()[0].name, "Player 2")

    def test_advanced_state(self):
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

        state = GameState(
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

        self.assertTrue(state.is_game_over())
        self.assertEqual(state.get_winners(), [player2])
        self.assertEqual(state.other_players(player1), [player2])
        self.assertEqual(state.other_players(player2), [player1])
