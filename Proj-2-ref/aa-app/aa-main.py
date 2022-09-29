import time
import random
from player import Player
from Board import Board

def main():
    player = Player("artificial_andys")
    board = Board()

    print(f'[Initialized player]: {player.team_name}')

    while not player.check_end():                                     
        if player.check_for_turn():                                  
            print("============== My turn ==============")            
            opponent_move = player.read_move(board)                         # Get the opponents last move

            # update opponents move here

            print(" ============== Sleep ==============")
            time.sleep(2.5)

            pass # Make the move here
            
            print(player.check_time())
            # player.make_move((opponent_move[1], random.randint(0,8))) # This will be the tuple that we generate


if __name__ == '__main__':
    main()