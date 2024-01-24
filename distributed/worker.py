import os
from collections import deque
from datetime import datetime

import dill
from dill import Pickler

from training.coach import Coach
from go.go_game import GoGame as Game
from neural_network.neural_net_wrapper import NNetWrapper as nn
from utils.config_handler import ConfigHandler
from definitions import CONFIG_PATH, SENS_CONFIG_PATH, DIS_MODEL_PATH, DIS_EXAMPLE_PATH
from ssh_connector import SSHConnector

"""
The Worker class defines the behavior of a single worker thread used to generate training examples during the 
self play portion of the learning life cycle. Many worker threads can be created in start_worker.py
according to the parameter "num_parallel_games" defined in configs/config.yaml.
"""


class Worker:

    def __init__(self):
        self.config = ConfigHandler(CONFIG_PATH)
        self.sensitive_config = ConfigHandler(SENS_CONFIG_PATH)
        self.connector = SSHConnector()

    def play_game(self, game, nnet, config, identifier, iteration, disable_resignation_threshold):
        """
        Plays a single game through "Coach" (reference to training/coach.py) and saves the file locally.
        Returns file_name and file_path of the single saved game.
        """
        dill.settings['recurse'] = True
        Pickler.settings['recurse'] = True

        train_examples_history = []
        iteration_train_examples = deque([], maxlen=config["max_length_of_queue"])

        for eps in range(config["num_games_per_distributed_batch"]):
            coach = Coach(game, nnet, config)
            iteration_train_examples += coach.executeEpisode(iteration=iteration,
                                                             disable_resignation_threshold=disable_resignation_threshold)

        # save the generated train examples in their own file
        train_examples_history.append(iteration_train_examples)
        timestamp = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")

        file_name = (f'{self.sensitive_config["worker_machine_tag"]}_checkpoint_' + str(timestamp) + "_proc_" + str(
            identifier) + '.pth.tar')
        file_path = os.path.join(DIS_EXAMPLE_PATH, file_name)

        with open(file_path, "wb+") as f:
            Pickler(f).dump(train_examples_history)

        return file_name, file_path

    def start(self, identifier, iteration, disable_resignation_threshold):
        """
        Initializes a game object and loads the neural network located at DIS_MODEL_PATH/best.pth.tar
        (note DIS_MODEL_PATH is defined in definitions.py). Then, plays a single game using the play_game function.
        The results of the game are uploaded and subsequently deleted from the local machine.
        """
        game = Game(self.config["board_size"])
        neural_network = nn(game, self.config)

        # Load recent model into nnet
        neural_network.load_checkpoint(DIS_MODEL_PATH, 'best.pth.tar')

        print(f"Starting game on process: {identifier}")

        # Generate training examples
        file_name, file_path = self.play_game(game=game, nnet=neural_network, config=self.config, identifier=identifier,
                                              iteration=iteration,
                                              disable_resignation_threshold=disable_resignation_threshold)

        print(
            f"Game complete on process {identifier}. Sending examples to {self.sensitive_config['master_server_address']}")

        self.connector.upload_game(file_name, file_path)

        # delete file from the local machine
        os.remove(file_path)
