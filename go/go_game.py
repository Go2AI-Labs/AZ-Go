from __future__ import print_function

import numpy as np

from go.game import Game
from go.go_logic import Board
from itertools import permutations


class GoGame(Game):

    # TODO: should is_engine_game be a part of config.yaml instead?
    # I don't think we want to couple engine code and the GoGame class - HL
    def __init__(self, n, is_arena_game=False):
        super().__init__()
        self.n = n
        self.is_arena_game = is_arena_game
        self.stay_alive_threshold = 0.4

    def getInitBoard(self):
        # return initial board (numpy board)
        b = Board(self.n)
        return b

    def getBoardSize(self):
        # (a,b) tuple
        return (self.n, self.n)

    def getActionSize(self):
        # return number of actions
        return (self.n * self.n) + 1

    def getNextState(self, board, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        # print("getting next state from perspect of player {} with action {}".format(player,action))

        b = board.copy()
        if action == (self.n * self.n):
            move = None
        else:
            move = (int(action / self.n), action % self.n)
        b.execute_move(move, b.current_player)

        return b

    # modified
    #def getValidMoves(self, board, player, is_self_play):
    def getValidMoves(self, board):
        # return a fixed size binary vector
        valids = [0 for i in range(self.getActionSize())]
        #b = board.copy()
        legalMoves = board.get_legal_moves(board.current_player)
        valids[-1] = 1

        if self.is_arena_game and len(board.history) < 5:
            valids[-1] = 0

        if len(legalMoves) == 0:
            return np.array(valids)
        for x, y in legalMoves:
            valids[self.n * x + y] = 1
        return np.array(valids)

    def filter_valid_moves(self, valids):
        filtered = []
        for v in valids:
            if v != 0:
                filtered.append(v)
        return filtered

    # Self play games can terminate according to:
    #   - A dynamic score threshold (todo)
    #   - A move threshold (7 x 7 x 2 = 98)
    #   - Both players passing
    # Self play uses Tromp-Taylor rules (todo)
    def getGameEndedSelfPlay(self, board, return_score=False, mcts=None):
        winner = 0
        score_is_cached = False
        score = None
        if mcts is not None:
            canonicalBoard = self.getCanonicalForm(board, board.current_player)
            score_is_cached, score = mcts.checkScoreCache(canonicalBoard)
        if score_is_cached:
            (score_black, score_white) = score
        else:
            (score_black, score_white) = self.getScore(board)
        by_score = 0.5 * ((board.n * board.n) + board.komi)
        black_difference = score_black - score_white
        white_difference = score_white - score_black

        # determine maximum number of allowed moves
        """max_moves = 0
        if iteration < 11:
            # iteration 1 to 10
            max_moves = 25
        elif iteration < 21:
            # iteration 11 to 20
            max_moves = 50
        elif iteration < 31:
            # iteration 21 to 30
            max_moves = 75
        else:"""
        # iteration 31 and higher
        """max_moves = 98

        # limit games to 98 moves, determine winner based on score of current board
        if len(board.history) >= max_moves:
            if score_black > score_white:
                if player == 1:
                    winner = 1
                else:
                    winner = -1
            elif score_white > score_black:
                if player == -1:
                    winner = 1
                else:
                    winner = -1
            else:
                # Tie
                winner = 1e-4"""

        # End game "normally"
        #if enable_resignation_threshold and len(board.history) > 1:
        if len(board.history) > 3:
            # Check if both players passed in succession
            #print(f"History Length > 1 -- [-1] = {board.history[-1]} -- [-2] = {board.history[-2]}")
            if board.history[-1] is None and board.history[-2] is None:
                if score_black > score_white:
                    if board.current_player == 1:
                        winner = 1
                    else:
                        winner = -1
                elif score_white > score_black:
                    if board.current_player == -1:
                        winner = 1
                    else:
                        winner = -1
                else:
                    # Tie
                    winner = 1e-4
            # score threshold is enabled, games can be ended early based on score
            elif black_difference > by_score or white_difference > by_score:
                print("Self play ended early by score threshold")
                if score_black > score_white:
                    if board.current_player == 1:
                        winner = 1
                    else:
                        winner = -1
                elif score_white > score_black:
                    if board.current_player == -1:
                        winner = 1
                    else:
                        winner = -1
                else:
                    # Tie
                    winner = 1e-4
            # allow maximum number of moves to end game in self play scoring
            elif len(board.history) >= 98:
                print("Self play ended by maximum move count reached")
                if score_black > score_white:
                    if board.current_player == 1:
                        winner = 1
                    else:
                        winner = -1
                elif score_white > score_black:
                    if board.current_player == -1:
                        winner = 1
                    else:
                        winner = -1
                else:
                    # Tie
                    winner = 1e-4

        if return_score:
            return winner, (score_black, score_white)

        return winner

    # Arena games can terminate according to:
    #   - A move threshold (7 x 7 x 2 = 98)
    #   - Both players passing
    # Arena uses the Chinese ruleset (todo)
    def getGameEndedArena(self, board, returnScore=False):
        winner = 0
        (score_black, score_white) = self.getScore(board)

        # limit games to 98 moves, determine winner based on score of current board
        if len(board.history) >= 98:
            if score_black > score_white:
                #if board.current_player == 1:
                winner = 1
                """else:
                    winner = -1"""
            elif score_white > score_black:
                #if board.current_player == -1:
                winner = -1
                """else:
                    winner = -1"""
            else:
                # Tie
                winner = 1e-4

        elif len(board.history) > 1:
            # score threshold (by_score) is disabled, both players must pass to end game (or until 98 moves reached)
            if board.history[-1] is None and board.history[-2] is None:
                if score_black > score_white:
                    #if board.current_player == 1:
                    winner = 1
                    """else:
                        winner = -1"""
                elif score_white > score_black:
                    #if board.current_player == -1:
                    winner = -1
                    """else:
                        winner = -1"""
                else:
                    # Tie
                    winner = 1e-4

        if returnScore:
            return winner, (score_black, score_white)
        return winner

    # tromp taylor
    def getScore(self, board):
        score_white = np.sum(board.pieces == -1)
        score_black = np.sum(board.pieces == 1)
        # empties = zip(*np.where(board.pieces == 0))
        """if len(board.history) > 1:
            print(f"History > 1 -- [-1] = {board.history[-1]} -- [-2] = {board.history[-2]}")"""
        """print(f"Empties: {empties}")
        print(f"Score black before eye: {score_black}")
        print(f"Score white before eye: {score_white}")"""
        """for empty in empties:
            # Check that all surrounding points are of one color
            if board.is_eyeish(empty, 1):
                #print(f"Black Eye at {empty}")
                score_black += 1
            elif board.is_eyeish(empty, -1):
                #print(f"White Eye at {empty}")
                score_white += 1"""
        score_white += board.komi
        reach_mat = np.zeros((7, 7, 2))
        reach_mat = self.get_reachable(board, reach_mat)
        for i in range(7):
            for j in range(7):
                if reach_mat[i][j][0] == 1 and reach_mat[i][j][1] == 0:
                    score_black += 1
                elif reach_mat[i][j][0] == 0 and reach_mat[i][j][1] == 1:
                    score_white += 1
                #print(f"({reach_mat[i][j][0]}, {reach_mat[i][j][1]})", end="  ")
            #print()
        """for i in range(7):
            for j in range(7):
                print(f"({i}, {j}) - {board.group_sets[i][j]}")
                for coord in board.group_sets[i][j]:
                    
                print()
            print()"""
        """for i in range(7):
            for j in range(7):
                print(f"({i}, {j}) - {board.liberty_sets[i][j]}")
            print("\n")"""
        #print(f"Black: {score_black}, White: {score_white}")
        if len(board.history) > 10 and board.history[-1] is not None:
            score_black, score_white = self.get_dead_stones(board, score_black, score_white, reach_mat)
        else:
            print("NOT CHECKING DEADSTONES")
        """score_white -= board.passes_white
        score_black -= board.passes_black"""
        return (score_black, score_white)

    # old score implementation, same as repo we originally forked from
    def getScore_old_system(self, board):
        score_white = np.sum(board.pieces == -1)
        score_black = np.sum(board.pieces == 1)
        empties = zip(*np.where(board.pieces == 0))
        for empty in empties:
            # Check that all surrounding points are of one color
            if board.is_eyeish(empty, 1):
                score_black += 1
            elif board.is_eyeish(empty, -1):
                score_white += 1
        score_white += board.komi
        score_white -= board.passes_white
        score_black -= board.passes_black
        return (score_black, score_white)
    
    def get_dead_stones(self, board, score_black, score_white, reach_mat):
        """
        Method to identify dead stones on the board and adjust the score accordingly
        """
        """
        Get the horizontal and vertical groups that may border deadstone territories
        """
        vertical_groups, horizontal_groups = self.get_deadstone_groups(board)

        """
        Calculate deadstone terriorites for the current board state
        --> 'dead_territories' is a dictionary holding information about 'dead territories' on the current board
            in the form (starting column, starting row, territory owner)
        """
        dead_territories, dead_territories_exist = self.get_deadstone_territories(board, vertical_groups, horizontal_groups)
        if not dead_territories_exist:
            return score_black, score_white
        
        """
        Simulate playouts within 'deadstone territories' to determine if stones within the territory are actually dead
        """
        left_above_deadstones, left_below_deadstones, right_above_deadstones, right_below_deadstones = self.handle_deadstone_simulations(board, dead_territories, reach_mat)
        
        """
        Calculate score accounting for deadstones
        """
        score_black, score_white = self.calculate_deadstone_score(board, dead_territories, left_above_deadstones, left_below_deadstones, right_above_deadstones, right_below_deadstones, score_black, score_white)
        # print(f"\nAfter Removing Deadstones, Score :: Black: {score_black}, White: {score_white}")
        return score_black, score_white
    
    def get_deadstone_groups(self, board):
        vertical_groups = []
        # Check for 'vertical groups'
        for c in range(1, 6, 1):
            # Check groups starting at row 0
            current_group_top = board.group_sets[0][c]
            if len(current_group_top) >= 3:
                visited_intersections = [False for _ in range(7)]
                visited_intersections[0] = True
                for coords in current_group_top:
                    if coords[1] == c:
                        visited_intersections[coords[0]] = True
                vr_max = -1
                for r in range(7):
                    if visited_intersections[r] == True:
                        vr_max += 1
                    else:
                        break
                vertical_groups.append((0, vr_max, c))
            # Check groups starting at row 6
            current_group_bottom = board.group_sets[6][c]
            if len(current_group_bottom) >= 3:
                visited_intersections = [False for _ in range(7)]
                visited_intersections[6] = True
                for coords in current_group_bottom:
                    if coords[1] == c:
                        visited_intersections[coords[0]] = True
                vr_min = 7
                for r in range(6, -1, -1):
                    if visited_intersections[r] == True:
                        vr_min -= 1
                    else:
                        break
                if (vr_min, 6, c) not in vertical_groups:
                    vertical_groups.append((vr_min, 6, c)) 
        # Check for horizontal groups
        horizontal_groups = []
        for r in range(1, 6, 1):
            # Check groups starting at column 0
            current_group_left = board.group_sets[r][0]
            if len(current_group_left) >= 3:
                visited_intersections = [False for _ in range(7)]
                visited_intersections[0] = True
                for coords in current_group_left:
                    if coords[0] == r:
                        visited_intersections[coords[1]] = True
                hc_max = -1
                for c in range(7):
                    if visited_intersections[c] == True:
                        hc_max += 1
                    else:
                        break
                horizontal_groups.append((0, hc_max, r))
            # Check groups starting at column 6
            current_group_right = board.group_sets[r][6]
            if len(current_group_right) >= 3:
                visited_intersections = [False for _ in range(7)]
                visited_intersections[6] = True
                for coords in current_group_right:
                    if coords[0] == r:
                        visited_intersections[coords[1]] = True
                hc_min = 7
                for c in range(6, -1, -1):
                    if visited_intersections[c] == True:
                        hc_min -= 1
                    else:
                        break
                if (hc_min, 6, r) not in horizontal_groups:
                    horizontal_groups.append((hc_min, 6, r))
        return vertical_groups, horizontal_groups
    
    def get_deadstone_territories(self, board, vertical_groups, horizontal_groups):
        dead_territories = {
            'left_above': (-1, -1, 0),
            'left_below': (-1, 7, 0),
            'right_above': (7, -1, 0),
            'right_below': (7, 7, 0)
        }
        current_board = board.pieces
        dead_territories_exist = False
        # Loop through groups to find if there are any 'dead territories' on the board
        for i in range(len(vertical_groups)):
            current_vg = vertical_groups[i]
            row_min = current_vg[0]
            row_max = current_vg[1]
            col_number = current_vg[2]
            if current_board[row_min][col_number] == 1:
                vg_color = 1
            else:
                vg_color = -1
            for j in range(len(horizontal_groups)):
                current_hg = horizontal_groups[j]
                col_min = current_hg[0]
                col_max = current_hg[1]
                row_number = current_hg[2]
                # If the horizontal group is outside the range of the vertical group, continue
                if row_number > row_max+1 or row_number < row_min-1:
                    continue
                if current_board[row_number][col_min] == 1:
                    hg_color = 1
                else:
                    hg_color = -1
                # If colors of the horizontal and vertical group don't match, continue
                if vg_color != hg_color:
                    continue
                # Check if the horizontal and vertical group intersect to form a deadstone region
                possible_intersection = False
                is_left = False
                is_right = False
                is_above = False
                is_below = False
                # Check if the horizontal group may form an intersection
                if col_min == 0 and col_max == 6:
                    possible_intersection = True
                    is_left = True
                    is_right = True
                elif col_max == col_number or col_max == col_number-1:
                    possible_intersection = True
                    is_left = True
                elif col_min == col_number or col_min == col_number+1:
                    possible_intersection = True
                    is_right = True
                # Continue if an intersection is not possible
                if not possible_intersection:
                    continue
                # Check if the vertical group may form an intersection
                if row_min == 0 and row_max == 6:
                    is_above = True
                    is_below = True
                elif row_max == row_number or row_max == row_number-1:
                    is_above = True
                elif row_min == row_number or row_min == row_number+1:
                    is_below = True
                # Continue if an intersection is not possible
                if not is_above and not is_below:
                    continue
                # Assign values to the proper deadstone region if it exists
                if is_left and is_above and row_min == 0 and col_min == 0:
                    if col_number > dead_territories['left_above'][0] and row_number > dead_territories['left_above'][1]:
                        dead_territories['left_above'] = (col_number, row_number, hg_color)
                        dead_territories_exist = True
                if is_left and is_below and row_max == 6 and col_min == 0:
                    if col_number > dead_territories['left_below'][0] and row_number < dead_territories['left_below'][1]:
                        dead_territories['left_below'] = (col_number, row_number, hg_color)
                        dead_territories_exist = True
                if is_right and is_above and row_min == 0 and col_max == 6:
                    if col_number < dead_territories['right_above'][0] and row_number > dead_territories['right_above'][1]:
                        dead_territories['right_above'] = (col_number, row_number, hg_color)
                        dead_territories_exist = True
                if is_right and is_below and row_max == 6 and col_max == 6:
                    if col_number < dead_territories['right_below'][0] and row_number < dead_territories['right_below'][1]:
                        dead_territories['right_below'] = (col_number, row_number, hg_color)
                        dead_territories_exist = True

        return dead_territories, dead_territories_exist
    
    def handle_deadstone_simulations(self, board, dead_territories, reach_mat):
        # Simulate for lower-right region if there is one
        start_r = dead_territories['right_below'][1]
        start_c = dead_territories['right_below'][0]
        right_below_deadstones = False
        if start_r != 7 and start_c != 7:
            # print("\nRIGHT BELOW")
            move_combos, contested_intersections_count = self.get_move_permutations(start_r+1, 7, start_c+1, 7, reach_mat, dead_territories['right_below'][2])
            print(contested_intersections_count)
            if contested_intersections_count > 0 and contested_intersections_count <= 2:
                right_below_deadstones = True
            elif contested_intersections_count > 0 and (contested_intersections_count < 5 or (dead_territories['right_below'][2] == board.current_player and contested_intersections_count == 5)):
                right_below_deadstones = self.deadstone_simulation(board.copy(), move_combos, start_r+1, 7, start_c+1, 7, dead_territories['right_below'][2])
        # Simulate for lower-left region if there is one
        start_r = dead_territories['left_below'][1]
        start_c = dead_territories['left_below'][0]
        left_below_deadstones = False
        if start_r != 7 and start_c != -1:
            # print("\nLEFT BELOW")
            move_combos, contested_intersections_count = self.get_move_permutations(start_r+1, 7, 0, start_c, reach_mat, dead_territories['left_below'][2])
            if contested_intersections_count > 0 and contested_intersections_count <= 2:
                left_below_deadstones = True

            elif contested_intersections_count > 0 and (contested_intersections_count < 5 or (dead_territories['left_below'][2] == board.current_player and contested_intersections_count == 5)):
                left_below_deadstones = self.deadstone_simulation(board.copy(), move_combos, start_r+1, 7, 0, start_c, dead_territories['left_below'][2])
        # Simulate for upper-left region if there is one
        start_r = dead_territories['left_above'][1]
        start_c = dead_territories['left_above'][0]
        left_above_deadstones = False
        if start_r != -1 and start_c != -1:
            # print("\nLEFT ABOVE")
            move_combos, contested_intersections_count = self.get_move_permutations(0, start_r, 0, start_c, reach_mat, dead_territories['left_above'][2])
            if contested_intersections_count > 0 and contested_intersections_count <= 2:
                left_above_deadstones = True
            elif contested_intersections_count > 0 and (contested_intersections_count < 5 or (dead_territories['left_above'][2] == board.current_player and contested_intersections_count == 5)):
                left_above_deadstones = self.deadstone_simulation(board.copy(), move_combos, 0, start_r, 0, start_c, dead_territories['left_above'][2])
        # Simulate for upper-right region if there is one
        start_r = dead_territories['right_above'][1]
        start_c = dead_territories['right_above'][0]
        right_above_deadstones = False
        if start_r != -1 and start_c != 7:
            # print("\nRIGHT ABOVE")
            move_combos, contested_intersections_count = self.get_move_permutations(0, start_r, start_c+1, 0, reach_mat, dead_territories['right_above'][2])
            if contested_intersections_count > 0 and contested_intersections_count <= 2:
                right_above_deadstones = True
            elif contested_intersections_count > 0 and (contested_intersections_count < 5 or (dead_territories['right_above'][2] == board.current_player and contested_intersections_count == 5)):
                right_above_deadstones = self.deadstone_simulation(board.copy(), move_combos, 0, start_r, start_c+1, 0, dead_territories['right_above'][2])
        
        return left_above_deadstones, left_below_deadstones, right_above_deadstones, right_below_deadstones

    def get_move_permutations(self, start_r, end_r, start_c, end_c, reach_mat, dt_owner):
        reach_test_contested = np.array([1, 1])
        reach_test_white = np.array([0, 1])
        reach_test_black = np.array([1, 0])
        contested_intersections_count = 0
        white_intersections_count = 0
        black_intersections_count = 0
        dt_moves = []
        for i in range(start_r, end_r):
            for j in range(start_c, end_c):
                if np.array_equal(reach_mat[i, j], reach_test_contested) or (dt_owner == -1 and np.array_equal(reach_mat[i, j], reach_test_black)) or (dt_owner == 1 and np.array_equal(reach_mat[i, j], reach_test_white)):
                    contested_intersections_count += 1
                    new_move = i*7 + j
                    dt_moves.append(new_move)
                elif np.array_equal(reach_mat[i, j], reach_test_black):
                    black_intersections_count += 1
                elif np.array_equal(reach_mat[i, j], reach_test_white):
                    white_intersections_count += 1
        if contested_intersections_count <= 5 and contested_intersections_count > 2:
            move_combos = list(permutations(dt_moves))
            return move_combos, contested_intersections_count
        else:
            return None, contested_intersections_count
    
    def deadstone_simulation(self, board, move_combos, start_r, end_r, start_c, end_c, dt_owner):
        # print(f"MOVE COMBOS: {len(move_combos)}")
        stay_alive_count = 0
        stones_are_dead = False
        for m in range(len(move_combos)):
            curr_moves = move_combos[m]
            test_board = board.copy()
            for i in range(len(curr_moves)):
                try:
                    test_board = self.getNextState(test_board, curr_moves[i])
                except:
                    # print(f"Exception for move: {curr_moves[i]}")
                    continue
            reach_mat = np.zeros((7, 7, 2))
            reach_mat = self.get_reachable(test_board, reach_mat)
            reach_test_white = np.array([0, 1])
            reach_test_black = np.array([1, 0])
            white_intersections_count = 0
            black_intersections_count = 0
            for r in range(start_r, end_r):
                for c in range(start_c, end_c):
                    if np.array_equal(reach_mat[r, c], reach_test_black):
                        black_intersections_count += 1
                    elif np.array_equal(reach_mat[r, c], reach_test_white):
                        white_intersections_count += 1
            if white_intersections_count >= 2 and dt_owner == 1:
                # print(f"SIM Board:\n{test_board.pieces}\nWhite Intersec: {white_intersections_count}, Black Intersec: {black_intersections_count}")
                stay_alive_count += 1
            elif black_intersections_count >= 2 and dt_owner == -1:
                # print(f"White Intersec: {white_intersections_count}, Black Intersec: {black_intersections_count}")
                stay_alive_count += 1
            if (stay_alive_count + len(move_combos)-(m+1))/len(move_combos) <= self.stay_alive_threshold or stay_alive_count/len(move_combos) > self.stay_alive_threshold:
                break
        # print(f"Player {-dt_owner} Stay Alive Count: {stay_alive_count}")
        if stay_alive_count/len(move_combos) <= self.stay_alive_threshold:
            stones_are_dead = True
            # print("WILL REMOVE DEADSTONES")
        return stones_are_dead

    def calculate_deadstone_score(self, board, dead_territories, left_above_deadstones, left_below_deadstones, right_above_deadstones, right_below_deadstones, score_black, score_white):
        if left_above_deadstones:
            for i in range(0, dead_territories['left_above'][1]):
                for j in range(0, dead_territories['left_above'][0]):
                    if board.pieces[i][j] == 1 and dead_territories['left_above'][2] == -1:
                        score_black -= 1
                        score_white += 1
                    elif board.pieces[i][j] == -1 and dead_territories['left_above'][2] == 1:
                        score_white -= 1
                        score_black += 1
        if left_below_deadstones:
            for i in range(dead_territories['left_below'][1], 7):
                for j in range(0, dead_territories['left_below'][0]):
                    if board.pieces[i][j] == 1 and dead_territories['left_below'][2] == -1:
                        score_black -= 1
                        score_white += 1
                    elif board.pieces[i][j] == -1 and dead_territories['left_below'][2] == 1:
                        score_white -= 1
                        score_black += 1
                    if board.pieces[i][j] == 0 and dead_territories['left_below'][2] == -1:
                        score_white += 1
                    elif board.pieces[i][j] == 0 and dead_territories['left_below'][2] == 1:
                        score_black += 1
        if right_above_deadstones:
            for i in range(0, dead_territories['right_above'][1]):
                for j in range(dead_territories['right_above'][0], 7):
                    if board.pieces[i][j] == 1 and dead_territories['right_above'][2] == -1:
                        score_black -= 1
                        score_white += 1
                    elif board.pieces[i][j] == -1 and dead_territories['right_above'][2] == 1:
                        score_white -= 1
                        score_black += 1
        if right_below_deadstones:
            for i in range(dead_territories['right_below'][1], 7):
                for j in range(dead_territories['right_below'][0], 7):
                    if board.pieces[i][j] == 1 and dead_territories['right_below'][2] == -1:
                        score_black -= 1
                        score_white += 1
                    elif board.pieces[i][j] == -1 and dead_territories['right_below'][2] == 1:
                        score_white -= 1
                        score_black += 1
                    if board.pieces[i][j] == 0 and dead_territories['right_below'][2] == -1:
                        score_white += 1
                    elif board.pieces[i][j] == 0 and dead_territories['right_below'][2] == 1:
                        score_black += 1
        
        return score_black, score_white


    def get_reachable(self, board, reach_mat):
        changed = []
        for i in range(7):
            for j in range(7):
                if board.pieces[i][j] == 1:
                    color_idx = 0
                elif board.pieces[i][j] == -1:
                    color_idx = 1
                else:
                    continue
                for k in range(i - 1, -1, -1):
                    if board.pieces[k][j] == 0 and reach_mat[k][j][color_idx] == 0:
                        reach_mat[k][j][color_idx] = 1
                        changed.append((k, j))
                    else:
                        break
                for k in range(i + 1, 7, 1):
                    if board.pieces[k][j] == 0 and reach_mat[k][j][color_idx] == 0:
                        reach_mat[k][j][color_idx] = 1
                        changed.append((k, j))
                    else:
                        break
                for k in range(j - 1, -1, -1):
                    if board.pieces[i][k] == 0 and reach_mat[i][k][color_idx] == 0:
                        reach_mat[i][k][color_idx] = 1
                        changed.append((i, k))
                    else:
                        break
                for k in range(j + 1, 7, 1):
                    if board.pieces[i][k] == 0 and reach_mat[i][k][color_idx] == 0:
                        reach_mat[i][k][color_idx] = 1
                        changed.append((i, k))
                    else:
                        break
        for p in range(len(changed)):
            i = changed[p][0]
            j = changed[p][1]
            if board.pieces[i][j] == 0:
                if i > 0:
                    for k in range(i - 1, -1, -1):
                        if board.pieces[k][j] != 0:
                            break
                        if reach_mat[k][j][0] == 0 and reach_mat[i][j][0] == 1:
                            reach_mat[k][j][0] = 1
                        if reach_mat[k][j][1] == 0 and reach_mat[i][j][1] == 1:
                            reach_mat[k][j][1] = 1
                if i < 6:
                    for k in range(i + 1, 7, 1):
                        if board.pieces[k][j] != 0:
                            break
                        if reach_mat[k][j][0] == 0 and reach_mat[i][j][0] == 1:
                            reach_mat[k][j][0] = 1
                        if reach_mat[k][j][1] == 0 and reach_mat[i][j][1] == 1:
                            reach_mat[k][j][1] = 1
                if j > 0:
                    for k in range(j - 1, -1, -1):
                        if board.pieces[i][k] != 0:
                            break
                        if reach_mat[i][k][0] == 0 and reach_mat[i][j][0] == 1:
                            reach_mat[i][k][0] = 1
                        if reach_mat[i][k][1] == 0 and reach_mat[i][j][1] == 1:
                            reach_mat[i][k][1] = 1
                if j < 6:
                    for k in range(j + 1, 7, 1):
                        if board.pieces[i][k] != 0:
                            break
                        if reach_mat[i][k][0] == 0 and reach_mat[i][j][0] == 1:
                            reach_mat[i][k][0] = 1
                        if reach_mat[i][k][1] == 0 and reach_mat[i][j][1] == 1:
                            reach_mat[i][k][1] = 1
        for i in range(7):
            for j in range(7):
                if board.pieces[i][j] != 0:
                    continue
                elif board.pieces[i][j] == 0 and (reach_mat[i][j][0] != 1 or reach_mat[i][j][1] != 1):
                    if i > 0:
                        for k in range(i - 1, -1, -1):
                            if board.pieces[k][j] != 0 or (reach_mat[i][j][0] == 1 and reach_mat[i][j][1] == 1):
                                break
                            if reach_mat[k][j][0] == 1 and reach_mat[i][j][0] == 0:
                                reach_mat[i][j][0] = 1
                            if reach_mat[k][j][1] == 1 and reach_mat[i][j][1] == 0:
                                reach_mat[i][j][1] = 1
                    if i < 6:
                        for k in range(i + 1, 7, 1):
                            if board.pieces[k][j] != 0 or (reach_mat[i][j][0] == 1 and reach_mat[i][j][1] == 1):
                                break
                            if reach_mat[k][j][0] == 1 and reach_mat[i][j][0] == 0:
                                reach_mat[i][j][0] = 1
                            if reach_mat[k][j][1] == 1 and reach_mat[i][j][1] == 0:
                                reach_mat[i][j][1] = 1
                    if j > 0:
                        for k in range(j - 1, -1, -1):
                            if board.pieces[i][k] != 0 or (reach_mat[i][j][0] == 1 and reach_mat[i][j][1] == 1):
                                break
                            if reach_mat[i][k][0] == 1 and reach_mat[i][j][0] == 0:
                                reach_mat[i][j][0] = 1
                            if reach_mat[i][k][1] == 1 and reach_mat[i][j][1] == 0:
                                reach_mat[i][j][1] = 1
                    if j < 6:
                        for k in range(j + 1, 7, 1):
                            if board.pieces[i][k] != 0 or (reach_mat[i][j][0] == 1 and reach_mat[i][j][1] == 1):
                                break
                            if reach_mat[i][k][0] == 1 and reach_mat[i][j][0] == 0:
                                reach_mat[i][j][0] = 1
                            if reach_mat[i][k][1] == 1 and reach_mat[i][j][1] == 0:
                                reach_mat[i][j][1] = 1
        return reach_mat

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        canonicalBoard = board.copy()

        # canonicalBoard.pieces= board.pieces* player
        if player == -1:
            canonicalBoard.pieces = np.where(canonicalBoard.pieces == 1, -1,
                                             np.where(canonicalBoard.pieces == -1, 1, canonicalBoard.pieces))
        return canonicalBoard

    # modified
    def getSymmetries(self, board, pi):
        # mirror, rotational
        assert (len(pi) == self.n ** 2 + 1)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (self.n, self.n))
        l = []
        history_syms = []
        # b_pieces = board.pieces
        for i in range(1, 5):
            for j in [True, False]:
                history_syms = []
                for k in range(len(board)):
                    newB = np.rot90(board[k], i)
                    if j:
                        newB = np.fliplr(newB)
                    history_syms.append(newB)
                newPi = np.rot90(pi_board, i)
                if j:
                    newPi = np.fliplr(newPi)
                l += [(history_syms, list(newPi.ravel()) + [pi[-1]])]
        return l

    def stringRepresentation(self, board):
        # 8x8 numpy array (canonical board)
        return np.array(board.pieces).tostring()

    def getCanonicalHistory(self, x_boards, y_boards, canonicalBoard, player_board):
        history = []
        board_pieces = canonicalBoard.pieces
        new_x = np.copy(board_pieces)

        if -1 in board_pieces:
            new_x[new_x == -1] = 0
        else:
            new_x = board_pieces

        x_boards.append(new_x)

        board_pieces = np.where(board_pieces == 1, -1, np.where(board_pieces == -1, 1, board_pieces))

        new_y = np.copy(board_pieces)
        if -1 in board_pieces:
            new_y[new_y == -1] = 0
        else:
            new_y = board_pieces
        y_boards.append(new_y)

        x_boards = x_boards[1:]
        y_boards = y_boards[1:]

        for i in range(len(x_boards) - 1, -1, -1):
            history.append(x_boards[i])
            history.append(y_boards[i])

        history.append(self.make_sensibility_layer(canonicalBoard))
        history.append(player_board[0])
        history.append(player_board[1])

        return history, x_boards, y_boards

    def make_sensibility_layer(self, canonicalBoard):
        legal_and_not_eye = np.zeros((self.n, self.n))
        legal_moves = canonicalBoard.get_legal_moves(1)
        for i in range(self.n):
            for j in range(self.n):
                if not canonicalBoard.is_eye((i, j), 1) and ((i, j) in legal_moves):
                    legal_and_not_eye[i, j] = 1
        return legal_and_not_eye

    def init_x_y_boards(self):
        x_boards = []
        y_boards = []
        for i in range(8):
            x_boards.append(np.zeros((self.n, self.n)))
            y_boards.append(np.zeros((self.n, self.n)))

        return x_boards, y_boards


def display(board):
    state = ""
    b_pieces = np.array(board.pieces)
    n = 7
    
    for y in range(n):
        state = state + str(y) + " |"
    state += "\n"
    state += " -----------------------\n"
    for y in range(n):
        state += str(y) + "|"
        for x in range(n):
            piece = b_pieces[y][x]  # get the piece to print
            if piece == 1:
                state += "b "
            elif piece == -1:
                state += "W "
            else:
                if x == n:
                    state += "-"
                else:
                    state += "- "
        state += "|\n"

    state += " -----------------------"
    return state
