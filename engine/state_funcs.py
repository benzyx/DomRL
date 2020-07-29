from engine.card import CardType

"""
These apply the effect to a card in a player's hand.

The follow (essential) functions will mutate state.
"""
def play_card_from_hand(state, player, card):
    """ Play card from hand """
    if card.is_type(CardType.ACTION):
        assert(player.actions > 0)
        player.actions -= 1

    card_idx = player.hand.index(card)
    player.hand.pop(card_idx)
    player.play_area.append(card)
    card.play(state, player)

def gain_card_to_discard(state, player, pile):
    if pile.qty > 0:
        player.discard_pile.append(pile.card)
        pile.qty -= 1

def gain_card_to_hand(state, player, pile):
    if pile.qty > 0:
        player.hand.append(pile.card)
        pile.qty -= 1

def gain_card_to_topdeck(state, player, pile):
    if pile.qty > 0:
        player.deck.append(pile.card)
        pile.qty -= 1

def buy_card(state, player, card_name):
    """
    TODO (henry-prior): assert statements break execution, can we handle w
        a return to decision context and warning? (will only come up when human
        is playing)
    """
    assert(card_name in state.supply_piles)
    assert(state.supply_piles[card_name].qty > 0)

    pile = state.supply_piles[card_name]
    card = pile.card

    assert(player.coins >= card.cost)
    player.coins -= card.cost
    player.buys -= 1

    gain_card_to_discard(state, player, pile)

def player_discard_card_from_hand(state, player, card):
    card_idx = player.hand.index(card)
    player.hand.pop(card_idx)
    player.discard_pile.append(card)

def player_trash_card_from_hand(state, player, card):
    card_idx = player.hand.index(card)
    player.hand.pop(card_idx)
    state.trash.append(card)
