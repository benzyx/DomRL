# DomRL

DomRL is a simulation environment for the card game Dominion, created by Donald X Vaccarino, meant to simplify the development and testing of various AI strategies, specifically Reinforcement Learning algorithms.

The goal is to make an engine that stores a serializable state of the game. Improved state management would be helpful for building more complex AI agents.

The engine currently supports all cards in Base Dominion.

## Usage

If you want to play from the command line, simply run:

```
python main.py
```

Currently, this runs two `StdinAgent` instances against each other, so you can choose all the moves from command line.

If you want to run a game from a Jupyter notebook, between two separate agents, the following should suffice:

```
import engine.game.Game

Game(YourAgent(...), YourAgent(...)).run()
```

## Writing a Bot

Implement an agent, which is a class derived from `engine.agent.Agent` that implements

```
policy(self, state_view, decision) -> List<int>
```

where the output is the list of indices corresponding to the moves taken in this decision object.

## Upcoming Features

The following features are necessary before this project can reach an acceptable state for proper RL agent development.

- Testing for correctness.
- Baseline bots (such as big money)
- Undo feature (mostly for human convenience)
- Vector encoding interface for decisions.
- Improved logging (currently do not log draws), and unambiguous events (topdecking from hand vs topdecking from supply pile).