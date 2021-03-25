from domrl.engine.game import Game
from domrl.engine.agent import StdinAgent
from domrl.agents.big_money_agent import BigMoneyAgent
from domrl.agents.provincial_agent import ProvincialAgent
import domrl.engine.cards.base as base
from copy import deepcopy

def get_card_set(cards):
    dict = {}
    for key, val in base.BaseKingdom.items():
        if key in cards:
            dict[key] = deepcopy(val)
    return dict

buy_menu_one = [('Gold', 6, 99), ('Witch', 5, 1), ('Council Room', 5, 5), ('Militia', 4, 1), \
            ('Silver', 3, 1), ('Village', 3, 5), ('Silver', 3, 99)]

buy_menu_two = [('Gold', 6, 99), ('Mine', 5, 1), ('Silver', 3, 2), ('Library', 5, 1), \
            ('Village', 3, 1), ('Mine', 5, 1), ('Village', 3, 1), ('Library', 5, 1), \
            ('Village', 3, 2), ('Silver', 3, 99)]

provincial_buy_menu_one = [('Witch', 5, 1), ('Gold', 6, 99), ('Militia', 4, 1), ('Witch', 5, 1), \
            ('Market', 5, 3), ('Silver', 3, 99)]

buy_menu_big_money = [('Gold', 6, 99), ('Silver', 3, 99)]

card_set_one = ["Library", "Mine", "Village", "Militia", "Council Room", "Witch", "Cellar", \
                        "Gardens", "Artisan", "Sentry"]

card_set_two = ["Moat", "Village", "Bureaucrat", "Militia", "Smithy", "Council Room", "Library", \
                        "Market", "Mine", "Witch"]


buy_menu_testing = [[('Village', 3, 99), ('Silver', 3, 99)], \
                    [('Laboratory', 5, 99), ('Silver', 3, 99)], \
                    [('Market', 5, 99), ('Silver', 3, 99)], \
                    [('Festival', 5, 99), ('Silver', 3, 99)], \
                    [('Smithy', 4, 99), ('Silver', 3, 99)], \
                    [('Militia', 4, 99), ('Silver', 3, 99)], \
                    [('Gardens', 4, 99), ('Silver', 3, 99)], \
                    [('Chapel', 2, 1), ('Silver', 3, 99)], \
                    [('Witch', 5, 99), ('Silver', 3, 99)], \
                    [('Workshop', 3, 3), ('Gold', 6, 99), ('Silver', 3, 99), ('Copper', 1, 99)], \
                    [('Bandit', 5, 3), ('Silver', 3, 99)], \
                    [('Remodel', 4, 3), ('Silver', 3, 99), ('Copper', 0, 99)], \
                    [('Throne Room', 4, 5), ('Council Room', 5, 5), ('Silver', 3, 99)], \
                    [('Moneylender', 4, 3), ('Silver', 3, 99)], \
                    [('Poacher', 4, 3), ('Silver', 3, 99), ('Copper', 0, 99), ('Gold', 6, 99)], \
                    [('Merchant', 3, 3), ('Silver', 3, 99)], \
                    [('Cellar', 2, 3), ('Silver', 3, 99)], \
                    [('Mine', 5, 3), ('Gold', 6, 99), ('Silver', 3, 99)], \
                    [('Vassal', 3, 3), ('Silver', 3, 99)], \
                    [('Council Room', 5, 3), ('Silver', 3, 99)], \
                    [('Artisan', 6, 3), ('Silver', 3, 99)], \
                    [('Bureaucrat', 4, 3), ('Silver', 3, 99)], \
                    [('Sentry', 5, 3), ('Silver', 3, 99)], \
                    [('Harbinger', 3, 3), ('Silver', 3, 99)], \
                    [('Library', 5, 3), ('Silver', 3, 99)], \
                    [('Moat', 2, 2), ('Militia', 4, 1), ('Silver', 3, 99)]]

card_set_testing = [["Village", "Laboratory", "Market", "Festival", "Smithy", \
                        "Militia", "Gardens", "Chapel", "Witch", "Workshop"], \
                    ["Bandit", "Remodel", "Throne Room", "Moneylender", "Poacher", \
                        "Merchant", "Cellar", "Mine", "Vassal", "Council Room"], \
                    ["Artisan", "Bureaucrat", "Sentry", "Harbinger", "Library", \
                        "Moat", "Village", "Laboratory", "Market", "Militia"]]

card_set_test = get_card_set(card_set_testing[2])
buy_menu_test = buy_menu_testing[22]

if __name__ == '__main__':
    """
    Run instances of the game.
    """
    num_games = 1
    provincial_one_win_count = 0
    provincial_two_win_count = 0
    num_ties = 0
    for i in range(0, num_games):
        game = Game(
            agents=[ProvincialAgent(buy_menu = buy_menu_test), ProvincialAgent(buy_menu = buy_menu_test)],
            kingdoms=[card_set_test],
        )
        state = game.run()
        if state.current_player.total_vp() > state.other_players(state.current_player)[0].total_vp():
            if state.current_player.name == "Player 1":
                provincial_one_win_count += 1
            elif state.current_player.name == "Player 2":
                provincial_two_win_count += 1
        elif state.other_players(state.current_player)[0].total_vp() > state.current_player.total_vp():
            if state.current_player.name == "Player 1":
                provincial_two_win_count += 1
            elif state.current_player.name == "Player 2":
                provincial_one_win_count += 1
        else:
            num_ties += 1

    print("Provincial Buy Menu One won", provincial_one_win_count, "times.")
    print("Provincial Buy Menu Two won", provincial_two_win_count, "times.")
    print("They tied", num_ties, "many times.")
