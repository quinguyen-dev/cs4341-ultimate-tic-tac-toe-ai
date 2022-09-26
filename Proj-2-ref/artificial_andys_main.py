from player import Player
import time
import random

player = Player("artificialandys")
print(player.team_name)
while not player.check_end():
     if(player.check_for_turn()):
         print("My turn")
         opponent_move = player.get_move()
         print("sleep")
         time.sleep(2.5)
         print(player.check_time())
         player.make_move((opponent_move[1], random.randint(0,8)))