from random import shuffle
from .util import TurnPhase
from .supply import choose_supply_from_kingdoms
from .card import *
import domrl.engine.cards.base as base
import domrl.engine.logger as log
import math


class Player(object):
    """
    Player State Object.
    """
    def __init__(self,
                 name,
                 idx,
                 agent,
                 vp=None,
                 actions=None,
                 coins=None,
                 buys=None,
                 draw_pile=None,
                 discard_pile=None,
                 hand=None,
                 play_area=None,
                 phase=None,
                 ):
        self.name = name
        self.idx = idx
        self.agent = agent
        self.vp_tokens = vp or 0
        self.actions = actions or 0
        self.coins = coins or 0
        self.buys = buys or 0
        self.draw_pile = draw_pile or \
            [Copper for _ in range(7)] + [Estate for _ in range(3)]
        self.discard_pile = discard_pile or []
        self.hand = hand or []
        self.play_area = play_area or []
        self.phase = phase or TurnPhase.END_PHASE
        self.immune_to_attack = False

        # TODO: I don't think this is necessary.
        self.previous_deck = []

        # TODO: Move this to game start or something.
        shuffle(self.draw_pile)

    def __eq__(self, other):
        return self.idx == other.idx

    def __str__(self):
        return self.name

    def init_turn(self):
        self.actions = 1
        self.buys = 1
        self.coins = 0
        self.phase = TurnPhase.ACTION_PHASE

    @property
    def all_cards(self):
        return self.hand + self.play_area + self.draw_pile + self.discard_pile

    def total_vp(self):
        total = self.vp_tokens
        for card in self.all_cards:
            total += card.vp_constant

            # TODO(benzyx): vp_fn really shouldn't take all_cards...
            if card.vp_fn:
                total += card.vp_fn(self.all_cards)
        return total

class GameState(object):
    """
    Keeps track of the game state.
    """

    def __init__(self,
                 agents=None,
                 players=None,
                 turn=None,
                 current_player_idx=None,
                 preset_supply=None,
                 kingdoms=None,
                 verbose=True):
        self.trash = []
        self.event_log = log.EventLog(verbose)
        self.turn = turn or 0
        self.players = players or [Player(f"Player {i+1}", i, agent) for i, agent in enumerate(agents)]
        self.current_player_idx = current_player_idx or 0
        self.turn_triggers = []
        self.global_triggers = []

        """
        TODO(benzyx): Make supply piles handle mixed piles.
        """
        self.supply_piles = preset_supply or choose_supply_from_kingdoms(kingdoms)

        for _, pile in self.supply_piles.items():
            if pile.card.global_trigger:
                self.global_triggers.append(pile.card.global_trigger)

        if players is None:
            for player in self.players:
                draw_into_hand(self, player, 5)

        self.players[0].init_turn()

    def __str__(self):
        """
        TODO(benzyx): This sucks right now. Should integrate this with StateView.
        """
        ret = ""
        # Supply piles.
        for name, pile in self.supply_piles.items():
            ret += f"Supply pile contains {name}, {pile.qty} remaining.\n"

        # Who's turn it is.
        ret += f"{self.current_player.name}'s turn!"

        return ret

    @property
    def current_player(self):
        return self.players[self.current_player_idx]

    def next_player_turn(self):
        self.current_player_idx = self.next_player_idx(self.current_player_idx)

    def next_player_idx(self, idx):
        return (idx + 1) % len(self.players)

    @property
    def all_players(self):
        return self.players

    def other_players(self, player):
        ret = []
        idx = self.next_player_idx(player.idx)
        while idx != player.idx:
            ret.append(self.players[idx])
            idx = self.next_player_idx(idx)
        return ret

    def empty_piles(self):
        pile_outs = []
        for _, pile in self.supply_piles.items():
            if pile.qty == 0:
                pile_outs.append(pile)
        return pile_outs

    def is_game_over(self):
        province_pileout = self.supply_piles["Province"].qty == 0
        pileout_count = len(self.empty_piles())
        return pileout_count >= 3 or province_pileout

    def get_winners(self):
        winners = []
        best_vp = self.players[0].total_vp()
        best_vp_taken_extra_turn = False
        for player in self.players:
            if player.total_vp() > best_vp:
                winners = [player]
            elif player.total_vp() == best_vp:
                if not best_vp_taken_extra_turn and player.idx >= self.current_player_idx:
                    best_vp_taken_extra_turn = True
                    winners = [player]
                else:
                    winners.append(player)

        return winners
