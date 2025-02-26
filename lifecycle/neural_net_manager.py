from definitions import CONFIG_PATH, CHECKPOINT_PATH, EXAMPLES_PATH
from go.go_game import GoGame
from neural_network.neural_net_wrapper import NNetWrapper as NNetWrapper
from utils.config_handler import ConfigHandler


class NeuralNetManager:

    def __init__(self):
        self.config = ConfigHandler(CONFIG_PATH)
        self.go_game = GoGame(self.config["board_size"])

        # neural networks
        self.current_net = NNetWrapper(self.go_game, self.config)

        if self.config["load_model"]:
            self.current_net.load_checkpoint(f"{EXAMPLES_PATH}", 'best.pth.tar')
            print("Loaded checkpoint model")

        # previous best network, init to None
        self.previous_net = None

        # MCTS complete objects
        self.current_mcts = None
        self.previous_mcts = None

    def prepare_neural_net_for_training(self):
        # shallow copy
        self.previous_net = self.current_net
        self.save_previous_network_to_disk()
        # deep copy from disk
        self.load_previous_net_from_disk()

    def save_previous_network_to_disk(self):
        """
        Dumps previous model to disk with name "previous_net.pth.tar" at path config["checkpoint_directory"]
        """

        self.current_net.save_checkpoint(folder=CHECKPOINT_PATH, filename='previous_net.pth.tar')

    def save_current_network_to_disk(self):
        """
        Dumps current model to disk with name "current_net.pth.tar" at path config["checkpoint_directory"]
        """
        self.current_net.save_checkpoint(folder=CHECKPOINT_PATH, filename='current_net.pth.tar')

    def save_best_network_to_disk(self, iteration_num):
        """
        Dumps current model to disk as new best model with name "best.pth.tar" at path config["checkpoint_directory"]
        Also, save newly accepted model as checkpoint model for logging purposes
        """
        self.current_net.save_checkpoint(folder=CHECKPOINT_PATH, filename='best.pth.tar')
        self.current_net.save_checkpoint(folder=CHECKPOINT_PATH,
                                         filename=f'checkpoint_{iteration_num}.pth.tar')

    def load_previous_net_from_disk(self):
        """
        Sets the self.previous_net variable from the "temp.pth.tar" file at path config["checkpoint_directory"]
        """
        self.previous_net.load_checkpoint(folder=CHECKPOINT_PATH, filename='previous_net.pth.tar')

    def load_best_net_from_disk(self):
        """
        Sets the self.current_net variable from the "best.pth.tar" file at path config["checkpoint_directory"]
        """
        self.current_net.load_checkpoint(folder=CHECKPOINT_PATH, filename='best.pth.tar')

    def train_current_model(self, train_examples):
        """
        Trains current model with provided train examples and returns loss values generated during training
        """
        # TODO save_checkpoint from NNetWrapper will create logs directory in the wrong spot when called here
        return self.current_net.train(train_examples)

    def update_best_model_if_needed(self, should_accept_current_model, lifecycle_metadata):
        if should_accept_current_model:
            # save checkpoint file && save best.pth.tar file
            self.save_best_network_to_disk(lifecycle_metadata.iteration_num)
        else:
            print("Model rejected, load previous best model")

        # set current model for next iteration
        self.load_best_net_from_disk()
