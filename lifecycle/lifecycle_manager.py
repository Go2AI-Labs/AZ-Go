import glob
import time

from definitions import DIS_SELF_PLAY_PATH, CONFIG_PATH, DIS_ARENA_PATH
from utils.config_handler import ConfigHandler
from utils.data_serializer import load_json_from_disk

"""
This class basically handles the life cycle of self play and arena from the server side
"""


# TODO Add counter variable for number of games played
class LifecycleManager:

    def __init__(self, train_example_manager):
        self.config = ConfigHandler(CONFIG_PATH)
        self.train_example_manager = train_example_manager

        # TODO: Make this an entry in config.yaml
        # scanning parameters for both self_play and arena
        self.time_between_directory_checks = 15  # in seconds, do not set less than x seconds

        # self play parameters
        self.completed_games_self_play = 0
        self.is_complete_self_play = False

        # arena play parameters
        self.completed_games_arena = 0
        self.is_complete_arena = False
        self.current_model_wins = 0
        self.previous_model_wins = 0
        self.model_ties = 0

    def execute_self_play(self):
        while not self.is_complete_self_play:
            self.scan_self_play()
            print(f"Number of train examples: {len(self.train_example_manager.train_examples)}/"
                  f"{self.config['max_length_of_queue']}")
            # print()
            # avoid an extra sleep when breaking out of scan_self_play on completion
            if not self.is_complete_self_play:
                time.sleep(self.time_between_directory_checks)

    def scan_self_play(self):
        """
        Scans directory DIS_SELF_PLAY_PATH for self-play training examples until parameter "limit" is reached
        or until all files are read.
        """
        files = glob.glob(DIS_SELF_PLAY_PATH + "*")
        for file in files:
            if len(self.train_example_manager.train_examples) >= self.config["max_length_of_queue"]:
                self.is_complete_self_play = True
                break

            # load in the file
            self.train_example_manager.append_train_examples(file)

    def reset_self_play(self):
        """
        Resets relevant parameters for next iteration of self play
        """
        self.is_complete_self_play = False

    def execute_arena_play(self):
        while not self.is_complete_arena:
            self.scan_arena()
            print(f"Number of arena games played: {self.completed_games_arena}")
            # print()
            # avoid an extra sleep when breaking out of scan_self_play on completion
            if not self.is_complete_arena:
                time.sleep(self.time_between_directory_checks)

    def scan_arena(self):
        """
        Scans directory DIS_ARENA_PATH for arena training outcomes until parameter "num_arena_episodes" is reached
        or until all files are read.
        Return value from load_json_from_disk is:
            current_wins: integer
            previous_wins: integer
            ties: integer
            games_played: integer
        """
        files = glob.glob(DIS_ARENA_PATH + "*")
        for file in files:
            print(file)
            if self.completed_games_arena >= self.config["num_arena_episodes"]:
                self.is_complete_arena = True
                break

            # do something with files
            outcomes = load_json_from_disk(file)
            print(f"outcomes: {outcomes}")
            print(f"current_wins: {outcomes['current_wins']}")
            self.current_model_wins += outcomes["current_wins"]
            self.previous_model_wins += outcomes["previous_wins"]
            self.model_ties += outcomes["ties"]
            self.completed_games_arena += outcomes["games_played"]

    def handle_arena_outcome(self):
        """
        Determine whether to accept or reject the current model in favor of the previous model.
        Return True if current model is better than previous model, return False if current model worse than previous


        If accepting current model as best, save it as "best.pth.tar",
        else if rejecting current model, load previous best.pth.tar into current model
        """

        winrate = self.current_model_wins / self.completed_games_arena
        if winrate >= self.config["acceptance_threshold"]:
            print("ACCEPTING NEW MODEL")
            return True
        else:
            print("REJECTING NEW MODEL")
            return False

    def reset_arena_play(self):
        """
        Resets relevant parameters for next iteration of arena play
        """
        self.completed_games_arena = 0
        self.is_complete_arena = False
        self.current_model_wins = 0
        self.previous_model_wins = 0
        self.model_ties = 0
