import sys
from board import Board

class AI:

    INFINITE = sys.maxsize

    def __init__(self):
        print('Initialized')

    def determine_move():

        return 0
    
    @staticmethod
    def alphabeta(board: Board, depth: int, a: int, b: int, maximizing: bool):
        """ Minimaxing algorithm with alpha beta pruning

        Args:
            board (Board): The UTTT Board object
            depth (int): The current depth levels we have left for iterative deepening
            a (int): α value
            b (int): β value
            maximizing (bool): True if the algorithm is maximizing. False is minimizing.

        Todo: 
            Make sure the program figures out which board it needs to check
            Make sure to include if the node is terminal when the depth is 0

        Returns:
            int: The heuristic value of the optimal move
        """
        if depth == 0: 
            return board.get_heuristic()                                       # Get the heuristic value of the board state

        if maximizing:
            value = -AI.INFINITE
            
            for move in board.get_legal_moves():                               # For every possible move in the given board
                clone = board.deep_copy()                                      # Create a deep copy of the board
                clone.make_move(move)                                          # Make a legal move in the deep copy

                value = max(value, AI.alphabeta(clone, depth-1, a, b, False))  # Get the maximum value between the returning alpha value and the current best
                a = max(a, value)                                              # Get the maximum value between the passed in alpha and the current best
                
                if a >= b:                                                     # If alpha is greater than or equal to beta
                    break                                                      # Prune

            return value                                                       # Return the final best value (this comes from the heuristic conditional)

        else:
            value = AI.INFINITE
            
            for move in board.get_legal_moves():                               # For every possible move in the given board
                clone = board.deep_copy()                                      # Create a deep copy of the board
                clone.make_move(move)                                          # Make a legal move in the deep copy

                value = min(value, AI.alphabeta(clone, depth-1, a, b, True))    # Get the minimum value between the returning beta value and the current best
                b = min(b, value)                                              # Get the minimum value between the passed in beta and the current best
                
                if a >= b:                                                     # If alpha is greater than or equal to beta
                    break                                                      # Prune

            return value                                                       # Return the final best value (this comes from the heuristic conditional)