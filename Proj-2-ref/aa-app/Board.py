import copy
from math import floor
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
    
    # def __init__(self, player: int):
    #     '''Constructs a board object

    #         Args:
    #             player: which player is the agent representing
    #     '''
    #     self.player = player 

    # def __init__(self, represented_player: State):
    #     '''Constructs a board object

    #         Args:
    #             player: which player is the agent representing
    #     '''
    #     self.represented_player = represented_player 

    def __init__(self):
        ''' Constructs a board object

            Args:
                player: which player is the agent representing
        '''
    
    # todo 0 is player 1 and 1 is player 2

    def set_player(self, represented_player: State):
        self.represented_player = represented_player
        self.represented_opponent = (State.PLAYER_1 if (represented_player != State.PLAYER_1) else State.PLAYER_2)
        

    def get_current_player(self):
        ''' Calculates the current player

            Returns:
                State.PLAYER_1 (1) if it is Player 1's turn. State.PLAYER_2 (2) if it is Player 2's turn.
        '''
        return self.move_count % 2


    def set_current_player(self):
        ''' Calculates the current player '''
        self.current_player = State.PLAYER_1 if self.move_count % 2 == 0 else State.PLAYER_2


    def new_move(self, move: tuple[int, int], calc_heuristic: bool = False):
        '''
        Inserts a move into the board state
        Args:
            move: format of (small_board_index, local_board_position)
            calc_heuristic: True is heuristic needs to be updated, should be false when move is brought in from ref or when final move is selected
        
        Returns:

        '''
        # Set the current player for this turn
        self.set_current_player()

        self.board_array[move[0] * 9 + move[1]] = self.current_player # todo used to be + 1
        self.move_count += 1 # todo does this need to be here at this point?

        won_local_board = self.evaluate_local(move)

        if calc_heuristic:
            accumulated_heuristic += self.heuristic(self, move, won_local_board) * (-1 if self.current_player != self.represented_player else 1)
    

    def evaluate_local(self, move: tuple[int, int]):
        ''' Checks to see if the local board that the move was played on has been won or drawn. Changes status of small board in global_board

            Args:
                move: format of (small_board_index, local_board_position)
            
            Returns:
                State.Player1 if Player 1 won 
                State.Player2 if Player 2 won
                State.Draw if neither player won (draw)
                State.Unclaimed if board is not closed
        
        '''
        scores = []
        local_board_pos = move[0]
        local_board_move = move[1]
        
        # Update the number of moves played
        self.local_board_stats[local_board_pos][3] += 1

        # Calculate the row / column the 
        row_pos = floor(local_board_move / 3)
        col_pos = local_board_move % 3

        # Get the row stats of a local board and add the current player to its respective counter
        row_score = self.local_board_stats[local_board_pos][0][row_pos]
        print(self.current_player)
        row_score += self.current_player # todo change this to active player
        scores.append(row_score) #add row to scores array

        # Get the column stats of a local board and add the current player to its respective counter
        col_score = self.local_board_stats[local_board_pos][1][col_pos]
        col_score += self.current_player # todo change this to active player and make sure this is a reference
        scores.append(col_score) #add col to scores
        
        if local_board_move % 4 == 0: # Check the anti-diagonal
            anti_diag_score = self.local_board_stats[local_board_pos][2][1]
            anti_diag_score += self.current_player # todo change this to active player
            scores.append(anti_diag_score) 
        elif local_board_move % 2 == 0: # Check the diagonal 
            diag_score = self.local_board_stats[local_board_pos][2][0]
            diag_score += self.current_player # todo change this to active player
            scores.append(diag_score)

        # Check if a win condition has been met
        for score in scores: 
            if score == (self.current_player * 3): # todo ask about this
                self.global_board[local_board_pos] = self.current_player # Updates the closed status of the small board on the global list # todo change this to active player
                self.evaluate_global(local_board_pos) # Check if winning a small board has won a larger board
                return self.current_player #board is won 
        
        # If the number of moves is nine (max), return a draw
        if self.local_board_stats[local_board_pos][3] == 9:
            self.global_board[local_board_pos] = State.DRAW
            self.evaluate_global(local_board_pos) # Update global stats
            return State.DRAW

        return State.UNCLAIMED

    def evaluate_global(self, local_board_pos: int, heuristic = False):
        ''' Evaluates win conditions for the big board

            Args:
                local_board_pos: index of the small board that recently closed (i.e. the reason you would want to check if the global board has changed states)
            
            Returns:

        '''
        scores = []
        player = self.current_player

        row_pos = floor(local_board_pos / 3)
        col_pos = local_board_pos % 3

        if(heuristic):
            row_score = self.global_board_stats[0][row_pos]  
            scores.append(row_score) 

            col_score = self.global_board_stats[1][col_pos] 
            scores.append(col_score) 
        
            if local_board_pos % 4 == 0: # Check anti-diagonal
                anti_diag_score = self.global_board_stats[2][1]
                scores.append(anti_diag_score)
            elif local_board_pos % 2 == 0: # Check diagonal
                diag_score = self.global_board_stats[2][0] 
                scores.append(diag_score)

        
        else:
            self.global_board_stats[3] += 1
            row_score = self.global_board_stats[0][row_pos] 
            row_score += player  
            scores.append(row_score) 

            col_score = self.global_board_stats[1][col_pos] 
            col_score += player 
            scores.append(col_score) 
        
            if local_board_pos % 4 == 0: # Check anti-diagonal
                anti_diag_score = self.global_board_stats[2][1]
                anti_diag_score += player
                scores.append(anti_diag_score)
            elif local_board_pos % 2 == 0: # Check diagonal
                diag_score = self.global_board_stats[2][0] 
                diag_score += player 
                scores.append(diag_score)


        for score in scores: #check each win condition
            if score == self.current_player*3: #game is won
                return self.current_player
        if self.global_board_stats[3] == 9: #game is draw
            return State.DRAW
        return State.UNCLAIMED #game is not over


    def block_opponent(board: list, relative_move:int, index_offset:int, self): #did the last move block the opponent?
        ''' Checks to see if an opponent's win was blocked 

            Args:
                board: an array representing the relative board
                    can be either the entire 9x9 or the global state of the small boards (3x3)
                
                relative_move: an integer of which position on the board changed states

                index_offset: the offset from the front of the array to find the correct board that the move was played on
                    only useful when evaluating a small board, should be 0 if evaluating the large board
            
            Returns
                number of wins that the move blocked
        
        '''
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
                if(board[index-3] == opp and board[index+6] == opp): #col
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


    def move_adjacency(board: list, relative_move:int, index_offset:int, self): #was the last move adjacent to one of your previous moves
        '''Determines the number of adjacent moves that are of the same type and can lead to a win

            Args:
                board: an array representing the relative board
                    can be either the entire 9x9 or the global state of the small boards (3x3)
                
                relative_move: an integer of which position on the board changed states

                index_offset: the offset from the front of the array to find the correct board that the move was played on
                    only useful when evaluating a small board, should be 0 if evaluating the large board
            
            Returns:
                The number of adjacent moves
        '''
        index = relative_move + index_offset
        adjacent = 0
        match relative_move:
            case 0: #top left
                if(board[index+1] == self.current_player or board[index+2] == self.current_player): #check row block
                    adjacent +=1
                if(board[index+3] == self.current_player or board[index+6] == self.current_player): #check col block
                    adjacent += 1
                if(board[index+4] == self.current_player or board[index+8] == self.current_player): #check diagonal
                    adjacent += 1
            case 1: #top middle
                if(board[index-1] == self.current_player or board[index+1] == self.current_player): #row
                    adjacent +=1
                if(board[index+3] == self.current_player or board[index+6] == self.current_player): #col
                    adjacent += 1
            case 2: #top right
                if(board[index-2] == self.current_player or board[index-1] == self.current_player): #row
                    adjacent +=1
                if(board[index+3] == self.current_player or board[index+6] == self.current_player): #col
                    adjacent += 1
            case 3: #middle left
                if(board[index+1] == self.current_player or board[index+2] == self.current_player): #row
                    adjacent +=1
                if(board[index-3] == self.current_player or board[index+3] == self.current_player): #col
                    adjacent += 1
            case 4: #center
                if(board[index-1] == self.current_player or board[index+1] == self.current_player): #row
                    adjacent +=1
                if(board[index-3] == self.current_player or board[index+3] == self.current_player): #col
                    adjacent += 1
                if(board[index-4] == self.current_player or board[index+4] == self.current_player): #diag
                    adjacent +=1
                if(board[index-2] == self.current_player or board[index+2] == self.current_player): #antidiag
                    adjacent += 1 
            case 5: #middle right
                if(board[index-1] == self.current_player or board[index-2] == self.current_player): #row
                    adjacent +=1
                if(board[index-3] == self.current_player or board[index+6] == self.current_player): #col
                    adjacent += 1
            case 6: #bottom left
                if(board[index+1] == self.current_player or board[index+2] == self.current_player): #row
                    adjacent +=1
                if(board[index-3] == self.current_player or board[index-6] == self.current_player): #col
                    adjacent += 1
                if(board[index-2] == self.current_player or board[index-4] == self.current_player): #antidiag
                    adjacent +=1
            case 7: #bottom middle
                if(board[index-1] == self.current_player or board[index+1] == self.current_player): #row
                    adjacent +=1
                if(board[index-3] == self.current_player or board[index-6] == self.current_player): #col
                    adjacent += 1
            case 8: #bottom right
                if(board[index-1] == self.current_player or board[index-2] == self.current_player): #row
                    adjacent +=1
                if(board[index-3] == self.current_player or board[index-6] == self.current_player): #col
                    adjacent += 1
                if(board[index-4] == self.current_player or board[index-8] == self.current_player): #diag
                    adjacent += 1
        return adjacent


    def board_opportunity(board: list, relative_move: int):
        '''Determines the number of possible wins from a position on an empty board

            Args:
                board: an array representing the relative board
                    can be either the entire 9x9 or the global state of the small boards (3x3)
                
                relative_move: an integer of which position on the board changed states
            
            Returns:
                The number of possible wins minus 2
        '''
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

    
    def legal_moves(move: list, self):
        '''Determines the set if legal moves based on the current board

            Args:
                move: last move played in the format of (small_board_index, local_board_position)

            Returns
                list of legal moves in the format of (small_board_index, local_board_position)
        '''
        legal_moves = ()
        if self.global_board[move[0]] != 0:
            for i in range(0, 81):
                if self.board_array[i]== State.DRAW:
                    legal_moves.append((floor(i/9), i%9))
        else:
            for i in range(0,9):
                position = move[0]*9+i
                if(self.board_array[position]==-1):
                    legal_moves.append(position)
        return legal_moves


    def heuristic( move: list, self):
        '''
            Calculates heuristic of current board state

            Args:
                move: last move played in the format of (small_board_index, local_board_position)

            Returns:
                board's value
        '''
        win_local = self.global_board[move[0]]
        global_board_block = 0
        global_board_adj =  0
        global_board_opp = 0
        
        if win_local == self.represented_player: #won the board
            win_local = 1
            global_board_block = self.block_opponent(self.global_board, move[0], 0)
            global_board_adj = self.move_adjacency(self.global_board, move[0], 0)
            global_board_opp = self.board_opportunity(self.global_board, move[0], 0)
        elif win_local == -1: #drew the board
            win_local = 0.5
            global_board_block = self.block_opponent(self.global_board, move[0], 0)
        else:
            win_local = 0
        
        global_win = self.global_board_eval(move[0], True)
        if global_win == self.represented_player:
            global_win = 1
        elif global_win == State.DRAW:
            global_win = 0.25
        else:
            global_win = 0

        blocked_opp = self.block_opponent(self.board_array, move[1], move[0]*9)
        adj_bonus = self.move_adjacency(self.board_array, move[1], move[0]*9)

        #weights of each heuristic minus penalty for making a move that does nothing
        return (blocked_opp*20) + (adj_bonus*5) + (win_local*100) + (global_board_adj*200) + (global_board_block*150) + (global_board_opp*5) + (global_win*400) - 20




        


        

