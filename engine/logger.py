class Event(object):
    pass


class BuyEvent(Event):
    def __init__(self, player, card):
        self.player = player
        self.card = card

    def __str__(self):
        return f"{self.player.name} buys a {self.card}."


class GainEvent(Event):
    def __init__(self, player, card):
        self.player = player
        self.card = card

    def __str__(self):
        return f"{self.player.name} gains a {self.card}."


class PlayEvent(Event):
    def __init__(self, player, card):
        self.player = player
        self.card = card

    def __str__(self):
        return f"{self.player.name} plays a {self.card}."


class DrawEvent(Event):
    """
    TODO(benzyx): Figure out how to handle visibility.
    """

    def __init__(self, player, card):
        self.player = player
        self.card = card

    def __str__(self):
        return f"{self.player.name} draws a {self.card}."


class DiscardEvent(Event):
    """
    TODO(benzyx): Figure out how to handle visibility.
    """
    def __init__(self, player, card):
        self.player = player
        self.card = card

    def __str__(self):
        return f"{self.player.name} discards a {self.card}."


class TrashEvent(Event):
    """
    TODO(benzyx): Figure out how to handle visibility.
    """
    def __init__(self, player, card):
        self.player = player
        self.card = card

    def __str__(self):
        return f"{self.player.name} trashes a {self.card}."


class EventLog(object):
    """
    Event log.
    """
    def __init__(self, agents):
        self.agents = agents
        self.events = []

    def add_event(self, event):
        self.events.append(event)
        print(event)

    def print(self, player):
        print("=== Replaying log from beginning ===")
        for event in self.events:
            print(event)
        print("===             end              ===")
