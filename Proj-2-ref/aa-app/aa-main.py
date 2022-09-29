from player import Player
from Board import Board
from time import sleep
from threading import Thread
from ai import AI
from utility import State

def main():
    player = Player("artificial_andys")
    board = Board(State.PLAYER_1)

    print(f'[Initialized player]: {player.team_name}')           

    while not player.check_end():                   
        if player.check_for_turn():  # Sets the beginning time
            opponent_move = player.read_move(board)
            player_move = AI.determine_move(board, opponent_move) 
            # player.make_move(player_move)
            break
            

if __name__ == '__main__':
    main()