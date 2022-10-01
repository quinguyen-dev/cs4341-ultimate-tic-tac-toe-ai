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

    depth_one_moves = [] #array of legal moves
    depth_one_best_score = [] #heuristic value for each of the legal moves
    child_locks = [] #locks for each of the spawned threads

    print_lock = threading.Lock() #lock used to prevent race conditions when printing

    def thread_determine_move(self, board: Board, prev: tuple[int, int], max_threads: int = 9):
        '''
             Creates a set of threads to determine the best move by running the determine_move on the depth 1 child of the \'prev\' move
            
            Args
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

        # print(f'Child locks: {self.child_locks}', flush=True)

        # todo what does this do 
        # For every legal move in the local board
        for move_num in range(depth_one_length):
            locked_out = True

            while locked_out: 
                for lock_num in range(max_threads): 
                    if not self.child_locks[lock_num].locked(): 
                        locked_out = False
                        break

            #create a new thread that runs determine_move
            # print(f"move_num: {move_num}")
            thread_list.append(threading.Thread(target=self.determine_move, name=lock_num, args=(board, self.depth_one_moves[move_num], lock_num, move_num)))
            thread_list[-1].start() #start the thread
            
            # self.print_lock.acquire(True) #get permission to print
            # print(thread_list[-1].name+ "started")
            # self.print_lock.release() #let someone else print
        
        
        best_score = -AI.INFINITE

        # self.print_lock.acquire(True)
        # print(thread_list[-1].name + "waiting")
        # self.print_lock.release()

        while threading.active_count() != 1:
            sleep(0.01)

        # for thread in thread_list:
        #     while thread.is_alive(): #while a thread is running
        #         sleep(0.01) #wait

       #  print("threads dead")   
        # print(f'Depth one moves: {self.depth_one_moves}')
        # print(f'Depth one best scores: {self.depth_one_best_score}')

        print(f'The best scores: {self.depth_one_best_score}')
        for score_index in range(depth_one_length): #maximize
            if self.depth_one_best_score[score_index] > best_score:
                best_score = self.depth_one_best_score[score_index]
                best_move = self.depth_one_moves[score_index]

        print(f'The best move was: {best_move}')
        return best_move


    def determine_move(self, board: Board, prev: tuple[int, int], lock_index: int, move_num: int):  
        self.child_locks[lock_index].acquire(True) #lock to limit num of active threads
        
        best_move =  ()
        best_score = AI.INFINITE  # todo made this negative
        
        # self.print_lock.acquire(blocking=True) # gain access to std.out
        # print("determine move "+ str(lock_index), flush=True)
        # self.print_lock.release()

        for potential in board.legal_moves(prev):
            clone = board.clone()
            clone.new_move(potential, True)
            
            # self.print_lock.acquire(blocking=True)
            # print(str(potential), flush=True)
            # self.print_lock.release()

            score = AI.alphabeta(clone, 4, -AI.INFINITE, AI.INFINITE, True, potential) 
            if score < best_score: # todo inverted sign
                best_score = score
                best_move = potential
        
        self.depth_one_best_score[move_num] = best_score
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

        if depth == 0: 
            return board.accumulated_heuristic                                     # Get the heuristic value of the board state

        if maximizing:
            value = -AI.INFINITE
            
            for move in board.legal_moves(prev):                               # For every possible move in the given board
                clone = board.clone()                                     # Create a deep copy of the board
                clone.new_move(move, True)                                          # Make a legal move in the deep copy

                value = max(value, AI.alphabeta(clone, depth-1, a, b, False, move))  # Get the maximum value between the returning alpha value and the current best
                a = max(a, value)                                              # Get the maximum value between the passed in alpha and the current best

                if a >= b:                                                     # If alpha is greater than or equal to beta
                    break                                                      # Prune
            
            return value                                                       # Return the final best value (this comes from the heuristic conditional)

        else:
            value = AI.INFINITE
            
            for move in board.legal_moves(prev):                               # For every possible move in the given board
                clone = board.clone()                                    # Create a deep copy of the board
                clone.new_move(move, True)        # Make a legal move in the deep copy

                value = min(value, AI.alphabeta(clone, depth-1, a, b, True, move))    # Get the minimum value between the returning beta value and the current best
                b = min(b, value)                                              # Get the minimum value between the passed in beta and the current best

                if a >= b:                                                     # If alpha is greater than or equal to beta
                    break                                                      # Prune

            return value                                                       # Return the final best value (this comes from the heuristic conditional)