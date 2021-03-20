from enum import Enum
import logging

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
    SHUFFLE = 9
    CONTEXT = 10
    ENDTURN = 11

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
    return "[undefined action]"


class Event(object):
    # By default, do not hide the action at all.
    def obfuscate(self, player):
        return self

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
            return DrawEvent(self.player, None)
        else:
            return self


class DiscardEvent(CardEvent):
    """
    TODO(benzyx): Actually need to obfuscate some discards...
    """
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


class ShuffleEvent(Event):
    def __init__(self, player):
        self.event_type = EventType.SHUFFLE
        self.player = player

    def __str__(self):
        return f"{self.player} shuffles their deck."

    def to_dict(self):
        return {
            "type": EventType.SHUFFLE.name,
            "player": self.player.name,
            "str": str(self),
        }


class EnterContext(Event):
    def __init__(self):
        self.event_type = EventType.CONTEXT
        self.value = 1

    def to_dict(self):
        return {
            "type": self.event_type.name,
            "value": 1,
        }


class ExitContext(Event):
    def __init__(self):
        self.event_type = EventType.CONTEXT
        self.value = -1

    def to_dict(self):
        return {
            "type": self.event_type.name,
            "value": -1,
        }

class EndTurnEvent(Event):
    def __init__(self, player):
        self.event_type = EventType.ENDTURN
        self.player = player

    def __str__(self):
        return f"{self.player.name} ends their turn."

    def to_dict(self):
        return {
            "type": self.event_type.name,
            "str": str(self),
        }

def dict_log_to_string(event_dict_list):
    """
    This function will be used to easily print out a list of Events in dict form.
    """
    log_str = ""
    context_level = 0
    for event in event_dict_list:
        if event['type'] == EventType.CONTEXT.name:
            context_level += event["value"]
        else:
            log_str += "  " * context_level
            log_str += event['str']
            log_str += "\n"
    return log_str


class EventLog(object):
    """
    Event log.
    """
    def __init__(self, verbose):
        self.events = []
        self.context_level = 0
        self.verbose = verbose

    def add_event(self, event):
        self.events.append(event)

        if event.event_type == EventType.CONTEXT:
            self.context_level += event.value
        else:
            if self.verbose:
                for i in range(self.context_level):
                    print("  ", end="")
                print(event)

    def hide_for_player(self, player):
        return [event.obfuscate(player).to_dict() for event in self.events]

    def to_string(self):
        return dict_log_to_string(self.to_dict_log())

    def to_dict_log(self):
        return [event.to_dict() for event in self.events]

    def print(self):
        """
        This function will be used to easily print out a list of Events in dict form.
        """
        print("=== Replaying log from beginning ===")
        print(self.to_string())
        print("===             end              ===")
