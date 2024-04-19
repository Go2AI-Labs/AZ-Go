import numpy as np

'''
Board class.
Board data:
  -1=white, +1=black, 0=empty
'''
WHITE = -1
BLACK = +1
EMPTY = 0
PASS_MOVE = None


class Board:
    # Looking up positions adjacent to a given position takes a surprising
    # amount of time, hence this shared lookup table {boardsize: {position: [neighbors]}}
    __NEIGHBORS_CACHE = {}

    def __init__(self, n):
        self.n = n
        # Create the empty board array.
        self.pieces = np.zeros((self.n, self.n))

        self.ko = None
        self.komi = 6.5 if n <= 7 else 7.5  # set to decimal to prevent ties
        self.handicaps = []
        self.history = []
        self.num_black_prisoners = 0
        self.num_white_prisoners = 0

        # Each pass move by a player subtracts a point
        self.passes_white = 0
        self.passes_black = 0

        # `self.liberty_sets` is a 2D array with the same indexes as `board`
        # each entry points to a set of tuples - the liberties of a stone's
        # connected block. By caching liberties in this way, we can directly
        # optimize update functions (e.g. execute_move) and in doing so indirectly
        # speed up any function that queries liberties
        self._create_neighbors_cache()
        self.liberty_sets = [[set() for _ in range(n)] for _ in range(n)]
        for x in range(n):
            for y in range(n):
                self.liberty_sets[x][y] = set(self._neighbors((x, y)))
        # separately cache the 2D numpy array of the _size_ of liberty sets
        # at each board position
        self.liberty_counts = np.zeros((n, n), dtype=np.int_)
        self.liberty_counts.fill(-1)
        # initialize liberty_sets of empty board: the set of neighbors of each position
        # similarly to `liberty_sets`, `group_sets[x][y]` points to a set of tuples
        # containing all (x',y') pairs in the group connected to (x,y)
        self.group_sets = [[set() for _ in range(n)] for _ in range(n)]

        # on-the-fly record of 'age' of each stone
        self.stone_ages = np.zeros((n, n), dtype=np.int_) - 1

        self.enforce_superko = False
        # rng = np.random.RandomState(0)
        """self.hash_lookup = {
            WHITE: rng.randint(np.iinfo(np.uint64).max, size=(n, n), dtype='uint64'),
            BLACK: rng.randint(np.iinfo(np.uint64).max, size=(n, n), dtype='uint64')}
        self.current_hash = np.uint64(0)
        self.previous_hashes = set()"""
        self.previous_boards = []
        self.current_board = np.array(self.pieces).tostring()

        self.x_boards = [np.zeros((self.n, self.n)) for _ in range(8)]
        self.y_boards = [np.zeros((self.n, self.n)) for _ in range(8)]
        self.canonical_history = []
        # Initialize canonical history
        for i in range(len(self.x_boards)): # X and Y boards
            self.canonical_history.append(self.x_boards[i])
            self.canonical_history.append(self.y_boards[i])
        self.canonical_history.append(np.ones((self.n, self.n))) # Sensibility Layer
        self.canonical_history.append(np.ones((self.n, self.n))) # Current Player
        self.canonical_history.append(np.zeros((self.n, self.n))) # Opposing Player
        self.current_player = 1

    def get_canonical_history(self):
        return self.canonical_history.copy()

    def set_current_player(self, new_player):
        if self.current_player == new_player:
            return
        else:
            # Set new (current) player/flip x & y boards (current/opposing histories)
            self.current_player = new_player
            self.x_boards, self.y_boards = self.y_boards, self.x_boards
            new_history = []

            # Move history (from boards matching new player)
            for i in range(len(self.x_boards)):
                new_history.append(self.x_boards[i])
                new_history.append(self.y_boards[i])
            
            # Sensibility Layer
            new_history.append(self.make_sensibility_layer())

            # Player boards (All 1s/0s)
            if self.current_player == 1:
                new_history.append(np.ones((self.n, self.n)))
                new_history.append(np.zeros((self.n, self.n)))
            else:
                new_history.append(np.zeros((self.n, self.n)))
                new_history.append(np.zeros((self.n, self.n)))
            self.canonical_history = new_history
            


    #def get_canonical_history_with_update(self):
        """
        Method to construct the game history from the perspective of the current player
        Returns a 19xNxN matrix containing:
            - The current/opposing player's stones for the last 8 timesteps
            ----> 16 layers total -- 8 for each player
            - The 'sensibility layer'
            - Two layers encoding the current player/opposing player (all 1s for black, all 0s for white) 
        """
        """history = []
        canonical_board = np.where(self.pieces != 0, self.pieces * self.current_player, 0)
        # new_x = np.copy(canonical_board)
        new_x = np.where(canonical_board == 1, 1, 0)
        self.x_boards.append(new_x)
        new_y = np.where(canonical_board == -1, 1, 0)
        self.y_boards.append(new_y)

        # Remove the oldest board state from history
        self.x_boards = self.x_boards[1:]
        self.y_boards = self.y_boards[1:]

        for i in range(len(self.x_boards) - 1, -1, -1):
            history.append(self.x_boards[i])
            history.append(self.y_boards[i])
        history.append(self.make_sensibility_layer())
        if self.current_player == 1:
            history.append(np.ones((self.n, self.n)))
            history.append(np.zeros((self.n, self.n)))
        else:
            history.append(np.zeros((self.n, self.n)))
            history.append(np.ones((self.n, self.n)))
        return history"""
    
    #def get_canonical_history_no_update(self):
        """
        Method to construct the game history from the perspective of the current player
        Returns a 19xNxN matrix containing:
            - The current/opposing player's stones for the last 8 timesteps
            ----> 16 layers total -- 8 for each player
            - The 'sensibility layer'
            - Two layers encoding the current player/opposing player (all 1s for black, all 0s for white) 
        """
        """history = []

        for i in range(len(self.x_boards) - 1, -1, -1):
            history.append(self.x_boards[i])
            history.append(self.y_boards[i])
        history.append(self.make_sensibility_layer())
        if self.current_player == 1:
            history.append(np.ones((self.n, self.n)))
            history.append(np.zeros((self.n, self.n)))
        else:
            history.append(np.zeros((self.n, self.n)))
            history.append(np.ones((self.n, self.n)))
        return history"""

    def make_sensibility_layer(self):
        """
        Make the 'sensibility layer' to be used as part of the input
        to the NNet
        This is a NxN matrix marking all legal moves that do not fill 
        in the current player's own eyes
        """
        legal_and_not_eye = np.zeros((self.n, self.n))
        legal_moves = self.get_legal_moves(self.current_player)
        for i in range(self.n):
            for j in range(self.n):
                if not self.is_eye((i, j), self.current_player) and ((i, j) in legal_moves):
                    legal_and_not_eye[i, j] = 1
        return legal_and_not_eye

    def getStringRepresentation(self):
        # canonical_board = np.where(self.pieces != 0, self.pieces*self.current_player, 0)
        # TODO: should we even have a canonical board??
        return np.array(self.pieces).tostring()

    def rotate_history(self, r, history):
        for i in range(len(history)):
            history[i] = np.rot90(history[i], r % 4)
            if r >= 4:
                history[i] = np.fliplr(history[i])
        return history

    # add [][] indexer syntax to the Board
    def __getitem__(self, index):
        return self.pieces[index]

    def get_group(self, position):

        """Get the group of connected same-color stones to the given position
        Keyword arguments:
        position -- a tuple of (x, y)
        x being the column index of the starting position of the search
        y being the row index of the starting position of the search
        Return:
        a set of tuples consist of (x, y)s which are the same-color cluster
        which contains the input single position. len(group) is size of the cluster, can be large.
        """
        (x, y) = position
        # given that this is already cached, it is a fast lookup
        return self.group_sets[x][y]

    def get_groups_around(self, position):
        """returns a list of the unique groups adjacent to position
        'unique' means that, for example in this position:
            . . . . .
            . B W . .
            . W W . .
            . . . . .
            . . . . .
        only the one white group would be returned on get_groups_around((1,1))
        """
        groups = []
        for (nx, ny) in self._neighbors(position):
            group = self.group_sets[nx][ny]
            if len(group) > 0 and group not in groups:
                groups.append(self.group_sets[nx][ny])
        return groups

    def _on_board(self, position):
        """simply return True iff position is within the bounds of [0, self.size)
        """
        (x, y) = position
        return x >= 0 and y >= 0 and x < self.n and y < self.n

    def _create_neighbors_cache(self):
        if self.n not in Board.__NEIGHBORS_CACHE:
            Board.__NEIGHBORS_CACHE[self.n] = {}
            for x in range(self.n):
                for y in range(self.n):
                    neighbors = [xy for xy in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                                 if self._on_board(xy)]
                    Board.__NEIGHBORS_CACHE[self.n][(x, y)] = neighbors

    def _neighbors(self, position):
        """A private helper function that simply returns a list of positions neighboring
        the given (x,y) position. Basically it handles edges and corners.
        """
        return Board.__NEIGHBORS_CACHE[self.n][position]

    def _diagonals(self, position):
        """Like _neighbors but for diagonal positions
        """
        (x, y) = position
        return filter(self._on_board, [(x - 1, y - 1), (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1)])

    def _update_neighbors(self, position, color):

        """A private helper function to update self.group_sets and self.liberty_sets
        given that a stone was just played at `position`
        """

        (x, y) = position

        merged_group = set()
        merged_group.add(position)
        merged_libs = self.liberty_sets[x][y]
        for (nx, ny) in self._neighbors(position):
            # remove (x,y) from liberties of neighboring positions
            self.liberty_sets[nx][ny] -= set([position])
            # if neighbor was opponent, update group's liberties count
            # (current_player's groups will be updated below regardless)
            if self.pieces[nx][ny] == -color:
                new_liberty_count = len(self.liberty_sets[nx][ny])
                for (gx, gy) in self.group_sets[nx][ny]:
                    self.liberty_counts[gx][gy] = new_liberty_count
            # MERGE group/liberty sets if neighbor is the same color
            # note: this automatically takes care of merging two separate
            # groups that just became connected through (x,y)
            elif self.pieces[x][y] == self.pieces[nx][ny]:
                merged_group |= self.group_sets[nx][ny]
                merged_libs |= self.liberty_sets[nx][ny]

        # now that we have one big 'merged' set for groups and liberties, loop
        # over every member of the same-color group to update them
        # Note: neighboring opponent groups are already updated in the previous loop
        count_merged_libs = len(merged_libs)
        for (gx, gy) in merged_group:
            self.group_sets[gx][gy] = merged_group
            self.liberty_sets[gx][gy] = merged_libs
            self.liberty_counts[gx][gy] = count_merged_libs

    """
    def _update_hash(self, action, color):
        (x, y) = action
        self.current_hash = np.bitwise_xor(self.current_hash, self.hash_lookup[color][x][y])
    """

    def _update_current_board(self, action, color):
        self.current_board = self.getStringRepresentation()

    def _remove_group(self, group):

        """A private helper function to take a group off the board (due to capture),
        updating group sets and liberties along the way
        """
        for (x, y) in group:
            # self._update_hash((x, y), self.pieces[x, y])
            self._update_current_board((x, y), self.pieces[x, y])
            self.pieces[x, y] = EMPTY
        for (x, y) in group:
            # clear group_sets for all positions in 'group'
            self.group_sets[x][y] = set()
            self.liberty_sets[x][y] = set()
            self.liberty_counts[x][y] = -1
            self.stone_ages[x][y] = -1
            for (nx, ny) in self._neighbors((x, y)):
                if self.pieces[nx, ny] == EMPTY:
                    # add empty neighbors of (x,y) to its liberties
                    self.liberty_sets[x][y].add((nx, ny))
                else:
                    # add (x,y) to the liberties of its nonempty neighbors
                    self.liberty_sets[nx][ny].add((x, y))
                    for (gx, gy) in self.group_sets[nx][ny]:
                        self.liberty_counts[gx][gy] = len(self.liberty_sets[nx][ny])

    def copy(self):
        """get a copy of this Game state
        """
        other = Board(self.n)
        other.pieces = self.pieces.copy()
        other.ko = self.ko
        other.handicaps = list(self.handicaps)
        other.history = list(self.history)
        other.num_black_prisoners = self.num_black_prisoners
        other.num_white_prisoners = self.num_white_prisoners
        other.enforce_superko = self.enforce_superko
        # other.current_hash = self.current_hash.copy()
        # other.previous_hashes = self.previous_hashes.copy()
        other.previous_boards = self.previous_boards
        other.current_board = self.current_board
        other.x_boards = self.x_boards.copy()
        other.y_boards = self.y_boards.copy()
        other.current_player = self.current_player
        other.canonical_history = self.canonical_history

        # update liberty and group sets.
        #
        # group_sets and liberty_sets are shared between stones in the same
        # group.  We need to make sure this is the case in the copy, as well.
        #
        # we store set copies indexed by original id() in set_copies
        def get_copy(s, set_copies={}):
            if id(s) not in set_copies:
                set_copies[id(s)] = set(s)  # makes a copy of s
            return set_copies[id(s)]

        for x in range(self.n):
            for y in range(self.n):
                other.group_sets[x][y] = get_copy(self.group_sets[x][y])
                other.liberty_sets[x][y] = get_copy(self.liberty_sets[x][y])
        other.liberty_counts = self.liberty_counts.copy()
        return other

    def is_suicide(self, action, color):
        """return true if having this color play at <action> would be suicide
        """
        (x, y) = action
        num_liberties_here = len(self.liberty_sets[x][y])
        if num_liberties_here == 0:
            # no liberties here 'immediately'
            # but this may still connect to another group of the same color
            for (nx, ny) in self._neighbors(action):
                # check if we're saved by attaching to a friendly group that has
                # liberties elsewhere
                is_friendly_group = self.pieces[nx, ny] == color
                group_has_other_liberties = len(self.liberty_sets[nx][ny] - set([action])) > 0
                if is_friendly_group and group_has_other_liberties:
                    return False
                # check if we're killing an unfriendly group
                is_enemy_group = self.pieces[nx, ny] == -color
                if is_enemy_group and (not group_has_other_liberties):
                    return False
            # checked all the neighbors, and it doesn't look good.
            return True
        return False

    def is_positional_superko(self, action, color):
        """Find all actions that this color player has done in the past, taking into
        account the fact that history starts with BLACK when there are no
        handicaps or with WHITE when there are.
        """
        if len(self.handicaps) == 0 and color == BLACK:
            player_history = self.history[0::2]
        elif len(self.handicaps) > 0 and color == WHITE:
            player_history = self.history[0::2]
        else:
            player_history = self.history[1::2]

        if action not in self.handicaps and action not in player_history:
            return False

        state_copy = self.copy()
        state_copy.enforce_superko = False
        state_copy.execute_move(action, color)

        """
        if state_copy.current_hash in self.previous_hashes:
            return True
        else:
            return False"""

        if state_copy.current_board in self.previous_boards:
            return True
        else:
            return False

    def is_legal(self, action, color):
        """determine if the given action (x,y tuple) is a legal move
        """
        # passing is always legal
        if action is PASS_MOVE:
            return True
        (x, y) = action
        if not self._on_board(action):
            return False
        if self.pieces[x][y] != EMPTY:
            return False
        if self.is_suicide(action, color):
            return False
        if action == self.ko:
            return False
        if self.enforce_superko and self.is_positional_superko(action, color):
            return False
        return True

    def is_eyeish(self, position, owner):
        """returns whether the position is empty and is surrounded by all stones of 'owner'
        """
        (x, y) = position
        if self.pieces[x, y] != EMPTY:
            return False

        for (nx, ny) in self._neighbors(position):
            if self.pieces[nx][ny] != owner:
                return False
        return True

    def is_eye(self, position, owner, stack=[]):
        """returns whether the position is a true eye of 'owner'
        Requires a recursive call; empty spaces diagonal to 'position' are fine
        as long as they themselves are eyes
        """
        if not self.is_eyeish(position, owner):
            return False
        # (as in Fuego/Michi/etc) ensure that num "bad" diagonals is 0 (edges) or 1
        # where a bad diagonal is an opponent stone or an empty non-eye space
        num_bad_diagonal = 0
        # if in middle of board, 1 bad neighbor is allowable; zero for edges and corners
        allowable_bad_diagonal = 1 if len(self._neighbors(position)) == 4 else 0

        for d in self._diagonals(position):
            # opponent stones count against this being eye
            if self.pieces[d] == -owner:
                num_bad_diagonal += 1
            # empty spaces (that aren't themselves eyes) count against it too
            # the 'stack' keeps track of where we've already been to prevent
            # infinite loops of recursion
            elif self.pieces[d] == EMPTY and d not in stack:
                stack.append(position)
                if not self.is_eye(d, owner, stack):
                    num_bad_diagonal += 1
                stack.pop()
            # at any point, if we've surpassed # allowable, we can stop
            if num_bad_diagonal > allowable_bad_diagonal:
                return False
        return True

    def is_ladder_capture(self, action, color, prey=None, remaining_attempts=80):

        """Check if moving at action results in a ladder capture, defined as being next
        to an enemy group with two liberties, and with no ladder_escape move afterward
        for the other player.
        If prey is None, check all adjacent groups, otherwise only the prey
        group is checked.  In the (prey is None) case, if this move is a ladder
        capture for any adjance group, it's considered a ladder capture.
        Recursion depth between is_ladder_capture() and is_ladder_escape() is
        controlled by the remaining_attempts argument.  If it reaches 0, the
        move is assumed not to be a ladder capture.
        """

        # ignore illegal moves
        if not self.is_legal(action, color):
            return False

        # if we haven't found a capture by a certain number of moves, assume it's worked.
        if remaining_attempts <= 0:
            return True

        hunter_player = color
        prey_player = - color

        if prey is None:
            # default case is to check all adjacent prey_player groups that
            # have 2 liberties
            neighbor_groups_stones = [next(iter(group)) for group in self.get_groups_around(action)]
            potential_prey = [(nx, ny) for (nx, ny) in neighbor_groups_stones
                              if (self.pieces[nx][ny] == prey_player and
                                  self.liberty_counts[nx][ny] == 2)]
        else:
            # we are checking a specific group (called from is_ladder_escape)
            potential_prey = [prey]

        for (prey_x, prey_y) in potential_prey:
            # attempt to capture the group at prey_x, prey_y in a ladder
            tmp = self.copy()
            tmp.execute_move(action, color)

            # we only want to check a limited set of possible escape moves:
            # - extensions from the remaining liberty of the prey group.
            # - captures of enemy groups adjacent to the prey group.
            possible_escapes = tmp.liberty_sets[prey_x][prey_y].copy()

            # Check if any hunter groups adjacent to the prey groups
            # are in atari.  Capturing these groups are potential escapes.
            for prey_stone in tmp.group_sets[prey_x][prey_y]:
                for (nx, ny) in tmp._neighbors(prey_stone):
                    if (tmp.pieces[nx][ny] == hunter_player) and (tmp.liberty_counts[nx][ny] == 1):
                        possible_escapes |= tmp.liberty_sets[nx][ny]

            if not any(tmp.is_ladder_escape((escape_x, escape_y), color, prey=(prey_x, prey_y),
                                            remaining_attempts=(remaining_attempts - 1))
                       for (escape_x, escape_y) in possible_escapes):
                # we found at least one group that could be captured in a
                # ladder, so this move is a ladder capture.
                return True

        # no ladder captures were found
        return False

    def is_ladder_escape(self, action, color, prey=None, remaining_attempts=80):
        """Check if moving at action results in a ladder escape, defined as being next
        to a current player's group with one liberty, with no ladder captures
        afterward.  Going from 1 to >= 3 liberties is counted as escape, or a
        move giving two liberties without a subsequent ladder capture.
        If prey is None, check all adjacent groups, otherwise only the prey
        group is checked.  In the (prey is None) case, if this move is a ladder
        escape for any adjacent group, this move is a ladder escape.
        Recursion depth between is_ladder_capture() and is_ladder_escape() is
        controlled by the remaining_attempts argument.  If it reaches 0, the
        move is assumed not to be a ladder capture.
        """

        # ignore illegal moves
        if not self.is_legal(action, color):
            return False

        # if we haven't found an escape by a certain number of moves, give up.
        if remaining_attempts <= 0:
            return False

        prey_player = color

        if prey is None:
            # default case is to check all adjacent groups that might be in a
            # ladder (i.e., with one liberty)
            neighbor_groups_stones = [next(iter(group)) for group in self.get_groups_around(action)]
            potential_prey = [(nx, ny) for (nx, ny) in neighbor_groups_stones
                              if (self.pieces[nx][ny] == prey_player and
                                  self.liberty_counts[nx][ny] == 1)]
        else:
            # we are checking a specific group (called from is_ladder_capture)
            potential_prey = [prey]

        # This move is an escape if it's an escape for any of the potential_prey
        for (prey_x, prey_y) in potential_prey:
            # make the move, see if the group at (prey_x, prey_y) has escaped,
            # defined as having >= 3 liberties, or 2 liberties and not
            # ladder_capture() being true when played on either of those
            # liberties.
            tmp = self.copy()
            tmp.execute_move(action, color)

            # if we have >= 3 liberties, we've escaped
            if tmp.liberty_counts[prey_x][prey_y] >= 3:
                return True

            # if we only have 1 liberty, we've failed
            if tmp.liberty_counts[prey_x][prey_y] == 1:
                # not an escape - check next group
                continue

            # The current group has two liberties.  It may still be in a ladder.
            # Check both liberties to see if they are ladder captures
            if any(tmp.is_ladder_capture(possible_capture, color, prey=(prey_x, prey_y),
                                         remaining_attempts=(remaining_attempts - 1))
                   for possible_capture in tmp.liberty_sets[prey_x][prey_y]):
                # not an escape - check next group
                continue

            # reached two liberties that were no longer ladder-capturable
            return True

        # no ladder escape found
        return False

    def place_handicaps(self, actions):
        if len(self.history) > 0:
            raise IllegalMove("Cannot place handicap on a started game")
        self.handicaps.extend(actions)
        for action in actions:
            self.execute_move(action, BLACK)
        self.history = []

    def get_legal_moves(self, color):
        moves = set()  # stores the legal moves.
        for y in range(self.n):
            for x in range(self.n):
                if self.is_legal((x, y), color):
                    moves.add((x, y))
        return list(moves)

    def has_legal_moves(self, color):
        """Returns True if has legal move else False
        """
        for y in range(self.n):
            for x in range(self.n):
                if self.is_legal((x, y), color):
                    return True;
        return False
    
    def _update_canonical_history(self):
        history_temp = []
        canonical_board = np.where(self.pieces != 0, self.pieces * self.current_player, 0)
        # new_x = np.copy(canonical_board)
        new_x = np.where(canonical_board == 1, float(1), float(0))
        self.x_boards.append(new_x)
        new_y = np.where(canonical_board == -1, float(1), float(0))
        self.y_boards.append(new_y)

        # Remove the oldest board state from history
        self.x_boards = self.x_boards[1:]
        self.y_boards = self.y_boards[1:]

        for i in range(len(self.x_boards) - 1, -1, -1):
            history_temp.append(self.x_boards[i])
            history_temp.append(self.y_boards[i])
        history_temp.append(self.make_sensibility_layer())
        if self.current_player == 1:
            history_temp.append(np.ones((self.n, self.n)))
            history_temp.append(np.zeros((self.n, self.n)))
        else:
            history_temp.append(np.zeros((self.n, self.n)))
            history_temp.append(np.ones((self.n, self.n)))
        self.canonical_history = history_temp


    def execute_move(self, action, color):
        """Perform the given move on the board; flips pieces as necessary.
        color gives the color pf the piece to play (-1=white,1=black)
        """
        if self.is_legal(action, color):
            # reset ko
            self.ko = None
            # increment age of stones by 1
            self.stone_ages[self.stone_ages >= 0] += 1
            if action is not PASS_MOVE:
                (x, y) = action
                self.pieces[x][y] = color
                # self._update_hash(action, color)
                self._update_current_board(action, color)
                self._update_neighbors(action, color)
                self.stone_ages[x][y] = 0
                # print("player {} act {} --:".format(color,action))

                # check neighboring groups' liberties for captures
                for (nx, ny) in self._neighbors(action):
                    if self.pieces[nx][ny] == -color and len(self.liberty_sets[nx][ny]) == 0:
                        # capture occurred!
                        captured_group = self.group_sets[nx][ny]
                        num_captured = len(captured_group)
                        self._remove_group(captured_group)
                        if color == BLACK:
                            self.num_white_prisoners += num_captured
                        else:
                            self.num_black_prisoners += num_captured
                        # check for ko
                        if num_captured == 1:
                            # it is a ko iff, were the opponent to play at the captured position,
                            # it would recapture (x,y) only
                            # (a bigger group containing xy may be captured - this is 'snapback')
                            would_recapture = len(self.liberty_sets[x][y]) == 1
                            recapture_size_is_1 = len(self.group_sets[x][y]) == 1
                            if would_recapture and recapture_size_is_1:
                                # note: (nx,ny) is the stone that was captured
                                self.ko = (nx, ny)
                # _remove_group has finished updating the hash
                # self.previous_hashes.add(self.current_hash)
                self.previous_boards.append(self.current_board)
            else:
                if color == BLACK:
                    self.passes_black += 1
                if color == WHITE:
                    self.passes_white += 1
            self.history.append(action)
            # A new move has been played, so update variables to reflect the NEW current player
            self.current_player = -1 * self.current_player
            self.x_boards, self.y_boards = self.y_boards, self.x_boards
            self._update_canonical_history()
        else:
            raise IllegalMove(str(action) + ',' + str(color))


class IllegalMove(Exception):
    pass
