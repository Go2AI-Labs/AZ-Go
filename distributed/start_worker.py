import multiprocessing as mp
import os
import time

from ssh_connector import SSHConnector
from worker import Worker
from definitions import DIS_EXAMPLE_PATH

"""
Checks for remote model and initializes worker thread(s).
"""

if __name__ == "__main__":
    mp.set_start_method('spawn')

    pool_num = 1
    sleep_counter = 0

    connector = SSHConnector()
    worker = Worker()

    # ensure DIS_EXAMPLE_PATH exists for game data to be saved to later
    if not os.path.exists(DIS_EXAMPLE_PATH):
        os.makedirs(DIS_EXAMPLE_PATH)

    while True:
        if connector.download_model():
            # TODO: Investigate importance of disabling resignation threshold
            disable_resignation_threshold = True if pool_num % 5 == 0 else False

            print(f"Pool {pool_num} Started")

            with mp.Pool(worker.config["num_parallel_games"]) as pool:
                for i in range(worker.config["num_parallel_games"]):
                    pool.apply_async(worker.start, args=(i, pool_num, disable_resignation_threshold,))

                pool.close()
                pool.join()

            print(f"Pool {pool_num} Finished")
            pool_num += 1
        else:
            time.sleep(60)
            sleep_counter += 1
            print(f"Waiting for model to be uploaded, {sleep_counter} minutes elapsed.")