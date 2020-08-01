
class StateView(object):
    """
    The StateView object is what we are going to pass to an agent before they make a decision.

    It needs to hide the aspects of State that should not be exposed to the agent.

    In fact, it
    """
    def __init__(self, state, player):

        self.supply_piles = state.supply_piles
        self.player = player
