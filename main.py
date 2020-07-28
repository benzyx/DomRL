from engine.game import Game
from engine.agent import StdAgent

"""
Run instances of the game.
"""
if __name__ == '__main__':
	game = Game([StdAgent(), StdAgent()])
	game.run()
