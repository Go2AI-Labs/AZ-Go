from definitions import CONFIG_PATH
from go.go_game import GoGame
from logger.gtp_logger import GameType, GTPLogger
from utils.config_handler import ConfigHandler

if __name__ == "__main__":
    config = ConfigHandler(CONFIG_PATH)
    go_game = GoGame(config['board_size'])
    gtp_logger = GTPLogger()

    game_train_examples = []
    board = go_game.getInitBoard()
    turn_count = 0
    result = 0

    game_0 = [0, 1, 2, 3, 4, 5, 6]
    game_1 = [18, 24, 25, 31, 32, 38, 39, 17, 11, 10, 4, 3, 46, 45]
    game_2 = [3, 2, 10, 9, 17, 16, 24, 23, 31, 30, 38, 37, 45, 44, 12, 22, 40, 21, 26, 49, 27, 49, 25, 49, 49]
    game_3 = [3, 11, 10, 9, 18, 16, 12, 23, 17, 2, 24, 30, 31, 37, 38, 46, 45, 44, 39, 47, 40, 48, 4, 41, 34, 22]
    game_4 = [17, 25, 24, 30, 31, 26, 18, 23, 19, 16, 33, 37, 38, 44, 45, 9, 10, 11, 3, 2]
    game_5 = [17, 25, 24, 30, 31, 33, 19, 23, 18, 39, 38, 37, 45, 47, 41, 26, 20, 27, 10, 16, 22, 15, 29, 9, 3, 2, 36, 44, 43, 14, 21, 35, 32, 46]
    game_6 = [17, 25, 24, 30, 31, 33, 19, 23, 18, 39, 38, 37, 45, 47, 41, 26, 20, 27, 29, 44, 36, 16, 10, 9, 3, 2, 22, 15, 43, 14, 21, 35, 32, 46, 40, 7, 34, 1, 48, 28, 49, 49]
    game_7 = [10, 16, 17, 23, 24, 30, 31, 37, 38, 44, 45, 9, 3, 2, 5, 47, 12, 33, 11, 19, 13, 20, 39, 40, 27, 25, 34, 18, 41, 32]

    game_1_transposed = [30, 24, 31, 25, 32, 26, 33, 23, 29, 22, 28, 21, 34, 27]
    game_2_transposed = [21, 14, 22, 15, 23, 16, 24, 17, 25, 18, 26, 19, 27, 20, 36, 10, 40, 3, 38, 49, 45, 49, 31, 49, 49]
    game_3_transposed = [21, 29, 22, 15, 30, 16, 36, 17, 23, 14, 24, 18, 25, 19, 26, 34, 27, 20, 33, 41, 40, 48, 28, 47, 46, 10]
    game_4_transposed = [23, 31, 24, 18, 25, 38, 30, 17, 37, 16, 39, 19, 26, 20, 27, 15, 22, 29, 21, 14]
    game_5_transposed = [23, 31, 24, 18, 25, 39, 37, 17, 30, 33, 26, 19, 27, 41, 47, 38, 44, 45, 22, 16, 10, 9, 11, 15, 21, 14, 12, 20, 13, 2, 3, 5, 32, 34]

    current_game = game_5_transposed

    print(f"Board Komi: {board.komi}\n")

    while turn_count < len(current_game):
        print(f"Turn Number: {turn_count + 1}")
        print(f"Player: {board.current_player}, Move: {current_game[turn_count]}")

        gtp_logger.add_action(current_game[turn_count], board)

        # play the chosen move
        board = go_game.getNextState(board, current_game[turn_count])

        score = go_game.getScore(board.copy())
        old_score_system = go_game.getScore_old_system(board.copy())

        print(f"Old / Chinese scoring :: Black Score: {old_score_system[0]}, White Score: {old_score_system[1]}")
        print(f"New / Tromp Taylor :: Black Score: {score[0]}, White Score: {score[1]}")
        print()

        turn_count += 1

    gtp_logger.save_sgf(GameType.DEBUG)
