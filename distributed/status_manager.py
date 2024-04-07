import os
from enum import Enum

from definitions import DIS_STATUS_PATH
from distributed.ssh_connector import SSHConnector
from utils.data_serializer import overwrite_str_to_disk, read_str_from_disk


class Status(Enum):
    SELF_PLAY = "self_play"
    NEURAL_NET_TRAINING = "neural_net_training"
    ARENA = "arena"


class StatusManager:
    def __init__(self):
        self.status = Status.SELF_PLAY
        self.status_path = os.path.join(DIS_STATUS_PATH, "status.txt")
        self.connector = SSHConnector()

    def announce_status(self, status):
        """
        Write to status.txt file with current status of training to inform worker nodes.
        Also sets internal status parameter.
        """
        overwrite_str_to_disk(status, self.status_path)

    def check_status(self):
        """
        Read the status.txt file to determine what phase training is in. Used by worker.
        """

        # download status.txt from main
        self.connector.download_status()
        # read value from status.txt
        status = read_str_from_disk(DIS_STATUS_PATH + 'status.txt')
        # return value
        return status
