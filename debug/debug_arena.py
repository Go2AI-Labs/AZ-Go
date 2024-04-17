from distributed.worker import Worker
from utils.data_serializer import ensure_defined_directories_exist

"""
Single thread debug script for arena
"""

if __name__ == "__main__":
    ensure_defined_directories_exist()
    worker = Worker()
    worker.handle_arena_lifecycle()
