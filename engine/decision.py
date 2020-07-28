from engine.card import *
from engine.util import *
from engine.state_funcs import *

"""
An object that represents various Moves for a player to make.

Members:
- moves: List<Move>, list of Moves that a player can choose at this decision.
- player: Player, the Player that needs to make the decision.
- num_select: int, the number of moves that the player can legally select.
- optional: bool, True if the player can make any number of decision up to num_select,
                  False if the player must select exactly num_select Moves to make.
- prompt: str, The string that explains to Agent when given this decision.

"""
class Decision(object):
    def __init__(
            self,
            moves,
            player,
            num_select=1,
            optional=False,
            prompt="Unimplemented decision prompt"):
        self.moves = moves
        self.player = player
        self.num_select = num_select
        self.optional = optional
        self.prompt = prompt

class ActionPhaseDecision(Decision):

    def __init__(self, player):
        moves = []

        # Always allowed to end action Phase
        moves.append(EndActionPhase())

        # Play any action cards if we have remaining actions.
        if player.actions > 0:
            for card_idx, card in enumerate(player.hand):
                if card.is_type(CardType.ACTION):
                    moves.append(PlayCard(card))

        super().__init__(moves, player, prompt="Action Phase, choose card to play.")

class TreasurePhaseDecision(Decision):

    def __init__(self, player):
        moves = []

        # Always allowed to end treasure Phase
        moves.append(EndTreasurePhase())

        for card_idx, card in enumerate(player.hand):
            if card.is_type(CardType.TREASURE):
                moves.append(PlayCard(card))

        super().__init__(moves, player, prompt="Treasure Phase, choose card to play.")


class BuyPhaseDecision(Decision):

    def __init__(self, state, player):
        # Always allowed to end buy phase
        moves = [EndBuyPhase()]

        for card_name, supply_pile in state.supply_piles.items():
            if (supply_pile.qty > 0
                and player.coins >= supply_pile.card.cost
                and player.buys > 0):
                moves.append(BuyCard(card_name))

        super().__init__(moves, player, prompt="Buy Phase, choose card to buy.")


class EndPhaseDecision(Decision):

    def __init__(self, player):
        moves = [EndTurn()]

        super().__init__(moves, player, prompt="End Turn")




"""
An Move is an Action that a player can take.

Must implement do(game_state), which is called when the player selects that Move.
"""
class Move(object):
    def __init__(self):
        return

    def __str__(self):
        return "Unimplemented string for Move."

    def do(self, state):
        raise "Move does not implement do."

"""
Player plays a card.
"""
class PlayCard(Move):
    def __init__(self, card):
        self.card = card

    def __str__(self):
        return f"Play: {self.card}"

    def do(self, state):
        play_card_from_hand(state, state.current_player(), self.card)

class BuyCard(Move):
    def __init__(self, card_name):
        self.card_name = card_name

    def __str__(self):
        return f"Buy: {self.card_name}"

    def do(self, state):
        buy_card(state, state.current_player(), self.card_name)


"""
End Action Phase.
"""
class EndActionPhase(Move):
    def __str__(self):
        return "End Action Phase"

    def do(self, state):
        assert(state.current_player().phase == TurnPhase.ACTION_PHASE)
        state.current_player().phase = TurnPhase.TREASURE_PHASE

"""
End Treasure Phase.
"""
class EndTreasurePhase(Move):
    def __str__(self):
        return "End Treasure Phase"

    def do(self, state):
        assert(state.current_player().phase == TurnPhase.TREASURE_PHASE)
        state.current_player().phase = TurnPhase.BUY_PHASE

"""
End Buy Phase
"""
class EndBuyPhase(Move):
    def __str__(self):
        return "End Buy Phase"

    def do(self, state):
        assert(state.current_player().phase == TurnPhase.BUY_PHASE)
        state.current_player().phase = TurnPhase.END_PHASE

"""
End Turn
"""
class EndTurn(Move):
    def __str__(self):
        return "End Turn"

    def do(self, state):
        assert(state.current_player().phase == TurnPhase.END_PHASE)
        state.end_turn()
