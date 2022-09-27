class Node:

    def __init__(self, board):
        self.board = board
        self.heuristic = 0
        self.parent = None
        self.children = []