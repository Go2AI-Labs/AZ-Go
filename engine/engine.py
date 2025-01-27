import os
import sys

import numpy as np

from definitions import ROOT_DIR
from go.go_game import GoGame, display
from mcts import MCTS
from neural_network.neural_net_wrapper import NNetWrapper
from utils.config_handler import ConfigHandler

MODEL = "Model W"
VERSION = "2.0"
PROTOCOL_VERSION = "1.0"

'''
Based on ROOT_DIR pathing, the command: python run_engine.py
can only be run from the root directory of this project (i.e. AZ-Go/).
The script build_engine.sh can be run from any directory.
'''
class Engine:

    def __init__(self):
        if is_frozen_state():
            path = os.path.join(sys._MEIPASS, "engine_config.yaml")
            self.config = ConfigHandler(path)
        else:
            self.config = ConfigHandler(f"{ROOT_DIR}/engine/engine_config.yaml")

        self.board_size = self.config['board_size']
        self.go_game = GoGame(self.board_size, is_arena_game=True)
        self.board = self.go_game.getInitBoard()
        self.x_boards, self.y_boards = self.go_game.init_x_y_boards()
        self.c_boards = [np.ones((7, 7)), np.zeros((7, 7))]
        self._set_player_board()
        self.canonicalBoard = self.go_game.getCanonicalForm(self.board, self.board.current_player)
        self.canonicalHistory = self.go_game.getCanonicalHistory(self.x_boards, self.y_boards, self.canonicalBoard,
                                                                 self.player_board)
        self.neural_net = NNetWrapper(self.go_game, self.config)

        if is_frozen_state():
            self.neural_net.load_checkpoint(f"{sys._MEIPASS}", 'best.pth.tar')
        else:
            self.neural_net.load_checkpoint(f"{ROOT_DIR}/engine/", 'best.pth.tar')

        self.mcts = MCTS(game=self.go_game, nnet=self.neural_net, is_self_play=False, config=self.config)

    # set the player_board tuple based on the current player
    def _set_player_board(self, player=None):
        if player is None:
            current_player = self.board.current_player
        else:
            current_player = player
        self.player_board = (self.c_boards[0], self.c_boards[1]) if current_player == 1 else (
            self.c_boards[1], self.c_boards[0])

    # run the command passed to the engine
    def run_command(self, command):
        if 'name' in command:
            print(f"= {self.name()}\n")
        elif 'protocol_version' in command:
            print(f'= {PROTOCOL_VERSION}\n')
        elif 'version' in command:
            print(f'= {VERSION}\n')
        elif 'list_commands' in command:
            print('= protocol_version\n')
        elif 'boardsize' in command:
            self.set_board_size(command)
            print('=\n')
        elif 'clear_board' in command:
            self.clear_board()
            print('=\n')
        elif 'showboard' in command:
            self.print_board()
        elif 'loadsgf' in command:
            self.loadsgf(command)
        elif 'play' in command:
            self.play(command)
            print('=\n')
        elif 'genmove' in command:
            # print('=', generate_move(BLACK if command.split()[-1] == 'B' else WHITE) + '\n')
            self.generate_move()
        elif 'getscore' in command:
            self.get_score()
        elif 'quit' in command:
            sys.exit()
        else:
            print('=\n')  # skip unsupported commands

    ## maybe this could be a command line argument for better compatibility with PyInstaller?
    # commands
    def name(self):
        return f"TCU Go2AI {MODEL}"

    # change the board size for the game
    def set_board_size(self, command):
        size = int(command.split()[-1])
        if size in [7]:
            self.go_game = GoGame(size, is_arena_game=True)
            self.board_size = size
            self.board = self.go_game.getInitBoard()
        else:
            print('? current board size not supported\n')

    # reset the board
    def clear_board(self):
        self.board = self.go_game.getInitBoard()

    def get_score(self):
        score = self.go_game.getScore(self.board)
        print(f"= {score}\n")

    # display the current board state
    def print_board(self):
        print('=')
        print(display(self.board))

    # execute a move given by a human or model, and update all data related to the game state
    def execute_move(self, action):
        # make move on board
        self.board = self.go_game.getNextState(self.board, action)
        # Update histories to prepare for next move
        self.canonicalBoard = self.go_game.getCanonicalForm(self.board, self.board.current_player)
        self._set_player_board()
        self.canonicalHistory, self.x_boards, self.y_boards = self.go_game.getCanonicalHistory(self.x_boards,
                                                                                               self.y_boards,
                                                                                               self.canonicalBoard,
                                                                                               self.player_board)
        # player will switch, so switch x and y boards (current/opposing player histories)
        self.x_boards, self.y_boards = self.y_boards, self.x_boards

    # play a move given by a human
    def play(self, command):
        # get the command arguments
        play_cmd_args = command.split(" ")
        # get the selected move
        move = play_cmd_args[2]
        # map the given move coordinates to the corresponding action number
        action = self._gtp_coordinate_to_action(coord=move)
        self.execute_move(action)

    # generate and play a move provided by the model
    def generate_move(self):
        # prepare necessary data structures for the move
        self.canonicalBoard = self.go_game.getCanonicalForm(self.board, self.board.current_player)
        self._set_player_board()
        # generate a move based on most recent board state
        action = np.argmax(
            self.mcts.getActionProb(self.board, self.canonicalBoard, self.canonicalHistory, self.x_boards,
                                    self.y_boards, self.player_board, self.config["num_full_search_sims"], temp=0))
        # perform the move
        self.execute_move(action)
        # print the GTP coordinate of the move
        coordinate = self._action_to_gtp_coordinate(action)
        print(f"= {coordinate}\n")

    # translate an action (int) to the corresponding GTP coordinate (str)
    def _action_to_gtp_coordinate(self, action):
        row = self.config["board_size"] - int(action / self.config["board_size"])
        col_coords = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
        col = col_coords[action % 7]
        coordinate = col + str(row)
        return coordinate

    # translate a GTP coordinate (str) to the corresponding action (int)
    def _gtp_coordinate_to_action(self, coord):
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's']
        if coord.lower() == "pass":
            action = int(self.config["board_size"]) ** 2
        else:
            try:
                col = letters.index(coord[0].lower())
            except ValueError as e:
                col = int(coord[0])
            try:
                row = letters.index(coord[1].lower())
            except ValueError as e:
                row = int(self.config["board_size"]) - int(coord[1])
            action = (row * 7) + col
        return action

    # initialize board state from an SGF file
    def loadsgf(self, command):
        # Get SGF file as text
        parsed_cmd = command.split(" ")
        filepath = parsed_cmd[1]
        with open(filepath) as f:
            temp = f.read()
        temp = temp.replace("(", "").replace(")", "")
        # Get a list of moves and puzzle answer from the SGF file
        sgf_info = temp.split(';')
        sgf_info = sgf_info[2:]
        moves = []
        ans = []
        for elt in sgf_info:
            if "C" in elt:
                finalElt = elt.split("C")
                elt = finalElt[0]
                raw_ans = finalElt[1].split(" ")[1]
                ans = raw_ans.split(",")
                ans[1] = ans[1].replace("]", "")
            parsed_move = elt.split("[")
            parsed_move[1] = parsed_move[1].replace("]", "")
            moves.append(parsed_move)
        # play all moves contained in the SGF file
        for m in moves:
            fake_cmd = "play " + m[0] + " " + m[1]
            print(f"MOVE :: {m} --- CMD :: {fake_cmd}")
            self.play(fake_cmd)


# to check for frozen environment when using utilities like Pyinstaller
def is_frozen_state():
    if getattr(sys, 'frozen', False):
        return True
    else:
        return False