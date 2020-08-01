import numpy as np

from engine.card import CardType
import engine.logger as log


def trash(state, player, card, container):
    state.event_log.add_event(log.TrashEvent(player, card))
    card_idx = container.index(card)
    container.pop(card_idx)
    state.trash.append(card)


def discard(state, player, card, container):
    state.event_log.add_event(log.DiscardEvent(player, card))
    card_idx = container.index(card)
    container.pop(card_idx)
    player.discard_pile.append(card)


def topdeck(state, player, card, container):
    state.event_log.add_event(log.TopdeckEvent(player, card))
    card_idx = container.index(card)
    container.pop(card_idx)
    player.deck.append(card)


def play(state, player, card, container):
    state.event_log.add_event(log.PlayEvent(player, card))
    card_idx = container.index(card)
    container.pop(card_idx)
    player.play_area.append(card)
    card.play(state, player)
    apply_triggers(player, card)


def play_card_twice(state, player, card, container):
    for _ in range(2):
        state.event_log.add_event(log.PlayEvent(player, card))
    card_idx = container.index(card)
    container.pop(card_idx)
    player.play_area.append(card)
    card.play(state, player)
    apply_triggers(player, card)
    card.play(state, player)
    apply_triggers(player, card)


def apply_triggers(player, card):
    for trigger_type, triggers in player.trigger_state.items():
        """
        TODO (henry-prior): can we make specific cards inherit from the `Card`
            class instead? That way we can make the `is_type()` support things
            like:
            ```
            card = Silver()
            card.is_type(Silver) # True
            ```
        """
        if card.is_card(trigger_type) or card.is_type(trigger_type):
            remove_idxs = []
            for idx, trigger in enumerate(triggers):
                trigger.apply(state, player)
                if trigger.remove: remove_idxs.append(idx)

            triggers = list(np.delete(triggers, remove_idxs))


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
        state.event_log.add_event(log.GainEvent(player, pile.card))
        player.discard_pile.append(pile.card)
        pile.qty -= 1


def gain_card_to_hand(state, player, pile):
    if pile.qty > 0:
        state.event_log.add_event(log.GainEvent(player, pile.card))
        player.hand.append(pile.card)
        pile.qty -= 1


def gain_card_to_topdeck(state, player, pile):
    if pile.qty > 0:
        state.event_log.add_event(log.GainEvent(player, pile.card))
        player.deck.append(pile.card)
        pile.qty -= 1


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
    state.event_log.add_event(log.BuyEvent(player, card))
    gain_card_to_discard(state, player, pile)


def player_discard_card_from_hand(state, player, card):
    discard(state, player, card, player.hand)


def player_trash_card_from_hand(state, player, card):
    trash(state, player, card, player.hand)
