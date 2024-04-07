import os
import pickle
import json
import glob
from definitions import CHECKPOINT_PATH, EXAMPLES_PATH, GAME_HISTORY_PATH, GRAPH_PATH, \
    TRAIN_LOG_PATH, DIS_SELF_PLAY_PATH, DIS_ARENA_PATH, CONFIG_PATH
from utils.config_handler import ConfigHandler

"""
Provides wrapper functions for pickler interactions (serializing and deserializing data).
"""


def ensure_defined_directories_exist():
    """
    Create directories for other functions as specified (and imported) from definitions.py
    """
    paths = [CHECKPOINT_PATH, EXAMPLES_PATH, GAME_HISTORY_PATH, GRAPH_PATH, TRAIN_LOG_PATH]
    dis_paths = [DIS_SELF_PLAY_PATH, DIS_ARENA_PATH]

    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)

    config = ConfigHandler(CONFIG_PATH)
    if config['enable_distributed_training']:
        for dis_path in dis_paths:
            if not os.path.exists(dis_path):
                os.makedirs(dis_path)


def overwrite_str_to_disk(data, local_path):
    """
    Writes text to a file using "write", intended for use with strings
    If data already exists at local path, it will be OVERWRITTEN
    """
    with open(local_path, 'w') as file:
        file.write(data)


def read_str_from_disk(local_path):
    """
    Reads string value from file at local_path
    """
    with open(local_path, 'r') as file:
        data = file.read()

    return data


def save_obj_to_disk(data, local_path):
    """
    Uses pickle to save copy of memory into a file, intended for use with objects
    """
    with open(local_path, 'wb+') as file:
        pickle.dump(data, file)


def load_obj_from_disk(local_path):
    """
    Uses pickle to load a file, intended for use with objects
    """
    with open(local_path, 'rb') as file:
        data = pickle.load(file)
    return data


def save_json_to_disk(data, local_path):
    with open(local_path, 'w') as file:
        json.dump(data, file, sort_keys=True, indent=4)


def load_json_from_disk(local_path):
    """
    Read data from json file and return data of type dictionary
    """
    with open(local_path, 'r') as openfile:
        data = json.load(openfile)
    return data


def delete_directory_contents(local_path):
    """
    Delete all files within a specified directory "local_path"
    """
    files = glob.glob(local_path + "*")

    for f in files:
        os.remove(f)
