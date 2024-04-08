from definitions import CONFIG_PATH
from definitions import DIS_SELF_PLAY_PATH, DIS_ARENA_PATH
from distributed.status_manager import StatusManager, Status
from lifecycle.lifecycle_manager import LifecycleManager
from lifecycle.lifecycle_metadata import LifecycleMetadata
from lifecycle.neural_net_manager import NeuralNetManager
from lifecycle.train_example_manager import TrainExampleManager
from utils.config_handler import ConfigHandler
from utils.data_serializer import delete_directory_contents
from utils.print_debug import print_debug


class Overseer:

    def __init__(self):
        self.config = ConfigHandler(CONFIG_PATH)
        self.train_example_manager = TrainExampleManager()
        self.lifecycle_manager = LifecycleManager(train_example_manager=self.train_example_manager)
        self.lifecycle_metadata = LifecycleMetadata()
        self.status_manager = StatusManager()
        self.neural_net_manager = NeuralNetManager()

    def start(self):
        for i in range(1, self.config["num_iterations"]):
            print_debug(f"Started iteration {self.lifecycle_metadata.iteration_num}")

            if self.lifecycle_metadata.is_first_iteration:
                # need to save the current model
                self.neural_net_manager.save_best_network_to_disk(0)

            # MARK: SELF PLAY
            # clean up old self play training examples
            delete_directory_contents(DIS_SELF_PLAY_PATH)
            print_debug(f"Wiped self_play folder at {DIS_SELF_PLAY_PATH}")

            # send out signal for workers to generate self play games
            self.status_manager.announce_status(Status.SELF_PLAY.value)
            print_debug(f"Announced status: {Status.SELF_PLAY.value}")

            # poll every x minutes and scan directory for games
            self.lifecycle_manager.execute_self_play()
            print_debug(f"Completed self play with {len(self.train_example_manager.train_examples)} train examples")

            # MARK: NEURAL NET TRAINING
            # games are done, send out signal for workers to pause (NN signal)
            # save previous nn (pnet)
            # train new net and save (nnet)
            self.status_manager.announce_status(Status.NEURAL_NET_TRAINING.value)
            print_debug(f"Announced status: {Status.NEURAL_NET_TRAINING.value}")
            self.train_example_manager.prepare_train_examples_for_neural_network()
            print_debug("Finished preparing train examples for neural network training")

            # save previous network to disk
            # load previous network from disk into previous net
            # train new network
            self.neural_net_manager.prepare_neural_net_for_training()
            print_debug("Saved previous net and loaded previous net")
            self.neural_net_manager.train_current_model(self.train_example_manager.shuffled_train_examples)
            print_debug("Trained current neural network")
            self.neural_net_manager.save_current_network_to_disk()
            print_debug("Saved current neural network")

            # now that both networks are complete and saved

            # MARK: ARENA
            # send out signal for workers to play arena games
            # clean up old arena outcomes
            delete_directory_contents(DIS_ARENA_PATH)
            print_debug(f"Wiped arena folder at {DIS_ARENA_PATH}")

            self.status_manager.announce_status(Status.ARENA.value)
            print_debug(f"Announced status: {Status.ARENA.value}")

            # loop this until criteria has been reached:
            # poll every x minutes and scan directory for outcomes
            self.lifecycle_manager.execute_arena_play()
            print_debug(f"Completed arena with {self.lifecycle_manager.completed_games_arena} games")

            should_accept_current_model = self.lifecycle_manager.handle_arena_outcome()
            print_debug(f"Arena reported CURRENT WINS:{self.lifecycle_manager.current_model_wins}")
            print_debug(f"Arena reported PREV WINS:{self.lifecycle_manager.previous_model_wins}")
            print_debug(f"Arena winrate CURRENT/TOTAL: "
                        f"{self.lifecycle_manager.current_model_wins / self.lifecycle_manager.completed_games_arena}")
            print_debug(f"Should accept current model: {should_accept_current_model}")
            self.neural_net_manager.update_best_model_if_needed(should_accept_current_model=should_accept_current_model,
                                                                lifecycle_metadata=self.lifecycle_metadata)

            # record results to graphs
            # assign best.pth.tar as need

            # prepare for next iteration
            self.lifecycle_manager.reset_self_play()
            self.lifecycle_manager.reset_arena_play()
            self.lifecycle_metadata.iteration_num += 1
            self.lifecycle_metadata.is_first_iteration = False
            print("Reset self_play and arena for next iteration")
