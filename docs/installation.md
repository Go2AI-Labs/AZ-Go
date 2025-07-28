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

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install torch torchvision numpy pyyaml paramiko
```

Or use requirements.txt:
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
2. **Update worker list** in `configs/config.yaml`
3. **Ensure consistent Python environment** across nodes
4. **Test connectivity**:
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
- Activate virtual environment
- Reinstall dependencies

## Next Steps

- [Architecture Overview](architecture) - Understand the system design
- [Training Process](training) - Start training your model
- [Usage Guide](usage) - Run games and analysis