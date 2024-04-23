import sys
sys.path.append("..")
sys.path.append("../go")
sys.path.append("../utils")
import os
import numpy as np
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import cv2

from heatmap_generator import MapGenerator
from go.go_game import GoGame as Game
from go.go_game import display
from engine_mcts import MCTS
from neural_network.neural_net_wrapper import NNetWrapper as NNetWrapper
from training.coach import Coach
from utils.config_handler import ConfigHandler
from utils.path_handler import resource_path
from definitions import CONFIG_PATH

#--------------------------------------------#
#       Initialize Files/Directories         #
#--------------------------------------------#
# Make analysis folder if needed
analysis_dir = "analysis"
if not os.path.exists(analysis_dir):
    os.makedirs(analysis_dir)

# Make analysis folder for this game
game_folders = os.listdir(analysis_dir)
game_folder_name = f"Engine_Game_{len(game_folders) + 1}"
game_folder = os.path.join(analysis_dir, game_folder_name)
if not os.path.exists(game_folder):
    os.makedirs(game_folder)

# Make the text file to hold all data for this game
temp_filename= "All_Data.txt"
filename = os.path.join(game_folder, temp_filename)
if not os.path.exists(filename):
    with open(filename, "w") as f:
        line = "------------BEGINNING OF NEW GAME------------\n\n"
        f.write(line)
        line2 = "Model from path -- " + resource_path("model.tar") + "\n"
        f.write(line2)
    f.close()


config = ConfigHandler("/Users/blake/Research/Refactor_Codebase/AZ-Go/gtp/config.yaml")

VERSION = '1.0'

game = Game(config["board_size"], is_arena_game=True)
neural_network = NNetWrapper(game, config)
# Load in the specified model if given 
# If no model is given, use model.tar
argv = sys.argv
if(len(argv) > 1):
    if ".tar" not in argv[1]:
        model_file = argv[1] + ".tar"
    else:
        model_file = argv[1]
    model_path = os.path.join("model_files", model_file)
    if not os.path.exists(model_path):
        print(f"Model file {model_file} does not exist...")
        print("Trying to load default file -- model.tar")
        model_path = os.path.join("model_files", "model.tar")
else:
    model_path = os.path.join("model_files", "model.tar")
#neural_network.load_checkpoint("", model_path, cpu_only=True)
neural_network.load_checkpoint("", "/Users/blake/Research/Model_W/weight_files/iter_19 copy.tar", cpu_only=True)

# stones
BLACK = 1
WHITE = 2

# current board used
board = game.getInitBoard()
mcts = MCTS(game, neural_network, is_self_play=False)
coords = None
"""curPlayer = 1
x_boards = []
y_boards = []
c_boards = [np.ones((7, 7)), np.zeros((7, 7))]
for i in range(8):
    x_boards.append(np.zeros((config["board_size"], config["board_size"])))
    y_boards.append(np.zeros((config["board_size"], config["board_size"])))
canonicalBoard = game.getCanonicalForm(board, curPlayer)
player_board = (c_boards[0], c_boards[1])"""
#canonicalHistory, x_boards, y_boards = game.getCanonicalHistory(x_boards, y_boards, canonicalBoard, player_board)
move_count = 0

def print_board():
    global board
    print(display(board))


def set_board_size(command):
    # hook global variables
    global board
    # parse the board size
    size = int(command.split()[-1])
    # throw error if board size is not supported
    if size not in [7]:
        print('? current board size not supported\n')
        return
    # board = BOARDS[str(size)]
    g = Game(size)
    board = g.getInitBoard()


def clear_board():
    global board
    board = game.getInitBoard()


def generate_video(): 
    global game_folder
    image_folder = f'{os.getcwd()}/{game_folder}/' # make sure to use your folder 
    video_name = f'{image_folder}/All_Data_Video.mp4'
      
    images = []
    for i in range(len(os.listdir(image_folder))-1):
        j = i+1
        filename = f'Move_{j}/Move_{j}_All_Board.png'
        full_path = os.path.join(image_folder, filename)
        images.append(full_path)
    # Array images should only consider 
    # the image files ignoring others if any 
    #print(images)  
    frame = cv2.imread(os.path.join(image_folder, images[0])) 
    # setting the frame width, height width 
    # the width, height of first image 
    height, width, layers = frame.shape   
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    video = cv2.VideoWriter(video_name, fourcc, 1, (width, height))  
    # Appending the images to the video one by one 
    for image in images:  
        video.write(cv2.imread(image))  
    # Deallocating memories taken for window creation 
    cv2.destroyAllWindows()  
    video.release()  # releasing the video generated 

#TODO -- REMOVE deterministic
def log_analysis_data(board, counts, action):
    global filename, neural_network, move_count, game_folder
    # Get variables for current move 
    move_count += 1
    player_string = "Black" if board.current_player == 1 else "White"

    # Make folder to hold data for the current move 
    move_dir = f"Move_{move_count}"
    move_path = os.path.join(game_folder, move_dir)
    if not os.path.exists(move_path):
        os.makedirs(move_path)

    # Create map generator and initialize maps
    generator = MapGenerator()
    mcts_map = generator.init_new_map()
    nnet_map = generator.init_new_map()
    qval_map = generator.init_new_map()

    # Write data to the main file
    with open(filename, "a") as f:
        """
        --------------------------
        |        MCTS MAP        |
        --------------------------
        """
        header = f"--------------Player: {player_string}--------------\n--------------Move #{move_count}--------------\n----------------Counts from MCTS----------------\n"
        f.write(header)
        # Generate the heatmap
        mcts_map, percentages = generator.generate_map(mcts_map, counts, f)
        # Save the heatmap
        name = f"MCTS_mov_{move_count}.png"
        map_name = os.path.join(move_path, name)
        mcts_image = generator.draw_text(mcts_map, percentages)
        generator.save_image(mcts_image, map_name)
        # Write the pass move to the main file
        pass_move = round((counts[49] * 100), 2)
        pass_str = f"Pass Move Percentage = {pass_move}\n"
        f.write(pass_str)
        """
        --------------------------
        |      RAW Nnet Map      |
        --------------------------
        """
        # Print raw output for pi from NNet
        header2 = "\n---------------Raw Neural Net Output---------------\n"
        f.write(header2)
        #Get p and v from the neural network
        p, v = neural_network.predict(board.get_canonical_history())
        # Generate NNet Map
        nnet_map, percentages = generator.generate_map(nnet_map, p, f)
        # Save the NNet heatmap
        nnet_image = generator.draw_text(nnet_map, percentages)
        name = f"NNet_move_{move_count}.png"
        map_name = os.path.join(move_path, name)
        generator.save_image(nnet_image, map_name)
        # Write the pass move to the main file
        pass_move = round((p[49] * 100), 2)
        pass_str = f"Pass Move Percentage = {pass_move}\n"
        f.write(pass_str)
        """
        --------------------------
        |  Save Winrate Estimate |
        --------------------------
        """
        f.write("\n-------Winrate Estimate-------\n")
        valuestr = f"V = {v[0]}\n"
        f.write(valuestr)
        # Print raw NNet percentage and MCTS percentage of chosen move
        count_perc = round((counts[action] * 100), 2)
        formatted_count = " {:>5}% ".format(count_perc)
        raw_perc = round((p[action] * 100), 2)
        formatted_raw = " {:>5}% ".format(raw_perc)
        chosen = f"\n-------Chose move #{action}-------\nMCTS Count Percentage = {formatted_count}\nRaw NNet Percentage = {formatted_raw}\n\n"
        f.write(chosen)
        # Print the move that the neural network would have taken on its own 
        max_nnet = np.argmax(p)
        max_perc = round((p[max_nnet] * 100), 2)
        formatted_max = " {:>5}% ".format(max_perc)
        max_str = f"-------Max Probability from NNet-------\nMove = {max_nnet}\nProb = {formatted_max}"
        f.write(max_str)
        f.write("\n\n\n\n")
        """
        --------------------------
        |        QVAL MAP        |
        --------------------------
        """
        # Make map for Q vals in MCTS
        s = board.getStringRepresentation()
        q_vals = mcts.get_Q_vals(s, board.current_player)
        qval_map, percentages = generator.generate_map(qval_map, q_vals, f, use_val_colors=True)
        name = f"QVALS_mov_{move_count}.png"
        map_name = os.path.join(move_path, name)
        qval_image = generator.draw_text(qval_map, percentages, use_val_size=True) 
        generator.save_image(qval_image, map_name)
        """
        --------------------------
        |    Compile All Data    |
        --------------------------
        """
        name = f"Move_{move_count}_All.png"
        filename = os.path.join(move_path, name)
        generator.compile_one_image([mcts_image, nnet_image, qval_image], filename, move_count)
        """
        --------------------------
        |    Make Board Image    |
        --------------------------
        """
        board_image = generator.generate_game_board(board, action)
        name = f"Board_move_{move_count}.png"
        map_name = os.path.join(move_path, name)
        generator.save_image(board_image, map_name)
        name = f"Move_{move_count}_All_Board.png"
        filename = os.path.join(move_path, name)
        all_image = generator.compile_one_image_with_board([mcts_image, nnet_image, qval_image, board_image], filename, move_count)
        """if deterministic:
            all_image = generator.was_deterministic(all_image, action)"""
        generator.save_image(all_image, filename)

    f.close()


def generate_move(color):
    global board, mcts, filename, neural_network, move_count, game

    if color == BLACK:
        board.set_current_player(1)
    else:
        board.set_current_player(-1)
    #print(f"Set Current Player to {board.current_player}")

    

    #canonicalBoard = game.getCanonicalForm(board, curPlayer)

    # make move on board
    #player_board = (c_boards[0], c_boards[1]) if curPlayer == 1 else (c_boards[1], c_boards[0])

    #num_sims = config["num_full_search_sims"]

    # Generate a move based on most recent board state (new way for logging analysis data)
    #counts = mcts.getActionProb(canonicalBoard, canonicalHistory, x_boards, y_boards, player_board, False, num_sims, temp=0)
    #TODO Change this **FOR TEST ONLY
    #counts, probs, deterministic = mcts.getActionProb(canonicalBoard, canonicalHistory, x_boards, y_boards, player_board, False, num_sims, temp=0)
    #counts = mcts.getActionProb(canonicalBoard, canonicalHistory, x_boards, y_boards, player_board, False, num_sims, temp=0)
    counts = mcts.getActionProb(board, temp=1, is_full_search=True)
    action = np.argmax(counts)
    """
    if deterministic:
        action = np.argmax(probs)
    else:
        action = np.argmax(counts)
    """
    log_analysis_data(board, counts, action)

    #Old way of getting action
    """action = np.argmax(
        mcts.getActionProb(canonicalBoard, canonicalHistory, x_boards, y_boards, player_board, False, num_sims, temp=0))"""
    # Perform the move
    if not os.path.exists("Engine_Debug.txt"):
        with open("Engine_Debug.txt", "w") as f:
            f.write("\n\n\n--------GENMOVE COMMAND--------\n")
            f.write("--------GENMOVE COMMAND--------\n")
            f.write("--------GENMOVE COMMAND--------\n")
            f.write("Before Making Move\n")
            f.write(f"Playing Move -- {action}\n")
            f.write(f"Board Before:\n{board.pieces}\n")
            f.write(f"History Before:\n{board.get_canonical_history()}\n")
            f.write(f"Valids = {game.getValidMoves(board)}\n")
            f.write(f"Player Before = {board.current_player}\n")
    else:
        with open("Engine_Debug.txt", "a") as f:
            f.write("\n\n\n--------GENMOVE COMMAND--------\n")
            f.write("--------GENMOVE COMMAND--------\n")
            f.write("--------GENMOVE COMMAND--------\n")
            f.write("Before Making Move\n")
            f.write(f"Playing Move -- {action}\n")
            f.write(f"Board Before:\n{board.pieces}\n")
            f.write(f"History Before:\n{board.get_canonical_history()}\n")
            f.write(f"Valids = {game.getValidMoves(board)}\n")

    board = game.getNextState(board, action)

    if action == 49:
        coordinate = "pass"
        row = "Z"
        col = "Z"
    else:
        row = config["board_size"] - int(action / config["board_size"])
        col_coords = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
        col = col_coords[action % 7]
        coordinate = col + str(row)

    if not os.path.exists("Engine_Debug.txt"):
        with open("Engine_Debug.txt", "w") as f:
            f.write(f"\nPlayed Move -- {action} Successfully\n")
            f.write(f"Coords Used = C: {col} -- R: {row} ---> {coordinate}\n")
            f.write(f"Board After:\n{board.pieces}\n")
            f.write(f"History After:\n{board.get_canonical_history()}\n")
            f.write(f"Next Player = {board.current_player}\n")
    else:
        with open("Engine_Debug.txt", "a") as f:
            f.write(f"\nPlayed Move -- {action} Successfully\n")
            f.write(f"Coords Used = C: {col} -- R: {row} ---> {coordinate}\n")
            f.write(f"Board After:\n{board.pieces}\n")
            f.write(f"History After:\n{board.get_canonical_history()}\n")
            f.write(f"Next Player = {board.current_player}\n")
    # Update histories to prepare for next move
    #canonicalBoard = game.getCanonicalForm(board, curPlayer)
    """player_board = (c_boards[0], c_boards[1]) if curPlayer == 1 else (c_boards[1], c_boards[0])
    canonicalHistory, x_boards, y_boards = game.getCanonicalHistory(x_boards, y_boards, canonicalBoard,
                                                                    player_board)

    x_boards, y_boards = y_boards, x_boards"""

    # return the move
    return coordinate


# play command
def play(command):
    global board
    # parse color
    #curPlayer = 1 if command.split()[1] == 'B' else -1

    player_idx = command.find(" ") + 1
    move_idx = command.find(" ", player_idx) + 1

    # player = gtp[player_idx]
    player = 1 if command[player_idx].lower() == 'b' else -1
    board.set_current_player(player)
    #print(f"Set Current Player to {board.current_player}")
    move = command[move_idx:]

    if move == "pass" or move == "PASS":
        action = config["board_size"] * config["board_size"]
        row = 9
        col = 9
    else:
        # parse square
        square_str = command.split()[-1]
        letters = ["a", "b", "c", "d", "e", "f", "g"]
        numbers = ["7", "6", "5", "4", "3", "2", "1"]
        """
        col = ord(square_str[0]) - ord('A') + 1 - (1 if ord(square_str[0]) > ord('I') else 0)
        row_count = int(square_str[1:]) if len(square_str[1:]) > 1 else ord(square_str[1:]) - ord('0')
        """
        if square_str[0].lower() in letters:
            col = letters.index(square_str[0].lower())
        else:
            col = int(square_str[0])
        if square_str[1] in numbers:
            row = numbers.index(square_str[1])
        elif square_str[1].lower() in letters:
            row = letters.index(square_str[1].lower())
        else:
            row = int(square_str[1])
        action = (row*7) + col
        # row = (BOARD_RANGE - 1) - row_count
        # action = ((config["board_size"] - row_count) * config["board_size"]) + (col - 1)
        # square = row * BOARD_RANGE + col

    if not os.path.exists("Engine_Debug.txt"):
        with open("Engine_Debug.txt", "w") as f:
            f.write("\n\n\n--------PLAY COMMAND--------\n")
            f.write("--------PLAY COMMAND--------\n")
            f.write("--------PLAY COMMAND--------\n")
            f.write("Before Making Move\n")
            f.write(f"Playing Move -- {action}\n")
            f.write(f"Board Before:\n{board.pieces}\n")
            f.write(f"History Before:\n{board.get_canonical_history()}\n")
            f.write(f"Valids = {game.getValidMoves(board)}\n")
            f.write(f"Player Before = {board.current_player}\n")
    else:
        with open("Engine_Debug.txt", "a") as f:
            f.write("\n\n\n--------PLAY COMMAND--------\n")
            f.write("--------PLAY COMMAND--------\n")
            f.write("--------PLAY COMMAND--------\n")
            f.write("Before Making Move\n")
            f.write(f"Playing Move -- {action}\n")
            f.write(f"Board Before:\n{board.pieces}\n")
            f.write(f"History Before:\n{board.get_canonical_history()}\n")
            f.write(f"Valids = {game.getValidMoves(board)}\n")

    # make move on board
    board = game.getNextState(board, action)

    if action < 49:
        if not os.path.exists("Engine_Debug.txt"):
            with open("Engine_Debug.txt", "w") as f:
                f.write(f"\nPlayed Move -- {action} Successfully\n")
                f.write(f"Coords Used = C: {col} -- R: {row} ---> {action}\n")
                f.write(f"Board After:\n{board.pieces}\n")
                f.write(f"History After:\n{board.get_canonical_history()}\n")
                f.write(f"Next Player = {board.current_player}\n")
        else:
            with open("Engine_Debug.txt", "a") as f:
                f.write(f"\nPlayed Move -- {action} Successfully\n")
                f.write(f"Coords Used = C: {col} -- R: {row} ---> {action}\n")
                f.write(f"Board After:\n{board.pieces}\n")
                f.write(f"History After:\n{board.get_canonical_history()}\n")
                f.write(f"Next Player = {board.current_player}\n")

    """# Update histories to prepare for next move
    canonicalBoard = game.getCanonicalForm(board, curPlayer)
    player_board = (c_boards[0], c_boards[1]) if curPlayer == 1 else (c_boards[1], c_boards[0])
    canonicalHistory, x_boards, y_boards = game.getCanonicalHistory(x_boards, y_boards, canonicalBoard,
                                                                    player_board)

    # Player will switch, so switch x and y boards (current/opposing player histories)
    x_boards, y_boards = y_boards, x_boards"""

def loadsgf(command):
    #Get SGF file as text
    parsed_cmd = command.split(" ")
    filepath = parsed_cmd[1]
    
    with open(filepath) as f:
        temp = f.read()
    temp = temp.replace("(", "").replace(")", "")

    #Get a list of moves and puzzle answer from the SGF file
    sgf_info = temp.split(';')
    sgf_info = sgf_info[2:]
    moves = []
    ans = []
    for elt in sgf_info:
        if "C" in elt:
            finalElt = elt.split("C")
            elt = finalElt[0]

            raw_ans = finalElt[1].split(" ")[1]
            ans = raw_ans.split(",")
            ans[1] = ans[1].replace("]", "")        

        parsed_move = elt.split("[")
        parsed_move[1] = parsed_move[1].replace("]", "")
        moves.append(parsed_move)

    #get current/next player
    curr_player = "B" if moves[-1][0] == "W" else "W"
    prev_player = "B" if curr_player == "W" else "W"
    #return all information from SGF file

    for m in moves:
        fake_cmd = "play " + m[0] + " " + m[1]
        play(fake_cmd)

# GTP communication protocol
def gtp():
    # main GTP loop
    global curPlayer

    while True:
        # accept GUI command
        command = input()

        # handle commands
        if 'name' in command:
            print('= Go2AI\n')
        elif 'protocol_version' in command:
            print('= 1\n')
        elif 'version' in command:
            print('=', VERSION, '\n')
        elif 'list_commands' in command:
            print('= protocol_version\n')
        elif 'boardsize' in command:
            set_board_size(command)
            print('=\n')
        elif 'clear_board' in command:
            clear_board()
            print('=\n')
        elif 'showboard' in command:
            print('=')
            print_board()
        elif 'play' in command:
            play(command)
            print('=\n')
        elif 'genmove' in command:
            print('=', generate_move(BLACK if command.split()[-1].lower() == 'b' else WHITE) + '\n')
        elif 'loadsgf' in command:
            loadsgf(command)
            print('=\n')
        elif 'quit' in command:
            generate_video()
            sys.exit()
        else:
            print('=\n')  # skip unsupported commands


gtp()

