"""
This file contains paths and commands for running KataGo
"""

KATAGO_ROOT_PATH = '/home/harrison/katago/'
KATAGO_MODEL_NAME = 'kata1-b28c5-weights.bin.gz'
KATAGO_CONFIG_NAME = 'go2ai_analysis.cfg'

KATAGO_START_CMD = (f'{KATAGO_ROOT_PATH}katago analysis -model {KATAGO_ROOT_PATH}{KATAGO_MODEL_NAME} '
                    f'-config {KATAGO_ROOT_PATH}{KATAGO_CONFIG_NAME}')
