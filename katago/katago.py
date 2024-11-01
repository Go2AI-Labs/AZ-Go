"""
Wrapper class to handle KataGo lifecycle and requests.
"""
import json
import subprocess
import time
from threading import Thread
from typing import Tuple, List, Union, Literal, Dict
from logger.gtp_logger import GTPLogger
from threading import Thread

from katago_parameters import KATAGO_START_CMD


class KataGo:

    # initialization for KataGo will start a new KataGo instance - not a singleton
    def __init__(self, cmd):
        self.query_counter = 0

        self.katago = subprocess.Popen(
            cmd.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Go game parameters
        self.komi = 0
        self.rules = "tromp-taylor"
        self.board_size = 7

        self.stderr_thread = Thread(target=self._monitor_stderr)
        self.stderr_thread.start()

    def _monitor_stderr(self):
        while self.katago.poll() is None:
            data = self.katago.stderr.readline()
            time.sleep(0)
            if data:
                print("KataGo: ", data.decode(), end="")
        data = self.katago.stderr.read()
        if data:
            print("KataGo: ", data.decode(), end="")

    def query(self, moves):
        query = {
            "id": str(self.query_counter),
            "rules": self.rules,
            "komi": self.komi,
            "boardXSize": self.board_size,
            "boardYSize": self.board_size
        }

        # take a list of actions encoded as numbers and translate to col, row with player
        # assumes moves parameter is passed with the first move coming from black player
        formatted_moves = {}
        last_player = 'W'

        for (idx, move) in enumerate(moves):
            if last_player == 'B':
                last_player = 'W'
            elif last_player == 'W':
                last_player = 'B'

            action = gtp_logger.convert_action_to_katago(move)

            formatted_moves[idx] = [last_player, action]

        query["moves"] = [value for key, value in formatted_moves.items()]

        return self._query_raw(query)

    def get_score(self, response):
        # returns score from the perspective of the black player
        # this can be changed in the config file defined by KATAGO_START_CMD
        return response['rootInfo']['scoreLead']

    def get_nth_best_move(self, response, n: int):
        return response['moveInfos'][n]['move']

    # sends query to subprocess
    def _query_raw(self, query: Dict[str, any]):
        self.katago.stdin.write((json.dumps(query) + "\n").encode())
        self.katago.stdin.flush()

        response = None
        while response is None or "rootInfo" not in response:
            if self.katago.poll() is not None:
                raise Exception("KataGo has exited unexpectedly")

            line = self.katago.stdout.readline().decode().strip()

            # Check if a response has been received
            if line:
                response = json.loads(line)
                if "error" in response:
                    print(f"KataGo Error: {response['error']}")
                    return None
                elif "rootInfo" not in response:
                    print("Waiting for a complete response from KataGo...")
                    time.sleep(0.1)  # Add a small delay to avoid busy waiting

        return response

    def close(self):
        self.katago.stdin.close()


if __name__ == "__main__":
    gtp_logger = GTPLogger()

    katago = KataGo(KATAGO_START_CMD)

    time.sleep(10)

    game_1 = [18, 24, 25, 31, 32, 38, 39, 17, 11, 10, 4, 3, 46, 45]
    game_2 = [3, 2, 10, 9, 17, 16, 24, 23, 31, 30, 38, 37, 45, 44, 12, 22, 40, 21, 26, 49, 27, 49, 25, 49, 49]
    game_3 = [3, 11, 10, 9, 18, 16, 12, 23, 17, 2, 24, 30, 31, 37, 38, 46, 45, 44, 39, 47, 40, 48, 4, 41, 34, 22]
    game_4 = [17, 25, 24, 30, 31, 26, 18, 23, 19, 16, 33, 37, 38, 44, 45, 9, 10, 11, 3, 2]
    game_5 = [17, 25, 24, 30, 31, 33, 19, 23, 18, 39, 38, 37, 45, 47, 41, 26, 20, 27, 10, 16, 22, 15, 29, 9, 3, 2, 36,
              44, 43, 14, 21, 35, 32, 46]
    game_6 = [17, 25, 24, 30, 31, 33, 19, 23, 18, 39, 38, 37, 45, 47, 41, 26, 20, 27, 29, 44, 36, 16, 10, 9, 3, 2, 22,
              15, 43, 14, 21, 35, 32, 46, 40, 7, 34, 1, 48, 28, 49, 49]
    game_7 = [10, 16, 17, 23, 24, 30, 31, 37, 38, 44, 45, 9, 3, 2, 5, 47, 12, 33, 11, 19, 13, 20, 39, 40, 27, 25, 34,
              18, 41, 32]

    print()

    # single threaded -> much slower

    game_1_response = katago.query(game_1)
    print(f"Game 1 | Score: {katago.get_score(game_1_response)}, Next best move: {katago.get_nth_best_move(game_1_response, 0)}")

    game_2_response = katago.query(game_2)
    print(
        f"Game 2 | Score: {katago.get_score(game_2_response)}, Next best move: {katago.get_nth_best_move(game_2_response, 0)}")

    game_3_response = katago.query(game_3)
    print(
        f"Game 3 | Score: {katago.get_score(game_3_response)}, Next best move: {katago.get_nth_best_move(game_3_response, 0)}")

    game_4_response = katago.query(game_4)
    print(f"Game 4 |  Score: {katago.get_score(game_4_response)}, Next best move: {katago.get_nth_best_move(game_4_response, 0)}")

    game_5_response = katago.query(game_5)
    print(
        f"Game 5 | Score: {katago.get_score(game_5_response)}, Next best move: {katago.get_nth_best_move(game_5_response, 0)}")

    game_6_response = katago.query(game_6)
    print(
        f"Game 6 | Score: {katago.get_score(game_6_response)}, Next best move: {katago.get_nth_best_move(game_6_response, 0)}")

    game_7_response = katago.query(game_7)
    print(
        f"Game 7 | Score: {katago.get_score(game_7_response)}, Next best move: {katago.get_nth_best_move(game_7_response, 0)}")

    print()

    def query_game(katago, game_moves, game_title):
        response = katago.query(game_moves)
        time.sleep(0)
        print(f"{game_title} | Score: {katago.get_score(response)}, Next best move: {katago.get_nth_best_move(response, 0)}")


    # multi-threaded -> much faster
    game_threads = []
    for idx, game in enumerate([game_1, game_2, game_3, game_4, game_5, game_6, game_7]):
        game_thread = Thread(target=query_game, args=(katago, game, f"Game {idx + 1}"))
        game_threads.append(game_thread)
        game_thread.start()
        game_thread.join()  # Ensures each game completes before starting the next

    print()

    katago.close()