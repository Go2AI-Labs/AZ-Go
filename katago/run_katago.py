import time

from katago.katago_parameters import KATAGO_START_CMD
from katago.katago_wrapper import KataGoWrapper
from logger.gtp_logger import GTPLogger, load_sgf

if __name__ == "__main__":
    gtp_logger = GTPLogger()

    katago = KataGoWrapper(KATAGO_START_CMD)

    time.sleep(10)

    # load sgf
    moves = load_sgf("sgf/figure_c_1.sgf")

    print(f"Moves: {moves}")

    # convert to array of moves useful to katago
    actions = []
    for move in moves:
        actions.append(gtp_logger.convert_gtp_to_action(move))

    print(f"Actions: {actions}")

    # print next best move according to KataGo
    query = katago.query(actions)
    print(f"Score: {katago.get_score(query)}, Next best move: {katago.get_nth_best_move(query, 0)}")

    katago.close()
