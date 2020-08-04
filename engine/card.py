from enum import Enum
from typing import List, Callable

from .effect import Effect


class CardType(Enum):
    VICTORY = 1
    TREASURE = 2
    ACTION = 3
    REACTION = 4
    ATTACK = 5
    CURSE = 6
    DURATION = 7
    NIGHT = 8


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
        """
        TODO (henry-prior): can we make specific cards inherit from the `Card`
            class instead? That way we can make the `is_type()` support things
            like:
            ```
            card = Silver()
            card.is_type(Silver) # True
            ```
        """
        return card == self.name

    def draw_cards(self, player, num: int):
        player.draw_into_hand(num)

    def increment_actions(self, player, num: int):
        player.actions += num

    def increment_buys(self, player, num: int):
        player.buys += num

    def increment_coins(self, player, num: int):
        player.coins += num

    """
    The entry point for card play effect.
    - state: State of the Game
    - player: Player who played the card.
    """

    def play(self, state, player):
        self.draw_cards(player, self.add_cards)
        self.increment_actions(player, self.add_actions)
        self.increment_buys(player, self.add_buys)
        self.increment_coins(player, self.coins)

        for effect in self.effect_list:
            effect.run(state, player)

        if self.effect_fn:
            self.effect_fn(state, player)
