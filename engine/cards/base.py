from engine.card import Card, CardType
from engine.state_funcs import *

import engine.effect as effect
import engine.context as ctx

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

"""
Base Expansion Dominion Cards.
"""
Village = Card(
    name="Village",
    types=[CardType.ACTION],
    cost=3,
    add_cards=1,
    add_actions=2)

Laboratory = Card(
    name="Laboratory",
    types=[CardType.ACTION],
    cost=5,
    add_cards=2,
    add_actions=1)

Festival = Card(
    name="Festival",
    types=[CardType.ACTION],
    cost=5,
    add_actions=2,
    add_buys=1,
    coins=2)

Market = Card(
    name="Market",
    types=[CardType.ACTION],
    cost=5,
    add_actions=1,
    add_buys=1,
    coins=1,
    add_cards=1)

Smithy = Card(
    name="Smithy",
    types=[CardType.ACTION],
    cost=4,
    add_cards=3)


"""
Context for a player discarding a exactly or up to a number of cards.
"""
class DiscardCardsContext(ctx.ChooseCardsFromHandContext):
    def __init__(self, state, player, num_cards, filter_type, optional, prompt):
        super().__init__(
            state,
            player,
            num_cards,
            filter_type,
            optional,
            prompt,
        )

    def resolve(self, state):
        for card in self.cards:
            player_discard_card(self.state, self.player, card)

"""
Discard cards in player's hand. Example: Poacher.
"""
class DiscardCardsEffect(effect.Effect):
    def __init__(self, num_cards, filter_type, optional):
        self.num_cards = num_cards
        self.filter_type = filter_type
        self.optional = optional
        if optional:
            self.prompt = f"Discard up to {num_cards} cards."
        else:
            self.prompt = f"Discard exactly {num_cards} cards."

    def run(self, state, player):
        state.add_context(
            DiscardCardsContext(
                state=state,
                player=player,
                num_cards=self.num_cards,
                filter_type=self.filter_type,
                optional=self.optional,
                prompt=self.prompt))

"""
Discard down to some number of cards in player's hand. Example: Militia.
"""
class DiscardDownToEffect(effect.Effect):
    def __init__(self, num_cards_downto):
        self.num_cards_downto = num_cards_downto

    def run(self, state, player):

        num_to_discard = len(player.hand) - self.num_cards_downto
        state.add_context(
            DiscardCardsContext(
                state,
                player,
                num_to_discard,
                filter_type=None,
                optional=False,
                prompt=f"You must discard down to {self.num_cards_downto} cards. Discard {num_to_discard}:",
            )
        )

"""
Context for a player trashing a exactly or up to a number of cards.
"""
class TrashCardsContext(ctx.ChooseCardsFromHandContext):
    def __init__(self, state, player, num_cards, filter_type, optional, prompt):
        super().__init__(
            state,
            player,
            num_cards,
            filter_type,
            optional,
            prompt,
        )

    def resolve(self, state):
        for card in self.cards:
            player_trash_card_from_hand(self.state, self.player, card)


class TrashCardsEffect(effect.Effect):
    def __init__(self, num_cards, filter_type, optional):
        self.num_cards = num_cards
        self.filter_type = filter_type
        self.optional = optional
        if optional:
            self.prompt = f"Trash up to {num_cards} cards."
        else:
            self.prompt = f"Trash exactly {num_cards} cards."

    def run(self, state, player):
        state.add_context(
            TrashCardsContext(
                state=state,
                player=player,
                num_cards=self.num_cards,
                filter_type=self.filter_type,
                optional=self.optional,
                prompt=self.prompt
            )
        )

"""
Context for a player gaining a card from the supply.
"""
class GainCardFromSupplyContext(ctx.ChoosePileFromSupplyContext):
    def __init__(self, state, player, filter_func):
        super().__init__(self, state, player, filter_func)

    def resolve(self):
        gain_card_to_discard(self.state, self.player, self.pile)


class ChooseCardToGainFromSupplyEffect(effect.Effect):
    def __init__(self, filter_func):
        self.filter_func = filter_func

    def run(self, state, player):
        state.add_context(
            GainCardFromSupplyContext(
                state=state,
                player=player,
                filter_func=self.filter_func,
                prompt=self.prompt
            )
        )


class GainCardToDiscardPileEffect(effect.Effect):
    def __init__(self, card_name):
        self.card_name = card_name

    def run(self, state, player):
        assert(self.card_name in state.supply_piles)
        pile = state.supply_piles[self.card_name]
        gain_card_to_discard(state, player, pile)

"""

"""
class ApplyEffectToOpponentsContext(ctx.Context):
    """
    TODO(benzyx): Have it automatically run the effect after initialization.
    Need to call update to this when updating.
    """
    def __init__(self, state, player, effect):
        self.state = state
        self.player = player
        self.effect = effect
        self.opponents = state.other_players(player)
        self.opponents_idx = 0

    def update(self, res):
        if self.opponents_idx < len(self.opponents):
            opp = self.opponents[self.opponents_idx]
            self.effect.run(self.state, opp)
            self.opponents_idx += 1

    @property
    def can_resolve(self):
        return self.opponents_idx == len(self.opponents)

    def resolve(self, state):
        pass


class OpponentsDiscardDownToEffect(effect.Effect):

    def __init__(self, num_cards_downto):
        self.num_cards_downto = num_cards_downto

    def run(self, state, player):

        state.add_context(
            ApplyEffectToOpponentsContext(
                state,
                player,
                DiscardDownToEffect(self.num_cards_downto)))

        # TODO(benzy): Please fix this stupid hack somehow.
        # We need can't move this to __init__ for ApplyEffectToOpponentsContext.
        state.context_stack[-1].update(None)


class OpponentsGainCardEffect(effect.Effect):
    def __init__(self, card_name):
        self.card_name = card_name

    def run(self, state, player):
        state.add_context(
            ApplyEffectToOpponentsContext(
                state,
                player,
                GainCardToDiscardPileEffect(self.card_name)
            )
        )

        # TODO(benzy): Please fix this stupid hack somehow.
        # We need can't move this to __init__ for ApplyEffectToOpponentsContext.
        state.context_stack[-1].update(None)


class PlayActionFromHandTwiceContext(ctx.ChooseCardsFromHandContext):
    def __init__(self, state, player, num_cards, filter_type, optional, prompt):
        super().__init__(
            state,
            player,
            num_cards,
            filter_type,
            optional,
            prompt,
        )

    def resolve(self, state):
        for card in self.cards:
            play_card_from_hand_twice(self.state, self.player, card)


class PlayActionFromHandTwiceEffect(effect.Effect):
    def __init__(self):
        self.prompt = 'You may play an action card from your hand twice'

    def run(self, state, player):
        state.add_context(
            PlayActionFromHandTwiceContext(
                state=state,
                player=player,
                num_cards=1,
                filter_type=CardType.ACTION,
                optional=True,
                prompt=self.prompt,
            )
        )


Militia = Card(
    name="Militia",
    types=[CardType.ACTION, CardType.ATTACK],
    cost=4,
    coins=2,
    effect_list=[OpponentsDiscardDownToEffect(3)])


Gardens = Card(
    name="Gardens",
    types=[CardType.VICTORY],
    cost=4,
    vp_fn=lambda all_cards: len(all_cards)
)


Chapel = Card(
    name="Chapel",
    types=[CardType.ACTION],
    cost=2,
    effect_list=[TrashCardsEffect(4, filter_type=None, optional=True)]
)


Witch = Card(
    name="Witch",
    types=[CardType.ACTION, CardType.ATTACK],
    cost=5,
    add_cards=2,
    effect_list=[OpponentsGainCardEffect("Curse")])


Workshop = Card(
    name="Workshop",
    types=[CardType.ACTION],
    cost=3,
    effect_list=[
        ChooseCardToGainFromSupplyEffect(
            filter_func=lambda pile: (pile.card.cost <= 4)
        )
    ]
)


ThroneRoom = Card(
    name="Throne Room",
    types=[CardType.ACTION],
    cost=4,
    effect_list=[PlayActionFromHandTwiceEffect()],
)

"""
Remodel = Card(
    name="Remodel",
    types=[CardType.ACTION],
    cost=4,
    effect_list=[TrashAndGainUpToEffect()])


Bandit = Card(
    name="Bandit",
    types=
)


"""

