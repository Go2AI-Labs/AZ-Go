---
layout: default
title: Codebase Structure
parent: Technical Documentation
nav_order: 1
permalink: /codebase-structure
---

# Codebase Structure

This section provides a comprehensive overview of the AZ-Go codebase organization, helping developers understand the architecture and locate specific functionality.

## Directory Overview

```
AZ-Go/
├── configs/              # Configuration files
├── distributed/          # Distributed training components
├── engine/              # Go engine implementation
├── go/                  # Core Go game logic
├── gtp/                 # Go Text Protocol interface
├── katago/              # KataGo integration for analysis
├── lifecycle/           # Training lifecycle management
├── logger/              # Logging utilities
├── neural_network/      # Neural network models
├── pytorch_classification/  # Additional ML utilities
├── training/            # Training pipeline components
└── utils/               # General utilities
```

## Core Components

### Game Logic (`go/`)
The fundamental Go game implementation:
- `game.py` - Base game interface
- `go_game.py` - Go-specific game implementation
- `go_logic.py` - Core game rules and logic

### Neural Network (`neural_network/`)
Deep learning models for position evaluation:
- `go_alphanet.py` - Main AlphaZero network architecture
- `neural_net_wrapper.py` - PyTorch model wrapper
- `neural_net.py` - Base neural network interface

### Monte Carlo Tree Search (`mcts.py`)
The MCTS algorithm implementation for move selection, featuring:
- Tree search with UCB exploration
- Virtual loss for parallel search
- Dirichlet noise for exploration
- Tree reuse between moves

### Training Pipeline (`training/`)
Components for the self-play training loop:
- `coach.py` - Main training coordinator
- `self_play_manager.py` - Manages self-play game generation
- `arena.py` - Model comparison arena
- `worker.py` - Distributed worker implementation

### Distributed System (`distributed/`)
Infrastructure for distributed training:
- `ssh_connector.py` - SSH connection management
- `status_manager.py` - Worker status tracking

### Engine Interface (`engine/`)
Go engine implementation for playing against the model:
- `engine.py` - Main engine interface
- `run_engine.py` - Engine runner script
- `build_engine.sh` - Engine build script

### Analysis Tools (`katago/`)
Integration with KataGo for move analysis:
- `katago_wrapper.py` - KataGo interface wrapper
- `run_katago.py` - Analysis runner
- `sgf/` - Sample game files for analysis

## Entry Points

- `start_main.py` - Main training orchestrator
- `start_worker.py` - Distributed worker process
- `engine/run_engine.py` - Standalone Go engine

## Configuration

All configuration is managed through `configs/config.yaml`, which controls:
- Board size and game rules
- Neural network architecture
- MCTS parameters
- Training hyperparameters
- Distributed training settings

## Data Flow

1. **Self-Play**: Workers generate games using MCTS + current model
2. **Data Collection**: Games are collected and stored as training examples
3. **Neural Network Training**: Model is trained on collected data
4. **Model Evaluation**: New model is compared against previous best
5. **Model Update**: If improved, new model becomes current best

## Key Files Reference

| File | Purpose |
|------|---------|
| `mcts.py` | MCTS algorithm implementation |
| `go/go_logic.py` | Go game rules |
| `neural_network/go_alphanet.py` | Neural network architecture |
| `training/coach.py` | Training orchestration |
| `distributed/ssh_connector.py` | Remote worker management |
| `lifecycle/neural_net_manager.py` | Model versioning |
| `logger/graph_logger.py` | Training visualization |

## Development Guidelines

When modifying the codebase:
1. Game logic changes should be made in `go/`
2. Neural network modifications go in `neural_network/`
3. Training algorithm changes belong in `training/`
4. New analysis tools should integrate with `katago/`
5. Always update `configs/config.yaml` for new parameters