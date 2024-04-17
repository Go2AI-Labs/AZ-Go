from enum import Enum

from definitions import CONFIG_PATH
from utils.config_handler import ConfigHandler
from datetime import datetime
from definitions import GAME_HISTORY_PATH


class GameType(Enum):
    SELF_PLAY = "Self Play"
    ARENA = "Arena"


class GTPLogger:

    def __init__(self):
        self.config = ConfigHandler(CONFIG_PATH)
        self.board_size = self.config["board_size"]
        self.action_history = []

    def save_sgf(self, game_type):
        now = datetime.now()
        dt_string = now.strftime("%m.%d.%Y_%H:%M:%S")

        file_name = GAME_HISTORY_PATH + f"/{game_type.value} at {dt_string}.sgf"

        sgf_file = open(file_name, 'a')
        sgf_file.write(
            f"(;\nEV[AlphaGo Zero Game Record]\nGN[]\nDT[{dt_string}]\nPB[TCU_AlphaGo]\nPW[TCU_AlphaGo]"
            f"\nSZ[{self.board_size}]\nRU["
            f"Tromp Taylor]\n\n")

        for action in self.action_history:
            sgf_file.write(action)

        sgf_file.write("\n)")
        sgf_file.close()

        self.reset()

    def convert_action_to_gtp(self, action):
        # supports up to 26 x 26 boards
        coords = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                  'u', 'v', 'w', 'x', 'y', 'z']

        if action == self.board_size ** 2:
            return f''

        # return column + row (in form: 'aa', 'df', 'cd', etc.)
        return f'{coords[int(action / self.board_size)]}' + f'{coords[int(action % self.board_size)]}'

    def add_action(self, action, board):
        player_name = "B" if board.current_player == 1 else "W"
        self.action_history.append(f";{player_name}[{self.convert_action_to_gtp(action)}]")

    def reset(self):
        self.action_history = []
