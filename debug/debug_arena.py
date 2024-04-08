import numpy as np

from definitions import CONFIG_PATH, CHECKPOINT_PATH
from mcts import MCTS
from neural_network.neural_net_wrapper import NNetWrapper
from utils.config_handler import ConfigHandler
from utils.data_serializer import ensure_defined_directories_exist
from go.go_game import GoGame
from training.arena_manager import ArenaManager

"""
Single thread debug script for arena
"""

if __name__ == "__main__":
    ensure_defined_directories_exist()

    config = ConfigHandler(CONFIG_PATH)

    game = GoGame(config["board_size"])

    # define players
    neural_network_one = NNetWrapper(game, config)
    neural_network_one.load_checkpoint(CHECKPOINT_PATH, 'best.pth.tar')
    mcts_one = MCTS(game, neural_network_one)

    player1 = lambda x, y, z, a, b, c, d: np.argmax(mcts_one.getActionProb(x, y, z, a, b, c, d, temp=0))

    arena = ArenaManager(player1, player1)

    arena.play_games(2)
