import os.path
import time
class Player:
    team_name = ""
    turn_start_time = None
    my_turn = False
    def __init__(self, n):
        self.team_name = n

    # Checks for players turn
    def check_for_turn(self):
        self.my_turn = os.path.exists(self.team_name + ".go")
        if self.my_turn:
            self.turn_start_time = time.perf_counter()
        return self.my_turn

    # check time since turn started
    def check_time(self):
        if self.turn_start_time is None:
            raise Exception("Not your turn")

        return time.perf_counter() - self.turn_start_time

    # Check for end game file
    def check_end(self):
        return os.path.exists("end_game")

    # Move is a tuple comtaining (i,j) i being the selected board j being a move within the board
    def make_move(self, move):
        if(self.my_turn):
            move_file = open("move_file", "w")
            move_file.write(self.team_name + " " + str(move[0]) + " " + str(move[1]))
            move_file.close()
            while os.path.exists(self.team_name + ".go"):
                time.sleep(.1)
            self.my_turn = False
            self.turn_start_time = None
        else:
            raise Exception("Not your turn")


    def get_move(self):
        if(self.my_turn):
            move = ""
            if os.path.getsize("move_file") > 0:
                move_file = open("move_file", "r")
                move = move_file.read()
                move_file.close()
            else:
                # Get last move from first_four_moves
                for line in open("first_four_moves"):
                    pass
                move = line
            print(move)
            # convert move to to tuple and return
            move_tuple = move.replace("\n", "").split(" ")[1:]
            return tuple(map(int, move_tuple))
        else:
            raise Exception("Not your turn")