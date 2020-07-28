from enum import Enum

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
    def __init__(self, name, types, cost,
            vp=0,
            coins=0,
            add_cards=0,
            add_actions=0,
            add_buys=0,
            add_vp=0,
            effect_list=[]):
        self.name = name
        self.types = types
        self.cost = cost

        self.vp = vp
        self.coins = coins
        self.add_cards = add_cards
        self.add_actions = add_actions
        self.add_buys = add_buys
        self.add_vp = add_vp
        self.effect_list = effect_list

    def __str__(self):
        return self.name

    """
    TODO(benzyx): handle cost modifiers (such as bridge).
    """
    def get_cost(self):
        return cost

    def is_type(self, card_type):
        return card_type in self.types

    def draw_cards(self, state, num):
        state.current_player().draw(num)

    def increment_actions(self, state, num):
        state.current_player().actions += num

    def increment_buys(self, state, num):
        state.current_player().buys += num

    def increment_coins(self, state, num):
        state.current_player().coins += num

    """
    The entry point for card play effect.
    - state: State of the Game
    - player: Player who played the card.
    """
    def play(self, state, player):
        self.draw_cards(state, self.add_cards)
        self.increment_actions(state, self.add_actions)
        self.increment_buys(state, self.add_buys)
        self.increment_coins(state, self.coins)

        for effect in self.effect_list:
            effect.run(state, player)
