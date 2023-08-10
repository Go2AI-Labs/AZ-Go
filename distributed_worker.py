import os
from collections import deque
from datetime import datetime
import dill 
from dill import Pickler
import multiprocessing as mp

import paramiko
import yaml
from scp import SCPClient

from go.GoGame import GoGame as Game
from go.pytorch.NNet import NNetWrapper as nn
from GoCoach import Coach


def learn(game, nnet, config, identifier, disable_resignation_threshold):
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
        iterationTrainExamples += coach.executeEpisode(disable_resignation_threshold=disable_resignation_threshold)

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


def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client


def send_examples_to_server(sensitive_config, local_path):
    ssh = createSSHClient(sensitive_config["main_server_address"], 22, sensitive_config["main_username"],
                          sensitive_config["main_password"])
    scp = SCPClient(ssh.get_transport())
    scp.put(local_path, sensitive_config["distributed_examples_directory"])


with open("config.yaml", "r") as stream:
    try:
        config = yaml.safe_load(stream)
        # print(config)
    except yaml.YAMLError as exc:
        raise ValueError(exc)

with open("sensitive.yaml", "r") as stream:
    try:
        sensitive_config = yaml.safe_load(stream)
        # print(sensitive_config)
    except yaml.YAMLError as exc:
        raise ValueError(exc)


def worker_loop(identifier, disable_resignation_threshold):
    game = Game(config["board_size"])
    neural_network = nn(game, config)

    # Load recent model into nnet
    neural_network.load_checkpoint(sensitive_config["distributed_models_directory"], 'best.pth.tar')
    # print("Done loading model")

    # print(f"Starting game {iter_num}...")
    print(f"Starting game on process: {identifier}")
    # Generate training examples
    new_train_examples = learn(game=game, nnet=neural_network, config=config, identifier=identifier, disable_resignation_threshold=disable_resignation_threshold)

    print(f"Game complete on process {identifier}. Sending examples to {sensitive_config['main_server_address']}")
    # where is the file located on local machine
    local_path = new_train_examples
    send_examples_to_server(sensitive_config=sensitive_config, local_path=local_path)
    # print("Done sending examples to server")

    # delete it from the local machine
    os.remove(local_path)
    # print("Deleted example from local machine")
    # print()


if __name__ == "__main__":
    mp.set_start_method('spawn')

    pool_num = 1
    while True:
        mp.cpu_count()

        disable_resignation_threshold = True if pool_num % 5 == 0 else False

        print(f"Pool {pool_num} Started")

        # create and configure the process pool
        with mp.Pool(config["num_parallel_games"]) as pool:
            for i in range(config["num_parallel_games"]):
                pool.apply_async(worker_loop, args=(i, disable_resignation_threshold,))

            pool.close()
            pool.join()

        # process pool is closed automatically
        print(f"Pool {pool_num} Finished")
        print()

        pool_num += 1
