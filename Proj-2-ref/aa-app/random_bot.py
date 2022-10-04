from random import random
from player import Player
from Board import Board
from time import sleep
from threading import Thread
from ai import AI
from utility import State
import random

def main():
    player = Player("bot")
    board = Board() 

    print(f'[Initialized player]: {player.team_name}')           

    while not player.check_end():  
        player.read_first_four(board)  
              
        if player.check_for_turn():  
            player.read_move(board)

            opponent_move = player.last_move
            print(player.last_move)
            
            player_move = random.choice(board.legal_moves(opponent_move))
            sleep(0.5)
            
            board.new_move(player_move)
            player.make_move(player_move)
            
            print("\n=============================")

if __name__ == '__main__':
    main()