import os
import sys

# TODO: Only used by the engine.py file. Update engine to remove this dependency
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("..")

    return os.path.join(base_path, relative_path)