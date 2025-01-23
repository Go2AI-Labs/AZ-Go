from definitions import CONFIG_PATH, CHECKPOINT_PATH
from go.go_game import GoGame
from mcts import MCTS
from neural_network.neural_net_wrapper import NNetWrapper
from utils.config_handler import ConfigHandler

MODEL = "Model W"
VERSION = "2.0"
PROTOCOL_VERSION = "1.0"

class Engine:

    def __init__(self):
        self.config = ConfigHandler(CONFIG_PATH)
        self.go_game = GoGame(self.config['board_size'])
        self.neural_net = NNetWrapper(self.go_game, self.config)
        self.neural_net.load_checkpoint(CHECKPOINT_PATH, 'best.pth.tar')
        self.mcts = MCTS(game=self.go_game, nnet=self.neural_net, is_self_play=True)

    ## maybe this could be a command line argument for better compatibility with PyInstaller?
    # commands
    def name(self):
        return f"TCU Go2AI {MODEL}"