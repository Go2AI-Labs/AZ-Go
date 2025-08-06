from fabric.connection import Connection

from definitions import SENS_CONFIG_PATH, CHECKPOINT_PATH, DIS_STATUS_PATH
from utils.config_handler import ConfigHandler

"""
SSHConnector creates a uniform protocol for SSH interactions between the main server and
a worker server using Fabric.
"""


class SSHConnector:
    def __init__(self):
        self.sensitive_config = ConfigHandler(SENS_CONFIG_PATH)
        self.main_path = self.sensitive_config['main_directory']
        self.main_username = self.sensitive_config["main_username"]
        self.main_server_address = self.sensitive_config['main_server_address']

    # send worker info to main
    # previous_net.pth.tar
    # current_net.pth.tar
    def upload_arena_outcomes(self, local_path, file_name):
        remote_path = self.main_path + "/distributed/arena/" + file_name
        with Connection(self.main_server_address, self.main_username) as c:
            c.sftp().put(local_path, remote_path)

    def upload_self_play_examples(self, local_path, file_name):
        # assumes remote_path is on a LINUX machine
        remote_path = self.main_path + "/distributed/self_play/" + file_name
        with Connection(self.main_server_address, self.main_username) as c:
            c.sftp().put(local_path, remote_path)

    # needed for worker self play
    def download_best_model(self):
        with Connection(self.main_server_address, self.main_username) as c:
            try:
                c.get(self.main_path + "logs/checkpoints/best.pth.tar", CHECKPOINT_PATH + "best.pth.tar")
                return True
            except FileNotFoundError:
                print(f"No best.pth.tar found at {self.main_path + 'logs/checkpoints/best.pth.tar'}")
                return False

    # needed for worker arena
    def download_arena_models(self):
        with Connection(self.main_server_address, self.main_username) as c:
            try:
                c.get(self.main_path + "logs/checkpoints/previous_net.pth.tar", CHECKPOINT_PATH + "previous_net.pth.tar")
                c.get(self.main_path + "logs/checkpoints/current_net.pth.tar", CHECKPOINT_PATH + "current_net.pth.tar")
                return True
            except FileNotFoundError:
                print(f"No previous_net.pth.tar found at {self.main_path + 'logs/checkpoints/previous_net.pth.tar'}")
                return False

    # needed for worker flow
    def download_status(self):
        with Connection(self.main_server_address, self.main_username) as c:
            try:
                c.get(self.main_path + "distributed/status.txt", DIS_STATUS_PATH + "status.txt")
                return True
            except FileNotFoundError:
                print(f"No status.txt found at {self.main_path + 'distributed/status.txt'}")
                return False
