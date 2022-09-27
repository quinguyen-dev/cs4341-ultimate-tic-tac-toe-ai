import copy


class Board:
    boardArray = [-1]*81
    lastMove = (-1, -1)
    currMove = 0  #Current move in the game (so the move the agent will returm) i.e. if the last move was 4, current move will be five
    def Board(initMoves: list, self):
        for i in range(0, len(initMoves)):
            self.boardArray[initMoves[i][0]*9+initMoves[i][1]] = self.currMove%2
            self.currMove +=1
        self.lastMove = initMoves[-1]

    def newMove(move:list, self):
        self.boardArray[move[0] * 9 + move[1]] = self.currMove%2
        self.lastMove = copy.deepcopy(move)
        self.currMove +=1

    def legalMoves(self):
        return i for i, n in enumerate()
