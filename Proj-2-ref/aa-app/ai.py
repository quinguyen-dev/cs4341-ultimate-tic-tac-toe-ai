from ast import While
from concurrent.futures import thread
from copy import deepcopy
from multiprocessing import Lock
from os import dup
import sys
import threading
from time import sleep

from Board import Board

class AI:

    INFINITE = sys.maxsize

    def determine_move( board: Board, prev: tuple[int, int]):  
        
        best_move =  ()
        best_score = -AI.INFINITE  # todo made this negative
        

        for potential in board.legal_moves(prev):
            clone = board.clone()
            clone.new_move(potential, True)

            score = AI.alphabeta(clone, 4, -AI.INFINITE, AI.INFINITE, False, potential) 
            if score > best_score: # todo inverted sign
                best_score = score
                best_move = potential
        
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

        legal_moves = board.legal_moves(prev)

        if depth == 0 or len(legal_moves) == 0:
            print(board.accumulated_heuristic)
            return board.accumulated_heuristic                                     # Get the heuristic value of the board state



        if maximizing:
            value = -AI.INFINITE
            

            for move in legal_moves:                               # For every possible move in the given board
                
                clone = board.clone()                                     # Create a deep copy of the board
                clone.new_move(move, True)                                          # Make a legal move in the deep copy

                if(len(clone.legal_moves(move)) > 9 and depth > 2):
                    print("Opp Wild Card")
                    depth = 2

                value = max(value, AI.alphabeta(clone, depth-1, a, b, False, move))  # Get the maximum value between the returning alpha value and the current best
                a = max(a, value)                                              # Get the maximum value between the passed in alpha and the current best

                if a >= b:                                                     # If alpha is greater than or equal to beta
                    break                                                      # Prune
            
            return value                                                       # Return the final best value (this comes from the heuristic conditional)

        else:
            value = AI.INFINITE
            
            
            for move in legal_moves:                               # For every possible move in the given board
                clone = board.clone()                                    # Create a deep copy of the board
                clone.new_move(move, True)        # Make a legal move in the deep copy
                
                if(len(clone.legal_moves(move)) > 9 and depth > 2):
                    print("Opp Wild Card")
                    depth = 2

                value = min(value, AI.alphabeta(clone, depth-1, a, b, True, move))    # Get the minimum value between the returning beta value and the current best
                b = min(b, value)                                              # Get the minimum value between the passed in beta and the current best

                if a >= b :                                                     # If alpha is greater than or equal to beta
                    break                                                      # Prune

            return value                                                       # Return the final best value (this comes from the heuristic conditional)