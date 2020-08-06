from engine.card import Card, CardType
from engine.state_funcs import *
from engine.card import *

import engine.supply as supply
import engine.decision as dec
import engine.effect as effect
import engine.game as game
import engine.trigger as trig

SupplyPile = supply.SupplyPile

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


class DiscardCardsEffect(effect.Effect):
    """
    Discard cards in player's hand. Example: Poacher.
    """

    def __init__(self, num_cards, filter_func, optional):
        self.num_cards = num_cards
        self.filter_func = filter_func
        self.optional = optional

    def run(self, state, player):
        if self.optional:
            prompt = f"Discard up to {self.num_cards} cards."
        else:
            prompt = f"Discard exactly {self.num_cards} cards."

        cards = dec.choose_cards(
            state=state,
            player=player,
            num_select=self.num_cards,
            prompt=prompt,
            filter_func=self.filter_func,
            optional=self.optional,
        )

        for card in cards:
            player_discard_card_from_hand(state, player, card)


"""
Discard down to some number of cards in player's hand. Example: Militia.
"""


class DiscardDownToEffect(effect.Effect):
    def __init__(self, num_cards_downto):
        self.num_cards_downto = num_cards_downto

    def run(self, state, player):
        prompt = f"Discard down to {self.num_cards_downto} cards."
        num_to_discard = len(player.hand) - self.num_cards_downto

        cards = dec.choose_cards(
            state=state,
            player=player,
            num_select=num_to_discard,
            prompt=prompt,
            filter_func=None,
            optional=False,
        )

        for card in cards:
            player_discard_card_from_hand(state, player, card)


class TrashCardsEffect(effect.Effect):
    def __init__(self, num_cards, filter_func=None, optional=True):
        self.num_cards = num_cards
        self.filter_func = filter_func
        self.optional = optional

    def run(self, state, player):
        if self.optional:
            prompt = f"Trash up to {self.num_cards} cards."
        else:
            prompt = f"Trash exactly {self.num_cards} cards."

        cards = dec.choose_cards(
            state=state,
            player=player,
            num_select=self.num_cards,
            prompt=prompt,
            filter_func=self.filter_func,
            optional=self.optional
        )

        for card in cards:
            player_trash_card_from_hand(state, player, card)


class GainCardToDiscardPileEffect(effect.Effect):
    def __init__(self, card_name):
        self.card_name = card_name

    def run(self, state, player):
        assert (self.card_name in state.supply_piles)
        pile = state.supply_piles[self.card_name]
        gain_card_to_discard(state, player, pile)


class ChoosePileToGainEffect(effect.Effect):
    def __init__(self, filter_func):
        self.filter_func = filter_func

    def run(self, state, player):
        prompt = f"Choose a pile to gain card from."
        decision = dec.ChoosePileDecision(state, player, self.filter_func, prompt)
        game.process_decision(player.agent, decision, state)
        gain_card_to_discard(state, player, decision.pile)


class ChoosePileToGainToHandEffect(effect.Effect):
    def __init__(self, filter_func):
        self.filter_func = filter_func

    def run(self, state, player):
        prompt = f"Choose a pile to gain a card into your hand."
        decision = dec.ChoosePileDecision(state, player, self.filter_func, prompt)
        game.process_decision(player.agent, decision, state)
        gain_card_to_hand(state, player, decision.pile)


class OpponentsDiscardDownToEffect(effect.Effect):
    def __init__(self, num_cards_downto):
        self.num_cards_downto = num_cards_downto

    def run(self, state, player):
        for opp in state.other_players(player):
            DiscardDownToEffect(self.num_cards_downto).run(state, opp)


class OpponentsGainCardEffect(effect.Effect):
    def __init__(self, card_name):
        self.card_name = card_name

    def run(self, state, player):
        for opp in state.other_players(player):
            GainCardToDiscardPileEffect(self.card_name).run(state, opp)


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
    effect_list=[TrashCardsEffect(4, optional=True)]
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
        ChoosePileToGainEffect(
            filter_func=lambda pile: (pile.card.cost <= 4)
        )
    ]
)


class TrashAndGainEffect(effect.Effect):
    def __init__(self, add_cost: int, gain_exact_cost: bool):
        self.add_cost = add_cost
        self.gain_exact_cost = gain_exact_cost

    def run(self, state, player):
        cards = dec.choose_cards(
            state=state,
            player=player,
            num_select=1,
            prompt=f"Choose a card to trash.",
            filter_func=None,
            optional=False
        )

        assert (len(cards) == 1)
        trashed_card = cards[0]

        player_trash_card_from_hand(state, player, trashed_card)

        filter_function = lambda pile: pile.card.cost <= trashed_card.cost + self.add_cost
        if self.gain_exact_cost:
            filter_function = lambda pile: pile.card.cost == trashed_card.cost + self.add_cost

        ChoosePileToGainEffect(
            filter_func=filter_function
        ).run(state, player)


Remodel = Card(
    name="Remodel",
    types=[CardType.ACTION],
    cost=4,
    effect_list=[TrashAndGainEffect(2, False)],
)


def bandit_attack_fn(state, player):
    for opp in state.other_players(player):
        top_two_cards = player.draw(2)

        treasures = []
        non_treasures = []
        for card in top_two_cards:
            if card.is_type(CardType.TREASURE) and card.name != "Copper":
                treasures.append(card)
            else:
                non_treasures.append(card)

        # If there are two treasures:
        if len(treasures) == 2:
            cards = dec.choose_cards(
                state=state,
                player=opp,
                num_select=1,
                prompt="Select a card to trash from enemy Bandit.",
                filter_func=None,
                optional=False,
                card_container=treasures,
            )

            trash(state, opp, cards[0], treasures)
            discard(state, opp, treasures[0], treasures)
            assert (len(treasures) == 0)

        elif len(treasures) == 1:
            trash(treasures[0])
            assert (len(treasures) == 0)

        for card in non_treasures.copy():
            discard(state, opp, card, non_treasures)


Bandit = Card(
    name="Bandit",
    types=[CardType.ACTION, CardType.ATTACK],
    cost=5,
    effect_list=[
        GainCardToDiscardPileEffect("Gold")
    ],
    effect_fn=bandit_attack_fn,
)


def throne_fn(state, player):
    cards = dec.choose_cards(
        state,
        player,
        num_select=1,
        prompt="Select a card to play twice.",
        filter_func=lambda _card: _card.is_type(CardType.ACTION),
        optional=True,
        card_container=player.hand,
    )

    if cards:
        card = cards[0]

        # Refactor the moving of one container to another.
        card_idx = player.hand.index(card)
        player.hand.pop(card_idx)
        player.play_area.append(card)

        play_inplace(state, player, card)
        play_inplace(state, player, card)


ThroneRoom = Card(
    name="Throne Room",
    types=[CardType.ACTION],
    cost=4,
    effect_fn=throne_fn,
)


class MerchantTrigger(trig.Trigger):
    def __init__(self, player):
        self.triggered = False
        self.player = player

    def condition(self, event):
        return event.event_type == log.EventType.PLAY and event.card == Silver

    def apply(self, state):
        if not self.triggered:
            self.player.coins += 1
            self.triggered = True


def merchant_fn(state, player):
    state.turn_triggers.append(MerchantTrigger(player))


Merchant = Card(
    name="Merchant",
    types=[CardType.ACTION],
    cost=3,
    add_cards=1,
    add_actions=1,
    effect_fn=merchant_fn,
)


def moneylender_fn(state, player):
    cards = dec.choose_cards(
        state,
        player,
        num_select=1,
        prompt="Trash a copper to gain +3 coins. Choose none to skip.",
        filter_func=lambda card: card.name == "Copper",
        optional=True,
        card_container=player.hand,
    )

    if cards:
        trash(state, player, cards[0], player.hand)
        player.coins += 3


Moneylender = Card(
    name="Moneylender",
    types=[CardType.ACTION],
    cost=4,
    effect_fn=moneylender_fn,
)


def poacher_fn(state, player):
    pileout_count = len(state.empty_piles())
    if pileout_count > 0:
        cards = dec.choose_cards(
            state,
            player,
            num_select=2,
            prompt=f"You must discard {pileout_count} card(s).",
            filter_func=lambda card: card.name == "Copper",
            optional=False,
            card_container=player.hand,
        )
        for card in cards:
            player_discard_card_from_hand(state, player, card)


Poacher = Card(
    name="Poacher",
    types=[CardType.ACTION],
    cost=4,
    add_cards=1,
    add_actions=1,
    coins=1,
    effect_fn=poacher_fn,
)


def cellar_fn(state, player):
    chosen_cards = dec.choose_cards(
        state,
        player,
        num_select=len(player.hand),
        prompt="Discard as many cards as you would like to draw.",
        filter_func=None,
        optional=True,
        card_container=player.hand,
    )

    num_discarded = len(chosen_cards)
    for card in chosen_cards:
        player_discard_card_from_hand(state, player, card)

    player.draw_into_hand(num_discarded)


Cellar = Card(
    name="Cellar",
    types=[CardType.ACTION],
    cost=2,
    effect_fn=cellar_fn,
)


def mine_fn(state, player):
    trashed_card = dec.choose_cards(
        state,
        player,
        num_select=1,
        prompt="Choose a Treasure to upgrade.",
        filter_func=lambda card: card.is_type(CardType.TREASURE),
        optional=True,
        card_container=player.hand,
    )

    if trashed_card:
        trashed_card = trashed_card[0]
        card_cost = trashed_card.cost
        player_trash_card_from_hand(state, player, trashed_card)
        ChoosePileToGainToHandEffect(
            filter_func=lambda pile: pile.card.is_type(CardType.TREASURE) and pile.card.cost <= card_cost + 3
        ).run(state, player)


Mine = Card(
    name="Mine",
    types=[CardType.ACTION],
    cost=5,
    effect_fn=mine_fn,
)


def vassal_fn(state, player):
    cards = player.draw(1)
    if cards:
        drawn_card = cards[0]
        if drawn_card.is_type(CardType.ACTION):
            play(state, player, drawn_card, cards)
        else:
            discard(state, player, drawn_card, cards)


Vassal = Card(
    name="Vassal",
    types=[CardType.ACTION],
    cost=3,
    coins=2,
    effect_fn=vassal_fn,
)


def council_room_fn(state, player):
    for opp in state.other_players(player):
        opp.draw_into_hand(1)


CouncilRoom = Card(
    name="Council Room",
    types=[CardType.ACTION],
    cost=5,
    add_cards=4,
    add_buys=1,
    effect_list=council_room_fn,
)


def artisan_fn(state, player):
    ChoosePileToGainToHandEffect(
        filter_func=lambda pile: (pile.card.cost <= 5)
    ).run(state, player)

    # Topdeck a card.
    cards = dec.choose_cards(state,
                             player,
                             num_select=1,
                             prompt="Choose a card to topdeck.",
                             filter_func=None,
                             optional=False)

    if cards:
        topdeck(state, player, cards[0], player.hand)


Artisan = Card(
    name="Artisan",
    types=[CardType.ACTION],
    cost=6,
    effect_fn=artisan_fn,
)


def bureaucrat_fn(state, player):
    gain_card_to_topdeck(state, player, state.supply_piles["Silver"])
    for opp in state.other_players(player):
        victory_card_count = 0
        for card in opp.hand:
            if card.is_type(CardType.VICTORY):
                victory_card_count += 1
        if victory_card_count > 0:
            topdeck_card = dec.choose_cards(
                state,
                player=opp,
                num_select=1,
                prompt="Choose a Victory Card to topdeck.",
                filter_func=lambda card: card.is_type(CardType.VICTORY),
                optional=False
            )
            if topdeck_card:
                topdeck(state, opp, topdeck_card[0], opp.hand)
        else:
            for card in opp.hand:
                reveal(state, opp, card)


Bureaucrat = Card(
    name="Bureaucrat",
    types=[CardType.ACTION, CardType.ATTACK],
    cost=4,
    effect_fn=bureaucrat_fn,
)


def sentry_fn(state, player):
    drawn_cards = player.draw(2)

    # Choose trash.
    trash_cards = dec.choose_cards(state,
                                   player,
                                   num_select=len(drawn_cards),
                                   prompt="You may trash cards with Sentry.",
                                   filter_func=None,
                                   optional=True,
                                   card_container=drawn_cards)
    for card in trash_cards:
        trash(state, player, card, container=drawn_cards)

    # Choose discard.
    discard_cards = dec.choose_cards(state,
                                     player,
                                     num_select=len(drawn_cards),
                                     prompt="You may discard cards with Sentry.",
                                     filter_func=None,
                                     optional=True,
                                     card_container=drawn_cards)
    for card in discard_cards:
        discard(state, player, card, container=drawn_cards)

    # Choose order to topdeck.
    topdeck_cards = dec.choose_cards(state,
                                     player,
                                     num_select=len(drawn_cards),
                                     prompt="You may put cards back in any order with Sentry. Cards are topdecked in "
                                            "order, so the card listed last is placed on top.",
                                     filter_func=None,
                                     optional=False,
                                     card_container=drawn_cards)
    for card in topdeck_cards:
        topdeck(state, player, card, container=drawn_cards)


Sentry = Card(
    name="Sentry",
    types=[CardType.ACTION],
    cost=5,
    add_cards=1,
    add_actions=1,
    effect_fn=sentry_fn,
)

"""
Library = Card(
    name="Library",
    types=[CardType.ACTION],
    cost=5,
    effect_list=[],
)


Sentry = Card(
    name="Sentry",
    types=[CardType.ACTION],
    cost=5,
    effect_list=[],
)

Harbinger = Card(
    name="Harbinger",
    types=[CardType.ACTION],
    cost=3,
    add_cards=1,
    add_actions=1,
    effect_list=[],
)


Moat = Card(
    name="Moat",
    types=[CardType.ACTION, CardType.REACTION],
    cost=2,
    add_cards=2,
    effect_list=[],
)

"""

BaseKingdom = {
    "Village": SupplyPile(Village, 10),
    "Laboratory": SupplyPile(Laboratory, 10),
    "Market": SupplyPile(Market, 10),
    "Festival": SupplyPile(Festival, 10),
    "Smithy": SupplyPile(Smithy, 10),
    "Militia": SupplyPile(Militia, 10),
    "Gardens": SupplyPile(Gardens, 8),
    "Chapel": SupplyPile(Chapel, 10),
    "Witch": SupplyPile(Witch, 10),
    "Workshop": SupplyPile(Workshop, 10),
    "Bandit": SupplyPile(Bandit, 10),
    "Remodel": SupplyPile(Remodel, 10),
    "Throne Room": SupplyPile(ThroneRoom, 10),
    "Moneylender": SupplyPile(Moneylender, 10),
    "Poacher": SupplyPile(Poacher, 10),
    "Merchant": SupplyPile(Merchant, 10),
    "Cellar": SupplyPile(Cellar, 10),
    "Mine": SupplyPile(Mine, 10),
    "Vassal": SupplyPile(Vassal, 10),
    "Council Room": SupplyPile(CouncilRoom, 10),
    "Artisan": SupplyPile(Artisan, 10),
    "Bureaucrat": SupplyPile(Bureaucrat, 10),
}
