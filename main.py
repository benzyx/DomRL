from engine.game import Game
from engine.agent import StdinAgent
from agents.big_money_agent import BigMoneyAgent
import engine.cards.base as base


if __name__ == '__main__':
    """
    Run instances of the game.
    """
    game = Game(
        agents=[StdinAgent(), BigMoneyAgent()],
        kingdoms=[base.BaseKingdom],
    )
    game.run()
