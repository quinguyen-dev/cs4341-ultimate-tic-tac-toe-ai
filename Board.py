import copy


class Board:
    #state of big board
    boardArray = [-1]*81
    closedBoards = [(False, 0)]*9 #closed state and winner (0 for X, 1 for O)
    moves = []
    currMove = 0  #Current move in the game (so the move the agent will returm) i.e. if the last move was 4, current move will be five
   

   #state of small boards
    smallBoardPnts = [[[0,0,0], [0,0,0], [0,0]] for i in range(9)]

   
    def Board(initMoves: list, self):
        for i in range(0, len(initMoves)):
            self.boardArray[initMoves[i][0]*9+initMoves[i][1]] = self.currMove%2

            self.currMove +=1
        self.moves.append(copy.deepcopy(initMoves[-1]))
        

    def newMove(move:list, self):
        self.boardArray[move[0] * 9 + move[1]] = self.currMove%2
        self.moves.append(copy.deepcopy(move))
        self.currMove +=1

    def legalMoves(self):
        legalMoves = ()
        if(self.closedBoards[self.lastMove[1]][0]):
            for i in range(0, 81):
                if self.BoardArray[i]==-1:
                    legalMoves.append(self.boardArray[i])
        else:
            for i in range(0,9):
                if(self.boardArray[self.lastMove[1]*9+i]==-1):
                    legalMoves.append(self.lastMove[1]*9+i)
        return legalMoves
    
    def rollBackMove(self):
        self.currMove -= 1
        self.moves.pop()
    
    # def checkSmallBoards(self):
    #     for i in range(0, 9):

