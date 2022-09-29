from player import Player
import time
import random

time_limit = 10
player = Player("bot")
print(player.team_name)
while not player.check_end():
     if(player.check_for_turn()):
         print("My turn")
         opponent_move = player.get_move()
         time.sleep(3)
         print(player.check_time())
         player.make_move((opponent_move[1],random.randint(0,8)))