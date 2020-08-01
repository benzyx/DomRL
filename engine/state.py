from random import shuffle
from engine.util import TurnPhase
import engine.cards.base as base
import engine.logger as log


class Player(object):
    """
    Player State Object.
    """

    def __init__(self, name, idx, agent):
        self.name = name
        self.idx = idx
        self.agent = agent
        self.vp = 0
        self.actions = 0
        self.coins = 0
        self.buys = 0
        self.draw_pile = [base.Copper for _ in range(7)] + [base.Estate for _ in range(3)]
        self.discard_pile = []
        self.hand = []
        self.play_area = []
        self.phase = TurnPhase.END_PHASE

        shuffle(self.draw_pile)

    def __eq__(self, other):
        return self.idx == other.idx

    def __str__(self):
        return self.name

    def cycle_shuffle(self):
        """
        Moves all cards from discard pile to draw_pile, and shuffles it.
        """
        assert (len(self.draw_pile) == 0)
        self.draw_pile = self.discard_pile
        self.discard_pile = []
        shuffle(self.draw_pile)

    def draw_one(self):
        if len(self.draw_pile) == 0:
            self.cycle_shuffle()

        if len(self.draw_pile) >= 1:
            return self.draw_pile.pop()
        else:
            return None

    def draw(self, num):
        cards = []
        for i in range(num):
            card = self.draw_one()
            if card:
                cards.append(card)
        return cards

    def draw_into_hand(self, num):
        cards = self.draw(num)
        self.hand.extend(cards)

    def clean_up(self):
        self.discard_pile.extend(self.play_area)
        self.discard_pile.extend(self.hand)
        self.play_area = []
        self.hand = []
        self.draw_into_hand(5)

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
    def __init__(self, card, qty, buyable=True):
        self.card = card
        self.qty = qty
        self.buyable = buyable

    def __str__(self):
        return str(self.card)


class GameState(object):
    """
    Keeps track of the game state.
    """

    def __init__(self, agents):
        self.trash = []
        self.event_log = log.EventLog(agents)
        self.turn = 0
        self.players = [Player(f"Player {i + 1}", i, agent) for i, agent in enumerate(agents)]
        self.current_player_idx = 0

        """
        TODO(benzyx): Make supply piles handle mixed piles.
        """
        self.supply_piles = {
            "Curse": SupplyPile(base.Curse, 10),
            "Estate": SupplyPile(base.Estate, 8),
            "Duchy": SupplyPile(base.Duchy, 8),
            "Province": SupplyPile(base.Province, 8),
            "Copper": SupplyPile(base.Copper, 46),
            "Silver": SupplyPile(base.Silver, 30),
            "Gold": SupplyPile(base.Gold, 16),

            # Testing mode:
            "Village": SupplyPile(base.Village, 10),
            "Laboratory": SupplyPile(base.Laboratory, 10),
            "Market": SupplyPile(base.Market, 10),
            "Festival": SupplyPile(base.Festival, 10),
            "Smithy": SupplyPile(base.Smithy, 10),
            "Militia": SupplyPile(base.Militia, 10),
            "Chapel": SupplyPile(base.Chapel, 10),
            "Witch": SupplyPile(base.Witch, 10),
            "Workshop": SupplyPile(base.Workshop, 10),
            "Bandit": SupplyPile(base.Bandit, 10),
            "Remodel": SupplyPile(base.Remodel, 10),


            "Throne Room": SupplyPile(base.ThroneRoom, 10),
            "Moneylender": SupplyPile(base.Moneylender, 10),
            "Poacher": SupplyPile(base.Poacher, 10),
        }

        for player in self.players:
            player.draw_into_hand(5)

        self.players[0].init_turn()

    def __str__(self):
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

    def end_turn(self):
        self.current_player.clean_up()
        self.next_player_turn()
        self.current_player.init_turn()

    def empty_piles(self):
        pileouts = []
        for _, pile in self.supply_piles.items():
            if pile.qty == 0:
                pileouts.append(pile)
        return pileouts

    def is_game_over(self):
        province_pileout = self.supply_piles["Province"].qty == 0
        pileout_count = len(self.empty_piles())
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
