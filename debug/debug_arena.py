from training.worker import Worker
from utils.data_serializer import ensure_defined_directories_exist
import multiprocessing as mp

"""
Single thread debug script for arena
"""

if __name__ == "__main__":
    ensure_defined_directories_exist()
    worker = Worker()
    worker.handle_arena_lifecycle()

    # with mp.Pool(2) as pool:
    #     for i in range(2):
    #         pool.apply_async(worker.handle_arena_lifecycle)
    #
    #     pool.close()
    #     pool.join()


