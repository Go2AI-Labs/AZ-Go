from engine.engine import Engine

engine = Engine()

while True:
    command = input()

    if 'name' in command:
        engine.name()