from engine.card import CardType
import engine.logger as log


def process_event(state, event):
    """
    This function is the entrypoint for all new events that are processed.
    """
    state.event_log.add_event(event)

    # Process all reaction triggers.
    # for trigger in state.reaction_triggers:
    #     if trigger.condition(event):
    #         trigger.apply(state)

    # Process all turn triggers (Merchant, Goons, etc).
    print("Entry point reached.")
    for trigger in state.turn_triggers:
        print("Processing a trigger.")
        if trigger.condition(event):
            print("Trigger condition met!")
            trigger.apply(state)


# The following functions are the entry points for most
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
    player.deck.append(card)


def play_inplace(state, player, card):
    process_event(state, log.PlayEvent(player, card))
    card.play(state, player)
    # apply_triggers(player, card)


def play(state, player, card, container):
    card_idx = container.index(card)
    container.pop(card_idx)
    player.play_area.append(card)
    play_inplace(state, player, card)


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
    process_event(state, log.BuyEvent(player, card))
    gain_card_to_discard(state, player, pile)


def player_discard_card_from_hand(state, player, card):
    discard(state, player, card, player.hand)


def player_trash_card_from_hand(state, player, card):
    trash(state, player, card, player.hand)
