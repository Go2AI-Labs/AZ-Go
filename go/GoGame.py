from __future__ import print_function
try:
    from Game import Game
    from GoLogic import Board
except:
    try:
        from alphabrain.Game import Game
        from alphabrain.go.GoLogic import Board
    except:
        from Game import Game
        from go.GoLogic import Board
import numpy as np
import copy


class GoGame(Game):
    def __init__(self, n=19):
        self.n = n

    def getInitBoard(self):
        # return initial board (numpy board)
        b = Board(self.n)
        return b

    def getBoardSize(self):
        # (a,b) tuple
        return (self.n, self.n)

    def getActionSize(self):
        # return number of actions
        return self.n * self.n + 1

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        # print("getting next state from perspect of player {} with action {}".format(player,action))

        b = board.copy()
        if action == self.n * self.n:
            b.history.append(None)
            return (b, -player)

        move = (int(action / self.n), action % self.n)

        b.execute_move(move,player)

        return (b, -player)

    # modified
    def getValidMoves(self, board, player, is_self_play):
        # return a fixed size binary vector
        valids = [0 for i in range(self.getActionSize())]
        b = board.copy()
        legalMoves = b.get_legal_moves(player)
        valids[-1] = 1

        if len(board.history) < 15 and is_self_play:
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
    def getGameEndedSelfPlay(self, board, player, returnScore=False, disable_resignation_threshold=False):
        winner = 0
        (score_black, score_white) = self.getScore(board)
        by_score = 0.5 * (board.n * board.n + board.komi)

        # limit games to 98 moves, determine winner based on score of current board
        if len(board.history) >= 98:
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
                winner = 1e-4

        #End game "normally"
        elif not disable_resignation_threshold and len(board.history) > 1:
            #Check if both players passed in succession
            if board.history[-1] is None and board.history[-2] is None:
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
                        winner = 1e-4
            # score threshold is enabled, games can be ended early based on score
            elif score_black > by_score or score_white > by_score:
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
                    winner = 1e-4
        
        #Check if both players have passed in succession
        elif len(board.history) >= 2:
            if board.history[-1] is None and board.history[-2] is None:
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
                        winner = 1e-4

        if returnScore:
            return winner, (score_black, score_white)
        return winner

    # Arena games can terminate according to:
    #   - A move threshold (7 x 7 x 2 = 98)
    #   - Both players passing
    # Arena uses the Chinese ruleset (todo)
    def getGameEndedArena(self, board, player, returnScore=False):
        winner = 0
        (score_black, score_white) = self.getScore(board)

        # limit games to 98 moves, determine winner based on score of current board
        if len(board.history) >= 98:
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
                winner = 1e-4

        elif len(board.history) > 1:
            # score threshold (by_score) is disabled, both players must pass to end game (or until 98 moves reached)
            if board.history[-1] is None and board.history[-2] is None:
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
                    winner = 1e-4

        if returnScore:
            return winner, (score_black, score_white)
        return winner

    def getScore(self, board):
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

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        canonicalBoard=board.copy()

        #canonicalBoard.pieces= board.pieces* player
        if player == -1:
            canonicalBoard.pieces = np.where(canonicalBoard.pieces == 1, -1, np.where(canonicalBoard.pieces == -1, 1, canonicalBoard.pieces))
        return canonicalBoard

    # modified
    def getSymmetries(self, board, pi):
        # mirror, rotational
        assert(len(pi) == self.n**2 + 1)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (self.n, self.n))
        l = []
        history_syms = []
        #b_pieces = board.pieces
        for i in range(1, 5):
            for j in [True, False]:
                history_syms = []
                for k in range(len(board)):
                    newB = np.rot90(board[k], i)
                    newPi = np.rot90(pi_board, i)
                    if j:
                        newB = np.fliplr(newB)
                        newPi = np.fliplr(newPi)
                    history_syms.append(newB)
                l += [(history_syms, list(newPi.ravel()) + [pi[-1]])]
        return l

    def stringRepresentation(self, board):
        # 8x8 numpy array (canonical board)
        return np.array(board.pieces).tostring()

    def action_space_to_GTP(self, action):
        # supports up to 26 x 26 boards
        coords = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                  'u', 'v', 'w', 'x', 'y', 'z']

        if action == self.getBoardSize()[0] ** 2:
            return f''

        # x coord = action / board_size
        # y coord = action % board_size

        # return column + row (in form: 'aa', 'df', 'cd', etc.)
        return f'{coords[int(action / self.getBoardSize()[0])]}' + f'{coords[int(action % self.getBoardSize()[0])]}'

    def getCanonicalHistory(self, x_boards, y_boards, canonicalBoard, player_board):
        history = []

        new_x = np.copy(canonicalBoard)

        if -1 in canonicalBoard:
            new_x[new_x == -1] = 0
        else:
            new_x = canonicalBoard

        x_boards.append(new_x)

        canonicalBoard = np.where(canonicalBoard == 1, -1, np.where(canonicalBoard == -1, 1, canonicalBoard))

        new_y = np.copy(canonicalBoard)
        if -1 in canonicalBoard:
            new_y[new_y == -1] = 0
        else:
            new_y = canonicalBoard
        y_boards.append(new_y)


        x_boards = x_boards[1:]
        y_boards = y_boards[1:]

        for i in range(len(x_boards)-1, -1, -1):
            history.append(x_boards[i])
            history.append(y_boards[i])

        history.append(player_board[0])
        history.append(player_board[1])
        return history, x_boards, y_boards


def display(board):
    state = ""
    b_pieces = np.array(board.pieces)

    n = b_pieces.shape[0]

    for y in range(n):
        state = state + str(y) + " |"
    state += "\n"
    state += " -----------------------\n"
    for y in range(n):
        state += str(y) + "|"
        for x in range(n):
            piece = b_pieces[y][x]    # get the piece to print
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