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

    def arbitrary_timer_callback():
        print("timer done")

    def determine_move( board: Board, prev: tuple[int, int]):  
        timer = threading.Timer(9.8, AI.arbitrary_timer_callback)
        timer.start()
        
        best_move =  ()
        best_score = -AI.INFINITE
        depth = 1

        while timer.is_alive():
            for potential in board.legal_moves(prev):
                if timer.is_alive():
                    clone = board.clone()
                    clone.new_move(potential, True)

                    score = AI.alphabeta(clone, depth, -AI.INFINITE, AI.INFINITE, False, potential, timer)
                    if score > best_score:
                        best_score = score
                        best_move = potential

                    print(f'The best move is: {best_move} with score {best_score}')
                else:
                    break

            depth += 1
            print(f"Going Deeper: Depth = {depth}")

        timer.cancel()
        return best_move
    
    
    @staticmethod
    def alphabeta(board: Board, depth: int, a: int, b: int, maximizing: bool, prev: tuple[int, int], timer:threading.Timer):
        """ Minimaxing algorithm with alpha beta pruning.

        Args:
            board (Board): The Ultimate Tic-Tac-Toe Board object.
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

        if depth == 0 or len(legal_moves) == 0 or not timer.is_alive():
            return board.accumulated_heuristic                                    

        if maximizing:
            value = -AI.INFINITE
    
            for move in legal_moves:                              
                
                clone = board.clone()                                  
                clone.new_move(move, True)                                        

                if (len(clone.legal_moves(move)) > 9 and depth > 2):
                    depth = 2

                value = max(value, AI.alphabeta(clone, depth-1, a, b, False, move, timer)) 
                a = max(a, value)                                             

                if a >= b:                                                    
                    break                                                      
            
            return value                                                       

        else:
            value = AI.INFINITE
            
            for move in legal_moves:                           
                clone = board.clone()                                
                clone.new_move(move, True)       

                if (len(clone.legal_moves(move)) > 9 and depth > 2):
                    depth = 2

                value = min(value, AI.alphabeta(clone, depth-1, a, b, True, move, timer))   
                b = min(b, value)                                             

                if a >= b :                                                   
                    break                                                     

            return value                                                      