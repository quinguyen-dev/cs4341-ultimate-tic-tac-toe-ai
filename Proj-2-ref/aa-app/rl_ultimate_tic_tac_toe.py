from genericpath import exists
import numpy as np
import pickle
from Board import Board
from utility import State

BOARD_ROWS = 3
BOARD_COLS = 3
LOCAL_BOARDS = 9

#source: https://towardsdatascience.com/reinforcement-learning-implement-tictactoe-189582bea542
#source: https://github.com/MJeremy2017/reinforcement-learning-implementation/blob/master/TicTacToe/ticTacToe.py 

class Environment_State:
    def __init__(self, p1, p2):
        self.board = Board() #2D array of board initialized with 0s in every location
        self.p1 = p1 #player 1
        self.p2 = p2 #player 2
        self.isEnd = False #has the game ended
        self.boardHash = None #hash of the board state
        self.last_move = None #store last move played
        # init p1 plays first
        self.playerSymbol = State.PLAYER_1

    # get unique hash of current board state
    def getHash(self):
        self.boardHash = str(self.board.board_array)
        return self.boardHash

    def winner(self):
        # row
        game_winner = self.board.has_game_ended()
        if( game_winner != None):
            self.isEnd = True
            return game_winner
        else:
            return None

    def availablePositions(self): #returns array of legal positions
        return self.board.legal_moves(self.last_move, True)

    def updateState(self, position): #switches perspective
        self.board.new_move(position)

        self.last_move = position
        # switch to another player
        self.playerSymbol = State.PLAYER_2 if self.playerSymbol == State.PLAYER_1 else State.PLAYER_1

    # only when game ends
    def giveReward(self):
        result = self.winner()
        # backpropagate reward
        if result == 1:
            self.p1.feedReward(1)
            self.p2.feedReward(0)
        elif result == -1:
            self.p1.feedReward(0)
            self.p2.feedReward(1)
        else:
            self.p1.feedReward(0.1)
            self.p2.feedReward(0.5)

    # board reset after game is won
    def reset(self):
        #print("RESET BOARD")
        del self.board
        self.board = Board()
        self.boardHash = None
        self.isEnd = False
        self.playerSymbol = State.PLAYER_1
        self.last_move = None

    def play(self, rounds=100):
        for i in range(rounds):
            if i % 50 == 0:
                print("Rounds {}".format(i))
            while not self.isEnd:
                # Player 1
                positions = self.availablePositions()
                p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol)
                # take action and update board state
                self.updateState(p1_action)
                board_hash = self.getHash()
                self.p1.addState(board_hash)
                # check board status if it is end

                win = self.winner()
                if win is not None:
                    #print(f"WINNER: {win}")
                    #self.showBoard()
                    # ended with p1 either win or draw
                    self.giveReward()
                    self.p1.reset()
                    self.p2.reset()
                    self.reset()
                    break

                else:
                    # Player 2
                    positions = self.availablePositions()
                    p2_action = self.p2.chooseAction(positions, self.board, self.playerSymbol)
                    self.updateState(p2_action)
                    board_hash = self.getHash()
                    self.p2.addState(board_hash)

                    win = self.winner()
                    if win is not None:
                        # self.showBoard()
                        # ended with p2 either win or draw
                        self.giveReward()
                        self.p1.reset()
                        self.p2.reset()
                        self.reset()
                        break

    # play with human
    def play2(self):
        while not self.isEnd:
            # Player 1
            positions = self.availablePositions()
            p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol)
            # take action and update board state
            self.updateState(p1_action)
            self.showBoard()
            print(f"move_count: {self.board.move_count}")
            # check board status if it is end
            win = self.winner()
            if win is not None:
                if win == 1:
                    print(self.p1.name, "wins!")
                else:
                    print("tie!")
                self.reset()
                break

            else:
                # Player 2
                positions = self.availablePositions()
                print(self.last_move)
                p2_action = self.p2.chooseAction(positions)

                self.updateState(p2_action)
                self.showBoard()
                win = self.winner()
                if win is not None:
                    if win == -1:
                        print(self.p2.name, "wins!")
                    else:
                        print("tie!")
                    self.reset()
                    break

    def showBoard(self):
        # p1: x  p2: o
        self.board.print_board_pretty()
        


class Player:
    def __init__(self, name, exp_rate=0.3, decay_gamma: float = 1, learning_rate: float = 0.2):
        self.name = name
        self.states = []  # record all positions taken
        self.lr = 0.2
        self.exp_rate = exp_rate
        self.decay_gamma = decay_gamma
        self.states_value = {}  # state -> value

    def getHash(self, board: Board):
        boardHash = str(board.board_array)
        return boardHash

    def chooseAction(self, positions:tuple[tuple[int, int]], current_board:Board, symbol):
        if np.random.uniform(0, 1) <= self.exp_rate: #if a value is randomly selected to explore options instead of follow policy
            # take random action
            idx = np.random.choice(len(positions))
            action = positions[idx]
        else:
            value_max = -999
            for p in positions: #for each possible position
                next_board = current_board.clone() #copy current board
                next_board.new_move(p)#add new move
                next_boardHash = self.getHash(next_board) #get hashed value of move
                value = 0 if self.states_value.get(next_boardHash) is None else self.states_value.get(next_boardHash) #check if board config has been seen before, return cumulative reward for state if seen before, else return 0
                #print("value", value)
                if value >= value_max: #if best so far
                    value_max = value
                    action = p #set as next recommended action
        # print("{} takes action {}".format(self.name, action))
        return action #return best action or random action

    # append a hash state
    def addState(self, state):
        #adds a hashed board array to state
        self.states.append(state)

    # at the end of game, backpropagate and update states value
    def feedReward(self, reward):
        for st in reversed(self.states): #states is the record of moves taken
            if self.states_value.get(st) is None: #if a state has never been seen prior to this game
                self.states_value[st] = 0 #add to dictionary and set value to 0
            #add to the value of the state, the learning rate * (the discount * the value of the next state in the sequence - current value for reward)
            self.states_value[st] += self.lr * (self.decay_gamma * reward - self.states_value[st])
            reward = self.states_value[st]

    def reset(self):
        self.states = []

    def savePolicy(self):
        fw = open('policy_' + str(self.name), 'wb')
        pickle.dump(self.states_value, fw)
        fw.close()

    def loadPolicy(self, file):
        if exists(file):
            fr = open(file, 'rb')
            self.states_value = pickle.load(fr)
            fr.close()


class HumanPlayer:
    def __init__(self, name):
        self.name = name

    def chooseAction(self, positions):
        while True:
            row = int(input("Input your action board:"))
            col = int(input("Input your action rel pos:"))

            action = (row, col)
            if action in positions:
                return action

    # append a hash state
    def addState(self, state):
        pass

    # at the end of game, backpropagate and update states value
    def feedReward(self, reward):
        pass

    def reset(self):
        pass


if __name__ == "__main__":
    # training
    p1 = Player("p1", 0.2, 0.6, 0.4)
    p2 = Player("p2")

    p1.loadPolicy("policy_p1")
    p2.loadPolicy("policy_p2")

    st = Environment_State(p1, p2)
    print("training...")
    st.play(10)
    p1.savePolicy()
    p2.savePolicy()

    # play with human
    p1 = Player("computer", exp_rate=0)
    p1.loadPolicy("policy_p1")

    p2 = HumanPlayer("human")

    st = Environment_State(p1, p2)
    st.play2()



    '''because theres so many moves its possible that the latter steps are receiving almost no rewards'''