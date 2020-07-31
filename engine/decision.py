from engine.card import *
from engine.util import *
from engine.state_funcs import *

class Move(object):
    """
    An Move is an Action that a player can take.

    Must implement do(game_state), which is called when the player selects that Move.
    """
    def __init__(self):
        return

    def __str__(self):
        return "Unimplemented string for Move."

    def do(self, state):
        raise "Move does not implement do."


class Decision(object):
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
        # Always allowed to end treasure Phase
        moves = [EndTreasurePhase()]

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


class ChooseCardsDecision(Decision):
    """
    Decision for choosing cards (from the players hand).
    """
    def __init__(self,
        player,
        num_select,
        prompt,
        filter_func=None,
        optional=True,
        card_container=None):
        
        self.cards = []
        moves = []

        # By default, this decision chooses from the player's hand.
        if card_container == None:
            card_container = player.hand

        for card_idx, card in enumerate(card_container):
            if filter_func is None or filter_func(card):
                moves.append(self.ChooseCard(card, self))

        super().__init__(
            moves,
            player,
            num_select=num_select,
            optional=optional,
            prompt=prompt
        )


    class ChooseCard(Move):
        """
        Add a card to the context.
        """
        def __init__(self, card, decision):
            self.decision = decision
            self.card = card

        def __str__(self):
            return f"Choose: {self.card}"

        def do(self, state):
            self.decision.cards.append(self.card)


class ChoosePileDecision(Decision):
    """
    Decision for choosing one supply pile.

    TODO(benzyx): maybe one day you need to select multiple piles?
    """
    def __init__(self, state, player, filter_func, prompt):
        moves = []
        for card_name, pile in state.supply_piles.items():
            if filter_func is None or filter_func(pile):
                moves.append(self.ChoosePile(self, pile))

        self.pile = None

        super().__init__(moves, player, prompt=prompt)

    class ChoosePile(Move):
        """
        Add a card to the Decision.
        """
        def __init__(self, decision, pile):
            self.decision = decision
            self.pile = pile

        def __str__(self):
            return f"Choose: {self.pile.card.name} pile"

        def do(self, state):
            print("DOING THE CHOOSEPILE MOVE!")
            print(self.decision)
            self.decision.pile = self.pile



"""
Player plays a card.
"""
class PlayCard(Move):
    def __init__(self, card):
        self.card = card

    def __str__(self):
        return f"Play: {self.card}"

    def do(self, state):
        play_card_from_hand(state, state.current_player, self.card)

class BuyCard(Move):
    def __init__(self, card_name):
        self.card_name = card_name

    def __str__(self):
        return f"Buy: {self.card_name}"

    def do(self, state):
        buy_card(state, state.current_player, self.card_name)


"""
End Action Phase.
"""
class EndActionPhase(Move):
    def __str__(self):
        return "End Action Phase"

    def do(self, state):
        assert(state.current_player.phase == TurnPhase.ACTION_PHASE)
        state.current_player.phase = TurnPhase.TREASURE_PHASE

"""
End Treasure Phase.
"""
class EndTreasurePhase(Move):
    def __str__(self):
        return "End Treasure Phase"

    def do(self, state):
        assert(state.current_player.phase == TurnPhase.TREASURE_PHASE)
        state.current_player.phase = TurnPhase.BUY_PHASE

"""
End Buy Phase
"""
class EndBuyPhase(Move):
    def __str__(self):
        return "End Buy Phase"

    def do(self, state):
        assert(state.current_player.phase == TurnPhase.BUY_PHASE)
        state.current_player.phase = TurnPhase.END_PHASE

"""
End Turn
"""
class EndTurn(Move):
    def __str__(self):
        return "End Turn"

    def do(self, state):
        assert(state.current_player.phase == TurnPhase.END_PHASE)
        state.end_turn()
