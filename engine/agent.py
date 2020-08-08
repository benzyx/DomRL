import engine.logger as log
from .decision import *
from .util import TurnPhase
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


class Agent(object):
    def policy(self, decision, state_view):
        return decision.moves[0]


class StdinAgent(Agent):
    def policy(self, decision, state_view):

        # Autoplay
        if not decision.optional and len(decision.moves) == 1:
            return [0]
        if decision.optional and len(decision.moves) == 0:
            return []

        player = decision.player

        print(f" ==== Decision to be made by {player} ==== ")
        print(f"Actions: {player.actions} | Buys: {player.buys} | Coins: {player.coins}")
        print("Hand: ", list(map(str, player.hand)))
        print(decision.prompt)

        for idx, move in enumerate(decision.moves):
            print(f"{idx}: {move}")

        # Get user input and process it.
        # TODO(benzyx): Refactor this into helper functions.
        choices = None
        while True:
            print("Enter '?' to look at state and logs.")
            # Prompt how to make decision.
            if decision.optional:
                print(f"Make up to {decision.num_select} choice(s), each separated by a comma, or enter for no "
                      f"selection.\n> ", end="")
            else:
                print(f"Make exactly {decision.num_select} choice(s), each separated by a comma, or enter for no "
                      f"selection.\n> ", end="")

            user_input = input()

            if user_input == "?":
                log.print_dict_log(state_view.event_log)

                # Refactor this to be somewhere else.
                for _, pile in state_view.supply_piles.items():
                    print(f"{pile.card_name}: {pile.qty} remaining.")

                print(f" ==== Decision to be made by {player} ==== ")
                print(f"Actions: {player.actions} | Buys: {player.buys} | Coins: {player.coins}")
                print("Hand: ", list(map(str, player.hand)))
                print(decision.prompt)
            else:
                if user_input == "":
                    choices = []
                else:
                    choices = list(map(lambda x: int(x.strip()), user_input.split(',')))

                invalid = False
                invalid_reason = None
                used_choices = set()
                if not decision.optional and len(choices) != decision.num_select:
                    invalid = True
                    print(f"Must make exactly {decision.num_select} choices, {len(choices)} given.")
                if decision.optional and len(choices) > decision.num_select:
                    invalid = True
                    print(f"Must make at most {decision.num_select} choices, {len(choices)} given.")
                for choice in choices:
                    if not (0 <= choice < len(decision.moves)):
                        invalid = True
                        print(f"Decision index {choice} out of bounds.")
                    if choice in used_choices:
                        invalid = True
                        print(f"Decision index {choice} repeated.")
                    used_choices.add(choice)

                if invalid:
                    continue

                break

        return choices


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
            hand_money_ev = np.mean(all_cards_money) * 5 / len(all_cards_money)

            if state_view.player.coins >= 8 and hand_money_ev > 8:
                return find_card_in_decision(decision, 'Province')
            elif state_view.player.coins >= 6:
                return find_card_in_decision(decision, 'Gold')
            elif state_view.player.coins >= 3:
                return find_card_in_decision(decision, 'Silver')

        return [0]

