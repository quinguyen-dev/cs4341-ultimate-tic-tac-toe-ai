from locale import strcoll
import os.path
import time
from Board import Board

class Player:

    team_name = ""
    turn_start_time = None
    my_turn = False

    def __init__(self, team_name):
        self.team_name = team_name


    def check_for_turn(self):
        """ Check if the '[team_name].go' file exist to determine turn.

        Returns:
            bool: True if a '[team_name].go' file exist. False is not.
        """
        self.my_turn = os.path.exists(f'../{self.team_name}.go')
        if self.my_turn:
            self.turn_start_time = time.perf_counter()

        return self.my_turn


    def check_time(self):
        """ Check time since the turn has started.

        Raises:
            Exception: If it is not the player's turn.

        Returns:
            _type_: _description_
        """
        if self.turn_start_time is None:
            raise Exception("Not your turn")

        return time.perf_counter() - self.turn_start_time


    def check_end(self):
        """ Checks for the 'end_game' file.

        Returns:
            bool: True if 'end_game' exist in the directory.
        """
        return os.path.exists("../end_game")


    def make_move(self, move):
        """ Makes a move on the board.

        Args:
            move (tuple): (i, j) where i is being the selected board and j is the local location.

        Raises:
            Exception: If it is not the player's turn.
        """
        if self.my_turn:
            move_file = open("../move_file", "w")
            move_file.write(self.team_name + " " + str(move[0]) + " " + str(move[1]))
            move_file.close()

            while os.path.exists(f'../{self.team_name}.go'):
                time.sleep(.1)

            self.my_turn = False
            self.turn_start_time = None
        else:
            raise Exception("Not your turn")


    def read_move(self, board: Board | None):
        """ Get either the first four moves or the opponents move.

        Raises:
            Exception: If it is not the player's turn.

        Returns:
            tuple: _description_
        """
        if self.my_turn:
            move = ""
            if os.path.getsize("../move_file") > 0:
                move_file = open("../move_file", "r")
                move = move_file.read()
                move_file.close()
            else:
                for line in open("../first_four_moves"):
                    board.new_move(Player.parse_move(line))
                move = line

            print(move)

            move_tuple = Player.parse_move(move)
            return move_tuple
        else:
            raise Exception("Not your turn") 


    @staticmethod
    def parse_move(move: str):
        parsed = move.replace("\n", "").split(" ")[1:]

        return tuple(map(int, parsed))