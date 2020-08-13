import domrl.engine.state as st
from .decision import *
from .util import TurnPhase
from .state_view import StateView


def process_decision(agent, decision, state):

    # Create a StateView object, to hide information in state from the agent.
    state_view = StateView(state, decision.player)

    # Get decision from agent, giving them the view of the state.
    move_indices = agent.policy(decision, state_view)

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
    def __init__(self, agents, players=None, kingdoms=None):
        self.state = st.GameState(agents, players=players, kingdoms=kingdoms)
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

        winners = state.get_winners()
        if len(winners) == 1:
            print(f'The winner is {winners[0]}!')
        else:
            print('It\'s a tie!')

        vps = [player.total_vp() for player in state.players]
        vp_messages = ['Player {}: {} VP'.format(i+1, v)
                        for i, v in enumerate(vps)]
        for message in vp_messages:
            print(message)
