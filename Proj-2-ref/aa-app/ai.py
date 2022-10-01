from ast import While
from concurrent.futures import thread
from copy import deepcopy
from multiprocessing import Lock
from os import dup
from utility import State
import sys
import threading
from time import sleep

from Board import Board

class AI:

    INFINITE = sys.maxsize

    depth_one_moves = [] #array of legal moves
    depth_one_best_score = [] #heuristic value for each of the legal moves
    child_locks = [] #locks for each of the spawned threads

    print_lock = threading.Lock() #lock used to prevent race conditions when printing

    def thread_determine_move(self, board: Board, prev: tuple[int, int], max_threads: int = 69):
        ''' Creates a set of threads to determine the best move by running the determine_move on the depth 1 child of the \'prev\' move
            
            Args:
                board: current game board
                prev: last moved played (this move should have been played by opponent)
                max_threads: maximum number of threads the system is allowed to run

        '''
        # Clear all arrays and create an emily list of mutex locks
        self.depth_one_moves.clear()
        self.depth_one_best_score.clear()
        self.child_locks.clear() 

        # Get an array of depth first moves (open moves on the given board)
        self.depth_one_moves = board.legal_moves(prev)

        depth_one_length = len(self.depth_one_moves)

        # Create a new array that holds the best score of each depth_one moves
        self.depth_one_best_score = [(-AI.INFINITE) for i in range(depth_one_length)] 

        # Create an array to hold any Thread objects that are created
        thread_list = []

        # Create a lock for each of the allowed threads
        for i in range(max_threads):
            self.child_locks.append(threading.Lock()) 

        for move_num in range(depth_one_length):
            locked_out = True

            while locked_out: 
                for lock_num in range(max_threads): 
                    if not self.child_locks[lock_num].locked(): 
                        locked_out = False
                        break

            thread_list.append(threading.Thread(target=self.determine_move, name=lock_num, args=(board, self.depth_one_moves[move_num], lock_num, move_num)))
            thread_list[-1].start()
        
        best_score = -AI.INFINITE

        while threading.active_count() != 1:
            sleep(0.01)

        for score_index in range(depth_one_length): #maximize
            if self.depth_one_best_score[score_index] > best_score:
                best_score = self.depth_one_best_score[score_index]
                best_move = self.depth_one_moves[score_index]

        return best_move


    def determine_move(self, board: Board, prev: tuple[int, int], lock_index: int, move_num: int):  
        self.child_locks[lock_index].acquire(True)
        
        best_move =  ()
        best_score = AI.INFINITE  
        
        for potential in board.legal_moves(prev):
            clone = board.clone()
            clone.new_move(potential, True)

            score = AI.alphabeta(clone, 8, -AI.INFINITE, AI.INFINITE, True, potential) 
            if score < best_score: 
                best_score = score
                best_move = potential
        
        self.depth_one_best_score[move_num] = best_score
        self.child_locks[lock_index].release()
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
            return board.accumulated_heuristic                                     

        if maximizing:
            value = -AI.INFINITE
            
            for move in legal_moves:                             
                clone = board.clone()                                    
                clone.new_move(move, True)      

                # if move gives opponent a closed board
                if  len(clone.legal_moves(move)) > 10:
                    print(f'{depth}: Opponent move is a wildcard')
                    print(clone.global_board)
                    depth = 1

                value = max(value, AI.alphabeta(clone, depth-1, a, b, False, move))  
                a = max(a, value)                                           

                if a >= b:                                                   
                    break                                                  
            
            return value                                                     

        else:
            value = AI.INFINITE
            
            for move in legal_moves:                              
                clone = board.clone()                                  
                clone.new_move(move, True)     

                if len(clone.legal_moves(move)) > 10:
                    print(f'{depth}: Opponent move is a wildcard')
                    print(clone.global_board)
                    depth = 1

                value = min(value, AI.alphabeta(clone, depth-1, a, b, True, move))   
                b = min(b, value)                                 

                if a >= b :                                                   
                    break                                                     

            return value                                                     