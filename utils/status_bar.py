import sys


class StatusBar:
    BAR_WIDTH = 45
    PRINT_PERCENT = True

    def __init__(self, title, label, suffix, total_steps, current_step=0):
        self.title = title
        self.label = label
        self.suffix = suffix
        self.total_steps = total_steps
        self.current_step = current_step

    # pass new current_step value, not an amount to increment current step
    def step_bar(self, current_step):
        self.current_step = current_step
        self.__make_bar()

    def __make_bar(self):
        # UTF-8 left blocks: 1, 1/8, 1/4, 3/8, 1/2, 5/8, 3/4, 7/8
        utf_8s = ["█", "▏", "▎", "▍", "▌", "▋", "▊", "█"]
        perc = 100 * float(self.current_step) / float(self.total_steps)
        max_ticks = self.BAR_WIDTH * 8
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

        if len(self.title) > 0:
            disp = self.title + ": "  # Optional title to progress display

        # Print progress bar in green: https://stackoverflow.com/a/21786287/6929343
        disp += "\x1b[0;32m"  # Color Green
        disp += bar  # Progress bar to progress display
        disp += "\x1b[0m"  # Color Reset
        if self.PRINT_PERCENT:
            # If requested, append percentage complete to progress display
            if perc > 100.0:
                perc = 100.0  # Fix "100.04 %" rounding error
            disp += " {:6.2f}".format(perc) + " %"
        disp += f"   {self.current_step}/{self.total_steps} {self.label} {self.suffix}"

        # Output to terminal repetitively over the same line using '\r'.
        sys.stdout.write("\r" + disp)
        sys.stdout.flush()

        # print newline when finished
        if self.current_step >= self.total_steps:
            print()
