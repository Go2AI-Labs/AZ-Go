import os
import pickle
from collections import deque
from random import shuffle

from definitions import CONFIG_PATH
from definitions import EXAMPLES_PATH
from utils.config_handler import ConfigHandler
from utils.data_serializer import save_obj_to_disk


class TrainExampleManager:
    def __init__(self):
        self.config = ConfigHandler(CONFIG_PATH)
        # training examples from most recent iteration
        self.train_examples = deque([], maxlen=self.config["max_length_of_queue"])
        """
        Historical collection of training examples from config.yaml
        "max_num_iterations_in_train_example_history" latest iterations
        """
        self.train_examples_history = []
        """
        Initialized to None and only modified by shuffle_train_examples, these are used by neural network for training
        """
        self.shuffled_train_examples = []
        self.checkpoint_number = 1

    def append_train_examples(self, file_path):
        """
        Given "file_path" load training examples from file into current iteration train_examples
        """
        with open(file_path, "rb") as f:
            try:
                examples = pickle.load(f)
                for i in range(len(examples)):
                    self.train_examples += examples[i]
                # once examples have been loaded in, delete the file
                os.remove(file_path)
            except:
                print(
                    f"Error loading file: {file_path}\n"
                    f"File not found on local device. Maybe there was an issue downloading it?")
                pass

    def prepare_train_examples_for_neural_network(self):
        self.migrate_train_examples()
        self.save_train_examples_to_disk()
        # reset train_examples
        self.train_examples = deque([], maxlen=self.config["max_length_of_queue"])
        self.shuffle_train_examples()

    def shuffle_train_examples(self):
        self.shuffled_train_examples = []
        for e in self.train_examples_history:
            self.shuffled_train_examples.extend(e)
        shuffle(self.shuffled_train_examples)

    def save_train_examples_to_disk(self):
        checkpoint_name = f"checkpoint_{self.checkpoint_number}.pth.tar.examples"
        file_path = os.path.join(EXAMPLES_PATH, checkpoint_name)
        save_obj_to_disk(self.train_examples, file_path)

    def migrate_train_examples(self):
        """
        Copy current training examples to train_example_history and check that history is within specified limits
        """
        self.train_examples_history.append(self.train_examples)
        while len(self.train_examples_history) > self.config["max_num_iterations_in_train_example_history"]:
            self.train_examples_history.pop(0)
            print(f"Truncated trainExamplesHistory to "
                  f"{len(self.train_examples_history)}. Length exceeded config limit.")
