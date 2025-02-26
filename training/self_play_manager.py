import random

import numpy as np

from definitions import CONFIG_PATH
from go.go_game import GoGame
from logger.gtp_logger import GTPLogger, GameType
from utils.config_handler import ConfigHandler


class SelfPlayManager:

    def __init__(self, neural_net, mcts):
        self.config = ConfigHandler(CONFIG_PATH)
        self.go_game = GoGame(self.config['board_size'])
        self.neural_net = neural_net
        self.mcts = mcts
        self.gtp_logger = GTPLogger()

    def execute_game(self):
        game_train_examples = []
        board = self.go_game.getInitBoard()
        turn_count = 0
        result = 0
        # For new MCTS
        c_boards = [np.ones((7, 7)), np.zeros((7, 7))]
        x_boards, y_boards = self.go_game.init_x_y_boards()

        while result == 0:
            turn_count += 1
            temp = int(turn_count < self.config["temperature_threshold"])
            # Code for old MCTS
            x_boards, y_boards = y_boards, x_boards

            # Code for old MCTS
            canonicalBoard = self.go_game.getCanonicalForm(board, board.current_player)
            player_board = (c_boards[0], c_boards[1]) if board.current_player == 1 else (c_boards[1], c_boards[0])
            canonicalHistory, x_boards, y_boards = self.go_game.getCanonicalHistory(x_boards, y_boards, canonicalBoard, player_board)

            num_sims = self.config["num_full_search_sims"]
            is_full_search = True

            pi = self.mcts.getActionProb(board, canonicalBoard, canonicalHistory, x_boards, y_boards, player_board, num_sims, temp=temp)

            # choose a move
            if temp == 1:
                action = np.random.choice(len(pi), p=pi)
            else:
                action = np.argmax(pi)

            self.gtp_logger.add_action(action, board)

            masked_pi = [0 for _ in range(self.go_game.getActionSize())]
            masked_pi[action] = 1

            # get different symmetries/rotations of the board if full search was done
            if is_full_search:
                canonical_history = board.get_canonical_history()
                sym = self.go_game.getSymmetries(canonical_history, masked_pi)
                for b, p in sym:
                    game_train_examples.append([b, board.current_player, p, None])

            # play the chosen move
            board = self.go_game.getNextState(board, action)
            result, score = self.go_game.getGameEndedSelfPlay(board.copy(), return_score=True, mcts=self.mcts)

        # save 10% of self play games
        if random.random() <= 0.10:
            self.gtp_logger.save_sgf(GameType.SELF_PLAY)
        else:
            self.gtp_logger.reset()
        
        # return game result
        return [(x[0], x[2], result * ((-1) ** (x[1] != board.current_player))) for x in game_train_examples]
