import engine.logger as log


class Trigger:
    def condition(self, event: log.Event):
        raise NotImplementedError('`Trigger` must be subclassed to have condition')

    def apply(self, state):
        raise NotImplementedError('`Trigger` must be subclassed to be applied')
