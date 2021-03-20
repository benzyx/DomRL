import domrl.engine.logger as log
from .decision import *

class Agent(object):
    def policy(self, decision, state_view):
        return decision.moves[0]


class StdinAgent(Agent):
    """
    StdinAgent is an agent that reads from Stdin for its policy.

    It is used for humans to test games against bots.
    """
    def policy(self, decision, state_view):

        # Autoplay
        if not decision.optional and len(decision.moves) == 1:
            return [0]
        if decision.optional and len(decision.moves) == 0:
            return []

        player = decision.player

        # Get user input and process it.
        # TODO(benzyx): Refactor this into helper functions.
        choices = None
        while True:
            self.initial_prompt(decision)
            self.helper_prompt(decision)

            user_input = input()

            if user_input == "?":
                # Replay log.
                print("=== Replaying log from beginning ===")
                print(log.dict_log_to_string(state_view.events))
                print("===             end              ===")

                # Print the state of the board (quantities of piles).
                for _, pile in state_view.supply_piles.items():
                    print(f"{pile.card_name}: {pile.qty} remaining.")
            else:
                if user_input == "":
                    choices = []
                else:
                    choices = [int(x.strip()) for x in user_input.split(',')]

                if self.check_choice_validity(decision, choices):
                    break

        return choices

    def initial_prompt(self, decision):
        player = decision.player
        print(f" ==== Decision to be made by {player} ==== ")
        print(f"Actions: {player.actions} | Buys: {player.buys} | Coins: {player.coins}")
        print(f"Hand: {str(c) for c in player.hand}")
        print(decision.prompt)

        for idx, move in enumerate(decision.moves):
            print(f"{idx}: {move}")

    def helper_prompt(self, decision):
        print("Enter '?' to look at state and logs.")
        # Prompt how to make decision.
        if decision.optional:
            print(f"Make up to {decision.num_select} choice(s), each separated by a comma, or enter for no "
                  f"selection.\n> ", end="")
        else:
            print(f"Make exactly {decision.num_select} choice(s), each separated by a comma, or enter for no "
                  f"selection.\n> ", end="")

    def check_choice_validity(self, decision, choices) -> bool:
        valid = True
        if not decision.optional and len(choices) != decision.num_select:
            valid = False
            print(f"Must make exactly {decision.num_select} choices, {len(choices)} given.")
        if decision.optional and len(choices) > decision.num_select:
            valid = False
            print(f"Must make at most {decision.num_select} choices, {len(choices)} given.")

        used_choices = set()
        for choice in choices:
            if not (0 <= choice < len(decision.moves)):
                valid = False
                print(f"Decision index {choice} out of bounds.")
            if choice in used_choices:
                valid = False
                print(f"Decision index {choice} repeated.")
            used_choices.add(choice)
        return valid

