import numpy as np

from definitions import CONFIG_PATH, CHECKPOINT_PATH
from go.go_game import GoGame
from mcts_dis import MCTSDis
from neural_network.neural_net_wrapper import NNetWrapper
from training.arena_manager import ArenaManager
from utils.config_handler import ConfigHandler
from utils.data_serializer import ensure_defined_directories_exist

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
    # mcts_one = MCTS(game, neural_network_one)
    mcts_one = MCTSDis(game, neural_network_one)

    neural_network_two = NNetWrapper(game, config)
    neural_network_two.load_checkpoint(CHECKPOINT_PATH, 'best.pth.tar')
    # mcts_one = MCTS(game, neural_network_one)
    mcts_two = MCTSDis(game, neural_network_two)

    player1 = lambda x: np.argmax(mcts_one.getActionProb(x, temp=0))
    player2 = lambda x: np.argmax(mcts_two.getActionProb(x, temp=0))

    arena = ArenaManager(player1, player1, mcts_one, mcts_two)

    arena.play_games(2)
