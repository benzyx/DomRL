import domrl.engine.state as st
from .decision import *
from .util import TurnPhase
from .state_view import StateView

class Game(object):
    def __init__(self, agents, players=None, kingdoms=None, verbose=True):
        self.state = st.GameState(agents, players=players, kingdoms=kingdoms, verbose=verbose)
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
        return state

    def print_result(self):
        state = self.state
        winners = state.get_winners()
        if len(winners) == 1:
            print(f'The winner is {winners[0]}!')
        else:
            print("It's a tie!")

        vps = [player.total_vp() for player in state.players]
        vp_messages = ['Player {}: {} VP'.format(i+1, v)
                        for i, v in enumerate(vps)]
        for message in vp_messages:
            print(message)