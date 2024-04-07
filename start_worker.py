import multiprocessing as mp

from distributed.worker import Worker
from utils.data_serializer import ensure_defined_directories_exist

"""
Entrypoint for starting a single worker node
"""

if __name__ == "__main__":
    ensure_defined_directories_exist()
    mp.set_start_method('spawn')
    worker = Worker()
    worker.start()
