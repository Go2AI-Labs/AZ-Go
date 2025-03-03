"""
Wrapper class to handle KataGo lifecycle and requests.
"""
import json
import subprocess
import time
from threading import Thread
from typing import Dict

from logger.gtp_logger import GTPLogger


class KataGoWrapper:

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
        self.komi = 7
        self.rules = "chinese"
        self.board_size = 9

        self.logger = GTPLogger()

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

        # take a list of actions encoded as numbers (actions) and translate to col, row with player
        # assumes moves parameter is passed with the first move coming from black player
        formatted_moves = {}
        last_player = 'W'

        for (idx, move) in enumerate(moves):
            if last_player == 'B':
                last_player = 'W'
            elif last_player == 'W':
                last_player = 'B'

            action = self.logger.convert_action_to_katago(move)

            formatted_moves[idx] = [last_player, action]

        # Does not imply board history
        query["initialStones"] = [value for key, value in formatted_moves.items()]
        query["moves"] = []
        query["initialPlayer"] = "white"

        print(f"Query: {query}")

        return self._query_raw(query)

    def get_score(self, response):
        # returns score from the perspective of the black player
        # this can be changed in the config file defined by KATAGO_START_CMD
        return response['rootInfo']['scoreLead']

    def get_nth_best_move(self, response, n: int):
        return response['moveInfos'][n]

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
                try:
                    response = json.loads(line)
                    if "error" in response:
                        print(f"KataGo Error: {response['error']}")
                        raise Exception(f"KataGo Error: {response['error']}")
                    elif "rootInfo" not in response:
                        print("Waiting for a complete response from KataGo...")
                        time.sleep(0.1)  # Add a small delay to avoid busy waiting
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON response: {line}")
                    time.sleep(0.1)
                    continue

        # Make sure we have a complete response before returning
        return response

    def close(self):
        self.katago.stdin.close()
