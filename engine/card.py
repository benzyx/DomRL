from typing import List, Callable
from .effect import Effect
from .state_funcs import draw_into_hand
from .util import CardType


class Card(object):
    """
    Base class for all cards.
    """

    def __init__(self,
                 name: str,
                 types: List[CardType],
                 cost: int,
                 vp_constant: int = 0,
                 coins: int = 0,
                 add_cards: int = 0,
                 add_actions: int = 0,
                 add_buys: int = 0,
                 add_vp: int = 0,
                 effect_list: List[Effect] = [],
                 effect_fn: Callable = None,
                 vp_fn: Callable = None,
                 global_trigger = None,
                 ):
        self.name = name
        self.types = types
        self.cost = cost
        self.vp_constant = vp_constant
        self.coins = coins
        self.add_cards = add_cards
        self.add_actions = add_actions
        self.add_buys = add_buys
        self.add_vp = add_vp
        self.effect_list = effect_list
        self.effect_fn = effect_fn
        self.vp_fn = vp_fn
        self.global_trigger = global_trigger

    def __str__(self) -> str:
        return self.name

    """
    TODO(benzyx): handle cost modifiers (such as bridge).
    """

    def get_cost(self) -> int:
        return self.cost

    def is_type(self, card_type: CardType) -> bool:
        return card_type in self.types

    def is_card(self, card: str) -> bool:
        return card == self.name


    def play(self, state, player):
        """
        The entry point for card play effect.
        - state: State of the Game
        - player: Player who played the card.
        """

        # Draw cards
        draw_into_hand(state, player, self.add_cards)

        # Increment actions
        player.actions += self.add_actions

        # Increment Buys
        player.buys += self.add_buys

        # Increment Coins
        player.coins += self.coins

        for effect in self.effect_list:
            effect.run(state, player)

        if self.effect_fn:
            self.effect_fn(state, player)


"""
Implementations of base treasure and cards.
"""
Copper = Card(
    name="Copper",
    types=[CardType.TREASURE],
    cost=0,
    coins=1)

Silver = Card(
    name="Silver",
    types=[CardType.TREASURE],
    cost=3,
    coins=2)

Gold = Card(
    name="Gold",
    types=[CardType.TREASURE],
    cost=6,
    coins=3)

Curse = Card(
    name="Curse",
    types=[CardType.VICTORY],
    cost=0,
    vp_constant=-1)

Estate = Card(
    name="Estate",
    types=[CardType.VICTORY],
    cost=2,
    vp_constant=1)

Duchy = Card(
    name="Duchy",
    types=[CardType.VICTORY],
    cost=5,
    vp_constant=3)

Province = Card(
    name="Province",
    types=[CardType.VICTORY],
    cost=8,
    vp_constant=6)