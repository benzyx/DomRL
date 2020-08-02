
class Trigger:
    def __init__(self):
        pass

    def apply(self, player):
        raise NotImplementedError('`Trigger` must be subclassed to be applied')


class PlusCoinTrigger(Trigger):
    def __init__(self, one_time: bool = True):
        self.one_time = one_time
        self.triggered = False

    def apply(self, player):
        player.coins += 1
        self.triggered = True

    @property
    def remove(self) -> bool:
        return self.one_time or self.triggered
