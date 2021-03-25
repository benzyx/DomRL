from ..engine.agent import Agent
from ..engine.decision import *

import numpy as np
from typing import Union

PlayDecision = Union[ActionPhaseDecision, TreasurePhaseDecision]

######################## PRIORITY SCORES #########################
# https://github.com/techmatt/Provincial/blob/master/bin/data/priority.txt?fbclid=IwAR2FEAceo0joExsbratljHgnFFoJZlkDDbcuEMfREA1voe4PL_66w3V5Pyo
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
"Chapel" : (116 - 115 + 1),
# filled in the priorities, since he set the rest to -1
# https://github.com/techmatt/Provincial/blob/3e636570d7ef359b823cb0dab3c5f8c3f1cb36b2/DominionDLL/CardDatabase.cpp#L213
"Artisan" : 106,
"Bandit" : 96,
"Vassal" : 73,
"Poacher" : 41,
"Merchant" : 25,
"Harbinger" : 11,
"Sentry" : 5
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
estate_buy_threshold = 2
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
    else:
        for idx, move in enumerate(decision.moves):
            if hasattr(move.pile, 'card') and move.pile.card.name == card_name:
                return [idx]
    return []

# helper to sort a list of tuples by the second element
def Sort_List_Of_Tuples(tup):
    # getting length of list of tuples
    lst = len(tup)
    for i in range(lst):
        for j in range(0, lst-i-1):
            if (tup[j][1] < tup[j + 1][1]):
                temp = tup[j]
                tup[j]= tup[j + 1]
                tup[j + 1]= temp
    return tup

# helper to check if a card is in their hand
def hand_contains(state_view, card_name):
    for card in state_view.player.hand:
        if card == card_name:
            return True
    return False
###################### END HELPER FUNCTIONS ######################

######################### PHASE FUNCTIONS ########################
def provincial_buy_menu(decision, state_view, buy_menu):
    # provincial greedy green card
    # https://github.com/techmatt/Provincial/blob/master/DominionDLL/BuyAgenda.cpp#L245
    prov_index = find_card_in_decision(decision, 'Province')
    duchy_index = find_card_in_decision(decision, 'Duchy')
    estate_index = find_card_in_decision(decision, 'Estate')
    prov_count = state_view.supply_piles["Province"].qty

    if prov_index != []:
        return prov_index
    if duchy_index != [] and prov_count < duchy_buy_threshold:
        return duchy_index
    if estate_index != [] and prov_count < estate_buy_threshold:
        return estate_index

    for i in range(len(buy_menu)):
        card = buy_menu[i][0]
        cost = buy_menu[i][1]
        amount_to_buy = buy_menu[i][2]
        pos = find_card_in_decision(decision, card)
        if amount_to_buy > 0 and pos != []:
            buy_menu[i] = (card, cost, amount_to_buy - 1)
            return pos

    return [0] #### buy default item

# provoncial treasure phase strategy
def provincial_treasure_phase(decision):
    return [len(decision.moves) - 1] # defaults to play all treasures

# provincial action phase strategy
def provincial_action_phase(decision, state_view):
    if len(decision.moves) == 0:
        return []
    # rank cards
    cards_ordered = []
    for i in range(len(decision.moves)):
        move = decision.moves[i]
        # https://github.com/techmatt/Provincial/blob/master/DominionDLL/PlayerHeuristic.cpp#L171
        if hasattr(move, 'card') and move.card.name == "Moneylender" and not hand_contains(state_view, "Copper"):
            cards_ordered.append((i, -1))
        elif hasattr(move, 'card'):
            cards_ordered.append((i, action_priority[move.card.name]))

    return [Sort_List_Of_Tuples(cards_ordered)[0][0]]
####################### END PHASE FUNCTIONS ######################

############################ REACTIONS ###########################
# reaction for card cellar
def provincial_reaction_cellar(decision):
    # rank cards
    cards_to_discard = []
    for i in range(len(decision.moves)):
        move = decision.moves[i]
        # https://github.com/techmatt/Provincial/blob/3e636570d7ef359b823cb0dab3c5f8c3f1cb36b2/DominionDLL/PlayerHeuristic.cpp#L292
        if hasattr(move, 'card') and (move.card.name in discard_priority or move.card.cost <= 2):
            cards_to_discard.append(i)

    return cards_to_discard

# https://github.com/techmatt/Provincial/blob/master/DominionDLL/PlayerHeuristic.cpp#L294
# reaction for card chapel
def provincial_reaction_chapel(decision, state_view):
    treasure_total = 0
    for card in state_view.player.all_cards:
        if card.name == 'Copper':
            treasure_total += 1
        elif card.name == 'Silver':
            treasure_total += 3
        elif card.name == 'Gold':
            treasure_total += 6

    trashCoppers = (treasure_total >= 7)
    cards_to_trash = []
    i = 0
    while i < len(decision.moves) and len(cards_to_trash) < 4:
        move = decision.moves[i]
        if hasattr(move, 'card') and \
            move.card.name == 'Chapel' or \
            (move.card.name == 'Estate' and state_view.supply_piles['Province'].qty > 2) or \
            move.card.name == 'Curse' or \
            (trashCoppers and move.card.name == 'Copper'):
            cards_to_trash.append(i)
        i += 1

    return cards_to_trash

# reaction for card bureaucrat
def provincial_reaction_bureaucrat(decision):
    return [0] # provincial always just chooses the first victory card

# reaction for card militia
def provincial_reaction_militia(state_view, decision):
    # rank cards
    cards_ordered = []
    for i in range(len(decision.moves)):
        move = decision.moves[i]
        if hasattr(move, 'card') and move.card.name in discard_priority:
            cards_ordered.append((i, discard_priority[move.card.name]))
        elif hasattr(move, 'card'):
            cards_ordered.append((i, -100 - move.card.cost)) # ranking provincial uses

    cards_ordered = Sort_List_Of_Tuples(cards_ordered)
    cards_to_discard = []
    num_to_discard = len(decision.moves) - 3
    for index in range(num_to_discard):
        cards_to_discard.append(cards_ordered[index][0])

    return cards_to_discard

# reaction for card throne room
def provincial_reaction_throne_room(decision, state_view):
    return provincial_action_phase(decision, state_view) # always use action policy here

# reaction for card library
def provincial_reaction_library(decision, state_view):
    # https://github.com/techmatt/Provincial/blob/3e636570d7ef359b823cb0dab3c5f8c3f1cb36b2/DominionDLL/PlayerHeuristic.cpp#L341
    if state_view.player.actions == 0:
        return [1]
    return [0]

# reaction for card mine
def provincial_reaction_mine_trash_card(decision, state_view):
    # rank cards
    cards_ordered = []
    for i in range(len(decision.moves)):
        move = decision.moves[i]
        if hasattr(move, 'card') and move.card.name == 'Silver' and state_view.supply_piles['Gold'].qty > 0:
            cards_ordered.append((i, mine_priority[move.card.name]))
        elif hasattr(move, 'card') and move.card.name == 'Copper' and state_view.supply_piles['Silver'].qty > 0:
            cards_ordered.append((i, mine_priority[move.card.name]))
        elif hasattr(move, 'card'):
            cards_ordered.append((i, -1*move.card.cost)) # ranking provincial uses

    return [Sort_List_Of_Tuples(cards_ordered)[0][0]]

# reaction for bandit
def provincial_reaction_bandit(decision):
    for i in range(len(decision.moves)):
        move = decision.moves[i]
        if move.card.name == 'Silver':
            return [i]
    return [0] # have to give up Gold

def provincial_reaction_remodel(decision, state_view):
    # https://github.com/techmatt/Provincial/blob/3e636570d7ef359b823cb0dab3c5f8c3f1cb36b2/DominionDLL/PlayerHeuristic.cpp#L56
    remodel_expensive_things = (state_view.supply_piles['Province'].qty < 8)
    # rank cards
    cards_ordered = []
    for i in range(len(decision.moves)):
        move = decision.moves[i]
        card = move.card
        if remodel_expensive_things and \
            (card.name != 'Province' and card.name != 'Dutchy' and card.name != 'Estate' and card.cost >= 6):
            cards_ordered.append((i, 20 + card.cost))
        elif card.name == 'Curse':
            cards_ordered.append((i, 19))
        elif card.name == 'Estate':
            cards_ordered.append((i, 18))
        elif (card.name == 'Province' or card.name == 'Dutchy'):
            cards_ordered.append((i, -200 + card.cost))
        else:
            cards_ordered.append((i, -card.cost))

    return [Sort_List_Of_Tuples(cards_ordered)[0][0]]


# reaction for moneylender
def provincial_reaction_moneylender(decision):
    for i in range(len(decision.moves)):
        move = decision.moves[i]
        if move.card.name == 'Copper':
            return [i]
    return [0]

# reaction for poacher
def provinicial_reaction_poacher(decision, state_view, num_to_discard):
    # rank cards
    cards_ordered = []
    for i in range(len(decision.moves)):
        move = decision.moves[i]
        if hasattr(move, 'card') and move.card.name in discard_priority:
            cards_ordered.append((i, discard_priority[move.card.name]))
        elif hasattr(move, 'card'):
            cards_ordered.append((i, -100 - move.card.cost)) # ranking provincial uses

    cards_ordered = Sort_List_Of_Tuples(cards_ordered)
    cards_to_discard = []
    for index in range(num_to_discard):
        cards_to_discard.append(cards_ordered[index][0])

    return cards_to_discard

########################## END REACTIONS #########################

class ProvincialAgent(Agent):
    def __init__(self, buy_menu):
        copy = [arg for arg in buy_menu]
        ######################## BUY MENU ########################
        self.buy_menu = copy
        ######################## BUY MENU ########################

    def policy(self, decision, state_view):
        # print("player", state_view.player.name)
        # print("actions", state_view.player.actions)
        # print("buys", state_view.player.buys)
        # print("coins", state_view.player.coins)
        # print("hand", state_view.player.hand)
        # print("number of cards", len(state_view.player.all_cards))
        # print("vc", state_view.player.total_vp)
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
            return provincial_reaction_throne_room(decision, state_view)

        # library is played
        if decision.prompt[0:13] == 'Library draws':
            return provincial_reaction_library(decision, state_view)

        # mine is played
        if decision.prompt == 'Choose a Treasure to upgrade.':
            return provincial_reaction_mine_trash_card(decision, state_view)

        # for mine and artisan (note: if Gold isn't in buy menu, mine will trade in Silver for Silver)
        if decision.prompt == 'Choose a pile to gain a card into your hand.':
            return provincial_buy_menu(decision, state_view, self.buy_menu)

        if decision.prompt == 'Choose a card to topdeck.':
            return [0] # provincial doesn't have artisan so just pick first card for now

        if decision.prompt[0:16] == "You must discard":
            num_to_discard = int(decision.prompt[17:19])
            # provincial doesn't have poacher but we apply same
            return provinicial_reaction_poacher(decision, state_view, num_to_discard)

        # workshop or remodel is played
        if decision.prompt == "Choose a pile to gain card from.":
            return provincial_buy_menu(decision, state_view, self.buy_menu)

        # bandit is played
        if decision.prompt == "Select a card to trash from enemy Bandit.":
            return provincial_reaction_bandit(decision)

        # remodel is played
        if decision.prompt == "Choose a card to trash and gain card costing 2 more.":
            return provincial_reaction_remodel(decision, state_view)

        # moneylender is played
        if decision.prompt == "Trash a copper to gain +3 coins. Choose none to skip.":
            return provincial_reaction_moneylender(decision)

        # Harbinger is played
        if decision.prompt == 'You may topdeck a card from your discard pile.':
            return [0] #provincial doesn't have this so just default for now

        # Sentry is played
        if decision.prompt == "You may trash cards with Sentry.":
            return [0] #provincial doesn't have this so just default for now
        if decision.prompt == "You may discard cards with Sentry.":
            return [0] #provincial doesn't have this so just default for now

        # chancelor is removed
        # feast is removed
        # spy is removed
        #################### END REACTIONS #######################

        ######################## PHASES ##########################
        if state_view.player.phase == TurnPhase.TREASURE_PHASE:
            return provincial_treasure_phase(decision)

        if state_view.player.phase == TurnPhase.BUY_PHASE:
            return provincial_buy_menu(decision, state_view, self.buy_menu)

        if state_view.player.phase == TurnPhase.ACTION_PHASE:
            return provincial_action_phase(decision, state_view)
        ###################### END PHASES ########################

        return [0] # always the default action
