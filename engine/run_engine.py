from engine import Engine
import sys

# Create the engine
engine = Engine()
# Collect arguments and set variables accordingly
args = sys.argv[1:]
if "-cli" in args:
    command_prompt = "\n>> "
else:
    command_prompt = ""
# Main execution loop
while True:
    command = input(command_prompt)
    engine.run_command(command)