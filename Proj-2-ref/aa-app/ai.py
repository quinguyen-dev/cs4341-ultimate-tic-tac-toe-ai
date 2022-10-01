from ast import While
from concurrent.futures import thread
from copy import deepcopy
from multiprocessing import Lock
from os import dup
import sys
import threading
from time import sleep

from numpy import Infinity
from Board import Board

class AI:

    INFINITE = sys.maxsize

    depth_one_moves = [] #array of legal moves
    child_best_score = [] #heuristic value for each of the legal moves
    child_locks = [] #locks for each of the spawned threads

    print_lock = threading.Lock() #lock used to prevent race conditions when printing

    def thread_determine_move(self, board: Board, prev: tuple[int, int], max_threads: int = 8):
        '''
             Creates a set of threads to determine the best move by running the determine_move on the depth 1 child of the \'prev\' move
            
            Args
                board: current game board
                prev: last moved played (this move should have been played by opponent)
                max_threads: maximum number of threads the system is allowed to run

        '''
        self.depth_one_moves = board.legal_moves(prev) #save the list of legal moves
        self.child_best_score = [-self.INFINITE in range(len(self.depth_one_moves))] #create a new array to hold 
        self.child_locks.clear() # empty list of mutex locks 
        thread_list = [] #holds Thread objects created 

        for i in range(max_threads):
            self.child_locks.append(threading.Lock()) #create a mutex for each allowed thread
        print(self.child_locks)
        for move_num in range(len(self.depth_one_moves)): # for each legal move
            locked_out = True

            while(locked_out): #while there are already max num of living threads
                for lock_num in range(max_threads): 
                    if(not self.child_locks[lock_num].locked()): #check to see if any thread locks have been released (these locks are released right before a thread returns)
                        locked_out = False
                        break

            #create a new thread that runs determine_move
            thread_list.append(threading.Thread(target=self.determine_move,name=lock_num, args=(board, self.depth_one_moves[move_num], lock_num, move_num)))
            thread_list[-1].start() #start the thread
            
            self.print_lock.acquire(True) #get permission to print
            print(thread_list[-1].name+ "started")
            self.print_lock.release() #let someone else print
        
        
        best_score = -Infinity
        self.print_lock.acquire(True)
        print(thread_list[-1].name+ "waiting")
        self.print_lock.release()
        for thread in thread_list:
            while thread.is_alive(): #while a thread is running
                sleep(0.01) #wait
        print("threads dead")   
        for score_index in range(len(self.depth_one_moves)): #maximize
            if (self.child_best_score[score_index] > best_score):
                best_score = self.child_best_score[score_index]
                best_move = self.depth_one_moves[score_index]
        print(best_move)
        return best_move


                


    def determine_move(self, board: Board, prev: tuple[int, int], lock_index: int, move_num:int):  
        self.child_locks[lock_index].acquire(True) #lock to limit num of active threads
        
        best_move =  ()
        best_score = AI.INFINITE 
        
        self.print_lock.acquire(blocking=True) # gain access to std.out
        print("determine move "+ str(lock_index), flush=True)
        self.print_lock.release()

        for potential in board.legal_moves(prev):
            duplicate = board.clone()
            duplicate.new_move(potential, True)
            self.print_lock.acquire(blocking=True)
            print(str(potential), flush=True)
            self.print_lock.release()
            score = AI.alphabeta(duplicate, 4, -AI.INFINITE, AI.INFINITE, True, potential) #todo 
            if (score < best_score):
                best_score = score
                best_move = potential
        
        self.depth_one_moves.insert(move_num, prev)
        self.child_best_score.insert(move_num, score)

        self.child_locks[lock_index].release() #release lock after threading is done
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

        global best_move_

        if depth == 0: 
            return board.accumulated_heuristic                                     # Get the heuristic value of the board state

        if maximizing:
            value = -AI.INFINITE
            
            # todo once 
            for move in board.legal_moves(prev):                               # For every possible move in the given board
                # print(f'{move}: {board.legal_moves(prev)}')
                clone = board.clone()                                     # Create a deep copy of the board
                clone.new_move(move, True)                                          # Make a legal move in the deep copy

                # value = max(value, AI.alphabeta(clone, depth-1, a, b, False, move))  # Get the maximum value between the returning alpha value and the current best

                s = AI.alphabeta(clone, depth-1, a, b, False, move)
                if s > value:
                    value = s
                    a = max(a, value) 
                    best_move_ = move

                # print(best_move_)
                #a = max(a, value)                                              # Get the maximum value between the passed in alpha and the current best

                if a >= b:                                                     # If alpha is greater than or equal to beta
                    break                                                      # Prune
            
            return value                                                       # Return the final best value (this comes from the heuristic conditional)

        else:
            value = AI.INFINITE
            
            for move in board.legal_moves(prev):                               # For every possible move in the given board
               #  print(f'{move}: {board.legal_moves(prev)}')
                clone = board.clone()                                    # Create a deep copy of the board
                clone.new_move(move, True)        # Make a legal move in the deep copy

                #value = min(value, AI.alphabeta(clone, depth-1, a, b, True, move))    # Get the minimum value between the returning beta value and the current best
                #b = min(b, value)                                              # Get the minimum value between the passed in beta and the current best
                
                s = AI.alphabeta(clone, depth-1, a, b, True, move)
                if s < value:
                    value = s
                    b = min(b, value) 
                    best_move_ = move

                # print(move)

                if a >= b:                                                     # If alpha is greater than or equal to beta
                    break                                                      # Prune

            return value                                                       # Return the final best value (this comes from the heuristic conditional)