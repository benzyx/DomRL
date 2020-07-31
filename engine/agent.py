
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
        while True:
            user_input = input()
            if user_input == "?":
                state.event_log.print(player)
                print(state)
            else:
                ans = list(map(lambda x: int(x.strip()), user_input.split(',')))

                break
        return ans


class BigMoneyAgent(Agent):
    def choose(self, decision, state):
        pass

