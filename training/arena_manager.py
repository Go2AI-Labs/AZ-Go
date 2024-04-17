from definitions import CONFIG_PATH
from go.go_game import GoGame
from logger.gtp_logger import GTPLogger, GameType
from utils.config_handler import ConfigHandler


class ArenaManager:

    def __init__(self, player1, player2, mcts1, mcts2):
        self.config = ConfigHandler(CONFIG_PATH)
        self.player1 = player1
        self.player2 = player2
        self.mcts1 = mcts1
        self.mcts2 = mcts2
        self.game = GoGame(self.config["board_size"])
        self.gtp_logger = GTPLogger()

    def play_games(self, num_games):
        threshold = num_games * (self.config['acceptance_threshold'])

        one_wins, two_wins, draws = 0, 0, 0

        for i in range(num_games):
            game_result = self.play_game()

            if (i % 2) == 0:
                if game_result == 1:
                    one_wins += 1
                elif game_result == -1:
                    two_wins += 1
                else:
                    draws += 1
            else:
                if game_result == -1:
                    one_wins += 1
                elif game_result == 1:
                    two_wins += 1
                else:
                    draws += 1

            # If one of the models meets the threshold for games won AND there is more than 1 game left to play,
            # return from arena play
            if one_wins >= threshold or two_wins >= threshold:
                return one_wins, two_wins, draws

            self.player1, self.player2 = self.player2, self.player1

        return one_wins, two_wins, draws

    def play_game(self):
        # print("Arena Game Started")
        self.game = GoGame(self.config["board_size"])
        board = self.game.getInitBoard()
        players = [self.player2, None, self.player1]

        self.clear_mcts()

        while self.game.getGameEndedArena(board) == 0:
            action = players[board.current_player + 1](board)
            self.gtp_logger.add_action(action, board)
            board = self.game.getNextState(board, action)

        self.gtp_logger.save_sgf(GameType.ARENA)
        return self.game.getGameEndedArena(board)

    def clear_mcts(self):
        if self.mcts1:
            self.mcts1.clear()
        if self.mcts2:
            self.mcts2.clear()
