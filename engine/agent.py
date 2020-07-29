
class Agent(object):
	def choose(self, decision, state):
		return decision.moves[0]

class StdinAgent(Agent):
	def choose(self, decision, state):
		# Autoplay
		if len(decision.moves) == 1:
			return [0]

		print(decision.prompt)
		for idx, move in enumerate(decision.moves):
			print(f"{idx}: {move}")
		ans = list(map(lambda x: int(x.strip()), input().split(',')))

		return ans


class BigMoneyAgent(Agent):
	def choose(self, decision, state):
		pass

