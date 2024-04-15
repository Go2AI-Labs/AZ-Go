import numpy as np

from definitions import CONFIG_PATH, CHECKPOINT_PATH
from distributed.worker import Worker
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
    worker = Worker()
    worker.handle_arena_lifecycle()
