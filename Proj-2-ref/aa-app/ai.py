from copy import deepcopy
from os import dup
import sys
from Board import Board

class AI:

    INFINITE = sys.maxsize

    def determine_move(board: Board, prev: tuple[int, int]):  
        best_move =  ()
        best_score = -AI.INFINITE

        for potential in board.legal_moves(prev):
            duplicate = board.clone()
            duplicate.new_move(potential)

            print(f'================== {potential} ============')
            score = AI.alphabeta(duplicate, 2, -AI.INFINITE, AI.INFINITE, True, potential)
            if (score > best_score):
                best_score = score
                best_move = potential
        
        print(f'This is the best move: {best_move}')

        return best_move
    
    
    @staticmethod
    def alphabeta(board: Board, depth: int, a: int, b: int, maximizing: bool, prev: tuple[int, int]):
        """ Minimaxing algorithm with alpha beta pruning.

        Args:
            board (Board): The UTTT Board object.
            depth (int): The current depth levels we have left for iterative deepening.
            a (int): α value.
            b (int): β value.
            maximizing (bool): True if the algorithm is maximizing. False is minimizing.

        Todo: 
            Make sure the program figures out which board it needs to check.
            Make sure to include if the node is terminal when the depth is 0.

        Returns:
            int: The heuristic value of the optimal move.
        """
        if depth == 0: 
            # todo return this value 0,0 
            print(f'Heuristic {prev}: {board.heuristic(prev)}\n')
            return board.heuristic(prev)                                       # Get the heuristic value of the board state

        if maximizing:
            value = -AI.INFINITE
            
            # todo once 
            for move in board.legal_moves(prev):                               # For every possible move in the given board
                clone = board.clone()                                     # Create a deep copy of the board
                clone.new_move(move)                                          # Make a legal move in the deep copy

                value = max(value, AI.alphabeta(clone, depth-1, a, b, False, move))  # Get the maximum value between the returning alpha value and the current best
                a = max(a, value)                                              # Get the maximum value between the passed in alpha and the current best
                
                if a >= b:                                                     # If alpha is greater than or equal to beta
                    break                                                      # Prune

            return value                                                       # Return the final best value (this comes from the heuristic conditional)

        else:
            value = AI.INFINITE
            
            for move in board.legal_moves(prev):                               # For every possible move in the given board
                clone = board.clone()                                    # Create a deep copy of the board
                clone.new_move(move)        # Make a legal move in the deep copy

                value = min(value, AI.alphabeta(clone, depth-1, a, b, True, move))    # Get the minimum value between the returning beta value and the current best
                b = min(b, value)                                              # Get the minimum value between the passed in beta and the current best
                
                if a >= b:                                                     # If alpha is greater than or equal to beta
                    break                                                      # Prune

            return value                                                       # Return the final best value (this comes from the heuristic conditional)