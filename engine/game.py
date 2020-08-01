import random

from engine.state import *
from engine.decision import *
from engine.agent import *
from engine.util import TurnPhase
from engine.process_decision import process_decision

from enum import Enum


class Game(object):
    def __init__(self, agents, players=None):
        self.state = GameState(agents, players=players)
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
