from enum import Enum


class EventType(Enum):
    CUSTOM = 0
    BUY = 1
    GAIN = 2
    PLAY = 3
    DRAW = 4
    DISCARD = 5
    TRASH = 6
    TOPDECK = 7
    REVEAL = 8
    CONTEXT = 9


def get_action_word(event_type: EventType) -> str:
    if event_type == EventType.BUY:
        return "buys"
    if event_type == EventType.GAIN:
        return "gains"
    if event_type == EventType.PLAY:
        return "plays"
    if event_type == EventType.DRAW:
        return "draws"
    if event_type == EventType.DISCARD:
        return "discards"
    if event_type == EventType.TRASH:
        return "trashes"
    if event_type == EventType.TOPDECK:
        return "topdecks"
    if event_type == EventType.REVEAL:
        return "reveals"
    return ""


class Event(object):
    def obfuscate(self, player):
        raise NotImplementedError("Event does not implement hide_if_needed")

    def to_dict(self):
        raise NotImplementedError("Event does not implement to_dict")


class CardEvent(Event):
    def __init__(self, event_type, player, card):
        self.event_type = event_type
        self.player = player
        self.card = card

    def __str__(self):
        action_word = get_action_word(self.event_type)
        if self.card:
            return f"{self.player.name} {action_word} a {self.card}."
        else:
            return f"{self.player.name} {action_word} a card."

    # By default, do not hide the action at all.
    def obfuscate(self, player):
        return self

    def to_dict(self):
        return {
            "type": self.event_type.name,
            "player": self.player.name,
            "card": self.card.name if self.card else None,
            "str": str(self),
        }


class BuyEvent(CardEvent):
    def __init__(self, player, card):
        super().__init__(EventType.BUY, player, card)


class GainEvent(CardEvent):
    def __init__(self, player, card):
        super().__init__(EventType.GAIN, player, card)


class PlayEvent(CardEvent):
    def __init__(self, player, card):
        super().__init__(EventType.PLAY, player, card)


class DrawEvent(CardEvent):
    def __init__(self, player, card):
        super().__init__(EventType.DRAW, player, card)

    # Other players should not see the card being drawn.
    def obfuscate(self, player):
        if player != self.player:
            return DrawEvent(self, player, None)
        else:
            return self


class DiscardEvent(CardEvent):
    def __init__(self, player, card):
        super().__init__(EventType.DISCARD, player, card)


class TrashEvent(CardEvent):
    def __init__(self, player, card):
        super().__init__(EventType.TRASH, player, card)


class TopdeckEvent(CardEvent):
    def __init__(self, player, card):
        super().__init__(EventType.TOPDECK, player, card)


class RevealEvent(CardEvent):
    def __init__(self, player, card):
        super().__init__(EventType.REVEAL, player, card)


class EnterContext(Event):
    def __init__(self):
        self.event_type = EventType.CONTEXT
        self.value = 1

    def obfuscate(self, player):
        return self

    def to_dict(self):
        return {
            "type": EventType.CONTEXT,
            "value": 1,
        }


class ExitContext(Event):
    def __init__(self):
        self.event_type = EventType.CONTEXT
        self.value = -1

    def obfuscate(self, player):
        return self

    def to_dict(self):
        return {
            "type": EventType.CONTEXT,
            "value": -1,
        }


def print_dict_log(event_dict_list):
    """
    This function will be used to easily print out a list of Events in dict form.
    """
    print("=== Replaying log from beginning ===")
    context_level = 0
    for event in event_dict_list:
        if event["type"] == EventType.CONTEXT:
            context_level += event["value"]
        else:
            for i in range(context_level):
                print("  ", end="")
            print(event["str"])
    print("===             end              ===")


class EventLog(object):
    """
    Event log.
    """

    def __init__(self, agents):
        self.agents = agents
        self.events = []
        self.context_level = 0

    def add_event(self, event):
        self.events.append(event)

        # For now, actually print the contents of the log.
        if event.event_type == EventType.CONTEXT:
            self.context_level += event.value
        else:
            for i in range(self.context_level):
                print("  ", end="")
            print(event)

    def hide_for_player(self, player):
        return [event.obfuscate(player).to_dict() for event in self.events]
