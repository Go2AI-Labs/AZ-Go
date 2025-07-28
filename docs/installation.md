---
layout: default
title: Installation Guide
parent: Getting Started
nav_order: 1
permalink: /installation
---

# Installation Guide

## Prerequisites

- **Python 3.7+** (tested with 3.8, 3.9)
- **CUDA-capable GPU** (recommended for training)
- **4GB+ RAM** per worker node
- **SSH access** (for distributed training)

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

Benefits of using Conda:
- Consistent environments across different machines
- Better handling of system-level dependencies
- Easier to manage CUDA/PyTorch versions
- Works seamlessly in distributed settings

### 3. Install Dependencies

Using conda (recommended for better CUDA support):
```bash
conda install pytorch torchvision cudatoolkit=11.8 -c pytorch
conda install numpy pyyaml
pip install paramiko fabric
```

Or use pip with requirements.txt:
```bash
pip install -r requirements.txt
```

## Optional Components

### KataGo Integration

For game analysis features:

1. Download KataGo binary from [KataGo releases](https://github.com/lightvector/KataGo/releases)
2. Place in project root or update path in config
3. Download neural network weights
4. Configure in `engine/engine_config.yaml`

### Distributed Training Setup

For multi-node training:

1. **Configure SSH keys** for passwordless authentication
2. **Create sensitive configuration file** at `configs/sensitive.yaml`:
   
   ```yaml
   # configuration file for SSH over local network
   
   # configuration for main machine
   main_username: your_username         # username for login to main server
   main_password: your_password         # password for login to main server (optional if using SSH keys)
   main_server_address: hostname.edu    # location of main server
   main_directory: /home/user/AZ-Go     # project directory on main server
   
   # configuration for worker machine
   worker_username: worker_user         # username for login to worker server
   worker_password: worker_pass         # password for login to worker server (optional if using SSH keys)
   worker_server_address: worker.edu    # location of remote server
   
   # directories for scp
   distributed_models_directory: /home/user/dis/models     # directory on worker server to send models to
   distributed_examples_directory: /home/user/dis/examples # directory on main server to send examples to
   ```
   
   **Important**: 
   - Keep `sensitive.yaml` secure and never commit it to version control
   - Add `configs/sensitive.yaml` to your `.gitignore` file
   - Use SSH keys instead of passwords for better security

3. **Update worker list** in `configs/config.yaml`
4. **Ensure consistent Python environment** across nodes
5. **Test connectivity**:
   ```bash
   python distributed/ssh_connector.py
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

# Distributed settings
num_parallel_workers: 4
worker_hosts:
  - localhost
  - worker1.example.com
  - worker2.example.com
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
- Check GPU availability: `python -c "import torch; print(torch.cuda.is_available())"`

### SSH Connection Failed
- Verify SSH keys: `ssh-add -l`
- Test manual connection: `ssh user@host`
- Check firewall settings

### Import Errors
- Ensure project root is in PYTHONPATH
- Activate conda environment: `conda activate azgo`
- Reinstall dependencies: `conda install --file requirements.txt`

## Next Steps

- [Architecture Overview](architecture) - Understand the system design
- [Training Process](training) - Start training your model
- [Usage Guide](usage) - Run games and analysis