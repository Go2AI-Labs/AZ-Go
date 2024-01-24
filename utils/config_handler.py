import yaml


class ConfigHandler:

    def __init__(self, file_path):
        with open(file_path, "r") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise ValueError(exc)

    def __getitem__(self, item):
        return self.config[item]
