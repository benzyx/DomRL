from engine.game import Game
from engine.agent import StdinAgent

"""
Run instances of the game.
"""
if __name__ == '__main__':
	game = Game([StdinAgent(), StdinAgent()])
	game.run()
