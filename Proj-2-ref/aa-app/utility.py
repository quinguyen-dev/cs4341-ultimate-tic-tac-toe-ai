from enum import Enum

class State(Enum):
    DRAW = -1,
    UNCLAIMED = 0,
    PLAYER_1 = 1,
    PLAYER_2 = 2,

    ROW = 0, 
    COL = 1,
    DIAG = 2
    SCORES = 3,
