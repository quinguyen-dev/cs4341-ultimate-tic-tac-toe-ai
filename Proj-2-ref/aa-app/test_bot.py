from player import Player
from Board import Board
from ai import AI
import time

def main():
    player = Player("bot")
    board = Board()
    ai = AI()

    print(f'[Initialized player]: {player.team_name}')           

    while not player.check_end():  
        player.read_first_four(board)  
              
        if player.check_for_turn():
            start = time.perf_counter()

            player.read_move(board)

            opponent_move = player.last_move
            player_move = AI.determine_move(board, opponent_move) 

            board.new_move(player_move)
            player.make_move(player_move)

            print(f'Time: {time.perf_counter()  -start:0.04f}')

if __name__ == '__main__':
    main()