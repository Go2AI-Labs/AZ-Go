import multiprocessing as mp
import os
import time
from collections import deque
from datetime import datetime

import dill
import paramiko
import yaml
from dill import Pickler
from scp import SCPClient

from coach import Coach
from go.go_game import GoGame as Game
from neural_network.neural_net_wrapper import NNetWrapper as nn
from utils.config_handler import ConfigHandler


class DistributedWorker:

    def __init__(self):
        self.config = ConfigHandler("config.yaml")
        self.sensitive_config = ConfigHandler("sensitive.yaml")

    def learn(self, game, nnet, config, identifier, iteration, disable_resignation_threshold):
        """
        Performs numIters iterations with numEps episodes of self-play in each
        iteration. After every iteration, it retrains neural network with
        examples in trainExamples (which has a maximum length of maxlenofQueue).
        It then pits the new neural network against the old one and accepts it
        only if it wins >= updateThreshold fraction of games.
        """
        dill.settings['recurse'] = True
        Pickler.settings['recurse'] = True

        trainExamplesHistory = []
        iterationTrainExamples = deque([], maxlen=config["max_length_of_queue"])

        for eps in range(config["num_games_per_distributed_batch"]):
            coach = Coach(game, nnet, config)
            iterationTrainExamples += coach.executeEpisode(iteration=iteration,
                                                           disable_resignation_threshold=disable_resignation_threshold)

        # save the generated train examples in their own file
        trainExamplesHistory.append(iterationTrainExamples)
        timestamp = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")

        folder = config["checkpoint_directory"]
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, 'checkpoint_' + str(timestamp) + "_proc_" + str(identifier) + '.pth.tar')
        with open(filename, "wb+") as f:
            Pickler(f).dump(trainExamplesHistory)
        f.closed

        return filename

    def createSSHClient(self, server, port, user, password):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server, port, user, password)
        return client

    def send_examples_to_server(self, sensitive_config, local_path):
        ssh = self.createSSHClient(sensitive_config["main_server_address"], 22, sensitive_config["main_username"],
                              sensitive_config["main_password"])
        scp = SCPClient(ssh.get_transport())
        scp.put(local_path, sensitive_config["distributed_examples_directory"])

    def determine_iteration(self):
        with open(f'{self.sensitive_config["distributed_models_directory"]}/training_update.txt', "r") as stream:
            try:
                iteration = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise ValueError(exc)

        return int(iteration)

    def worker_loop(self, identifier, iteration, disable_resignation_threshold):
        game = Game(self.config["board_size"])
        neural_network = nn(game, self.config)

        # Load recent model into nnet
        neural_network.load_checkpoint(self.sensitive_config["distributed_models_directory"], 'best.pth.tar')
        # print("Done loading model")

        # print(f"Starting game {iter_num}...")
        print(f"Starting game on process: {identifier}")
        # Generate training examples
        new_train_examples = self.learn(game=game, nnet=neural_network, config=self.config, identifier=identifier,
                                   iteration=iteration, disable_resignation_threshold=disable_resignation_threshold)

        print(f"Game complete on process {identifier}. Sending examples to {self.sensitive_config['main_server_address']}")
        # where is the file located on local machine
        local_path = new_train_examples
        self.send_examples_to_server(sensitive_config=self.sensitive_config, local_path=local_path)
        # print("Done sending examples to server")

        # delete it from the local machine
        os.remove(local_path)
        # print("Deleted example from local machine")


if __name__ == "__main__":
    mp.set_start_method('spawn')

    pool_num = 1
    sleep_counter = 0

    worker = DistributedWorker()

    while True:
        if not os.path.exists(os.path.join(worker.sensitive_config["distributed_models_directory"], 'best.pth.tar')):
            print(f"Waiting for model to be uploaded, {sleep_counter} minutes elapsed.")
            time.sleep(60)
            sleep_counter += 1
        else:
            disable_resignation_threshold = True if pool_num % 5 == 0 else False

            # load information file from server
            iteration = worker.determine_iteration()

            print(f"Pool {pool_num} Started, Training at Iteration {iteration}")

            # create and configure the process pool
            with mp.Pool(worker.config["num_parallel_games"]) as pool:
                for i in range(worker.config["num_parallel_games"]):
                    pool.apply_async(worker.worker_loop, args=(i, iteration, disable_resignation_threshold,))

                pool.close()
                pool.join()

            # process pool is closed automatically
            print(f"Pool {pool_num} Finished")
            print()

            pool_num += 1
