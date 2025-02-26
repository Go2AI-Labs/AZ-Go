import copy
import math
import sys
import os
import datetime
import numpy as np
from heatmap_generator import MapGenerator
from definitions import CONFIG_PATH
from utils.config_handler import ConfigHandler

EPS = 1e-8

class MCTS:
    """
    This class handles the MCTS tree.
    """

    def get_stack_size(self):
        size = 2  # current frame and caller's frame always exist
        while True:
            try:
                sys._getframe(size)
                size += 1
            except ValueError:
                return size - 1  # subtract current frame

    def __init__(self, game, nnet, is_self_play):
        self.game = game
        self.nnet = nnet
        self.config = ConfigHandler(CONFIG_PATH)
        self.cpuct = self.config["c_puct"]

        self.Qsa = {}  # stores Q values for s,a (as defined in the paper)
        self.Nsa = {}  # stores #times edge s,a was visited
        self.Ns = {}  # stores #times board s was visited
        self.Ps = {}  # stores initial policy (returned by neural net)

        self.Es = {}  # stores game.getGameEnded ended for board s
        self.Vs = {}  # stores game.getValidMoves for board s

        self.is_self_play = is_self_play
        self.is_root = True
        self.generator = MapGenerator()
        self.simnum = 0

    def getActionProb(self, board, temp=1, is_full_search=True):
        """
        This function performs numMCTSSims simulations of MCTS starting from
        canonicalBoard.

        Returns:
            probs: a policy vector where the probability of the ith action is
                   proportional to Nsa[(s,a)]**(1./temp)
        """
        num_sims = self.config["num_full_search_sims"]

        for i in range(num_sims):
            self.restore_root_state()
            self.search(board)

        s = board.getStringRepresentation()
        player = board.current_player
        counts = np.array([self.Nsa[(s, a)][player] if (s, a) in self.Nsa and player in self.Nsa[(s, a)] else 0 for a in range(self.game.getActionSize())])
        
        # if np.sum(counts) == 0:
        #     counts = valids
        # else:
        #     counts *= valids

        if temp == 0:
            bestAs = np.array(np.argwhere(counts == np.max(counts))).flatten()
            bestA = np.random.choice(bestAs)
            probs = [0] * len(counts)
            probs[bestA] = 1
            return probs

        counts = [x ** (1. / temp) for x in counts]
        counts_sum = float(sum(counts))
        probs = [x / counts_sum for x in counts]
        return probs

    def search(self, board):
        """
        This function performs one iteration of MCTS. It is recursively called
        till a leaf node is found. The action chosen at each node is one that
        has the maximum upper confidence bound as in the paper.

        Once a leaf node is found, the neural network is called to return an
        initial policy P and a value v for the state. This value is propogated
        up the search path. In case the leaf node is a terminal state, the
        outcome is propogated up the search path. The values of Ns, Nsa, Qsa are
        updated.

        NOTE: the return values are the negative of the value of the current
        state. This is done since v is in [-1,1] and if v is the value of a
        state for the current player, then its value is -v for the other player.

        Returns:
            v: the negative of the value of the current canonicalBoard
        """
        player = board.current_player
        s = board.getStringRepresentation()
        # Check if simulation has reached a terminal state
        if s not in self.Es or (s in self.Es and player not in self.Es[s]):
            if s not in self.Es:
                self.Es[s] = {}
            self.Es[s][player] = self.game.getGameEndedSelfPlay(board)
        elif s in self.Es and (len(board.history) > 1 and (board.history[-1] is None and board.history[-2] is None)):
            self.Es[s][player] = self.game.getGameEndedSelfPlay(board)
        if self.Es[s][player] != 0 and self.Es[s][player] is not None:
            # terminal node
            return -self.Es[s][player]

        if s not in self.Ps or (s in self.Ps and player not in self.Ps[s]):
            p, v = self.predict(board)
            if s not in self.Ps:
                self.Ps[s] = {}
                self.Vs[s] = {}
                self.Ns[s] = {}
            self.Ps[s][player] = p
            valids = self.game.getValidMoves(board)
            self.Ps[s][player] = self.Ps[s][player] * valids  # masking invalid moves
            sum_Ps_s = np.sum(self.Ps[s][player])
            if sum_Ps_s > 0:
                self.Ps[s][player] /= sum_Ps_s  # renormalize
            else:
                # if all valid moves were masked make all valid moves equally probable

                # NB! All valid moves may be masked if either your NNet architecture is insufficient or you've get overfitting or something else.
                # If you have got dozens or hundreds of these messages you should pay attention to your NNet and/or training process.
                # log.error("All valid moves were masked, doing a workaround.")
                print("All valid moves were masked, doing a workaround...")
                self.Ps[s][player] = self.Ps[s][player] + valids
                self.Ps[s][player] /= np.sum(self.Ps[s][player])

            self.Vs[s][player] = valids
            self.Ns[s][player] = 0
            return -v

        valids = self.Vs[s][player]
        # Check if ko changed between first time board state 's' is encountered
        # and subsequent encounters throughout MCTS
        if board.ko is not None:
            invalid = board.ko[0]*7 + board.ko[1]
            valids[invalid] = 0
        cur_best = -float('inf')
        best_act = -1

        # print("Valids in MCTS: ", valids)
        # pick the action with the highest upper confidence bound
        # add noise for root node prior probabilities (encourages exploration)
         # Initialize dirichlet noise to be used at the root during self play
        if self.is_root and self.is_self_play:
            noise = np.random.dirichlet([0.03] * len(self.game.filter_valid_moves(valids)))
            # use to keep track of index of next move's dirichlet noise if being used
            noise_idx = -1 
    
        # pick the action with the highest upper confidence bound
        for a in range(self.game.getActionSize()):
            if valids[a]:
                if (s, a) in self.Qsa and player in self.Qsa[(s, a)] and self.Qsa[(s, a)][player] != None:
                    q = self.Qsa[(s, a)][player]
                    n_sa = self.Nsa[(s, a)][player]
                    ns = self.Ns[s][player]
                    """u = self.Qsa[(s, a)] + self.c_puct * self.Ps[s][a] * math.sqrt(self.Ns[s]) / (
                            1 + self.Nsa[(s, a)])"""
                else:
                    q = 0
                    n_sa = 0
                    ns = self.Ns[s][player] + EPS
                    """u = self.c_puct * self.Ps[s][a] * math.sqrt(self.Ns[s] + EPS)  # Q = 0 ?"""
                p = self.Ps[s][player][a]
                if self.is_root and self.is_self_play:
                    noise_idx += 1
                    p = (1 - 0.25) * p + 0.25 * noise[noise_idx]
                u = q + self.cpuct * p * math.sqrt(ns) / (1 + n_sa)

                if u > cur_best:
                    cur_best = u
                    best_act = a
        a = best_act

        # Returns a copy of the board state and the next player to play
        next_s = self.game.getNextState(board, a)
        self.is_root = False
        v = self.search(next_s)

        if (s, a) in self.Qsa and player in self.Qsa[(s, a)]:
            self.Qsa[(s, a)][player] = (self.Nsa[(s, a)][player] * self.Qsa[(s, a)][player] + v) / (self.Nsa[(s, a)][player] + 1)
            self.Nsa[(s, a)][player] += 1

        else:
            if (s, a) not in self.Qsa:
                self.Qsa[(s, a)] = {}
                self.Nsa[(s, a)] = {}
            self.Qsa[(s, a)][player] = v
            self.Nsa[(s, a)][player] = 1

        self.Ns[s][player] += 1
        return -v
    
    def predict(self, board):
        # randomly rotate and flip before network predict
        r = np.random.randint(8)
        nnet_input = board.get_canonical_history()
        nnet_input = board.rotate_history(r, nnet_input)
        pi, v = self.nnet.predict(nnet_input)

        # policy need to rotate and flip back
        pi_board = np.reshape(pi[:-1], (self.game.n, self.game.n))
        if r >= 4:
            pi_board = np.fliplr(pi_board)
        pi_board = np.rot90(pi_board, 4 - r % 4)
        p = list(pi_board.ravel()) + [pi[-1]]

        return p, v
    
    def restore_root_state(self):
        self.is_root = True

    def update_next_mcts_state(self):
        self.is_root = False 

    def get_Q_vals(self, s, player):
        q_vals = []
        for a in range(self.game.getActionSize()):
            if (s,a) in self.Qsa and player in self.Qsa[(s,a)]:
                try:
                    q_vals.append(self.Qsa[(s,a)][player][-1])
                except:
                    q_vals.append(self.Qsa[(s,a)][player])
            else:
                q_vals.append(0.0)
        return q_vals
    
    def get_u_map(self, fmtd_arr, raw_arr):
        u_val_map = self.generator.init_new_map()
        u_val_map, percentages =self.generator.generate_map(u_val_map, raw_arr, 0, use_val_colors=True)
        name = f"UVALS_call_{self.simnum}.png"
        uval_image = self.generator.draw_text(u_val_map, percentages, use_val_size=True)
        self.generator.save_image(uval_image, name)
