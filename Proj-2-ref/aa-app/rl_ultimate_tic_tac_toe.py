from genericpath import exists
import random
from statistics import mode
import time
from xmlrpc.client import Boolean
from ai import AI
import numpy as np
import pickle
from Board import Board
from utility import State
from tensorflow import keras
from keras import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import SGD
from scipy.ndimage.interpolation import shift

def generate_model():
    model = Sequential()
    model.add(Dense(162, input_dim = 81, kernel_initializer='normal', activation='relu'))
    model.add(Dropout(0.1))
    model.add(Dense(81, kernel_initializer='normal', activation='relu'))
    model.add(Dropout(0.1))
    model.add(Dense(1, kernel_initializer='normal'))

    learning_rate = 0.001
    momentum = 0.8
    sgd = SGD(lr=learning_rate, momentum= momentum, nesterov=False)
    model.compile(loss='mean_squared_error', optimizer=sgd)
    model.summary()
    return model

def select_move(model:Sequential, board_state:Board):
    move_scores = {}

    legal_moves = board_state.legal_moves(board_state.last_move)
    for move in legal_moves:
        clone = board_state.clone()
        clone.new_move(move)
        score = model.predict(np.array(clone.board_array).reshape(1,81))
        move_scores[move] = score 
    selected_move = max(move_scores, key=move_scores.get)
    new_board = board_state.clone()
    new_board.new_move(selected_move)
    return selected_move, new_board, move_scores[selected_move]

def unison_shuffled_copies(a, b):
    assert len(a) == len(b)
    p = np.random.permutation(len(a))
    return a[p], b[p]

def train_model(model: Sequential, print_progress: Boolean = False, random_agent: Boolean = False):
    if print_progress:
        print("\n\n----------------------------------------------------------")
        print("new game")
    
    rl_player_id = State.PLAYER_1 if random.randint(1,2) == 1 else State.PLAYER_2
    opponent_id = State.PLAYER_1 if rl_player_id == State.PLAYER_2 else State.PLAYER_2

    board = Board(represented_player=opponent_id)
    score_list = []
    new_board_states_list = []
    corrected_scores_list = []
    winner = None

    
    
    while(1):
        if board.current_player == rl_player_id:
            selected_move, cloned_board,score = select_move(model, board)
            score_list.append(score[0][0])
            new_board_states_list.append(cloned_board.board_array)
            board.new_move(selected_move)
            if print_progress:
                print(f"RL chose {selected_move}")
        elif(not random_agent):
            player_move = AI.determine_move(board, board.last_move, time=6) 

            board.new_move(player_move)
            if print_progress:
                print(f"Minimax chose: {player_move}")
        else:
            player_move = random.choice(board.legal_moves())
            board.new_move(player_move)
            if print_progress:
                print(f"Random Agent Chose: {player_move}")
        
        if(board.has_game_ended() != winner):
            winner = board.has_game_ended()
            board.print_board_pretty()
            break 
    
    #assign values to viewed states based on win/draw/loss
    new_board_states_list = tuple(new_board_states_list)
    new_board_states_list = np.vstack(new_board_states_list)

    if winner == rl_player_id:
        corrected_scores_list = shift(score_list, -1, cval=1.0)
        result = "Won"
    elif winner == opponent_id:
        corrected_scores_list = shift(score_list, -1, cval=-1.0)
        result = "Lost"
    else:
        corrected_scores_list = shift(score_list, -1, cval=0)
        result = "Draw"
    if print_progress:
        print(f"Program has {result}")
        print("Correcting the scores and updating model weights: ")
        print("----------------------------------------------------")
    x = new_board_states_list
    y = corrected_scores_list

    x,y = unison_shuffled_copies(x, y)
    x=x.reshape(-1, 81)
    model.fit(x,y,epochs=1,batch_size=1,verbose=0)
    return model,y,result




if __name__ == '__main__':
    if exists("rl_uttt_model.h5"):
        model = keras.models.load_model("rl_uttt_model.h5")
    else:
        model = generate_model()
    board = Board()
    print(select_move(model, board))
    wins = 0
    mode_selections = [True, False, True]
    wins_over_time = []
    easy_wins = 0
    hard_wins = 0
    for i in range(1000):
        random_agent = random.choice(mode_selections)
        updated_model,y,result = train_model(model, True, random_agent=random_agent)
        if result == "Won":
            wins += 1
            if(random_agent):
                easy_wins += 1
            else:
                hard_wins += 1
        if i % 50 == 0:
            wins_over_time.append([i, wins, easy_wins, hard_wins])

    print(f"\n\n {wins_over_time}")
    print(f"WINS: {wins/1000}\n\n")

    model.save("rl_uttt_model.h5")