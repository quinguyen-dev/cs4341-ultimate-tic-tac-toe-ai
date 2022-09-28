from cgitb import small
import copy
from math import floor
from nis import match


class Board:
    #state of big board
    board_array = [-1]*81
    global_board = [0 for i in range(9)] #0 for local board that is open, 1 for player 1, 2 for player 2, -1 for draw
    move_count = 0 #number of moves played
    player = 0  #Player who made the last move (either player 1 or player 2)
    win_cond = [[0,0,0], [0,0,0], [0,0], 0] #rows, cols, [diag, anit-diag], and moves made on global board

    #state of small boards
    small_board_win = [[[0,0,0], [0,0,0], [0,0], 0] for i in range(9)] #rows, cols, [diag, anit-diag], and moves made on local boards


    #accumulated heuristic value
    board_value = 0
   
    #value that represents our player
    player = -1

    
    #intakes the first 4 mo
    def __init__(player:int, self):
        '''constructs a board object

            Args:
                player: which player is the agent representing

            Returns:
        
        '''
        self.player = player          
        
    def get_curr_player(self):
        '''calculates the current player

            Returns:
                1 if it is player1's turn.

                2 if it is player2's turn
        '''
        return self.move_count%2


    def newMove(move:list, calc_heuristic:bool, self):
        '''
        Inserts a move into the board state
        Args:
            move: format of (small_board_index, local_board_position)
            calc_heuristic: true is heuristic needs to be updated
                should be false when move is brought in from ref or when final move is selected
        
        Returns:

        '''
        self.board_array[move[0] * 9 + move[1]] = (self.get_curr_player)+1
        self.move_count +=1
        won_local_board = self.evalLocalBoard(move)

        if(calc_heuristic):
            board_value += (self.heuristic(self, move, won_local_board))
        

    
    
    def evalLocalboard(move:list, self):
        '''Checks to see if the local board that the move was played on has been won or drawn. changes status of small board in global_board

            Args:
                move: format of (small_board_index, local_board_position)
            
            Returns:
                1 if player1 won 
                2 if player2 won
                -1 if neither player won (draw)
                0 if board is not closed
        
        '''
        scores = []
        
        self.small_board_win[move[0]][3] += 1

        self.small_board_win[move[0]][0][floor(move[1]/3)] += self.get_curr_player #get the board -> get the row array -> get the row the move the was played in
        scores.append(self.small_board_win[move[0]][0][floor(move[1]/3)-move[0]]) #add row to scores array
        self.small_board_win[move[0]][1][floor(move[1]/3)] += self.get_curr_player #get the board -> get the col array -> get the  col the move the was played in
        scores.append(self.small_board_win[move[0]][0][floor(move[1]/3)-move[0]]) #add col to scores
        
        if(move[1]-(9*move[0]))%4==0: #check antidiagonal
            self.small_board_win[move[0]][2][1] += self.get_curr_player
            scores.append(self.small_board_win[move[0]][2][2]) 
        else:
            if(move[1]-(9*move[0]))%2==0: #check diagonal
               self.small_board_win[move[0]][2][1] += self.get_curr_player
               scores.append(self.small_board_win[move[0]][2][0])

        for score in scores: #check if win condition has been met
            if score == (self.get_curr_player*3):
                self.global_board[move[0]] = self.get_curr_player
                self.evalBigBoard(move[0]) #Updates the closed status of the small board on the global list
                return self.get_curr_player() #board is won
        
        if self.small_board_win[move[0]][3] == 9:
            self.global_board[move[0]] = -1
            return -1 #draw
        return 0 #board is still open


    def blockOpp(board: list, relative_move:int, index_offset:int, self): #did the last move block the opponent?
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
        opp = ((self.get_curr_player) + 1)%2
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


    def moveAdjacency(board: list, relative_move:int, index_offset:int, self): #was the last move adjacent to one of your previous moves
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
                if(board[index+1] == self.get_curr_player() or board[index+2] == self.get_curr_player()): #check row block
                    adjacent +=1
                if(board[index+3] == self.get_curr_player() or board[index+6] == self.get_curr_player()): #check col block
                    adjacent += 1
                if(board[index+4] == self.get_curr_player() or board[index+8] == self.get_curr_player()): #check diagonal
                    adjacent += 1
            case 1: #top middle
                if(board[index-1] == self.get_curr_player() or board[index+1] == self.get_curr_player()): #row
                    adjacent +=1
                if(board[index+3] == self.get_curr_player() or board[index+6] == self.get_curr_player()): #col
                    adjacent += 1
            case 2: #top right
                if(board[index-2] == self.get_curr_player() or board[index-1] == self.get_curr_player()): #row
                    adjacent +=1
                if(board[index+3] == self.get_curr_player() or board[index+6] == self.get_curr_player()): #col
                    adjacent += 1
            case 3: #middle left
                if(board[index+1] == self.get_curr_player() or board[index+2] == self.get_curr_player()): #row
                    adjacent +=1
                if(board[index-3] == self.get_curr_player() or board[index+3] == self.get_curr_player()): #col
                    adjacent += 1
            case 4: #center
                if(board[index-1] == self.get_curr_player() or board[index+1] == self.get_curr_player()): #row
                    adjacent +=1
                if(board[index-3] == self.get_curr_player() or board[index+3] == self.get_curr_player()): #col
                    adjacent += 1
                if(board[index-4] == self.get_curr_player() or board[index+4] == self.get_curr_player()): #diag
                    adjacent +=1
                if(board[index-2] == self.get_curr_player() or board[index+2] == self.get_curr_player()): #antidiag
                    adjacent += 1 
            case 5: #middle right
                if(board[index-1] == self.get_curr_player() or board[index+1] == self.get_curr_player()): #row
                    adjacent +=1
                if(board[index-3] == self.get_curr_player() or board[index+6] == self.get_curr_player()): #col
                    adjacent += 1
            case 6: #bottom left
                if(board[index+1] == self.get_curr_player() or board[index+2] == self.get_curr_player()): #row
                    adjacent +=1
                if(board[index-3] == self.get_curr_player() or board[index-6] == self.get_curr_player()): #col
                    adjacent += 1
                if(board[index-2] == self.get_curr_player() or board[index-4] == self.get_curr_player()): #antidiag
                    adjacent +=1
            case 7: #bottom middle
                if(board[index-1] == self.get_curr_player() or board[index+1] == self.get_curr_player()): #row
                    adjacent +=1
                if(board[index-3] == self.get_curr_player() or board[index-6] == self.get_curr_player()): #col
                    adjacent += 1
            case 8: #bottom right
                if(board[index-1] == self.get_curr_player() or board[index-2] == self.get_curr_player()): #row
                    adjacent +=1
                if(board[index-3] == self.get_curr_player() or board[index-6] == self.get_curr_player()): #col
                    adjacent += 1
                if(board[index-4] == self.get_curr_player() or board[index-8] == self.get_curr_player()): #diag
                    adjacent += 1
        return adjacent




    
    def evalBigBoard(small_board_num: int, self):
        '''
            Evaluates win conditions for the big board

            Args:
                small_board_num: index of the small board that recently closed (i.e. the reason you would want to check if the global board has changed states)
            
            Returns:

        '''
        scores = []
        player = (self.move %2)+1
        self.win_cond[3] += 1

        self.win_cond[floor(small_board_num/3)] += player #get the row array -> get the row the move the was played in
        scores.append(self.win_cond[0][floor(small_board_num/3)]) #add row to scores array
        self.win_cond[floor(small_board_num/3)] += player #get the col array -> get the col the move the was played in
        scores.append(self.win_cond[0][floor(small_board_num/3)]) #add col to scores
        
        if(small_board_num)%4==0: #check antidiagonal
            self.win_condition[2][1] += player
            scores.append(self.win_cond[2][2]) 
        else:
            if(small_board_num)%2==0: #check diagonal
               self.win_cond[2][1] += player 
               scores.append(self.win_cond[0][2][0])
        print('closed boards')
        #TODO something with win conditions here


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
        
            

    
    def legalMoves(move: list, self):
        '''Determines the set if legal moves based on the current board

            Args:
                move: last move played in the format of (small_board_index, local_board_position)

            Returns
                list of legal moves in the format of (small_board_index, local_board_position)
        '''
        legalMoves = ()
        if(self.global_board[move[0]] != 0):
            for i in range(0, 81):
                if self.board_array[i]==-1:
                    legalMoves.append((floor(i/9), i%9))
        else:
            for i in range(0,9):
                position = move[0]*9+i
                if(self.board_array[position]==-1):
                    legalMoves.append(position)
        return legalMoves

    def heuristic( move: list, self):
        '''
            Calculates heuristic of current board state

            Args:
                move: last move played in the format of (small_board_index, local_board_position)

            Returns:
                board's value
        '''
        win_local = self.global_board[move[0]]
        bigBoardBlock = 0
        bigBoardAdj =  0
        bigBoardOpportunity = 0
        
        if(win_local == self.player): #won the board
            win_local = 1
            bigBoardBlock = self.evalBigBoard(move[0])
            bigBoardAdj = self.moveAdjacency(self.global_board, move[0], 0)
            bigBoardOpportunity = self.board_opportunity(self.global_board, move[0], 0)
        elif(win_local == -1): #drew the board
            win_local = 0.5
            bigBoardBlock = self.evalBigBoard(move[0])
        blockedOpp = self.blockOpp(self.board_array, move[1], move[0]*9)
        adjacentBonus = self.moveAdjacency(self.board_array, move[1], move[0]*9)

        #weights of each heuristic minus penalty for making a move that does nothing
        return (win_local*100) + (bigBoardAdj*200) + (bigBoardBlock*150) + (blockedOpp*20) + (adjacentBonus*5) + (bigBoardOpportunity*5) - 20




        


        

