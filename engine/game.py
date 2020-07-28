import random

from engine.state import *
from engine.decision import *
from engine.agent import *

from enum import Enum


class Game(object):
    def __init__(self, agents):
        self.state = GameState(len(agents))
        self.agents = agents

    def run(self):
        state = self.state
        while not state.is_game_over():

            state.resolve_contexts()
            decision = state.get_next_decision()
            player = decision.player

            agent = self.agents[player.idx]
            
            # Print state of the board.
            print(state)
            print(f" ==== Decision to be made by {player} ==== ")
            print(f"Actions: {player.actions} | Buys: {player.buys} | Coins: {player.coins}")
            print("Hand: ", list(map(str, player.hand)))


            while True:
                # Get decision from agent.
                move_indices = agent.choose(decision, state)

                if decision.optional:
                    if len(move_indices) > decision.num_select:
                        print("Decision election error! Too many moves selected.")
                        continue
                else:
                    if len(move_indices) != decision.num_select:
                        print("Decision election error! Number of moves selected not correct.")
                        continue

                for idx in move_indices:
                    decision.moves[idx].do(state)

                break

