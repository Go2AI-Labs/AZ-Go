from training.overseer import Overseer
from utils.data_serializer import ensure_defined_directories_exist

"""
Start distributed main as overseer of worker nodes
"""

if __name__ == "__main__":
    ensure_defined_directories_exist()
    overseer = Overseer()
    overseer.start()
