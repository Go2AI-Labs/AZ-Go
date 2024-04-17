import matplotlib.pyplot as plt
import numpy as np

from datetime import datetime

from definitions import CONFIG_PATH
from utils.config_handler import ConfigHandler


class GraphLogger:

    def __init__(self):
        self.config = ConfigHandler(CONFIG_PATH)

        now = datetime.now()
        self.init_date_time = now.strftime("%m.%d.%Y_%H:%M:%S")

        self.p_loss_per_iteration = []
        self.v_loss_per_iteration = []
        self.win_rate_per_iteration = []

    def add_train_log(self, train_log):
        self.p_loss_per_iteration.append(np.average(train_log['P_LOSS'].to_numpy()))
        self.v_loss_per_iteration.append(np.average(train_log['V_LOSS'].to_numpy()))

    def add_win_rate(self, win_rate):
        self.win_rate_per_iteration.append(win_rate)

    def update_plots(self):
        plt.close()

        plt.rcParams["figure.figsize"] = (18, 12)

        ax = plt.subplot(2, 2, 1)
        ax.set_xlim(1, max(len(self.v_loss_per_iteration), 2))
        plt.title("V Loss During Training")
        plt.ylabel('V Loss')
        plt.xlabel('Iteration')
        plt.locator_params(axis='x', integer=True, tight=True)
        plt.plot(self.v_loss_per_iteration, label="V Loss")

        ax = plt.subplot(2, 2, 2)
        ax.set_xlim(1, max(len(self.p_loss_per_iteration), 2))
        plt.title("P Loss During Training")
        plt.ylabel('P Loss')
        plt.xlabel('Iteration')
        plt.locator_params(axis='x', integer=True, tight=True)
        plt.plot(self.p_loss_per_iteration, label="P Loss")

        ax = plt.subplot(2, 2, 3)
        ax.set_xlim(1, max(len(self.win_rate_per_iteration), 2))
        plt.title('Arena Play Win Rates (New Model vs. Old Model)')
        plt.xlabel('Iteration')
        plt.ylabel('Win Rate (%)')
        plt.locator_params(axis='x', integer=True, tight=True)
        plt.axhline(y=self.config["acceptance_threshold"], color='b', linestyle='-')
        plt.plot(self.win_rate_per_iteration, 'r', label='Win Rate')

        plt.savefig(self.config["graph_directory"] + f"/Training_Result {self.init_date_time}.png")
