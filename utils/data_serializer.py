import pickle

"""
Provides wrapper functions for pickler interactions (serializing and deserializing data).
"""


def save_to_disk(data, local_path):
    with open(local_path, 'wb+') as file:
        pickle.dump(data, file)


def load_from_disk(local_path):
    with open(local_path, 'rb') as file:
        data = pickle.load(file)
    return data


