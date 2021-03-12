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

buy_menu_big_money = [('Gold', 6, 99), ('Silver', 3, 99)]

if __name__ == '__main__':
    """
    Run instances of the game.
    """
    num_games = 50
    provincial_one_win_count = 0
    provincial_two_win_count = 0
    num_ties = 0
    for i in range(0, num_games):
        card_set = get_card_set(["Library", "Mine", "Village", "Militia", "Council Room", "Witch", "Cellar", \
                                "Gardens", "Artisan", "Sentry"])

        game = Game(
            agents=[ProvincialAgent(buy_menu = buy_menu_two), ProvincialAgent(buy_menu = buy_menu_big_money)],
            kingdoms=[card_set],
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

    # print(res)
