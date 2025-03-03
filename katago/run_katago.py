import time
from katago.katago_parameters import KATAGO_START_CMD
from katago.katago_wrapper import KataGoWrapper
from logger.gtp_logger import GTPLogger, load_sgf

if __name__ == "__main__":
    gtp_logger = GTPLogger()
    katago = KataGoWrapper(KATAGO_START_CMD)
    try:
        time.sleep(10)  # Give KataGo time to initialize

        # load sgf
        moves = load_sgf("sgf/figure_c_1.sgf")
        print(f"Moves: {moves}")

        # convert to array of moves useful to katago
        actions = []
        for move in moves:
            actions.append(gtp_logger.convert_gtp_to_action(move))
        print(f"Actions: {actions}")

        # Submit query and wait for complete response
        query_result = katago.query(actions)

        # Only proceed if we have a valid response
        if query_result and "rootInfo" in query_result:
            score = katago.get_score(query_result)
            best_move = katago.get_nth_best_move(query_result, 0)
            print(f"Score: {score}, Next best move: {best_move}")
        else:
            print("Failed to get a valid response from KataGo")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Always close KataGo properly
        katago.close()
