from engine.util import *
from engine.decision import *

# A context is a game scope that needs to be resolved on the stack.
#
class Context(object):

    def __init__(self):
        pass

    def get_decision(self):
        raise Exception("get_decision is not implemented.")

    @property
    def can_resolve(self):
        raise Exception("can_resolve not implemented for context.")

    def update(self, paramter):
        raise Exception("update not implemented for context.")

    def resolve(self, state):
        raise Exception("resolve not implemented for context.")

class TurnContext(Context):

    def __init__(self, state):
        self.state = state

    def get_decision(self):
        state = self.state
        player = state.current_player()
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

        return decision

    @property
    def can_resolve(self):
        return False

    def update(self, res):
        pass


"""
Context when any player needs to choose cards from their hand.

Does not implement resolve() -- is meant to be implemented by derived classes.
"""
class ChooseCardsFromHandContext(Context):


    def __init__(self, state, player, num_cards, filter_type = None, optional = True, prompt = None):
        self.state = state
        self.player = player
        self.num_cards = num_cards
        self.num_remaining = num_cards
        self.optional = optional
        self.filter_type = filter_type
        self.done = False
        self.prompt = prompt

        self.cards = []

    def get_decision(self):
        return self.ChooseCardsDecision(
                player=self.player,
                context=self,
                num_select=self.num_cards,
                filter_type=self.filter_type,
                optional=self.optional,
                prompt=self.prompt)

    @property
    def can_resolve(self):
        return self.num_remaining == 0 or self.done

    def update(self, card):
        if card is not None:
            self.num_remaining -= 1
            self.cards.append(card)
        else:
            self.done = True

    def resolve(self, state):
        return self.cards


    """
    Decision for choosing cards.
    """
    class ChooseCardsDecision(Decision):
        def __init__(self, player, context, num_select, prompt, filter_type=None, optional=True):
            moves = []

            if optional:
                moves.append(self.AddCardToContext(None, context))
            for card_idx, card in enumerate(player.hand):
                if filter_type is None or card.is_type(filter_type):
                    moves.append(self.AddCardToContext(card, context))

            super().__init__(
                moves,
                player,
                num_select=num_select,
                optional=optional,
                prompt=prompt)


        class AddCardToContext(Move):
            """
            Add a card to the context.
            """
            def __init__(self, card, context):
                self.context = context
                self.card = card

            def __str__(self):
                return f"Choose: {self.card}"

            def do(self, state):
                self.context.update(self.card)


class ChoosePileFromSupplyContext(Context):
    """
    Context for choosing a supply pile. Only allow for choosing 1 pile at a time.
    """
    def __init__(self, state, player, filter_func, prompt):
        self.state = state
        self.player = player
        self.filter_func = filter_func
        self.pile = None

    def get_decision(self):
        return ChoosePileDecision(
            player = self.player,
            context = self,
            filter_func=self.filter_func,
            prompt=self.prompt,
        )

    """
    Decision for choosing cards.
    """
    class ChoosePileDecision(Decision):
        def __init__(self, player, context, filter_func, prompt):
            moves = []

            for card_idx, card in enumerate(player.hand):
                if filter_type is None or card.is_type(filter_type):
                    moves.append(self.AddPileToContext(card, context))

            super().__init__(moves, player, prompt=prompt)

        class AddPileToContext(Move):
            """
            Add a card to the context.
            """
            def __init__(self, pile, context):
                self.context = context
                self.pile = pile

            def __str__(self):
                return f"Choose: {self.pile}"

            def do(self, state):
                self.context.update(self.pile)
