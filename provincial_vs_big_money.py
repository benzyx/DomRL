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

buy_menu= [('Gold', 6, 99), ('Witch', 5, 1), ('Council Room', 5, 5), ('Militia', 4, 1), \
            ('Silver', 3, 1), ('Village', 3, 5), ('Silver', 3, 99)]

if __name__ == '__main__':
    """
    Run instances of the game.
    """
    num_games = 10
    provincial_win_count = 0
    big_money_win_count = 0
    for i in range(0, num_games):
        card_set = get_card_set(["Witch", "Council Room", "Militia", "Village", "Gardens", "Chapel", \
                                "Artisan", "Sentry", "Bureaucrat", "Cellar"])

        game = Game(
            agents=[ProvincialAgent(buy_menu = buy_menu), BigMoneyAgent()],
            kingdoms=[card_set],
        )
        state = game.run()
        if state.current_player.total_vp() > state.other_players(state.current_player)[0].total_vp():
            if state.current_player.name == "Player 1":
                provincial_win_count += 1
            else:
                big_money_win_count += 1
        elif state.other_players(state.current_player)[0].total_vp() > state.current_player.total_vp():
            if state.current_player.name == "Player 1":
                big_money_win_count += 1
            else:
                provincial_win_count += 1


    print("Provincial won ", provincial_win_count, " many times.")
    print("Big Money won ", big_money_win_count, " many times.")

    # print(res)
