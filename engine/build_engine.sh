#!/usr/bin/env python

if ! cd engine; then
    echo "Already in /engine subdirectory"
fi

if [ -d "build" ]; then
    echo "The folder 'build' exists"
    rm -r build
    echo "Removed folder 'build'"
else
    echo "The folder 'build' does not exist"
fi

if [ -d "dist" ]; then
    echo "The folder 'dist' exists"
    rm -r dist
    echo "Removed folder 'dist'"
else
    echo "The folder 'dist' does not exist"
fi

if [ -e "run_engine.spec" ]; then
    echo "The file 'run_engine.spec' exists"
    rm run_engine.spec
    echo "Removed 'run_engine.spec'"
else
    echo "The file 'run_engine.spec' does not exist."
fi

pyinstaller -p ../ -p ../pytorch_classification/utils/progress --add-data "engine_config.yaml:." --add-data "best.pth.tar:." --onefile run_engine.py

echo "Finished creating executable :)"