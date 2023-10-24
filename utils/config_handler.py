import yaml
from utils.path_handler import resource_path


class ConfigHandler:

    def __init__(self, filename):
        with open(resource_path(filename), "r") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise ValueError(exc)

    def __getitem__(self, item):
        return self.config[item]
