import domrl.engine.state as st
from .decision import *
from .util import TurnPhase
from .state_view import StateView
import pandas as pd

class Game(object):
    def __init__(self, agents, players=None, kingdoms=None, verbose=True):
        self.state = st.GameState(agents, players=players, kingdoms=kingdoms, verbose=verbose)
        self.agents = agents

    def run(self, print_logs=False):
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
        
        return self.state

    def get_log(self):
        return self.state.event_log

    def get_result_df(self):
        state = self.state
        winners_names = [p.name for p in state.get_winners()]
        dicts = []
        for i, player in enumerate(state.players):
            player_dict = {}
            player_dict['Player'] = player.name
            player_dict['VP'] = player.total_vp()
            player_dict['Turns'] = player.turns
            player_dict['Winner'] = player.name in winners_names
            dicts.append(player_dict)
        return pd.DataFrame(dicts)

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
