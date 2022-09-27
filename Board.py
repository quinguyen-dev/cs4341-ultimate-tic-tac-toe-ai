from cgitb import small
import copy
from math import floor
from nis import match


class Board:
    #state of big board
    boardArray = [-1]*81
    globalBoard = [0 for i in range(9)] #0 for local board that is open, 1 for player 1, 2 for player 2, -1 for draw
    moves = [] #set of played moves in format of (b, index) where b is the local board that was play and index is the index in the local board
    player = 0  #Player who made the last move (either player 1 or player 2)
    winCond = [[0,0,0], [0,0,0], [0,0], 0] #rows, cols, [diag, anit-diag], and moves made on global board

    #state of small boards
    smallBoardPnts = [[[0,0,0], [0,0,0], [0,0], 0] for i in range(9)] #rows, cols, [diag, anit-diag], and moves made on local boards

   
    def Board(initMoves: list, self):
        for i in range(0, len(initMoves)):
            self.player = (self.player+1)%2
            self.boardArray[initMoves[i][0]*9+initMoves[i][1]] = self.player            
        self.moves.append(copy.deepcopy(initMoves[-1]))
        

    #new move 
    def newMove(move:list, self):
        self.player = (self.player+1)%2
        self.boardArray[move[0] * 9 + move[1]] = self.player
        self.moves.append(copy.deepcopy(move))
        return self.evalLocalBoard(move)

    
    
    def evalLocalboard(move:list, self):
        scores = []
        
        self.smallBoardPnts[move[0]][3] += 1

        self.smallBoardPnts[move[0]][0][floor(move[1]/3)] += self.player #get the board -> get the row array -> get the row the move the was played in
        scores.append(self.smallBoardPnts[move[0]][0][floor(move[1]/3)-move[0]]) #add row to scores array
        self.smallBoardPnts[move[0]][1][floor(move[1]/3)] += self.player #get the board -> get the col array -> get the  col the move the was played in
        scores.append(self.smallBoardPnts[move[0]][0][floor(move[1]/3)-move[0]]) #add col to scores
        
        if(move[1]-(9*move[0]))%4==0: #check antidiagonal
            self.smallBoardPnts[move[0]][2][1] += self.player
            scores.append(self.smallBoardPnts[move[0]][2][2]) 
        else:
            if(move[1]-(9*move[0]))%2==0: #check diagonal
               self.smallBoardPnts[move[0]][2][1] += self.player 
               scores.append(self.smallBoardPnts[move[0]][2][0])

        for score in scores: #check if win condition has been met
            if score == (self.player*3):
                self.globalBoard[move[0]] = self.player
                return self.player #board is won
        
        if self.smallBoardPnts[move[0]][3] == 9:
            self.globalBoard[move[0]] = -1
            return -1 #draw
        return 0 #board is still open


    def localBlockOpp(move:list, self): #did the last move block the opponent?
        opp = (self.player + 1)%2
        index = move[0]*9+move[1]
        blocked = 0
        match move[1]:
            case 0: #top left
                if(self.board[index+1] == opp and self.board[index+2] == opp): #check row block
                    blocked +=1
                if(self.board[index+3] == opp and self.board[index+6] == opp): #check col block
                    blocked += 1
                if(self.board[index+4] == opp and self.board[index+8] == opp): #check diagonal
                    blocked += 1
            case 1: #top middle
                if(self.board[index-1] == opp and self.board[index+1] == opp): #row
                    blocked +=1
                if(self.board[index+3] == opp and self.board[index+6] == opp): #col
                    blocked += 1
            case 2: #top right
                if(self.board[index-2] == opp and self.board[index-1] == opp): #row
                    blocked +=1
                if(self.board[index+3] == opp and self.board[index+6] == opp): #col
                    blocked += 1
            case 3: #middle left
                if(self.board[index+1] == opp and self.board[index+2] == opp): #row
                    blocked +=1
                if(self.board[index-3] == opp and self.board[index+3] == opp): #col
                    blocked += 1
            case 4: #center
                if(self.board[index-1] == opp and self.board[index+1] == opp): #row
                    blocked +=1
                if(self.board[index-3] == opp and self.board[index+3] == opp): #col
                    blocked += 1
                if(self.board[index-4] == opp and self.board[index+4] == opp): #diag
                    blocked +=1
                if(self.board[index-2] == opp and self.board[index+2] == opp): #antidiag
                    blocked += 1 
            case 5: #middle right
                if(self.board[index-1] == opp and self.board[index+1] == opp): #row
                    blocked +=1
                if(self.board[index-3] == opp and self.board[index+6] == opp): #col
                    blocked += 1
            case 6: #bottom left
                if(self.board[index+1] == opp and self.board[index+2] == opp): #row
                    blocked +=1
                if(self.board[index-3] == opp and self.board[index-6] == opp): #col
                    blocked += 1
                if(self.board[index-2] == opp and self.board[index-4] == opp): #antidiag
                    blocked +=1
            case 7: #bottom middle
                if(self.board[index-1] == opp and self.board[index+1] == opp): #row
                    blocked +=1
                if(self.board[index-3] == opp and self.board[index-6] == opp): #col
                    blocked += 1
            case 8: #bottom right
                if(self.board[index-1] == opp and self.board[index-2] == opp): #row
                    blocked +=1
                if(self.board[index-3] == opp and self.board[index-6] == opp): #col
                    blocked += 1
                if(self.board[index-4] == opp and self.board[index-8] == opp): #diag
                    blocked += 1
        return blocked


    def localAdjacency(move:list, self): #was the last move adjacent to one of your previous moves?
        index = move[0]*9+move[1]
        adjacent = 0
        match move[1]:
            case 0: #top left
                if(self.board[index+1] == self.player or self.board[index+2] == self.player): #check row block
                    adjacent +=1
                if(self.board[index+3] == self.player or self.board[index+6] == self.player): #check col block
                    adjacent += 1
                if(self.board[index+4] == self.player or self.board[index+8] == self.player): #check diagonal
                    adjacent += 1
            case 1: #top middle
                if(self.board[index-1] == self.player or self.board[index+1] == self.player): #row
                    adjacent +=1
                if(self.board[index+3] == self.player or self.board[index+6] == self.player): #col
                    adjacent += 1
            case 2: #top right
                if(self.board[index-2] == self.player or self.board[index-1] == self.player): #row
                    adjacent +=1
                if(self.board[index+3] == self.player or self.board[index+6] == self.player): #col
                    adjacent += 1
            case 3: #middle left
                if(self.board[index+1] == self.player or self.board[index+2] == self.player): #row
                    adjacent +=1
                if(self.board[index-3] == self.player or self.board[index+3] == self.player): #col
                    adjacent += 1
            case 4: #center
                if(self.board[index-1] == self.player or self.board[index+1] == self.player): #row
                    adjacent +=1
                if(self.board[index-3] == self.player or self.board[index+3] == self.player): #col
                    adjacent += 1
                if(self.board[index-4] == self.player or self.board[index+4] == self.player): #diag
                    adjacent +=1
                if(self.board[index-2] == self.player or self.board[index+2] == self.player): #antidiag
                    adjacent += 1 
            case 5: #middle right
                if(self.board[index-1] == self.player or self.board[index+1] == self.player): #row
                    adjacent +=1
                if(self.board[index-3] == self.player or self.board[index+6] == self.player): #col
                    adjacent += 1
            case 6: #bottom left
                if(self.board[index+1] == self.player or self.board[index+2] == self.player): #row
                    adjacent +=1
                if(self.board[index-3] == self.player or self.board[index-6] == self.player): #col
                    adjacent += 1
                if(self.board[index-2] == self.player or self.board[index-4] == self.player): #antidiag
                    adjacent +=1
            case 7: #bottom middle
                if(self.board[index-1] == self.player or self.board[index+1] == self.player): #row
                    adjacent +=1
                if(self.board[index-3] == self.player or self.board[index-6] == self.player): #col
                    adjacent += 1
            case 8: #bottom right
                if(self.board[index-1] == self.player or self.board[index-2] == self.player): #row
                    adjacent +=1
                if(self.board[index-3] == self.player or self.board[index-6] == self.player): #col
                    adjacent += 1
                if(self.board[index-4] == self.player or self.board[index-8] == self.player): #diag
                    adjacent += 1
        return adjacent




    
    def evalBigBoard(smallB: int, self):
        scores = []
        player = (self.move %2)+1
        self.winCond[3] += 1

        self.winCond[floor(smallB/3)] += player #get the row array -> get the row the move the was played in
        scores.append(self.winCond[0][floor(smallB/3)]) #add row to scores array
        self.winCond[floor(smallB/3)] += player #get the col array -> get the col the move the was played in
        scores.append(self.winCond[0][floor(smallB/3)]) #add col to scores
        
        if(smallB)%4==0: #check antidiagonal
            self.winCondition[2][1] += player
            scores.append(self.winCond[2][2]) 
        else:
            if(smallB)%2==0: #check diagonal
               self.winCond[2][1] += player 
               scores.append(self.winCond[0][2][0])
        print('closed boards')
        #TODO something with win conditions here
        
            

    
    def legalMoves(self):
        legalMoves = ()
        if(self.globalBoard[self.lastMove[1]] != 0):
            for i in range(0, 81):
                if self.BoardArray[i]==-1:
                    legalMoves.append(self.boardArray[i])
        else:
            for i in range(0,9):
                if(self.boardArray[self.lastMove[1]*9+i]==-1):
                    legalMoves.append(self.lastMove[1]*9+i)
        return legalMoves
    
    
    # def rollBackMove(self):
    #     self.currMove -= 1
    #     self.moves.pop()

    @staticmethod
    def heuristic(board: Board, move: list):
        didLocalWin = board.newMove(move)
        winLocal = 0
        if(didLocalWin == Board.player): #won the board
            winLocal = 1
            bigBoardBlock = board.evalBigBoard(move[0])
            bigBoardAdj = board.evalBigBoardAdj(move[0])
            bigBoardOpportunity = board.evalBigOpp(move[0])
        elif(didLocalWin == -1): #drew the board
            winLocal = 0.5
            bigBoardBlock = board.evalBigBoard(move[0])
        blockedOpp = board.localBlockOpp(move)
        adjacentBonus = board.localAdjacency(move)



        


        

