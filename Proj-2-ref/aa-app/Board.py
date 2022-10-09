import copy
from math import floor
from xmlrpc.client import Boolean
from utility import State

class Board:

    board_array = [State.UNCLAIMED] * 81

    # Number of moves played
    move_count = 0 

    #the player who made the last move
    current_player = State.UNCLAIMED

    # Player the agent represents (either player 1 or player 2)
    represented_player = State.UNCLAIMED
    represented_opponent = State.UNCLAIMED

    # Possible values: State.UNCLAIMED (0), State.PLAYER_1 (1), State.PLAYER_2 (2), 
    global_board = [State.UNCLAIMED for i in range(9)] 

    # [ [Row Win States], [Column Win States], [ Diagonal WS, Anti-Diagonal WS], Total Moves ]
    global_board_stats = [[0,0,0], [0,0,0], [0,0], 0]
    local_board_stats  = [[[0,0,0], [0,0,0], [0,0], 0] for i in range(9)]

    # The heuristic value of the global board
    accumulated_heuristic = 0

    last_move = None

    def __init__(self):
        pass

    def __init__(self, represented_player: State = State.UNCLAIMED):
        '''Constructs a board object.

            Args:
                player: which player is the agent representing.
        '''
        self.board_array = [State.UNCLAIMED] * 81

        # Number of moves played
        self.move_count = 0 

        #the player who made the last move
        self.current_player = State.UNCLAIMED

        # Player the agent represents (either player 1 or player 2)
        self.represented_player = State.UNCLAIMED
        self.represented_opponent = State.UNCLAIMED

        # Possible values: State.UNCLAIMED (0), State.PLAYER_1 (1), State.PLAYER_2 (2), 
        self.global_board = [State.UNCLAIMED for i in range(9)] 

        # [ [Row Win States], [Column Win States], [ Diagonal WS, Anti-Diagonal WS], Total Moves ]
        self.global_board_stats = [[0,0,0], [0,0,0], [0,0], 0]
        self.local_board_stats  = [[[0,0,0], [0,0,0], [0,0], 0] for i in range(9)]

        # The heuristic value of the global board
        self.accumulated_heuristic = 0

        self.represented_player = represented_player if represented_player == State.UNCLAIMED else State.PLAYER_1
        self.represented_opponent = (State.PLAYER_1 if (represented_player != State.PLAYER_1) else State.PLAYER_2)

        self.last_move = None

    def config_player(self, represented_player: State):
        """ Set the configuration of a given Board.

        Args:
            represented_player (State): The player that will be represented in this Board state.
        """
        self.represented_player = represented_player 
        self.represented_opponent = (State.PLAYER_1 if (represented_player != State.PLAYER_1) else State.PLAYER_2)

    def clone(self):
        """ Creates a deep copy clone of this Board.

        Returns:
            Board: The deepcopy Board object.
        """

        new_board = Board(self.represented_player)
        new_board.board_array = copy.deepcopy(self.board_array)
        new_board.move_count = copy.deepcopy(self.move_count)
        
        new_board.represented_player = copy.deepcopy(self.represented_player)
        new_board.represented_opponent = copy.deepcopy(self.represented_opponent)

        new_board.global_board = copy.deepcopy(self.global_board)

        new_board.global_board_stats = copy.deepcopy(self.global_board_stats)
        new_board.local_board_stats = copy.deepcopy(self.local_board_stats)

        new_board.accumulated_heuristic = copy.deepcopy(self.accumulated_heuristic)

        return new_board


    def set_current_player(self):
        ''' Calculates the current player. '''
        self.current_player = State.PLAYER_1 if self.move_count % 2 == 0 else State.PLAYER_2


    def new_move(self, move: tuple[int, int], calc_heuristic: bool = False):
        """ Inserts a move into the Board state.

        Args:
            move (tuple[int, int]): The move to be inserted.
            calc_heuristic (bool, optional): True if heuristic should be updated. Defaults to False.
        """

        # Set the current player for this turn
        self.set_current_player()

        legal = False
        for moves in self.legal_moves(self.last_move):
            if moves == move:
                legal = True
                break
        
        while(not legal):
            print("made illegal move")

        self.board_array[move[0] * 9 + move[1]] = self.current_player 
        self.evaluate_local(move)

        if calc_heuristic:
            self.accumulated_heuristic += self.heuristic(move) * (-1 if self.current_player != self.represented_player else 1)

        self.move_count += 1

        self.last_move = move
  

    def evaluate_local(self, move: tuple[int, int]):
        ''' Checks to see if the local board that the move was played on has been won or drawn. Changes status of small board in global_board.

        Args:
            move (tuple[int, int]): The last move played.
            
        Returns: 
            State:  State.PLAYER_1 if Player 1 won. State.PLAYER_2 if Player 2 won. State.DRAW if neither player won (draw).State.UNCLAIMED if board is not closed.
        '''
        scores = []
        local_board_pos = move[0]
        local_board_move = move[1]
        
        # Update the number of moves played
        self.local_board_stats[local_board_pos][3] += 1

        row_pos = floor(local_board_move / 3)
        col_pos = local_board_move % 3

        # Get the row stats of a local board and add the current player to its respective counter
        self.local_board_stats[local_board_pos][0][row_pos] += self.current_player
        scores.append(self.local_board_stats[local_board_pos][0][row_pos]) 

        # Get the column stats of a local board and add the current player to its respective counter
        self.local_board_stats[local_board_pos][1][col_pos] += self.current_player
        scores.append(self.local_board_stats[local_board_pos][1][col_pos]) 
        
        if local_board_move == 4:
            self.local_board_stats[local_board_pos][2][1] += self.current_player
            self.local_board_stats[local_board_pos][2][0] += self.current_player
            scores.append(self.local_board_stats[local_board_pos][2][1]) 
            scores.append(self.local_board_stats[local_board_pos][2][0])
        elif local_board_move % 4 == 0: 
            self.local_board_stats[local_board_pos][2][1] += self.current_player
            scores.append(self.local_board_stats[local_board_pos][2][1]) 
        elif local_board_move % 2 == 0: 
            self.local_board_stats[local_board_pos][2][0] += self.current_player
            scores.append(self.local_board_stats[local_board_pos][2][0])

        for score in scores: 
            if score == (self.current_player * 3): # todo ask about this
                self.global_board[local_board_pos] = self.current_player 
                self.evaluate_global(local_board_pos) 
                return self.current_player
        
        # If the number of moves is nine (max), return a draw.
        if self.local_board_stats[local_board_pos][3] == 9:
            self.global_board[local_board_pos] = State.DRAW
            self.evaluate_global(local_board_pos) 
            return State.DRAW

        return State.UNCLAIMED


    def evaluate_global(self, local_board_pos: int, heuristic = False):
        """ Evaluates win conditions for the big board

        Args:
            local_board_pos (int): Index of the small board that recently closed (i.e. the reason you would want to check if the global board has changed states).
            heuristic (bool, optional): True if heuristic should be updated. Defaults to False.

        Returns:
            State:  State.PLAYER_1 if Player 1 won. State.PLAYER_2 if Player 2 won. State.DRAW if neither player won (draw).State.UNCLAIMED if board is not closed.
        """
        scores = []
        player = self.current_player

        row_pos = floor(local_board_pos / 3)
        col_pos = local_board_pos % 3

        if heuristic:
            scores.append(self.global_board_stats[0][row_pos]) 
            scores.append(self.global_board_stats[1][col_pos]) 
        
            if local_board_pos == 4:
                scores.append(self.global_board_stats[2][1])
                scores.append(self.global_board_stats[2][0])
            elif local_board_pos % 4 == 0: 
                scores.append(self.global_board_stats[2][1])
            elif local_board_pos % 2 == 0:
                scores.append(self.global_board_stats[2][0])
        
        else:
            self.global_board_stats[3] += 1
            self.global_board_stats[0][row_pos] += player  
            scores.append(self.global_board_stats[0][row_pos]) 

            self.global_board_stats[1][col_pos] += player 
            scores.append(self.global_board_stats[1][col_pos]) 
        
            if local_board_pos == 4:
                self.global_board_stats[2][1] += player
                self.global_board_stats[2][0] += player 
                scores.append(self.global_board_stats[2][1])
                scores.append(self.global_board_stats[2][0])
            elif local_board_pos % 4 == 0:
                self.global_board_stats[2][1] += player
                scores.append(self.global_board_stats[2][1])
            elif local_board_pos % 2 == 0:
                self.global_board_stats[2][0] += player 
                scores.append(self.global_board_stats[2][0])

        for score in scores: 
            if score == self.current_player * 3: 
                return self.current_player
        if self.global_board_stats[3] == 9:
            return State.DRAW

        return State.UNCLAIMED


    def block_opponent(self, board: list, relative_move: int, index_offset: int):
        """ Checks to see if an opponent's win was blocked 

        Args:
            board (list): An array representing the relative board that can be either the entire 9x9 or the global state of the small boards (3x3).
            relative_move (int): An integer of which position on the board changed states.
            index_offset (int): the offset from the front of the array to find the correct board that the move was played on.

        Returns:
            int: Number of wins that the move blocked.
        """
        opp = self.represented_opponent
        index = relative_move + index_offset
        blocked = 0
        match relative_move:
            case 0: #top left
                if(board[index+1] == opp and board[index+2] == opp): #check row block
                    blocked +=1
                if(board[index+3] == opp and board[index+6] == opp): #check col block
                    blocked += 1
                if(board[index+4] == opp and board[index+8] == opp): #check diagonal
                    blocked += 1
            case 1: #top middle
                if(board[index-1] == opp and board[index+1] == opp): #row
                    blocked +=1
                if(board[index+3] == opp and board[index+6] == opp): #col
                    blocked += 1
            case 2: #top right
                if(board[index-2] == opp and board[index-1] == opp): #row
                    blocked +=1
                if(board[index+3] == opp and board[index+6] == opp): #col
                    blocked += 1
            case 3: #middle left
                if(board[index+1] == opp and board[index+2] == opp): #row
                    blocked +=1
                if(board[index-3] == opp and board[index+3] == opp): #col
                    blocked += 1
            case 4: #center
                if(board[index-1] == opp and board[index+1] == opp): #row
                    blocked +=1
                if(board[index-3] == opp and board[index+3] == opp): #col
                    blocked += 1
                if(board[index-4] == opp and board[index+4] == opp): #diag
                    blocked +=1
                if(board[index-2] == opp and board[index+2] == opp): #antidiag
                    blocked += 1 
            case 5: #middle right
                if(board[index-1] == opp and board[index+1] == opp): #row
                    blocked +=1
                if(board[index-3] == opp and board[index+3] == opp): #col
                    blocked += 1
            case 6: #bottom left
                if(board[index+1] == opp and board[index+2] == opp): #row
                    blocked +=1
                if(board[index-3] == opp and board[index-6] == opp): #col
                    blocked += 1
                if(board[index-2] == opp and board[index-4] == opp): #antidiag
                    blocked +=1
            case 7: #bottom middle
                if(board[index-1] == opp and board[index+1] == opp): #row
                    blocked +=1
                if(board[index-3] == opp and board[index-6] == opp): #col
                    blocked += 1
            case 8: #bottom right
                if(board[index-1] == opp and board[index-2] == opp): #row
                    blocked +=1
                if(board[index-3] == opp and board[index-6] == opp): #col
                    blocked += 1
                if(board[index-4] == opp and board[index-8] == opp): #diag
                    blocked += 1

        return blocked


    def move_adjacency(self, board: list, relative_move:int, stats_array: tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int], int]): 
        """ Determines the number of adjacent moves that are of the same type and can lead to a win.

        Args:
            board (list): An array representing the relative board that can be either the entire 9x9 or the global state of the small boards (3x3).
            relative_move (int): An integer of which position on the board changed states.
            stats_array (tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int], int]): A stats array of a given board.

        Returns:
            int: The number of adjacent moves.
        """
        adjacent = 0

        for score_list in range(3):
            for score in stats_array[score_list]: 
                if score == 2 * self.current_player: 
                    adjacent += 1

        return adjacent


    def board_opportunity(self, board: list, relative_move: int):
        """ Determines the number of possible wins from a position on an empty board

        Args:
            board (list): An array representing the relative board.
            relative_move (int): An integer of which position on the board changed states.

        Returns:
            int: (The number of possible wins - 2)
        """
        opportunity = 0
        match relative_move:
            case 0: #top left
                opportunity = 1
            case 1: #top middle
                opportunity = 0
            case 2: #top right
                opportunity = 1
            case 3: #middle left
                opportunity = 0
            case 4: #center
                opportunity = 2
            case 5: #middle right
                opportunity = 0
            case 6: #bottom left
                opportunity = 1
            case 7: #bottom middle
                opportunity = 0
            case 8: #bottom right
                opportunity = 1
                
        return opportunity 

    
    def legal_moves(self, move: tuple[int, int] = None):
        """ Determines the set if legal moves based on the current board.

        Args:
            move (tuple[int, int]): The last move played.

        Returns:
            list(tuple[int, int]):  The list of legal moves.
        """
        if(move == None):
            move = self.last_move
        legal_moves = []
        if (self.last_move == None) or self.global_board[move[1]] != State.UNCLAIMED:  # if the local board for next move is closed
            for board_index in range(9): # for every available board
                if self.global_board[board_index] == State.UNCLAIMED: # if the global board is not claimed
                    for local_board_index in range(9):
                        if self.board_array[9*board_index+local_board_index] == State.UNCLAIMED:
                            legal_moves.append((board_index, local_board_index))
        else:
            for i in range(0,9):
                position = move[1] * 9 + i
                if self.board_array[position] == State.UNCLAIMED:
                    legal_moves.append((move[1], i))

        return legal_moves


    def heuristic(self, move: tuple[int, int]):
        """ Calculates heuristic of current board state.

        Args:
            move (tuple[int, int]): The last move played.

        Returns:
            int: The Board's accumulative heuristic value.
        """
        win_local = self.global_board[move[0]]
        global_board_block = 0
        global_board_adj =  0
        global_board_opp = 0
        
        if win_local == self.current_player: 
            win_local = 1
            global_board_block = self.block_opponent(self.global_board, move[0], 0) # did closing the small board block a global win
            global_board_adj = self.move_adjacency(self.global_board, move[0], self.global_board_stats) # was the closed board near another closed board of the same player
            global_board_opp = self.board_opportunity(self.global_board, move[0]) # how many ways can you win from the current position
        elif win_local == -1: #no winner the board
            win_local = 0.5
            global_board_block = self.block_opponent(self.global_board, move[0], 0)
        else:
            win_local = 0
        
        global_win = self.evaluate_global(move[0], True) # Check if the move caused a win
        if global_win == self.represented_player: # If the board was won by the current player
            global_win = 1
        elif global_win == State.DRAW: # A draw should be prioritized over a lose
            global_win = 0.25
        else:
            global_win = 0

        blocked_opp = self.block_opponent(self.board_array, move[1], move[0] * 9)
        adj_bonus = self.move_adjacency(self.board_array, move[1], self.local_board_stats[move[0]])

        heuristic_ = (blocked_opp*20) + (adj_bonus*10) + (win_local*100) + (global_board_adj * 200) + (global_board_block * 150) + (global_board_opp * 40) + (global_win * 100000)
        return heuristic_ if heuristic_ > 0 else -20

    def has_game_ended(self):
        for winCond in range(3):
            for score in self.global_board_stats[winCond]:
                #print(f"Score: {score}\t Boards: {self.global_board}\t Scores: {self.global_board_stats}\t Moves: {self.move_count}")
                if(score == State.PLAYER_1 *3):
                    #print("PLAYER 1 HAS WON")
                    return State.PLAYER_1
                if(score == State.PLAYER_2 * 3):
                    #print("PLAYER 2 HAS WON")
                    return State.PLAYER_2
        if(self.global_board_stats[3] == 9):
            return State.UNCLAIMED
        return None

    def printBoard(self): 
        """ Utility to print a viewable Board state. """
        for i in range(len(self.board_array)):
            if i is not 0 and i % 9 == 0: 
                print("\n")
            print(f'{self.board_array[i]} ', end = '')
    
    def print_board_pretty(self):
        print(f"{self.board_array[0]} {self.board_array[1]} {self.board_array[2]}  |  {self.board_array[9]} {self.board_array[10]} {self.board_array[11]}  |  {self.board_array[18]} {self.board_array[19]} {self.board_array[20]}")
        print(f"{self.board_array[3]} {self.board_array[4]} {self.board_array[5]}  |  {self.board_array[12]} {self.board_array[13]} {self.board_array[14]}  |  {self.board_array[21]} {self.board_array[22]} {self.board_array[23]}")
        print(f"{self.board_array[6]} {self.board_array[7]} {self.board_array[8]}  |  {self.board_array[15]} {self.board_array[16]} {self.board_array[17]}  |  {self.board_array[24]} {self.board_array[25]} {self.board_array[26]}")
        print("-----------------------------")
        print(f"{self.board_array[27]} {self.board_array[28]} {self.board_array[29]}  |  {self.board_array[36]} {self.board_array[37]} {self.board_array[38]}  |  {self.board_array[45]} {self.board_array[46]} {self.board_array[47]}")
        print(f"{self.board_array[30]} {self.board_array[31]} {self.board_array[32]}  |  {self.board_array[39]} {self.board_array[40]} {self.board_array[41]}  |  {self.board_array[48]} {self.board_array[49]} {self.board_array[50]}")
        print(f"{self.board_array[33]} {self.board_array[34]} {self.board_array[35]}  |  {self.board_array[42]} {self.board_array[43]} {self.board_array[44]}  |  {self.board_array[51]} {self.board_array[52]} {self.board_array[53]}")
        print("-----------------------------")
        print(f"{self.board_array[54]} {self.board_array[55]} {self.board_array[56]}  |  {self.board_array[63]} {self.board_array[64]} {self.board_array[65]}  |  {self.board_array[72]} {self.board_array[73]} {self.board_array[74]}")
        print(f"{self.board_array[57]} {self.board_array[58]} {self.board_array[59]}  |  {self.board_array[66]} {self.board_array[67]} {self.board_array[68]}  |  {self.board_array[75]} {self.board_array[76]} {self.board_array[77]}")
        print(f"{self.board_array[60]} {self.board_array[61]} {self.board_array[62]}  |  {self.board_array[69]} {self.board_array[70]} {self.board_array[71]}  |  {self.board_array[78]} {self.board_array[79]} {self.board_array[80]}")
        print("-----------------------------")

        print("\n")
