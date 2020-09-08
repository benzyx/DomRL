from domrl.engine.game import Game
from domrl.engine.agent import StdinAgent
from domrl.agents.big_money_agent import BigMoneyAgent
import domrl.engine.cards.base as base


if __name__ == '__main__':
    """
    Run instances of the game.
    """
    game = Game(
        agents=[StdinAgent(), BigMoneyAgent()],
        kingdoms=[base.BaseKingdom],
    )
    game.run()

