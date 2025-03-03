from datetime import datetime
from enum import Enum
from random import randint

from definitions import CONFIG_PATH
from definitions import GAME_HISTORY_PATH
from utils.config_handler import ConfigHandler


class GameType(Enum):
    SELF_PLAY = "Self Play"
    ARENA = "Arena"
    DEBUG = "Debug"


class PlayerType(Enum):
    PREVIOUS = "Previous_Model"
    CURRENT = "Current_Model"

    def __str__(self):
        return self.value


class GTPLogger:

    def __init__(self):
        self.config = ConfigHandler(CONFIG_PATH)
        self.board_size = self.config["board_size"]
        self.action_history = []
        self.player_black = "TCU_AlphaGo"
        self.player_white = "TCU_AlphaGo"

        self.coords = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                       't','u', 'v', 'w', 'x', 'y', 'z']

    def set_players(self, player_black, player_white):
        self.player_black = player_black
        self.player_white = player_white

    def save_sgf(self, game_type):
        now = datetime.now()
        dt_string = now.strftime("%m.%d.%Y_%H:%M:%S")

        file_name = GAME_HISTORY_PATH + f"/{game_type.value} at {dt_string}_{randint(1, 1000)}.sgf"
        print(file_name)

        sgf_file = open(file_name, 'a')
        sgf_file.write(
            f"(;\nEV[AlphaGo Zero Game Record]\nGN[]\nDT[{dt_string}]\nPB[{self.player_black}]\nPW[{self.player_white}]"
            f"\nSZ[{self.board_size}]\nRU["
            f"Tromp Taylor]\n\n")

        for action in self.action_history:
            sgf_file.write(action)

        sgf_file.write("\n)")
        sgf_file.close()

        self.reset()

    def convert_action_to_gtp(self, action):
        # supports up to 26 x 26 boards
        if action == self.board_size ** 2:
            return f''

        # return column + row (in form: 'aa', 'df', 'cd', etc.)
        return f'{self.coords[int(action % self.board_size)]}' + f'{self.coords[int(action / self.board_size)]}'


    # TODO: make sure board_size is set in config.
    def convert_gtp_to_action(self, gtp):
        # supports up to 26 x 26 boards
        if gtp == '' or gtp.lower() == 'pass':
            # if it's an empty string or 'pass', assume it's a pass
            return self.board_size ** 2

        col = self.coords.index(gtp[0])
        row = self.coords.index(gtp[1])

        # Return the corresponding action as an integer
        return row * self.board_size + col

    # Must skip I, refer to GTP Protocol for more info: http://www.lysator.liu.se/~gunnar/gtp/gtp2-spec-draft2/gtp2-spec.html#SECTION000311000000000000000
    def convert_action_to_katago(self, action):
        # takes action 0-49 and converts it to letter|number format for use with KataGo
        # supports up to 25 x 25 boards
        if action == self.board_size ** 2:
            return f'pass'

        # Calculate column and row indices
        col_idx = int(action % self.board_size)
        row_idx = int(action // self.board_size)

        # Convert column index to letter, skipping 'I'
        if col_idx < 8:  # A through H
            col_letter = chr(65 + col_idx)  # ASCII 'A' is 65
        else:  # J through T (and beyond if needed)
            col_letter = chr(65 + col_idx + 1)  # Skip 'I' by adding 1

        # Get row number (bottom to top)
        row_number = self.board_size - row_idx

        # Return column + row (in form: 'a1', 'd6', 'c4', etc.)
        return f'{col_letter}{row_number}'

    def add_action(self, action, board):
        player_name = "B" if board.current_player == 1 else "W"
        self.action_history.append(f";{player_name}[{self.convert_action_to_gtp(action)}]")

    def reset(self):
        self.action_history = []


def load_sgf(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Find all moves that start with 'B[' or 'W['
        moves = []
        i = 0
        while i < len(content):
            if content[i] == ';':
                i += 1
                # Check if the next character is 'B' or 'W'
                if i < len(content) and content[i] in ['B', 'W']:
                    i += 1  # Move past 'B' or 'W'
                    # Check for opening bracket
                    if i < len(content) and content[i] == '[':
                        i += 1  # Move past '['
                        # Extract the coordinates
                        move_start = i
                        # Find the closing bracket
                        while i < len(content) and content[i] != ']':
                            i += 1

                        if i < len(content) and content[i] == ']':
                            # Extract just the coordinates
                            coordinates = content[move_start:i]
                            moves.append(coordinates)
            i += 1

        return moves
    except Exception as e:
        print(f"Error reading SGF file: {e}")
        return []
