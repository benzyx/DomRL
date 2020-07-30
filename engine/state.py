from random import shuffle

from engine.context import *
from engine.cards.base import *

class Player(object):
    """
    Player State Object.
    """
    def __init__(self,
                 name,
                 idx,
                 vp=None,
                 actions=None,
                 coins=None,
                 buys=None,
                 draw_pile=None,
                 discard_pile=None,
                 hand=None,
                 play_area=None,
                 ):
        self.name = name
        self.idx = idx
        self.vp = vp or 0
        self.actions = actions or 0
        self.coins = coins or 0
        self.buys = buys or 0
        self.draw_pile = draw_pile or [Copper for _ in range(7)] + [Estate for _ in range(3)]
        self.discard_pile = discard_pile or []
        self.hand = hand or []
        self.play_area = play_area or []
        self.phase = TurnPhase.END_PHASE

        shuffle(self.draw_pile)

    def __eq__(self, other):
        return self.idx == other.idx

    def __str__(self):
        return self.name

    def cycle_shuffle(self):
        assert(len(self.draw_pile) == 0)
        self.draw_pile = self.discard_pile
        self.discard_pile = []
        shuffle(self.draw_pile)

    # TODO(ben): Refactor this to use draw_one() repeatedly.
    def draw(self, num):

        # Enough cards left to draw.
        # We draw cards from the back of the list.
        if len(self.draw_pile) >= num:
            cards_to_draw = self.draw_pile[:num]
            self.draw_pile = self.draw_pile[num:]
            self.hand.extend(cards_to_draw)
        else:
            remaining = num - len(self.draw_pile)

            self.hand.extend(self.draw_pile)
            self.draw_pile = []
            self.cycle_shuffle()

            if len(self.draw_pile) > 0:
                self.draw(remaining)

    def clean_up(self):
        self.discard_pile.extend(self.play_area)
        self.discard_pile.extend(self.hand)
        self.play_area = []
        self.hand = []
        self.draw(5)

    def init_turn(self):
        self.actions = 1
        self.buys = 1
        self.coins = 0
        self.phase = TurnPhase.ACTION_PHASE

    @property
    def all_cards(self):
        return self.hand + self.play_area + self.draw_pile + self.discard_pile

    def total_vp(self):
        total = self.vp
        for card in self.all_cards:
            """
            TODO(henry-prior): keep track of deck state as counter and pass
                here (no change in deck state = no vp computations)
            """
            total += card.vp(self.all_cards)
        return total


class SupplyPile(object):
    def __init__(self, card, qty, buyable = True):
        self.card = card
        self.qty = qty
        self.buyable = buyable

class GameState(object):
    """
    Keeps track of the game state.
    """
    def __init__(self, num_players, players=None):
        self.trash = []
        self.turn = 0
        self.players = players or [Player(f"Player {i+1}", i) for i in range(num_players)]
        self.current_player_idx = 0
        self.context_stack = [TurnContext(self)]

        """
        TODO(benzyx): Make supply piles handle mixed piles.
        """
        self.supply_piles = {
            "Curse" : SupplyPile(Curse, 10),
            "Estate" : SupplyPile(Estate, 8),
            "Duchy" : SupplyPile(Duchy, 8),
            "Province" : SupplyPile(Province, 8),
            "Copper" : SupplyPile(Copper, 46),
            "Silver" : SupplyPile(Silver, 30),
            "Gold" : SupplyPile(Gold, 16),

            # Testing mode:
            "Village" : SupplyPile(Village, 10),
            "Laboratory" : SupplyPile(Laboratory, 10),
            "Market" : SupplyPile(Market, 10),
            "Festival" : SupplyPile(Festival, 10),
            "Smithy" : SupplyPile(Smithy, 10),
            "Militia" : SupplyPile(Militia, 10),
            "Chapel" : SupplyPile(Chapel, 10),
            "Witch" : SupplyPile(Witch, 10),
            "Workshop" : SupplyPile(Workshop, 10),
        }

        if players is None:
            for player in self.players:
                player.draw(5)

        self.players[0].init_turn()

    def __str__(self):
        ret = ""
        # Supply piles.
        for name, pile in self.supply_piles.items():
            ret += f"Supply pile contains {name}, {pile.qty} remaining.\n"

        # Who's turn it is.
        ret += f"{self.current_player().name}'s turn!"

        return ret

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
        while (idx != player.idx):
            ret.append(self.players[idx])
            idx = self.next_player_idx(idx)
        return ret

    def end_turn(self):
        self.current_player().clean_up()
        self.next_player_turn()
        self.current_player().init_turn()

    def is_game_over(self):
        province_pileout = False
        pileout_count = 0
        for _, pile in self.supply_piles.items():
            if pile.card.name == "Province" and pile.qty == 0:
                province_pileout = True
            if pile.qty == 0:
                pileout_count += 1
        return pileout_count >= 3 or province_pileout

    def get_winners(self):
        winners = []
        best_vp = self.players[0].total_vp()
        for player in self.players:
            if player.total_vp() > best_vp:
                winners = [player]
            elif player.total_vp() == best_vp:
                winners.append(player)

        return winners

    def get_next_decision(self):
        if len(self.context_stack) == 0:
            raise Exception("Context stack is empty!")
        context = self.context_stack[-1]
        return context.get_decision()

    def resolve_contexts(self):
        while self.current_context().can_resolve:
            result = self.current_context().resolve(self)
            self.pop_context()
            self.current_context().update(result)

    def current_context(self):
        return self.context_stack[-1]

    def add_context(self, context):
        self.context_stack.append(context)

    def pop_context(self):
        self.context_stack.pop()
