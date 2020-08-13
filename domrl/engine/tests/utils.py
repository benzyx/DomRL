from ..agent import Agent
from ..card import CardType


class ThroneRoomAgent(Agent):
    """
    TODO (henry-prior): clean up this try-except mess by creating a cleaner
        interface around `move` which allows us to check these attributes even
        if `None`
    """

    def policy(self, decision, state_view):
        for idx, move in enumerate(decision.moves):
            print(f"{idx}: {move}")
            try:
                if move.card.name == 'Throne Room':
                    return [idx]
            except:
                pass

        for idx, move in enumerate(decision.moves):
            try:
                if move.card.is_type(CardType.ACTION):
                    state_view.supply_piles['Province'].qty = 0
                    return [idx]
            except:
                pass

        return [0]
