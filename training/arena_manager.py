import numpy as np

from definitions import CONFIG_PATH
from go.go_game import GoGame
from utils.config_handler import ConfigHandler


class ArenaManager:

    def __init__(self, player1, player2):
        self.config = ConfigHandler(CONFIG_PATH)
        self.player1 = player1
        self.player2 = player2
        self.game = GoGame(self.config["board_size"])

    def play_games(self, num_games):
        threshold = num_games * (self.config['acceptance_threshold'])

        one_wins, two_wins, draws = 0, 0, 0

        for i in range(num_games):
            game_result = self.play_game()
            print(game_result)

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
            if (one_wins >= threshold or two_wins >= threshold):
                print(
                    f"\nEnded after {i + 1} games\nOne Won: {one_wins} || Two Won: {two_wins} || One %: {one_wins / self.config['acceptance_threshold']} || Two %: {two_wins / self.config['acceptance_threshold']}")
                return one_wins, two_wins, draws

            self.player1, self.player2 = self.player2, self.player1

        print(f"One Wins: {one_wins}, Two Wins: {two_wins}, Draws: {draws}")
        return one_wins, two_wins, draws

    def play_game(self):
        print("Play Game Started")
        players = [self.player2, None, self.player1]
        cur_player = 1
        board = self.game.getInitBoard()
        x_boards, y_boards, c_boards = [], [], [np.ones((7, 7)), np.zeros((7, 7))]
        action_history = []

        for i in range(8):
            x_boards.append(np.zeros((self.config["board_size"], self.config["board_size"])))
            y_boards.append(np.zeros((self.config["board_size"], self.config["board_size"])))

        while self.game.getGameEndedArena(board, cur_player) == 0:
            canonical_board = self.game.getCanonicalForm(board, cur_player)
            player_board = (c_boards[0], c_boards[1]) if cur_player == 1 else (c_boards[1], c_boards[0])
            canonical_history, x_boards, y_boards = self.game.getCanonicalHistory(x_boards, y_boards,
                                                                                  canonical_board, player_board)

            action = players[cur_player + 1](canonical_board, canonical_history, x_boards, y_boards, player_board, False,
                                            self.config["num_full_search_sims"])
            player_name = "B" if cur_player == 1 else "W"
            action_history.append(f";{player_name}[{self.game.action_space_to_GTP(action)}]")
            print(action_history)

            board, cur_player = self.game.getNextState(board, cur_player, action)
            x_boards, y_boards = y_boards, x_boards

        return self.game.getGameEndedArena(board, 1)
