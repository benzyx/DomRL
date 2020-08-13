from ..engine.agent import Agent
from ..engine.decision import *

import numpy as np
from typing import Union

PlayDecision = Union[ActionPhaseDecision, TreasurePhaseDecision]


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


def get_minimum_coin_card(decision):
    card_coins = [c.coins for c in decision.moves.card]
    return [np.argmin(card_coins)]


class BigMoneyAgent(Agent):
    def policy(self, decision, state_view):
        if not decision.optional and len(decision.moves) == 1:
            return [0]
        if decision.optional and len(decision.moves) == 0:
            return []

        if decision.prompt == 'Select a card to trash from enemy Bandit.' or \
                decision.prompt == 'Discard down to 3 cards.':
            return get_minimum_coin_card(decision)

        if state_view.player.phase == TurnPhase.TREASURE_PHASE:
            return [1]

        if state_view.player.phase == TurnPhase.BUY_PHASE:
            all_cards_money = [c.coins for c in state_view.player.previous_deck] \
                              or [0]
            hand_money_ev = np.mean(all_cards_money) * 5

            if state_view.player.coins >= 8 and hand_money_ev > 8:
                return find_card_in_decision(decision, 'Province')
            elif state_view.player.coins >= 6:
                return find_card_in_decision(decision, 'Gold')
            elif state_view.player.coins >= 3:
                return find_card_in_decision(decision, 'Silver')

        return [0]
