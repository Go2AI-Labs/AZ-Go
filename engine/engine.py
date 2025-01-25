import sys
import os
from definitions import CONFIG_PATH, CHECKPOINT_PATH
from go.go_game import GoGame, display
from mcts import MCTS
from neural_network.neural_net_wrapper import NNetWrapper
from utils.config_handler import ConfigHandler
import numpy as np

MODEL = "Model W"
VERSION = "2.0"
PROTOCOL_VERSION = "1.0"

class Engine:

    def __init__(self):
        self.config = ConfigHandler(CONFIG_PATH)
        self.board_size = self.config['board_size']
        self.go_game = GoGame(self.board_size, is_arena_game=True)
        self.board = self.go_game.getInitBoard()
        self.x_boards, self.y_boards = self.go_game.init_x_y_boards()
        self.c_boards = [np.ones((7, 7)), np.zeros((7, 7))]
        self._set_player_board()
        self.canonicalBoard = self.go_game.getCanonicalForm(self.board, self.board.current_player)
        self.canonicalHistory = self.go_game.getCanonicalHistory(self.x_boards, self.y_boards, self.canonicalBoard, self.player_board)
        self.neural_net = NNetWrapper(self.go_game, self.config)
        # self.neural_net.load_checkpoint(CHECKPOINT_PATH, 'best.pth.tar')
        self.neural_net.load_checkpoint(f"{os.getcwd()}/model_weights/", 'best.pth.tar')
        self.mcts = MCTS(game=self.go_game, nnet=self.neural_net, is_self_play=False)


    # set the player_board tuple based on the current player
    def _set_player_board(self, player=None):
        if player is None:
            current_player = self.board.current_player
        else:
            current_player = player
        self.player_board = (self.c_boards[0], self.c_boards[1]) if current_player == 1 else (self.c_boards[1], self.c_boards[0])


    # run the command passed to the engine
    def run_command(self, command):
        if 'name' in command:
            print(self.name())
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
        self.canonicalHistory, self.x_boards, self.y_boards = self.go_game.getCanonicalHistory(self.x_boards, self.y_boards, self.canonicalBoard, self.player_board)
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
        action = np.argmax(self.mcts.getActionProb(self.board, self.canonicalBoard, self.canonicalHistory, self.x_boards, self.y_boards, self.player_board, self.config["num_full_search_sims"], temp=0))
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
        if coord == "pass" or coord == "PASS":
            action = self.config["board_size"] * self.config["board_size"]
        else: 
            col = ord(coord[0]) - ord('A') + 1 - (1 if ord(coord[0]) > ord('I') else 0)
            row_count = int(coord[1:]) if len(coord[1:]) > 1 else ord(coord[1:]) - ord('0')
            action = ((self.config["board_size"] - row_count) * self.config["board_size"]) + (col - 1)
        return action
