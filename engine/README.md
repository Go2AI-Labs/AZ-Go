# Engine Code
### Directory Structure
All engine-related files should be directly under `AZ-Go/engine/`. This includes the following:
- `engine-config.yaml`
- `best.pth.tar` (or whatever you want to name the model weights file)
### Model Loading
There are three types of models AZ-Go has trained, and the `engine-config.yaml` file allows you to load any of them by changing the value for the key `network_type`. Possible values are:
- `RES` -> 19 layer ResNet (the current default for new models)
- `DEP` -> Deprecated 18 layer ResNet (i.e. Model Q)
- `CNN` -> Convolutional Neural Network (not recommended)
### Building the Engine
Run the `build_engine.sh` script which will remove the folders `build` and `dist` (if needed) and create an executable in the  `dist` folder. This script *should* be able to be run from any directory.