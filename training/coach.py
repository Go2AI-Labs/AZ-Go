import glob
import os
import sys
import time
from collections import deque
import dill
from dill import Pickler, Unpickler
import random
from random import shuffle
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import paramiko
import psutil
import yaml

from training.arena import Arena
from mcts import MCTS
from go.go_game import display
# from utils.status_bar import StatusBar
from utils.config_handler import ConfigHandler
from definitions import SENS_CONFIG_PATH, DIS_EXAMPLE_PATH


class Coach:
    """
    This class executes the self-play + learning. It uses the functions defined
    in Game and NeuralNet. config is specified in config.yaml.
    """

    def __init__(self, game, nnet, config):
        self.game = game
        self.nnet = nnet
        self.pnet = self.nnet.__class__(self.game, config)  # the competitor network
        self.config = config
        self.mcts = MCTS(self.game, self.nnet, self.config)
        self.trainExamplesHistory = []  # history of examples from config["max_num_iterations_in_train_example_history"] latest iterations
        self.skipFirstSelfPlay = False  # can be overriden in loadTrainExamples()

        self.p_loss_per_iteration = []
        self.v_loss_per_iteration = []
        self.winRate = []
        self.iterationTrainExamples = deque([], maxlen=self.config["max_length_of_queue"])

        self.date_time = datetime.now().strftime("%m-%d-%Y %H:%M")
        self.latest_checkpoint = 0

        # Set recurse to true in order to fix segmentation fault error
        dill.settings['recurse'] = True
        Pickler.settings['recurse'] = True
        Unpickler.settings['recurse'] = True

        # if needed, import sensitive_config
        if config["enable_distributed_training"]:
            self.sensitive_config = ConfigHandler(SENS_CONFIG_PATH)

    def executeEpisode(self, iteration, disable_resignation_threshold=False):
        """
        This function executes one episode of self-play, starting with player 1.
        As the game is played, each turn is added as a training example to
        game_train_examples. The game is played till the game ends. After the game
        ends, the outcome of the game is used to assign values to each example
        in game_train_examples.

        It uses a temp=1 if episodeStep < tempThreshold, and thereafter
        uses temp=0.

        Returns:
            game_train_examples: a list of examples of the form (canonicalBoard,pi,v)
                           pi is the MCTS informed policy vector, v is +1 if
                           the player eventually won the game, else -1.
        """
        game_train_examples = []
        board = self.game.getInitBoard()
        self.curPlayer = 1
        episodeStep = 0
        c_boards = [np.ones((7, 7)), np.zeros((7, 7))]
        x_boards, y_boards = self.game.init_x_y_boards()
        r = 0

        while r == 0:
            x_boards, y_boards = y_boards, x_boards
            episodeStep += 1
            if self.config["display"] == 1:
                print("================Episode Playing Step:{}=====CURPLAYER:{}==========".format(episodeStep,
                                                                                                  "White" if self.curPlayer == -1 else "Black"))
                # Get the current board, current player's board, and game history at current state
            canonicalBoard = self.game.getCanonicalForm(board, self.curPlayer)
            player_board = (c_boards[0], c_boards[1]) if self.curPlayer == 1 else (c_boards[1], c_boards[0])
            canonicalHistory, x_boards, y_boards = self.game.getCanonicalHistory(x_boards, y_boards,
                                                                                 canonicalBoard.pieces, player_board)
            # set temperature variable and get move probabilities
            temp = int(episodeStep < self.config["temperature_threshold"])

            if random.random() <= 0.25:
                num_sims = self.config["num_full_search_sims"]
                use_noise = True
            else:
                num_sims = self.config["num_fast_search_sims"]
                use_noise = False
            pi = self.mcts.getActionProb(canonicalBoard, canonicalHistory, x_boards, y_boards, player_board, use_noise,
                                         num_sims, temp=temp)
            # get different symmetries/rotations of the board if full search was done 
            if num_sims == self.config["num_full_search_sims"]:
                sym = self.game.getSymmetries(canonicalHistory, pi)
                for b, p in sym:
                    game_train_examples.append([b, self.curPlayer, p, None])
            # choose a move
            if episodeStep < self.config["temperature_threshold"]:
                action = np.random.choice(len(pi), p=pi)
            else:
                action = np.argmax(pi)
            # play the chosen move
            board, self.curPlayer = self.game.getNextState(board, self.curPlayer, action)
            if self.config["display"] == 1:
                print("BOARD updated:")
                print(display(board))
                # get current game result
            r, score = self.game.getGameEndedSelfPlay(board.copy(), self.curPlayer, iteration=iteration,
                                                      returnScore=True,
                                                      disable_resignation_threshold=disable_resignation_threshold)
            if self.config["display"] == 1:
                print(f"Current score: b {score[0]}, W {score[1]}")

        if self.config["display"] == 1:
            print(
                "Current episode ends, {} wins with score b {}, W {}.".format('Black' if r == -1 else 'White', score[0],
                                                                              score[1]))
        # return game result
        return [(x[0], x[2], r * ((-1) ** (x[1] != self.curPlayer))) for x in game_train_examples]

    def learn(self):
        """
        Performs numIters iterations with numEps episodes of self-play in each
        iteration. After every iteration, it retrains neural network with
        examples in trainExamples (which has a maximum length of maxlenofQueue).
        It then pits the new neural network against the old one and accepts it
        only if it wins >= updateThreshold fraction of games.
        """
        iterHistory = {'ITER': [], 'ITER_DETAIL': [], 'PITT_RESULT': []}

        start_iter = 1

        if self.config["load_model"]:
            self.load_model()
            self.load_losses()

            with open(os.path.join(self.config["checkpoint_directory"], "training_update.txt"), "r") as stream:
                try:
                    start_iter = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    raise ValueError(exc)

        # helper distributed variables
        upload_number = 1
        new_model_accepted_in_previous_iteration = False

        # training loop
        for i in range(start_iter, self.config["num_iterations"] + 1):
            iterHistory['ITER'].append(i)
            games_played_during_iteration = 0

            if self.config["enable_distributed_training"]:
                print(f"##### Iteration {i} Distributed Training #####")

                if i == 1 and not self.config["load_model"]:
                    first_iteration_num_games = int(self.config["first_iter_num_games"])

                    # on first iteration, play X games, so a model can be updated to lambda
                    print(
                        f"First iteration. Play {first_iteration_num_games} self play games, so there is a model to upload to lambda.")

                    self.iterationTrainExamples = deque([], maxlen=self.config["max_length_of_queue"])
                    # play self play games
                    games_played_during_iteration = self.play_games(first_iteration_num_games,
                                                                    "1st Iter Games", games_played_during_iteration, i)

                else:
                    self.iterationTrainExamples = deque([], maxlen=self.config["max_length_of_queue"])

                    if not new_model_accepted_in_previous_iteration:
                        # download most recent training examples from the drive (until numEps is hit or files run out)
                        # previous examples are still valid training data
                        print("New model not accepted in previous iteration. Downloading from lambda.")
                        games_played_during_iteration += self.scan_examples_folder_and_load(
                            game_limit=self.config["num_self_play_episodes"])
                        status_bar(games_played_during_iteration, self.config["num_self_play_episodes"],
                                   title="Lambda Downloaded Games", label="Games")
                    else:
                        print("New model accepted in previous iteration. Start polling games.")

                    polling_tracker = 1
                    while len(self.iterationTrainExamples) < self.config["max_length_of_queue"]:
                        # play games and download from drive until limit is reached
                        print(f"Starting polling session #{polling_tracker}.")

                        # Play self play games
                        games_played_during_iteration = self.play_games(self.config["num_polling_games"],
                                                                        "Polling Games", games_played_during_iteration,
                                                                        i)

                        # after polling games are played, check drive and download as many "new" files as possible
                        num_downloads = self.scan_examples_folder_and_load(
                            game_limit=self.config["num_self_play_episodes"] - games_played_during_iteration)

                        if (self.config["num_self_play_episodes"] - games_played_during_iteration > 0):
                            status_bar(num_downloads,
                                   (self.config["num_self_play_episodes"] - games_played_during_iteration),
                                   title="Lambda Downloaded Games", label="Games")
                            print()

                        games_played_during_iteration += num_downloads
                        status_bar(games_played_during_iteration, self.config["num_self_play_episodes"],
                                   title="Self Play + Distributed Training", label="Games")
                        polling_tracker += 1

                        # spacers to ensure bar printouts are correct
                        print()
                        print()

            else:
                if not self.skipFirstSelfPlay or i > start_iter:
                    # normal (non-distributed) training loop
                    print(f"######## Iteration {i} Episode Play ########")
                    self.iterationTrainExamples = deque([], maxlen=self.config["max_length_of_queue"])
                    # Play self play games
                    games_played_during_iteration = self.play_games(self.config["num_self_play_episodes"],
                                                                    "Self Play", games_played_during_iteration, i)

            # Log how many games were added during each iteration
            self.log_game_counts(i, games_played_during_iteration)

            # Add new games to self.trainExamplesHistory and prune examples as needed
            self.update_train_examples_history()

            # backup history to a file
            # NB! the examples were collected using the model from the previous iteration, so (i-1)
            #self.saveTrainExamples(i - 1)
            self.save_iteration_train_examples(i - 1)

            # shuffle examples before training
            trainExamples = []
            for e in self.trainExamplesHistory:
                trainExamples.extend(e)
            shuffle(trainExamples)

            # training new network, keeping a copy of the old one
            self.nnet.save_checkpoint(folder=self.config["checkpoint_directory"], filename='temp.pth.tar')
            self.pnet.load_checkpoint(folder=self.config["checkpoint_directory"], filename='temp.pth.tar')
            pmcts = MCTS(self.game, self.pnet, self.config)

            trainLog = self.nnet.train(trainExamples)

            self.p_loss_per_iteration.append(np.average(trainLog['P_LOSS'].to_numpy()))
            self.v_loss_per_iteration.append(np.average(trainLog['V_LOSS'].to_numpy()))
            trainLog.to_csv(self.config["train_logs_directory"] + '/ITER_{}_TRAIN_LOG.csv'.format(i))

            iterHistory['ITER_DETAIL'].append(self.config["train_logs_directory"] + '/ITER_{}_TRAIN_LOG.csv'.format(i))

            nmcts = MCTS(self.game, self.nnet, self.config)

            print('\nPITTING AGAINST PREVIOUS VERSION')
            arena = Arena(lambda x, y, z, a, b, c, d: np.argmax(pmcts.getActionProb(x, y, z, a, b, c, d, temp=0)),
                          lambda x, y, z, a, b, c, d: np.argmax(nmcts.getActionProb(x, y, z, a, b, c, d, temp=0)),
                          self.game, self.config)
            pwins, nwins, draws, outcomes, total_played = arena.playGames(self.config["num_arena_episodes"])
            self.winRate.append(nwins / total_played)
            self.saveLosses()
            print('NEW/PREV WINS : %d / %d ; DRAWS : %d' % (nwins, pwins, draws))
            if pwins + nwins > 0 and float(nwins) / (pwins + nwins) < self.config["acceptance_threshold"]:
                print('REJECTING NEW MODEL')
                new_model_accepted_in_previous_iteration = False
                iterHistory['PITT_RESULT'].append('R')
                self.nnet.load_checkpoint(folder=self.config["checkpoint_directory"], filename='temp.pth.tar')
                if i == 1 and self.config["enable_distributed_training"] and not self.config["load_model"]:
                    # when running distributed training, save first model, so the workers have something to use
                    new_model_accepted_in_previous_iteration = True
                    self.nnet.save_checkpoint(folder=self.config["checkpoint_directory"], filename='best.pth.tar')

            else:
                print('ACCEPTING NEW MODEL')
                new_model_accepted_in_previous_iteration = True
                iterHistory['PITT_RESULT'].append('A')
                self.nnet.save_checkpoint(folder=self.config["checkpoint_directory"],
                                          filename=self.getCheckpointFile(i))
                self.nnet.save_checkpoint(folder=self.config["checkpoint_directory"], filename='best.pth.tar')
                if self.config["enable_distributed_training"]:
                    upload_number += 1
                    self.wipe_examples_folder()


            # write iteration count to file
            with open(f'{self.config["checkpoint_directory"]}/training_update.txt', 'w') as f:
                f.write(str(i))

            # if self.config["enable_distributed_training"]:
            #     # tell the worker server what iteration training is on
            #     self.send_training_updates_to_server(i)

            pd.DataFrame(data=iterHistory).to_csv(self.config["train_logs_directory"] + '/ITER_LOG.csv')

            self.create_sgf_files_for_games(games=outcomes, iteration=i)
            self.saveTrainingPlots()
            self.skipFirstSelfPlay = False

        pd.DataFrame(data=iterHistory).to_csv(self.config["train_logs_directory"] + '/ITER_LOG.csv')

    def play_games(self, loop_iters, title, games_played_during_iteration, iteration_num):
        game_count = games_played_during_iteration
        total_time = 0
        for eps in range(loop_iters):
            start_time = time.time()
            self.mcts = MCTS(self.game, self.nnet, self.config)
            self.iterationTrainExamples += self.executeEpisode(iteration=iteration_num)

            game_count += 1
            end_time = time.time()
            total_time += round(end_time - start_time, 2)
            status_bar(eps + 1, loop_iters,
                       title=title, label="Games",
                       suffix=f"| Eps: {round(end_time - start_time, 2)} | Avg Eps: {round(total_time / (eps + 1), 2)} | Total: {round(total_time, 2)}")
        return game_count
    
    def save_iteration_train_examples(self, iteration):
        folder = self.config["examples_directory"]
        if not os.path.exists(folder):
            os.makedirs(folder)
        checkpoint_name = self.getCheckpointFile(iteration) + ".examples"
        filename = os.path.join(folder, checkpoint_name)
        with open(filename, "wb") as f:
            Pickler(f).dump(self.iterationTrainExamples)
            f.close()

    def load_train_examples_helper(self, filename):
        with open(filename, "rb") as f:
            examples = Unpickler(f).load()
            f.close()
        return examples


    def load_train_examples(self):
        checkpoint_files = [file for file in os.listdir(self.config["examples_directory"]) if
                            file.startswith('checkpoint_') and file.endswith('.pth.tar.examples')]
        checkpoint_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
        if len(checkpoint_files) <= self.config['max_num_iterations_in_train_example_history']:
            for checkpoint in checkpoint_files:
                temp = self.load_train_examples_helper(checkpoint)
                self.trainExamplesHistory.append(temp)
        
        else: 
            start = len(checkpoint_files) - self.config['max_num_iterations_in_train_example_history']
            for checkpoint in checkpoint_files[start:]:
                temp = self.load_train_examples_helper(checkpoint)
                self.trainExamplesHistory.append(temp)
        self.skipFirstSelfPlay = True


    def update_train_examples_history(self):
        # save the iteration examples to the history
        if not self.skipFirstSelfPlay:
            self.trainExamplesHistory.append(self.iterationTrainExamples)
        # prune trainExamples to meet config recommendation
        while len(self.trainExamplesHistory) > self.config["max_num_iterations_in_train_example_history"]:
            self.trainExamplesHistory.pop(0)
            print(
                f"Truncated trainExamplesHistory to {len(self.trainExamplesHistory)}. Length exceeded config limit.")
       

    def getCheckpointFile(self, iteration):
        return 'checkpoint_' + str(iteration) + '.pth.tar'

    def load_model(self):
        checkpoint_files = [file for file in os.listdir(self.config["examples_directory"]) if
                            file.startswith('checkpoint_') and file.endswith('.pth.tar.examples')]
        self.latest_checkpoint = max(checkpoint_files, key=lambda x: int(x.split('_')[1].split('.')[0]))
        print("Loading checkpoint: ", self.latest_checkpoint)
        start_iter = int(self.latest_checkpoint.split('_')[1].split('.')[0]) + 1
        self.load_train_examples()
        #self.loadTrainExamples()
        #return checkpoint_files, start_iter

    """
    def saveTrainExamples(self, iteration):
        folder = self.config["checkpoint_directory"]
        if not os.path.exists(folder):
            os.makedirs(folder)
        filename = os.path.join(folder, self.getCheckpointFile(iteration) + ".examples")
        with open(filename, "wb") as f:  # Removed + after wb
            # print('RAM Used before dump (GB):', psutil.virtual_memory()[3] / 1000000000)
            is_error = True
            while is_error:
                try:
                    Pickler(f).dump(self.trainExamplesHistory)
                    is_error = False
                except:
                    is_error = True
            f.closed  # Indented this by one
    """

    """
    def loadTrainExamples(self):
        modelFile = os.path.join(self.config["checkpoint_directory"], self.latest_checkpoint)
        examplesFile = modelFile  # + ".examples"
        if not os.path.isfile(examplesFile):
            print(examplesFile)
            r = input("File with trainExamples not found. Continue? [y|n]")
            if r != "y":
                sys.exit()
        else:
            if os.path.getsize(examplesFile) > 0:
                # print("File Size: ", os.path.getsize(examplesFile))
                print(f"File with trainExamples found. Read it: {examplesFile}")
                with open(examplesFile, "rb") as f:
                    is_error = True
                    while is_error:
                        # try:
                        # print("Trying pickle")
                        self.trainExamplesHistory = Unpickler(f).load()
                        is_error = False
                        except:
                            print("Error while pickling")
                            is_error = True
                    f.closed  # Indented this by one
            else:
                print("File is empty")
            # examples based on the model were already collected (loaded)
            self.skipFirstSelfPlay = True
    """
    def load_examples_from_path(self, file_path):
        examplesFile = file_path
        with open(examplesFile, "rb") as f:
            try:
                examples = Unpickler(f).load()
                for i in range(len(examples)):
                    self.iterationTrainExamples += examples[i]
            except:
                print(
                    f"Error loading file: {file_path}\nFile not found on local device. Maybe there was an issue downloading it?")
                pass
        self.skipFirstSelfPlay = False
        f.closed

    def saveLosses(self):
        # Save ploss, vloss, and winRate so graphs are consistent across training sessions
        folder = self.config["graph_directory"]
        if not os.path.exists(folder):
            os.makedirs(folder)
        vloss_filename = os.path.join(folder, "vlosses")
        ploss_filename = os.path.join(folder, "plosses")
        winRate_filename = os.path.join(folder, "winrates")
        with open(vloss_filename, "wb+") as f:
            is_error = True
            while is_error:
                try:
                    Pickler(f).dump(self.v_loss_per_iteration)
                    is_error = False
                except:
                    is_error = True
        f.closed
        with open(ploss_filename, "wb+") as f:
            is_error = True
            while is_error:
                try:
                    Pickler(f).dump(self.p_loss_per_iteration)
                    is_error = False
                except:
                    is_error = True
        f.closed
        with open(winRate_filename, "wb+") as f:
            is_error = True
            while is_error:
                try:
                    Pickler(f).dump(self.winRate)
                    is_error = False
                except:
                    is_error = True
        f.closed

    def load_losses(self):
        # Load in ploss, vloss, and winRates from previous iterations so graphs are consistent
        vlossFile = os.path.join(self.config["graph_directory"], "vlosses")
        plossFile = os.path.join(self.config["graph_directory"], "plosses")
        winrateFile = os.path.join(self.config["graph_directory"], "winrates")
        if not os.path.isfile(vlossFile) or not os.path.isfile(plossFile):
            r = input("File with vloss or ploss not found. Continue? [y|n]")
            if r != "y":
                sys.exit()
        else:
            print("File with graph information found. Read it.")
            with open(vlossFile, "rb") as f:
                is_error = True
                while is_error:
                    try:
                        self.v_loss_per_iteration = Unpickler(f).load()
                        is_error = False
                    except:
                        is_error = True
            f.closed
            with open(plossFile, "rb") as f:
                is_error = True
                while is_error:
                    try:
                        self.p_loss_per_iteration = Unpickler(f).load()
                        is_error = False
                    except:
                        is_error = True
            f.closed
            with open(winrateFile, "rb") as f:
                is_error = True
                while is_error:
                    try:
                        self.winRate = Unpickler(f).load()
                        is_error = False
                    except:
                        is_error = True
            f.closed

    def log_game_counts(self, iter_num, games_played):
        file_name = self.config["train_logs_directory"] + "/Game_Counts.txt"
        if not os.path.isfile(file_name):
            counts_file = open(file_name, 'w')
            counts_file.close()
        counts_file = open(file_name, 'a')
        counts_file.write(
            f"\n Number of games added to train examples during iteration #{iter_num}: {games_played} games\n")
        counts_file.close()

    # plot/save v/p loss after training
    # plot/save Arena Play Win Rates after arena
    def saveTrainingPlots(self):
        # close previous graph
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
        ax.set_xlim(1, max(len(self.winRate), 2))
        plt.title('Arena Play Win Rates (New Model vs. Old Model)')
        plt.xlabel('Iteration')
        plt.ylabel('Win Rate (%)')
        plt.locator_params(axis='x', integer=True, tight=True)
        plt.axhline(y=self.config["acceptance_threshold"], color='b', linestyle='-')
        plt.plot(self.winRate, 'r', label='Win Rate')

        plt.savefig(self.config["graph_directory"] + f"/Training_Result {self.date_time}.png")

    def create_sgf_files_for_games(self, games, iteration):

        for game_idx in range(len(games)):
            # file_name = f'logs/go/Game_History/Iteration {iteration}, Game {game_idx + 1} {self.date_time}.sgf'
            file_name = self.config[
                            "game_history_directory"] + f"/Iteration {iteration}, Game {game_idx + 1} {self.date_time}.sgf"

            sgf_file = open(file_name, 'w')
            sgf_file.close()

            sgf_file = open(file_name, 'a')
            sgf_file.write(
                f"(;\nEV[AlphaGo Self-Play]\nGN[Iteration {iteration}]\nDT[{self.date_time}]\nPB[TCU_AlphaGo]\nPW[TCU_AlphaGo]"
                f"\nSZ[{self.game.getBoardSize()[0]}]\nRU["
                f"Chinese]\n\n")

            for move_idx in range(len(games[game_idx])):
                sgf_file.write(games[game_idx][move_idx])

            sgf_file.write("\n)")
            sgf_file.close()

    # local distributed training helper functions
    def createSSHClient(self, server, port, user, password):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server, port, user, password)
        return client

    # doesn't currently rename the file... which I think is fine
    # def send_model_to_server(self):
    #     local_path = os.path.join(self.config["checkpoint_directory"], 'best.pth.tar')
    #     ssh = self.createSSHClient(self.sensitive_config["worker_server_address"], 22,
    #                                self.sensitive_config["worker_username"], self.sensitive_config["worker_password"])
    #     scp = SCPClient(ssh.get_transport())
    #     scp.put(local_path, self.sensitive_config["distributed_models_directory"])
    #     print("New model uploaded.")

    # def send_training_updates_to_server(self, iteration):
    #     local_path = os.path.join(self.config["checkpoint_directory"], 'training_update.txt')
    #     ssh = self.createSSHClient(self.sensitive_config["worker_server_address"], 22,
    #                                self.sensitive_config["worker_username"], self.sensitive_config["worker_password"])
    #     scp = SCPClient(ssh.get_transport())
    #     scp.put(local_path, self.sensitive_config["distributed_models_directory"])
    #     print("Training update file uploaded.")

    def scan_examples_folder_and_load(self, game_limit):
        files = glob.glob(DIS_EXAMPLE_PATH + "*")

        game_count = 0

        for f in files:
            # game_count >= game_limit, STOP
            """
            if game_count >= game_limit:
                # print("game limit reached")
                break
            """
            if len(self.iterationTrainExamples) >= self.config['max_length_of_queue']:
                break

            # load in the file
            self.load_examples_from_path(f)

            # delete file from storage
            os.remove(f)

            # iterate game_count
            game_count += 1

        return game_count

    def wipe_examples_folder(self):
        files = glob.glob(DIS_EXAMPLE_PATH + "*")

        for f in files:
            os.remove(f)


# TODO: replace this with the StatusBar class, temp for compatibility
def status_bar(step, total_steps, bar_width=45, title="", label="", suffix="", print_perc=True):
    import sys

    # UTF-8 left blocks: 1, 1/8, 1/4, 3/8, 1/2, 5/8, 3/4, 7/8
    utf_8s = ["█", "▏", "▎", "▍", "▌", "▋", "▊", "█"]
    perc = 100 * float(step) / float(total_steps)
    max_ticks = bar_width * 8
    num_ticks = int(round(perc / 100 * max_ticks))
    full_ticks = num_ticks / 8  # Number of full blocks
    part_ticks = num_ticks % 8  # Size of partial block (array index)

    disp = bar = ""  # Blank out variables
    bar += utf_8s[0] * int(full_ticks)  # Add full blocks into Progress Bar

    # If part_ticks is zero, then no partial block, else append part char
    if part_ticks > 0:
        bar += utf_8s[part_ticks]

    # Pad Progress Bar with fill character
    bar += "▒" * int((max_ticks / 8 - float(num_ticks) / 8.0))

    if len(title) > 0:
        disp = title + ": "  # Optional title to progress display

    # Print progress bar in green: https://stackoverflow.com/a/21786287/6929343
    disp += "\x1b[0;32m"  # Color Green
    disp += bar  # Progress bar to progress display
    disp += "\x1b[0m"  # Color Reset
    if print_perc:
        # If requested, append percentage complete to progress display
        if perc > 100.0:
            perc = 100.0  # Fix "100.04 %" rounding error
        disp += " {:6.2f}".format(perc) + " %"
    disp += f"   {step}/{total_steps} {label} {suffix}"

    # Output to terminal repetitively over the same line using '\r'.
    sys.stdout.write("\r" + disp)
    sys.stdout.flush()

    # print newline when finished
    if step >= total_steps:
        print()
