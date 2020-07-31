import random

from engine.state import *
from engine.decision import *
from engine.agent import *
from engine.util import TurnPhase

from enum import Enum

def process_decision(agent, decision, state):

    # Get decision from agent.
    move_indices = agent.choose(decision, state)

    # TODO(benzyx): Enforce that the indices are not repeated.
    if decision.optional:
        if len(move_indices) > decision.num_select:
            raise Exception("Decision election error! Too many moves selected.")
    else:
        if len(move_indices) != decision.num_select:
            raise Exception("Decision election error! Number of moves selected not correct.")

    for idx in move_indices:
        decision.moves[idx].do(state)

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
            process_decision(agent, decision, state)

