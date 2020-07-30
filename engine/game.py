import random

from engine.state import *
from engine.decision import *
from engine.agent import *
from engine.util import TurnPhase

from enum import Enum

def process_decision(agent, decision, state):
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

class Game(object):
    def __init__(self, agents):
        self.state = GameState(agents)
        self.agents = agents

    def run(self):
        state = self.state
        while not state.is_game_over():

            player = state.current_player
            agent = player.agent
            decision = None

            # Determine the phase, and decision.
            if player.phase == TurnPhase.ACTION_PHASE:
                decision = ActionPhaseDecision(player)
            elif player.phase == TurnPhase.TREASURE_PHASE:
                decision = TreasurePhaseDecision(player)
            elif player.phase == TurnPhase.BUY_PHASE:
                decision = BuyPhaseDecision(state, player)
            elif player.phase == TurnPhase.END_PHASE:
                decision = EndPhaseDecision(player)
            else:
                raise Exception("TurnContext: Unknown current player phase")
            
            # Print state of the board.
            print(state)
            print(f" ==== Decision to be made by {player} ==== ")
            print(f"Actions: {player.actions} | Buys: {player.buys} | Coins: {player.coins}")
            print("Hand: ", list(map(str, player.hand)))


            process_decision(agent, decision, state)

