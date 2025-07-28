---
layout: default
title: Installation Guide
parent: Getting Started
nav_order: 1
permalink: /installation
---

# Installation Guide

## Basic Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/AZ-Go.git
cd AZ-Go
```

### 2. Create Conda Environment

We recommend using Conda for environment management, especially for distributed setups:

```bash
# Create a new conda environment with Python 3.8
conda create -n azgo python=3.8
conda activate azgo
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Distributed Training Setup

For multi-node training:

1. Configure SSH keys for passwordless authentication
2. Create sensitive configuration file at `configs/sensitive.yaml`:

   ⚠️ **Note**: This file does not exist in the git repository for security reasons. You must create it manually:
   
   ```yaml
   # configuration file for SSH over local network
   
   # configuration for main machine
   main_username: your_username         # username for login to main server
   main_server_address: hostname.edu    # location of main server
   main_directory: /home/user/AZ-Go     # project directory on main server
   
   # configuration for worker machine
   worker_username: worker_user         # username for login to worker server
   worker_server_address: worker.edu    # location of remote server
   
   # directories for scp
   distributed_models_directory: /home/user/dis/models     # directory on worker server to send models to
   distributed_examples_directory: /home/user/dis/examples # directory on main server to send examples to
   ```

## Configuration

Edit `configs/config.yaml` to customize:

```yaml
# Board and game settings
board_size: 7
komi: 5.5

# Training parameters
num_iterations: 500
num_episodes: 5000
num_mcts_sims: 500

# Neural network
nn_channels: 128
nn_depth: 18
learning_rate: 0.01
```

## Verify Installation

Run the test suite:

```bash
python -m pytest tests/
```

Or run a quick self-play game:

```bash
python debug/debug_self_play.py
```

## Troubleshooting

### CUDA Issues
- Ensure CUDA toolkit matches PyTorch version
- Check GPU availability: `python -c "import torch; print(torch.cuda.is_available())"` (should print `true`)

### SSH Connection Failed
- Verify SSH keys: `ssh-add -l`
- Test manual connection: `ssh user@host` (if successful, no password prompt will show)

### Import Errors
- Ensure project root is in PYTHONPATH
- Activate conda environment: `conda activate azgo`
- Reinstall dependencies: `conda install --file requirements.txt`

## Next Steps

- [Architecture Overview](architecture) - Understand the system design
- [Training Process](training) - Start training your model
- [Usage Guide](usage) - Run games and analysis