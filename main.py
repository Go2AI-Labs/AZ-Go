import os
import sys

from go.go_game import GoGame as Game
from neural_network.neural_net_wrapper import NNetWrapper as NNetWrapper
from training.coach import Coach
from utils.config_handler import ConfigHandler
from definitions import CONFIG_PATH

sys.setrecursionlimit(5000)

# TODO: MARKED FOR DELETION, replaced by start_main.py

if __name__ == "__main__":

    config = ConfigHandler(CONFIG_PATH)

    # create logs subdirectories
    if not os.path.exists(config["checkpoint_directory"]):
        os.makedirs(config["checkpoint_directory"])
    if not os.path.exists(config["game_history_directory"]):
        os.makedirs(config["game_history_directory"])
    if not os.path.exists(config["graph_directory"]):
        os.makedirs(config["graph_directory"])
    if not os.path.exists(config["train_logs_directory"]):
        os.makedirs(config["train_logs_directory"])

    game = Game(config["board_size"])
    neural_network = NNetWrapper(game, config)

    if config["load_model"]:
        # if you are loading a checkpoint created from a model without DataParallel
        # use the load_checkpoint_from_plain_to_parallel() function
        # instead of the load_checkpoint() function
        neural_network.load_checkpoint(config["checkpoint_directory"], 'best.pth.tar')

    c = Coach(game, neural_network, config)

    if config["load_model"]:
        c.skipFirstSelfPlay = True

    c.learn()
