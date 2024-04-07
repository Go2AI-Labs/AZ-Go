from definitions import CONFIG_PATH
from utils.config_handler import ConfigHandler


# TODO: Imports config.yaml every time function is called... bad practice I would assume
def print_debug(str):
    config = ConfigHandler(CONFIG_PATH)
    if config['debug_mode']:
        print(str)
