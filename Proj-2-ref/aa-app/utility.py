from enum import Enum
import threading

class State():
    DRAW = 10
    UNCLAIMED = 0
    PLAYER_1 = -1
    PLAYER_2 = 1

    ROW = 0
    COL = 1
    DIAG = 2
    SCORES = 3
