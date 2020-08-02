"""
An effect is essentially a function, applied to a particular state and player.

Cards will usually execute a series of effects, with the target player being
the player that played the card.

Must implement:
run(state, player) -> None
"""
class Effect(object):
    def run(self, state, player):
        raise Exception("Effect does not implement run!")
