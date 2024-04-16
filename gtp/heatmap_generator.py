from PIL import Image, ImageDraw, ImageFont
import numpy as np

class MapGenerator:
    def __init__(self, square_size=97, line_width=5, red_start_val=200, green_start_val=200, blue_start_val=0):
        self.SQUARE_SIZE = square_size
        self.LINE_WIDTH = line_width
        self.RED = red_start_val
        self.GREEN = green_start_val
        self.BLUE = blue_start_val
        self.ADD_RED = 255-self.RED
        self.ADD_GREEN = 255-self.GREEN

    def init_new_map(self, grid_color=28):
        cols = 7*self.SQUARE_SIZE + 8*self.LINE_WIDTH
        rows = 8*self.SQUARE_SIZE + 9*self.LINE_WIDTH
        # Initialize image arrays for mcts counts & nnet probabilities 
        new_map = np.zeros((rows, cols, 3), dtype=np.uint8)
    
        # Draw gridlines on the image
        for i in range(8):
            start = i * ((self.SQUARE_SIZE + self.LINE_WIDTH))
            stop = start + self.LINE_WIDTH
            new_map[start:stop, :] = [grid_color, grid_color, grid_color]
            new_map[:-(self.LINE_WIDTH+self.SQUARE_SIZE), start:stop] = [grid_color, grid_color, grid_color]
        
        # Draw Pass Move Lines on Image
        start = cols
        stop = rows
        new_map[-self.LINE_WIDTH:, :] = [grid_color, grid_color, grid_color]
        new_map[start:, 0:self.LINE_WIDTH] = [grid_color, grid_color, grid_color]
        new_map[start:, -self.LINE_WIDTH:] = [grid_color, grid_color, grid_color]
        
        return(new_map)
    
    def generate_game_board(self, board, action):
        board_arr = self.init_new_map(grid_color=64)
        for i in range(7):
            for j in range(7):
                pos = board.pieces[i][j]
                row_start = (i * self.SQUARE_SIZE) + (self.LINE_WIDTH * (i+1))
                col_start = (j * self.SQUARE_SIZE) + (self.LINE_WIDTH * (j+1))
                row_end = row_start+self.SQUARE_SIZE
                col_end = col_start+self.SQUARE_SIZE
                if action == ((i*7) + j): # Move just made
                    move_red, move_green, move_blue = 0, 175, 255
                elif pos == 1: # Black Piece
                    move_red, move_green, move_blue = 5, 5, 5
                elif pos == -1: # White Piece
                    move_red, move_green, move_blue = 250, 250, 250
                else: # Empty
                    move_red, move_green, move_blue = 122, 82, 49
                """elif curPlayer == 1:
                    if pos == 1:
                        move_red, move_green, move_blue = 5, 5, 5
                    elif pos == -1:
                        move_red, move_green, move_blue = 250, 250, 250
                    else: 
                        move_red, move_green, move_blue = 122, 82, 49
                elif curPlayer == -1:
                    if pos == 1:
                        move_red, move_green, move_blue = 250, 250, 250
                    elif pos == -1:
                        move_red, move_green, move_blue = 5, 5, 5
                    else:
                        move_red, move_green, move_blue = 122, 82, 49"""
                board_arr[row_start:row_end, col_start:col_end] = [move_red, move_green, move_blue]
        board_image = Image.fromarray(board_arr)
        return board_image
    

    def generate_map_color(self, raw_count):
        if raw_count > 0.50:
            move_red = int((self.RED - (self.RED*(raw_count-0.50)*2)))
            move_green = self.GREEN
            move_blue = self.BLUE
        else: 
            if raw_count >= 0.01:
                move_green = int((self.GREEN - (self.GREEN*(0.50-raw_count)*2)) + ((25*(1/raw_count))*raw_count))
            else: 
                move_green = int((self.GREEN - (self.GREEN*(0.50-raw_count)*2)))  
            move_red = self.RED
            move_blue = self.BLUE

        return move_red, move_green, move_blue


    def generate_v_color(self, v_val):
        if v_val > 0.0:
            move_red = int((self.RED - (self.RED*v_val)))
            if(move_red > 20):
                move_red = int(move_red - (.10 * (self.RED-move_red)))
            move_green = self.GREEN + int(self.ADD_GREEN * v_val)
            move_blue = self.BLUE
        else: 
            move_green = int((self.GREEN + (self.GREEN*v_val)))
            if(move_green > 20):
                move_green = int(move_green - (.10 * (self.GREEN-move_green)))
            move_red = self.RED + int(self.ADD_RED * (-v_val))
            move_blue = self.BLUE

        return move_red, move_green, move_blue


    def draw_text(self, map_array, percentages, use_val_size=False):
        SQUARE_SIZE = 97
        LINE_WIDTH = 5
        FONT_SIZE = int(SQUARE_SIZE/4) if not use_val_size else int(SQUARE_SIZE/4)-2
        image = Image.fromarray(map_array)
        # Draw the percentages on the image squares
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('Prototype.ttf', FONT_SIZE)
        row_count = 0
        col_count = 0
        for i in range(len(percentages)-1):
            row_pos = (row_count * SQUARE_SIZE) + (LINE_WIDTH * (row_count+1)) + int(FONT_SIZE+(FONT_SIZE/2))
            col_pos = (col_count * SQUARE_SIZE) + (LINE_WIDTH * (col_count+1)) + int((FONT_SIZE)*.375)
            if use_val_size:
                row_pos += 5
                col_pos += 5 if len(percentages[i])<6 else 0
            draw.text((col_pos, row_pos), "{:>5}".format(percentages[i]), font=font, fill='black')
            if col_count == 6:
                col_count = 0
                row_count += 1
            else: 
                col_count += 1

        row_pos = (7*SQUARE_SIZE + 8*LINE_WIDTH) + int(FONT_SIZE+(FONT_SIZE/2))
        col_pos = (3 * SQUARE_SIZE) + (LINE_WIDTH * 3) + int((FONT_SIZE)*.375)
        draw.text((col_pos, row_pos), "{:>5}".format(percentages[-1]), font=font, fill='black')
        return image


    def generate_map(self, map_arr, stats_arr, file, use_val_colors = False):
        SQUARE_SIZE = 97
        LINE_WIDTH = 5
        percentages = []
        for i in range(7):
            for j in range(7):
                idx = (7*i) + j
                raw_num = stats_arr[idx]
                percentage = round((raw_num * 100), 2)
                formatted = " {:>5}% ".format(percentage)
                # Array holding move % strings for mcts
                percentages.append(f"{round(raw_num * 100, 1)}%")
                # Get the color for the coresponding grid position
                if not use_val_colors:
                    move_red, move_green, move_blue = self.generate_map_color(raw_num)
                else:
                    move_red, move_green, move_blue = self.generate_v_color(raw_num)
                # Assing this color to the proper region of the image
                row_start = (i * self.SQUARE_SIZE) + (self.LINE_WIDTH * (i+1))
                col_start = (j * self.SQUARE_SIZE) + (self.LINE_WIDTH * (j+1))
                row_end = row_start+self.SQUARE_SIZE
                col_end = col_start+self.SQUARE_SIZE
                map_arr[row_start:row_end, col_start:col_end] = [move_red, move_green, move_blue]

        raw_num = stats_arr[-1]
        percentage = round((raw_num * 100), 2)
        formatted = " {:>5}% ".format(percentage)
        percentages.append(f"Pass: {round(raw_num * 100, 1)}%")
        if not use_val_colors:
            move_red, move_green, move_blue = self.generate_map_color(raw_num)
        else:
            move_red, move_green, move_blue = self.generate_v_color(raw_num)
        row_start = 7*SQUARE_SIZE + 8*LINE_WIDTH
        row_end = row_start+SQUARE_SIZE
        col_start = LINE_WIDTH
        col_end = -LINE_WIDTH
        map_arr[row_start:row_end, col_start:col_end] = [move_red, move_green, move_blue]
                
        return map_arr, percentages
    
    def save_image(self, image, filename):
        image.save(filename)

    def add_title(self, image, move_num):
        FONT_SIZE = 50
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('Prototype.ttf', FONT_SIZE)
        title = f"Move {move_num}"
        y = 25
        x = image.size[0]/2 - FONT_SIZE
        draw.text((x, y), title, font=font, fill='black')
        return image
    
    def add_subtitles(self, image, subtitles, subtitle_xs, subtitle_ys):
        FONT_SIZE = 35
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('Prototype.ttf', FONT_SIZE)
        #y = 130
        for i in range(len(subtitles)):
            text = subtitles[i]
            x = subtitle_xs[i]
            y = subtitle_ys[i]
            draw.text((x, y), text, font=font, fill='black')
        return image
    
    
    def compile_one_image(self, images, filename, move_num):
        dim = images[0].size
        height = dim[1] + 200
        width = (dim[0]*len(images)) + 80

        new_map = np.zeros((height, width, 3), dtype=np.uint8)
        new_map[:, :] = [255, 255, 255]
        background = Image.fromarray(new_map)
        
        image_width = images[0].size[0]
        image_height = images[0].size[1]
        subtitle_xs = []
        subtitle_ys = []
        x = 20
        y = 175
        for image in images:
            subtitle_x = x + image_width/3
            subtitle_xs.append(subtitle_x)
            subtitle_ys.append(130)
            background.paste(image, (x, y))
            x = x + image_width + 20

        background = self.add_title(background, move_num)
        subtitles = ["MCTS Visit Counts".center(19), "Raw NNet Pi".center(19), "MCTS Q-Values".center(19)]
        background = self.add_subtitles(background, subtitles, subtitle_xs, subtitle_ys)

        background.save(filename)

    def compile_one_image_with_board(self, images, filename, move_num):
        dim = images[0].size
        height = (dim[1] + 200)*2 - 100
        width = (dim[0]*(len(images)-1)) + 80

        new_map = np.zeros((height, width, 3), dtype=np.uint8)
        new_map[:, :] = [255, 255, 255]
        background = Image.fromarray(new_map)
        
        image_width = images[0].size[0]
        image_height = images[0].size[1]
        subtitle_xs = []
        subtitle_ys = []
        x = 20
        y = 175
        count = 0
        for image in images:
            if count >= 3:
                x = int((width/2)-(image_width/2))
                y = y + image_height + 80
                subtitle_x = x + image_width/3
                subtitle_xs.append(subtitle_x)
                subtitle_ys.append(y - 45)
                background.paste(image, (x, y))
            else:
                subtitle_x = x + image_width/3
                subtitle_xs.append(subtitle_x)
                subtitle_ys.append(130)
                background.paste(image, (x, y))
                x = x + image_width + 20
            count += 1

        background = self.add_title(background, move_num)
        subtitles = ["MCTS Visit Counts".center(19), "Raw NNet Pi".center(19), "MCTS Q-Values".center(19), "Board State".center(19)]
        background = self.add_subtitles(background, subtitles, subtitle_xs, subtitle_ys)
        return background
        #background.save(filename)

    def was_deterministic(self, image, action):
        FONT_SIZE = 40
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('Prototype.ttf', FONT_SIZE)
        x = image.size[0]-560
        y = image.size[1]-560
        text = f"A NNet Prob. Was Over 50%\nChose Action = {action}"
        draw.text((x, y), text, font=font, fill='black')
        return(image)




            
