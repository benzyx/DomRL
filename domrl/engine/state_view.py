class PlayerView(object):
    def __init__(self, player, is_player: bool):
        # Public player members.
        self.name = player.name
        self.idx = player.idx
        self.vp_tokens = player.vp_tokens
        self.total_vp = player.total_vp()
        self.actions = player.actions
        self.coins = player.coins
        self.buys = player.buys
        self.play_area = [card.name for card in player.play_area]
        self.phase = player.phase

        # Only visible to the player, not his opponents.
        self.discard_pile = [card.name for card in player.discard_pile] \
            if is_player else [None for card in player.discard_pile]
        self.hand = [card.name for card in player.hand] \
            if is_player else [None for card in player.discard_pile]
        # added to allow for full provincial functionality
        self.draw_pile = [card.name for card in player.draw_pile] \
            if is_player else [None for card in player.draw_pile]

        # added to allow for full provincial functionality
        self.all_cards = [card for card in player.discard_pile] + \
            [card for card in player.hand] + \
            [card for card in player.draw_pile]
        self.all_card_names = [card.name for card in player.discard_pile] + \
            [card.name for card in player.hand] + \
            [card.name for card in player.draw_pile]
        def CountFrequency(my_list):
            # Creating an empty dictionary
            freq = {}
            for item in my_list:
                if (item in freq):
                    freq[item] += 1
                else:
                    freq[item] = 1
            return freq
        self.all_card_counts = CountFrequency(self.all_card_names)


        # TODO(benzyx): do we really want this?
        self.previous_deck = player.previous_deck if is_player else \
            [None for card in player.previous_deck]

        # Never public to player view, but should have some partial information about.
        self.discard_pile_size = len(player.discard_pile)
        self.hand_size = len(player.hand)
        self.draw_pile_size = len(player.draw_pile)

        # self.draw_pile_contents = {}
        # for card in player.draw_pile:
        #   if card.name not in draw_pile_contents:
        #       draw_pile_contents[card.name] = 0
        #   draw_pile_contents[card.name] += 1

    def to_dict(self):
        raise NotImplemented("Too lazy for this right now")


class SupplyPileView(object):
    def __init__(self, supply_pile):
        self.card_name = supply_pile.card.name
        self.qty = supply_pile.qty
        self.buyable = supply_pile.buyable

    def to_dict(self):
        return {
            "card_name": self.card_name,
            "qty": self.qty,
            "buyable": self.buyable,
        }


class StateView(object):
    """
    The StateView object is what we are going to pass to an agent before they make a decision.

    It needs to hide the aspects of State that should not be exposed to the agent.
    """

    def __init__(self, state, player):
        self.supply_piles = {}
        for name, pile in state.supply_piles.items():
            self.supply_piles[name] = SupplyPileView(pile)
        self.player = PlayerView(player, True)
        self.other_players = [PlayerView(opp, False) for opp in state.other_players(player)]
        self.event_log = state.event_log.hide_for_player(player)
        self.trash = [card.name for card in state.trash]
