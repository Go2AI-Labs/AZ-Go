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

        while result == 0:
            turn_count += 1
            temp = int(turn_count < self.config["temperature_threshold"])
            # temp = 0

            # TODO: Is heuristic for full search sims vs fast sims acceptable?
            if random.random() <= 0.25:
                is_full_search = True
            else:
                is_full_search = False

            # print(f"Turn: {turn_count}, Temp: {temp}, is_full_search: {is_full_search}")

            pi = self.mcts.getActionProb(board, temp=temp, is_full_search=is_full_search)

            # TODO: Update temp to resemble the paper's implementation
            # choose a move
            if temp == 1:
                action = np.random.choice(len(pi), p=pi)
            else:
                action = np.argmax(pi)

            # print(f"Player: {board.current_player}, Move: {action}")

            # p, v = self.neural_net.predict(board.get_canonical_history())
            # print(f"NN move; {np.argmax(p)}")

            # # if passing, why?
            # if (action == 49):
            #     print(f"Pi: {pi}")

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
            # old_score_system = self.go_game.getScore_old_system(board.copy())

            # print(f"Old scoring :: Black Score: {old_score_system[0]}, White Score: {old_score_system[1]}")
            # print(f"Tromp Taylor :: Black Score: {score[0]}, White Score: {score[1]}")
            # print()

        # save 10% of self play games
        if random.random() <= 0.10:
            self.gtp_logger.save_sgf(GameType.SELF_PLAY)
        else:
            self.gtp_logger.reset()

        # self.gtp_logger.save_sgf(GameType.SELF_PLAY)

        # return game result
        return [(x[0], x[2], result * ((-1) ** (x[1] != board.current_player))) for x in game_train_examples]
