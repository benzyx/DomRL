from .util import CardType
from random import shuffle
import domrl.engine.logger as log


def process_event(state, event):
    """
    This function is the entrypoint for all new events that are processed.
    """
    state.event_log.add_event(event)

    # Process all reaction triggers.
    for trigger in state.global_triggers:
        if trigger.condition(event):
            trigger.apply(event, state)

    # Process all turn triggers (Merchant, Goons, etc).
    for trigger in state.turn_triggers:
        if trigger.condition(event):
            trigger.apply(event, state)


# The following functions are the entry points for most card operations.

def trash(state, player, card, container):
    process_event(state, log.TrashEvent(player, card))
    card_idx = container.index(card)
    container.pop(card_idx)
    state.trash.append(card)


def discard(state, player, card, container):
    process_event(state, log.DiscardEvent(player, card))
    card_idx = container.index(card)
    container.pop(card_idx)
    player.discard_pile.append(card)


def topdeck(state, player, card, container):
    process_event(state, log.TopdeckEvent(player, card))
    card_idx = container.index(card)
    container.pop(card_idx)
    player.draw_pile.append(card)


def play_inplace(state, player, card):
    process_event(state, log.PlayEvent(player, card))
    process_event(state, log.EnterContext())
    card.play(state, player)
    process_event(state, log.ExitContext())


def play(state, player, card, container):
    card_idx = container.index(card)
    container.pop(card_idx)
    player.play_area.append(card)
    play_inplace(state, player, card)


def reveal(state, player, card):
    process_event(state, log.RevealEvent(player, card))


# These next functions are for drawing cards.


def _cycle_shuffle(state, player):
    """
    Moves all cards from discard pile to draw_pile, and shuffles it.
    """
    process_event(state, log.ShuffleEvent(player))

    assert (len(player.draw_pile) == 0)
    player.draw_pile = player.discard_pile
    player.previous_deck = player.discard_pile
    player.discard_pile = []
    shuffle(player.draw_pile)


def draw_one(state, player, draw_event):
    if len(player.draw_pile) == 0:
        _cycle_shuffle(state, player)

    if len(player.draw_pile) >= 1:
        card = player.draw_pile.pop()
        if draw_event:
            process_event(state, log.DrawEvent(player, card))
        return card
    else:
        return None


def draw(state, player, num, draw_event=True):
    cards = []
    for i in range(num):
        card = draw_one(state, player, draw_event)
        if card:
            cards.append(card)
    return cards


def draw_into_hand(state, player, num):
    cards = draw(state, player, num)
    player.hand.extend(cards)


def clean_up(state, player):
    player.discard_pile.extend(player.play_area)
    player.discard_pile.extend(player.hand)
    player.play_area = []
    player.hand = []
    draw_into_hand(state, player, 5)


def end_turn(state):
    clean_up(state, state.current_player)
    state.next_player_turn()
    if state.current_player_idx == 0:
        state.turn += 1

    # Reset all Triggers for this turn (such as Merchant).
    state.turn_triggers = []

    state.current_player.init_turn()

"""
These apply the effect to a card in a player's hand.

The follow (essential) functions will mutate state.
"""


def play_card_from_hand(state, player, card):
    """ Play card from hand """
    if card.is_type(CardType.ACTION):
        assert (player.actions > 0)
        player.actions -= 1

    play(state, player, card, player.hand)


def gain_card_to_discard(state, player, pile):
    if pile.qty > 0:
        process_event(state, log.GainEvent(player, pile.card))
        player.discard_pile.append(pile.card)
        pile.qty -= 1


def gain_card_to_hand(state, player, pile):
    if pile.qty > 0:
        process_event(state, log.GainEvent(player, pile.card))
        player.hand.append(pile.card)
        pile.qty -= 1


def gain_card_to_topdeck(state, player, pile):
    if pile.qty > 0:
        process_event(state, log.GainEvent(player, pile.card))
        process_event(state, log.EnterContext())
        process_event(state, log.TopdeckEvent(player, pile.card))
        player.draw_pile.append(pile.card)
        pile.qty -= 1
        process_event(state, log.ExitContext())


def buy_card(state, player, card_name):
    """
    TODO (henry-prior): assert statements break execution, can we handle w
        a return to decision context and warning? (will only come up when human
        is playing)
    """
    assert (card_name in state.supply_piles)
    assert (state.supply_piles[card_name].qty > 0)

    pile = state.supply_piles[card_name]
    card = pile.card

    assert (player.coins >= card.cost)
    player.coins -= card.cost
    player.buys -= 1
    process_event(state, log.BuyEvent(player, card))
    process_event(state, log.EnterContext())
    gain_card_to_discard(state, player, pile)
    process_event(state, log.ExitContext())



def player_discard_card_from_hand(state, player, card):
    discard(state, player, card, player.hand)


def player_trash_card_from_hand(state, player, card):
    trash(state, player, card, player.hand)
