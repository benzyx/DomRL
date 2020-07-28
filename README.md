# DomRL

DomRL is a simulation environment for the card game Dominion, created by Donald X Vaccarino, meant to simplify the development and testing of various AI strategies, specifically Reinforcement Learning algorithms.

The goal is to make an engine that stores the context stack of the game, such that at each decision point, the entire known state of the game is available without needing to reconstruct the state from log information. This type of state management would be optimal for building RL agents.

## Usage

If you want to play from the command line, simply run:

```
python main.py
```

This runs two `StdinAgent` instances against each other, so you can choose all the moves from command line.

If you want to run a game from a Jupyter notebook, between two separate agents, the following should suffice:

```
import engine.game.Game

Game(YourAgent(...), YourAgent(...)).run()
```

## Writing a Bot

Implement an agent, which is a class derived from `engine.agent.Agent` that implements

```
choose(self, state, decision) -> List<int>
```

where the output is the list of indices corresponding to the moves taken in this decision object.

In the future, the plan will be to change interface from accepting State object to a StateView object, which obfuscates information from the agent (such as the order of your remaining cards).


## Upcoming Features

The following features are necessary before this project can reach an acceptable state for proper agent development.

- Finishing up the Dominion base expansion cards. Upcoming cards:
	- Artisan
	- Bureaucrat
	- Sentry
	- Gardens
	- Cellar
	- Bandit
	- Mine
	- Throne Room

- Logging, Event subscription interface for agents.
- Testing for correctness.
- Baseline bots (such as big money)
- StateView object, which obfuscates information.
- Vector encoding interface for decisions.