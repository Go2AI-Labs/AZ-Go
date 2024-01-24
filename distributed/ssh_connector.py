from fabric.connection import Connection
from utils.config_handler import ConfigHandler

from definitions import SENS_CONFIG_PATH, DIS_MODEL_PATH

"""
SSHConnector creates a uniform protocol for SSH interactions between the main server and
a worker server using Fabric.
"""


class SSHConnector:
    def __init__(self):
        self.sensitive_config = ConfigHandler(SENS_CONFIG_PATH)

    def upload_game(self, file_name, local_path):
        # assumes remote_path is on a LINUX machine
        remote_path = self.sensitive_config["master_directory_to_send_examples_to"] + "/" + file_name
        with Connection(self.sensitive_config["master_server_address"], self.sensitive_config["master_username"]) as c:
            c.sftp().put(local_path, remote_path)

    def download_model(self):
        with Connection(self.sensitive_config["master_server_address"], self.sensitive_config["master_username"]) as c:
            try:
                c.get(self.sensitive_config["master_directory_to_get_models_from"] + "/best.pth.tar",
                      DIS_MODEL_PATH + "best.pth.tar")
                return True
            except FileNotFoundError:
                print(f"No best.pth.tar file found at {self.sensitive_config['master_directory_to_get_models_from'] + '/best.pth.tar'}")
                return False
