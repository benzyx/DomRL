class Agent(object):
    def choose(self, decision, state):
        return decision.moves[0]


class StdinAgent(Agent):
    def choose(self, decision, state):

        # Autoplay
        if len(decision.moves) == 1:
            return [0]

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
            # Prompt how to make decision.
            if decision.optional:
                print(f"Make up to {decision.num_select} choice(s), each separated by a comma, or enter for no "
                      f"selection.\n> ", end="")
            else:
                print(f"Make exactly {decision.num_select} choice(s), each separated by a comma, or enter for no "
                      f"selection.\n> ", end="")
            user_input = input()

            if user_input == "?":
                state.event_log.print(player)
                print(state)
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
    def choose(self, decision, state):
        pass
