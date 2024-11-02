import time

import numpy as np

from go.go_game import display
from utils.status_bar import StatusBar


class Arena:
    """
    An Arena class where any 2 agents can be pit against each other.
    """

    def __init__(self, player1, player2, game, config):
        """
        Input:
            player 1,2: two functions that takes board as input, return action
            game: Game object
            display: a function that takes board as input and prints it (e.g.
                     display in othello/OthelloGame). Is necessary for verbose
                     mode.

        see othello/OthelloPlayers.py for an example. See pit.py for pitting
        human players/other baselines with each other.
        """
        self.player1 = player1
        self.player2 = player2
        self.game = game
        self.config = config

    def playGame(self, verbose=True):
        """
        Executes one episode of a game.

        Returns:
            either
                winner: player who won the game (1 if player1, -1 if player2)
            or
                draw result returned from the game that is neither 1, -1, nor 0.
        """
        players = [self.player2, None, self.player1]
        curPlayer = 1
        board = self.game.getInitBoard()
        it = 0
        action_history = []
        x_boards = []
        y_boards = []
        c_boards = [np.ones((7, 7)), np.zeros((7, 7))]
        for i in range(8):
            x_boards.append(np.zeros((self.config["board_size"], self.config["board_size"])))
            y_boards.append(np.zeros((self.config["board_size"], self.config["board_size"])))
        while self.game.getGameEndedArena(board, curPlayer) == 0:
            it += 1
            if verbose:
                score = self.game.getScore(board)

                if self.config["display"] == 1:
                    print("\nTurn ", str(it), "Player ", str(curPlayer))
                    print(display(board))
                    print(f"Current score: b {score[0]}, W {score[1]}")
            """canonicalBoard = self.game.getCanonicalForm(board, curPlayer)
            player_board = (c_boards[0], c_boards[1]) if curPlayer == 1 else (c_boards[1], c_boards[0])
            canonicalHistory, x_boards, y_boards = self.game.getCanonicalHistory(x_boards, y_boards,
                                                                                 canonicalBoard, player_board)"""
            # print("History used to make move: ", canonicalHistory)
            #action = players[curPlayer + 1](canonicalBoard, canonicalHistory, x_boards, y_boards, player_board, False, self.config["num_full_search_sims"])
            action = players[curPlayer + 1](board, temp=1, is_full_search=True)
            player_name = "B" if curPlayer == 1 else "W"
            action_history.append(f";{player_name}[{self.game.action_space_to_GTP(action)}]")

            valids = self.game.getValidMoves(board)

            # if valids[action] == 0:
            # print(action)
            # assert valids[action] >0
            board, curPlayer = self.game.getNextState(board, action)
            x_boards, y_boards = y_boards, x_boards

        if verbose:
            # assert(self.display)
            r, score = self.game.getGameEndedArena(board, 1, returnScore=True)

            if self.config["display"] == 1:
                print("\nGame over: Turn ", str(it), "Result ", str(r))
                print(display(board))
                print(f"Final score: b {score[0]}, W {score[1]}\n")
        return self.game.getGameEndedArena(board, 1), action_history

    def playGames(self, num, verbose=True):
        """
        Plays up to num games in which player1 and player2
        alternate which one starts each game.

        Will continue playing up to num games until one of 
        the players has won enough games to meet the threshold.  

        Returns:
            oneWon: games won by player1
            twoWon: games won by player2
            draws:  games won by nobody
        """
        total_time = 0

        eps = 0
        maxeps = int(num)
        originalNum = num

        num = int(num / 2)
        oneWon = 0
        twoWon = 0
        draws = 0

        outcomes = []

        threshold = maxeps * (self.config['acceptance_threshold'])
        for i in range(maxeps):
            start_time = time.time()

            gameResult, action_history = self.playGame(verbose=verbose)
            outcomes.append(action_history)

            if (i%2) == 0:
                if gameResult == 1:
                    oneWon += 1
                elif gameResult == -1:
                    twoWon += 1
                else:
                    draws += 1
            else:
                if gameResult == -1:
                    oneWon += 1
                elif gameResult == 1:
                    twoWon += 1
                else:
                    draws += 1

            eps += 1

            end_time = time.time()
            total_time += round(end_time - start_time, 2)
            status_bar(eps, maxeps,
                       title="Arena", label="Games",
                       suffix=f"| Eps: {round(end_time - start_time, 2)} | Avg Eps: {round(total_time / eps, 2)} | Total: {round(total_time, 2)}")
            
            #If one of the models meets the threshold for games won AND there is more than 1 game left to play, return from arena play
            if (oneWon >= threshold or twoWon >= threshold):
                print(f"\nEnded after {i+1} games\nOne Won: {oneWon} || Two Won: {twoWon} || One %: {oneWon/self.config['acceptance_threshold']} || Two %: {twoWon/self.config['acceptance_threshold']}")
                return oneWon, twoWon, draws, outcomes, (i+1)

            self.player1, self.player2 = self.player2, self.player1

        return oneWon, twoWon, draws, outcomes, maxeps

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