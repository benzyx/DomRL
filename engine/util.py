from enum import Enum

class CardType(Enum):
    VICTORY = 1
    TREASURE = 2
    ACTION = 3
    REACTION = 4
    ATTACK = 5
    CURSE = 6
    DURATION = 7
    NIGHT = 8

class TurnPhase(Enum):
    ACTION_PHASE = 1
    TREASURE_PHASE = 2
    BUY_PHASE = 3
    END_PHASE = 4
