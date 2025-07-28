---
layout: default
title: Usage Guide
parent: Getting Started
nav_order: 2
permalink: /usage
---

# Usage Guide

Learn how to use AZ-Go for training, playing games, and analyzing positions.

## Basic Commands

### Start Training

```bash
# Main coordinator (on primary machine)
python start_main.py

# Worker nodes (on each worker)
python start_worker.py

# Note: Both scripts take no command-line arguments.
# Configuration is done through configs/config.yaml
```

### Play Against the Model

```bash
# Interactive GTP engine
python engine/run_engine.py       # Standard mode
python engine/run_engine.py -cli  # With command prompt
```

### Analyze Games

```bash
# Analyze SGF file with KataGo
python katago/run_katago.py  # Analyzes sgf/figure_c1.sgf (hardcoded)
```

## Configuration Files

### Main Configuration (`configs/config.yaml`)

```yaml
# Customize training parameters
board_size: 7

# Adjust neural network
nn_args:
  num_channels: 128
  depth: 18
  value_head_size: 32
  policy_head_size: 32

# Modify MCTS
num_mcts_sims: 500
cpuct: 1.0
fpu_value: 0.0

# Training settings
batch_size: 512
learning_rate: 0.01
epochs: 10
```

**Note about Komi:** The komi value is hardcoded in `go/go_logic.py` (line 25) as 5.5 and cannot be changed through the config file. To modify komi, you need to edit the source code directly.

## Common Workflows

### 1. Training a New Model

```bash
# Step 1: Configure parameters
nano configs/config.yaml

# Step 2: Start overseer (only 1 across all machines)
python start_main.py

# Step 3: Start workers (up to two per machine)
python start_worker.py
```

### 2. Resuming Training

```bash
# Training automatically resumes from last checkpoint
# The overseer and workers handle checkpoint management internally
python start_main.py
```

## Integration with Go GUIs

### Sabaki

To use AZ-Go with Sabaki, you need to build a standalone executable:

1. **Configure the engine:**
   - Place your model file as `best.pth.tar` in the `engine/` directory
   - Edit `engine/engine_config.yaml` to set the correct `network_type`:
     - `RES` - 19 layer ResNet (current default)
     - `DEP` - Deprecated 18 layer ResNet (e.g., Model Q)
     - `CNN` - Convolutional Neural Network (not recommended)

2. **Build the GTP engine executable:**
   ```bash
   cd /path/to/AZ-Go
   ./engine/build_engine.sh
   ```
   This creates an executable in `engine/dist/run_engine` with the model embedded

3. **Add to Sabaki:**
   - Open Sabaki → Engines → Manage Engines
   - Add new engine:
     - Path: `/path/to/AZ-Go/engine/dist/run_engine`
     - No arguments needed

Note: The engine at `engine/run_engine.py` is the GTP interface. The `gtp/engine.py` file is for analysis and visualization, not for playing.

## Debugging and Analysis

### Debug Scripts

```bash
# Test self-play
python debug/debug_self_play.py

# Test arena
python debug/debug_arena.py

# Test scoring
python debug/debug_scoring.py

# Test worker self-play functionality
python debug/debug_worker.py
```