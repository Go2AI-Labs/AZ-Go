import multiprocessing as mp
import os
import time
from collections import deque
from random import randint

import numpy as np

from definitions import CONFIG_PATH, CHECKPOINT_PATH, SENS_CONFIG_PATH, DIS_SELF_PLAY_PATH, DIS_ARENA_PATH
from distributed.ssh_connector import SSHConnector
from distributed.status_manager import StatusManager, Status
from go.go_game import GoGame
from mcts_dis import MCTSDis as MCTS
from neural_network.neural_net_wrapper import NNetWrapper
from training.arena_manager import ArenaManager
from training.self_play_manager import SelfPlayManager
from utils.config_handler import ConfigHandler
from utils.data_serializer import save_obj_to_disk, save_json_to_disk


class Worker:
    def __init__(self):
        self.config = ConfigHandler(CONFIG_PATH)
        self.sensitive_config = ConfigHandler(SENS_CONFIG_PATH)
        self.status_manager = StatusManager()
        self.connector = SSHConnector()
        self.status = None

    def start(self):
        """
        Main function for switching between self play, arena, and NN training for worker node.
        Periodically check status of main server and execute needed function.
        """
        while True:
            self.status = self.status_manager.check_status()

            if self.status == Status.SELF_PLAY.value:
                print("Status: Self Play")
                self.connector.download_best_model()
                self.start_self_play()

            elif self.status == Status.NEURAL_NET_TRAINING.value:
                print("Status: NN Training")
                time.sleep(30)  # in seconds

            elif self.status == Status.ARENA.value:
                print("Status: Arena")
                self.connector.download_arena_models()
                self.start_arena()

            else:
                print("ERROR STATUS NOT FOUND")
                raise Exception()

    def start_self_play(self):
        """
        Helper function for handling multiprocessing pool for self play as specified in config.yaml
        """
        with mp.Pool(self.config["num_parallel_games"]) as pool:
            for i in range(self.config["num_parallel_games"]):
                pool.apply_async(self.handle_self_play_lifecycle)

            pool.close()
            pool.join()

    # TODO: when do we want to reset the MCTS tree? Currently per thread batch, not per game for self_play
    def handle_self_play_lifecycle(self):
        """
        PER THREAD FUNCTION
        Initializes a game object and loads the neural network located at CHECKPOINT_PATH/best.pth.tar
        (note CHECKPOINT_PATH is defined in definitions.py). Then, plays a single game using the play_game function.
        The results of the game are uploaded and subsequently deleted from the local machine.
        According to the paper, each game of training (self-play) should start with a fresh MCTS tree.
        See: https://github.com/suragnair/alpha-zero-general/discussions/24
        """
        go_game = GoGame(self.config['board_size'])
        neural_net = NNetWrapper(go_game, self.config)
        neural_net.load_checkpoint(CHECKPOINT_PATH, 'best.pth.tar')
        mcts = MCTS(game=go_game, nnet=neural_net, is_self_play=True)
        local_path, file_name = self.execute_self_play(go_game=go_game, neural_net=neural_net, mcts=mcts)
        self.connector.upload_self_play_examples(local_path, file_name)
        os.remove(local_path)

    def execute_self_play(self, go_game, neural_net, mcts):
        """
        PER THREAD FUNCTION
        Plays a single self play game for data collection
        :param go_game:
        :param neural_net:
        :return:
        """
        train_examples_history = []
        iteration_train_examples = deque([], maxlen=self.config["max_length_of_queue"])
        manager = SelfPlayManager(neural_net, mcts)
        for eps in range(self.config["num_games_per_distributed_batch"]):
            iteration_train_examples += manager.execute_game()
            print("Game completed.")

        # save the generated train examples in their own file
        train_examples_history.append(iteration_train_examples)

        file_name = (f'{self.sensitive_config["worker_machine_tag"]}_{randint(1, 1000)}' + '.pth.tar')
        local_path = os.path.join(DIS_SELF_PLAY_PATH, file_name)

        # save game data to disk
        save_obj_to_disk(train_examples_history, local_path)

        return local_path, file_name

    """
    For arena, we should create 1 MCTS that is parallelized across threads for a single game,
    NOT multiple arena games at once... a bit different than self_play
    """

    def start_arena(self):
        """
        Helper function for handling multiprocessing pool for arena as specified in config.yaml
        """
        with mp.Pool(self.config["num_parallel_games"]) as pool:
            for i in range(self.config["num_parallel_games"]):
                pool.apply_async(self.handle_arena_lifecycle)

            pool.close()
            pool.join()

    def handle_arena_lifecycle(self):
        """
        Function at thread level
        """
        go_game = GoGame(self.config['board_size'])
        previous_net = NNetWrapper(game=go_game, config=self.config)
        previous_net.load_checkpoint(CHECKPOINT_PATH, 'previous_net.pth.tar')
        current_net = NNetWrapper(game=go_game, config=self.config)
        current_net.load_checkpoint(CHECKPOINT_PATH, 'current_net.pth.tar')
        previous_mcts = MCTS(game=go_game, nnet=previous_net, is_self_play=False)
        current_mcts = MCTS(game=go_game, nnet=current_net, is_self_play=False)

        prev_player = lambda x: np.argmax(previous_mcts.getActionProb(x, temp=0))
        curr_player = lambda x: np.argmax(current_mcts.getActionProb(x, temp=0))

        arena = ArenaManager(prev_player, curr_player, previous_mcts, current_mcts)

        prev_wins, current_wins, draws = arena.play_games(2)

        outcomes = {"current_wins": current_wins, "previous_wins": prev_wins, "ties": draws,
                    "games_played": prev_wins + current_wins + draws}
        file_name = (f'{self.sensitive_config["worker_machine_tag"]}_{randint(1, 1000)}' + '.json')
        local_path = os.path.join(DIS_ARENA_PATH, file_name)
        save_json_to_disk(data=outcomes, local_path=local_path)
        self.connector.upload_arena_outcomes(local_path, file_name)
        os.remove(local_path)
