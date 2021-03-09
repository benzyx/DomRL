from ..engine.agent import Agent
from ..engine.decision import *

import numpy as np
from typing import Union

PlayDecision = Union[ActionPhaseDecision, TreasurePhaseDecision]

######################## PRIORITY SCORES #########################
action_priority = {
"Throne Room" : (116 - 2 + 1),
"Laboratory" : (116 - 10 + 1),
"Market" : (116 - 12 + 1),
"Festival" : (116 - 14 + 1),
"Village" : (116 - 17 + 1),
"Cellar" : (116 - 38 + 1),
"Witch" : (116 - 46 + 1),
"Council Room" : (116 - 53 + 1),
"Smithy" : (116 - 54 + 1),
"Library" : (116 - 64 + 1),
"Militia" : (116 - 65 + 1),
"Moneylender" : (116 - 93 + 1),
"Bureaucrat" : (116 - 102 + 1),
"Mine" : (116 - 105 + 1),
"Moat" : (116 - 108 + 1),
"Remodel" : (116 - 113 + 1),
"Workshop" : (116 - 114 + 1),
"Chapel" : (116 - 115 + 1)
}

discard_priority = {
"Estate" : 20,
"Dutchy" : 20,
"Province" : 20,
"Curse" : 19,
"Copper" : 18
}

mine_priority = {
"Silver" : 19,
"Copper" : 18
}

# provincial thresholds
# https://github.com/techmatt/Provincial/blob/master/DominionDLL/BuyAgenda.cpp#L118
province_buy_threshold = 4
duchy_buy_threshold = 3
estate_buy_threshold = 0 ### provincial has this as 2 but I think that's terrible
####################### END PRIORITY SCORES ######################

######################## HELPER FUNCTIONS ########################
# helper to find index of a card
def find_card_in_decision(decision, card_name):
    if isinstance(decision, PlayDecision.__args__):
        for idx, move in enumerate(decision.moves):
            if hasattr(move, 'card') and move.card.name == card_name:
                return [idx]
    elif isinstance(decision, BuyPhaseDecision):
        for idx, move in enumerate(decision.moves):
            if hasattr(move, 'card_name') and move.card_name == card_name:
                return [idx]
    return [0]

# helper to sort a list of tuples by the second element
def Sort_List_Of_Tuples(tup):
    # getting length of list of tuples
    lst = len(tup)
    for i in range(0, lst):
        for j in range(0, lst-i-1):
            if (tup[j][1] < tup[j + 1][1]):
                temp = tup[j]
                tup[j]= tup[j + 1]
                tup[j + 1]= temp
    return tup

# helper to check if a card is in their hand
def hand_contains(state_view, card_name):
    for card in state_view.player.hand:
        if card.name == card_name:
            return True
    return False
###################### END HELPER FUNCTIONS ######################

######################### PHASE FUNCTIONS ########################
def provincial_buy_menu(decision, state_view, coins, buy_menu):
    # provincial greedy green card
    # https://github.com/techmatt/Provincial/blob/master/DominionDLL/BuyAgenda.cpp#L245
    prov_index = find_card_in_decision(decision, 'Province')
    duchy_index = find_card_in_decision(decision, 'Duchy')
    estate_index = find_card_in_decision(decision, 'Estate')
    prov_count = state_view.supply_piles["Province"].qty
    duchy_count = state_view.supply_piles["Duchy"].qty
    estate_count = state_view.supply_piles["Estate"].qty

    if coins >= 8 and prov_index != [0]:
        return prov_index
    if coins >= 5 and duchy_index != [0] and prov_count < duchy_buy_threshold:
        return duchy_index
    if coins >= 1 and estate_index != [0] and prov_count < estate_buy_threshold:
        return estate_index

    for i in range(len(buy_menu)):
        card = buy_menu[i][0]
        cost = buy_menu[i][1]
        amount_to_buy = buy_menu[i][2]
        if amount_to_buy > 0 and state_view.supply_piles[card].qty > 0 and coins >= cost:
            buy_menu[i] = (card, cost, amount_to_buy - 1)
            return find_card_in_decision(decision, card)
    return [0] #### buy nothing

# provincial's buy menu for Big Money
def provincial_buy_menu_big_money(decision, state_view, coins):
    if coins >= 8:
        return find_card_in_decision(decision, 'Province')
    if coins >= 5 and state_view.supply_piles['Province'].qty <= 4:
        return find_card_in_decision(decision, 'Duchy')
    if coins >= 1 and state_view.supply_piles['Province'].qty <= 2:
        return find_card_in_decision(decision, 'Estate')
    elif coins >= 6:
        return find_card_in_decision(decision, 'Gold')
    elif coins >= 3:
        return find_card_in_decision(decision, 'Silver')
    else:
        return [0] #### buy nothing

# provoncial treasure phase strategy
def provincial_treasure_phase(decision):
    return [len(decision.moves) - 1] # defaults to play all treasures

# provincial action phase strategy
def provincial_action_phase(decision):
    # no actions in hand
    if len(decision.moves) == 1:
        return [0]

    # rank cards
    cards_ordered = []
    for i in range(1, len(decision.moves)):
        move = decision.moves[i]
        if hasattr(move, 'card') and move.card.name == "Moneylender" and hand_contains("Copper"):
            cards_ordered.append((i, action_priority[move.card.name]))
        elif hasattr(move, 'card'):
            cards_ordered.append((i, action_priority[move.card.name]))

    return [Sort_List_Of_Tuples(cards_ordered)[0][0]]
####################### END PHASE FUNCTIONS ######################

############################ REACTIONS ###########################
# reaction for card cellar
def provincial_reaction_cellar(decision):
    # no cards to discard
    if len(decision.moves) == 1:
        return [0]

    # rank cards
    cards_ordered = []
    for i in range(1, len(decision.moves)):
        move = decision.moves[i]
        if hasattr(move, 'card') and (move.card.name in discard_priority or move.card.cost <= 2):
            return [i]

    return [0]

# reaction for card chapel
def provincial_reaction_chapel(decision, state_view):
    # no cards to trash
    if len(decision.moves) == 1:
        return [0]

    treasure_total = 0
    for card in state_view.player.all_cards:
        if card.name == 'Copper':
            treasure_total += 1
        elif card.name == 'Silver':
            treasure_total += 3
        elif card.name == 'Gold':
            treasure_total += 6

    trashCoppers = (treasure_total >= 7)

    for i in range(1, len(decision.moves)):
        move = decision.moves[i]
        if hasattr(move, 'card') and \
            move.card.name == 'Chapel' or \
            (move.card.name == 'Estate' and state_view.supply_piles['Province'].qty > 2) or \
            move.card.name == 'Curse' or \
            (trashCoppers and move.card.name == 'Copper'):
            return [i]

    return [0]

def provincial_reaction_mine_gain_card(decision, state_view, buy_menu):
    card_options = [supply.pile.card.name for supply in decision.moves]
    gold_pos = "Gold" in card_options
    silver_pos = "Silver" in card_options
    if gold_pos:
        return [card_options.index("Gold")]
    if silver_pos:
        return [card_options.index("Silver")]
    return [0] #### last available option is copper

# reaction for card bureaucrat
def provincial_reaction_bureaucrat(decision):
    if len(decision.moves) == 1:
        return [0]
    return [1] # provincial always just chooses the first victory card

# reaction for card militia
def provincial_reaction_militia(state_view, decision):
    # no cards to discard
    if len(decision.moves) == 1:
        return [0]

    # rank cards
    cards_ordered = []
    for i in range(1, len(decision.moves)):
        move = decision.moves[i]
        if hasattr(move, 'card') and move.card.name in discard_priority:
            cards_ordered.append((i, discard_priority[move.card.name]))
        elif hasattr(move, 'card'):
            cards_ordered.append((i, -100 - move.card.cost)) # ranking provincial uses

    cards_ordered = Sort_List_Of_Tuples(cards_ordered)
    card_to_discard = []
    num_to_discard = len(decision.moves) - 3
    for index in range(num_to_discard):
        card_to_discard.append(cards_ordered[index][0])

    return card_to_discard

# reaction for card throne room
def provincial_reaction_throne_room(decision):
    return provincial_action_phase(decision) # always use action policy here

# reaction for card library
def provincial_reaction_library(decision):
    return [1] # for now we always keep action cards (need to check what provincial does)

# reaction for card mine
def provincial_reaction_mine_trash_card(decision, state_view):
    # no treasure cards in hand
    if len(decision.moves) == 1:
        return [0]

    # rank cards
    cards_ordered = []
    for i in range(1, len(decision.moves)):
        move = decision.moves[i]
        if hasattr(move, 'card') and move.card.name == 'Silver' and state_view.supply_piles['Gold'].qty > 0:
            cards_ordered.append((i, mine_priority[move.card.name]))
        elif hasattr(move, 'card') and move.card.name == 'Copper' and state_view.supply_piles['Silver'].qty > 0:
            cards_ordered.append((i, mine_priority[move.card.name]))
        elif hasattr(move, 'card'):
            cards_ordered.append((i, -1*move.card.cost)) # ranking provincial uses

    return [Sort_List_Of_Tuples(cards_ordered)[0][0]]
########################## END REACTIONS #########################

class ProvincialAgent(Agent):
    def __init__(self, buy_menu):
        copy = [arg for arg in buy_menu]
        ######################## BUY MENU ########################
        self.buy_menu = copy
        ######################## BUY MENU ########################

    def policy(self, decision, state_view):
        ######################## DEFAULT #########################
        if not decision.optional and len(decision.moves) == 1:
            return [0]
        if decision.optional and len(decision.moves) == 0:
            return []
        ###################### END DEFAULT #######################

        ######################## REACTIONS #######################
        # cellar is played
        if decision.prompt == 'Discard as many cards as you would like to draw.':
            return provincial_reaction_cellar(decision)

        # chapel is played
        if decision.prompt == 'Trash up to 4 cards.':
            return provincial_reaction_chapel(decision, state_view)

        # moat is handeled by global trigger

        # bureaucrat is played
        if decision.prompt == 'Choose a Victory Card to topdeck.':
            return provincial_reaction_bureaucrat(decision)

        # militia is played
        if decision.prompt == 'Discard down to 3 cards.':
            return provincial_reaction_militia(state_view, decision)

        # throneroom is played
        if decision.prompt == 'Select a card to play twice.':
            return provincial_reaction_throne_room(decision)

        # library is played
        if decision.prompt[0:13] == 'Library draws':
            return provincial_reaction_library(decision)

        # mine is played
        if decision.prompt == 'Choose a Treasure to upgrade.':
            return provincial_reaction_mine_trash_card(decision, state_view)
        if decision.prompt == 'Choose a pile to gain a card into your hand.':
            return provincial_reaction_mine_gain_card(decision, state_view, self.buy_menu)

        # chancelor is removed
        # feast is removed
        # spy is removed
        #################### END REACTIONS #######################

        ######################## PHASES ##########################
        if state_view.player.phase == TurnPhase.TREASURE_PHASE:
            return provincial_treasure_phase(decision)

        if state_view.player.phase == TurnPhase.BUY_PHASE:
            return provincial_buy_menu(decision, state_view, state_view.player.coins, self.buy_menu)

        if state_view.player.phase == TurnPhase.ACTION_PHASE:
            return provincial_action_phase(decision)
        ###################### END PHASES ########################

        return [0] # always the default action
