from ast import While
from audioop import mul
from concurrent.futures import thread
from copy import deepcopy
from multiprocessing import Lock
import multiprocessing
from os import dup
import sys

from time import sleep

from Board import Board

class AI:

    INFINITE = sys.maxsize



    def create_processes_determine_move( board: Board, prev: tuple[int, int], max_processes: int = 3):
        '''
             Creates a set of processes to determine the best move by running the determine_move on the depth 1 child of the \'prev\' move
            
            Args
                board: current game board
                prev: last moved played (this move should have been played by opponent)
                max_processes: maximum number of processes the system is allowed to run

        '''
        # Clear all arrays and create an emily list of mutex locks
        depth_one_moves = [] #array of legal moves
        child_locks = [] #locks for each of the spawned processes
        process_results_queue = multiprocessing.Queue() #multi process queue that holds results of each process. This is evaulated at end of all threads


        # Get an array of depth first moves (open moves on the given board)
        depth_one_moves = board.legal_moves(prev)

        #number of possible next moves
        depth_one_length = len(depth_one_moves) 

        # Create an array to hold any Thread objects that are created
        process_list = []

        # Create a lock for each of the allowed processes
        for i in range(max_processes):
            child_locks.append(multiprocessing.Lock()) 
        print(child_locks)

        
        i = 0
        print(f'Legal moves: {depth_one_length}')

        # For every legal move in the local board
        for move_num in range(depth_one_length):
            locked_out = True

            #while there are not any open locks for the move to use
            while locked_out: 
                for lock_num in range(max_processes):   
                    if child_locks[lock_num].acquire(block = False): #check each lock. do not wait for them to be open before iterating 
                        i += 1 #this is for debugging more than anything
                        locked_out = False #since a lock is available, set to exit loop
                        print(child_locks[lock_num]) #debug
                        break#leave loops

            #create a new process that runs determine_move
            process_list.append(multiprocessing.Process(target=AI.determine_move, name=str(i), args=(board, depth_one_moves[move_num], child_locks[lock_num], process_results_queue)))
            process_list[-1].start() #start the process
            child_locks[lock_num].release() #open the lock for the process to begin
        
        
        best_score = -AI.INFINITE

        while len(multiprocessing.active_children()) > 0: #while all of the processes are running, wait
            sleep(0.01)


        #maximize
        collect_best_scores = [] #debugging
        while not process_results_queue.empty(): #while there are results waiting
            result = process_results_queue.get() #get a result
            collect_best_scores.append(result) #debugging
            if result[0] > best_score: #maximize the results
                best_score = result[0]
                best_move = result[1]

        print(f'The moves and scores:\n {collect_best_scores}\n')
        return best_move


    def determine_move(board: Board, prev: tuple[int, int], lock: multiprocessing.Lock, queue: multiprocessing.Queue):  
        print('lock waiting', flush = True) #debugging
        lock.acquire(block=True) #lock to limit num of active threads
        print('lock acquired', flush = True) #debugging
        print(lock, flush=True)
        try: #the try block is here to ensure that even if an error occurs, the process will still die and release the lock properly
            
            best_move =  ()
            best_score = AI.INFINITE
            

            for potential in board.legal_moves(prev):
                clone = board.clone()
                clone.new_move(potential, True)
                

                score = AI.alphabeta(clone, 4, -AI.INFINITE, AI.INFINITE, True, potential) 
                if score < best_score:
                    best_score = score
                    best_move = potential
            print('waiting for queue', flush=True)
            queue.put([best_score, prev]) #put the score and move into a tuple, send the tuple into the process-shared queue so the main process can read it later
            queue.close() #let the queue know that its done in this process and it can be garbage collected for this process
        finally:
            lock.release() #release lock after process is done
            print('lock released', flush = True) #debugging
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
            return board.accumulated_heuristic                                     # Get the heuristic value of the board state

        # if len(legal_moves) > 9 and depth > 2:
        #     depth = 2

        if maximizing:
            value = -AI.INFINITE
            
            for move in legal_moves:                               # For every possible move in the given board
                clone = board.clone()                                     # Create a deep copy of the board
                clone.new_move(move, True)                                          # Make a legal move in the deep copy

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

                value = min(value, AI.alphabeta(clone, depth-1, a, b, True, move))    # Get the minimum value between the returning beta value and the current best
                b = min(b, value)                                              # Get the minimum value between the passed in beta and the current best

                if a >= b :                                                     # If alpha is greater than or equal to beta
                    break                                                      # Prune

            return value                                                       # Return the final best value (this comes from the heuristic conditional)