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
├── configs/             # Configuration files
├── debug/               # Debug and testing utilities
├── distributed/         # Distributed training components
├── docs/                # Documentation (Jekyll site)
├── engine/              # Go engine implementation
├── go/                  # Core Go game logic
├── gtp/                 # Go Text Protocol interface
├── katago/              # KataGo integration for analysis
├── lifecycle/           # Training lifecycle management
├── logger/              # Logging utilities
├── neural_network/      # Neural network models
├── pytorch_classification/  # Additional ML utilities
├── training/            # Training pipeline components
├── utils/               # General utilities
├── definitions.py       # Common path definitions
├── mcts.py              # Monte Carlo Tree Search implementation
├── start_main.py        # Main training orchestrator
└── start_worker.py      # Distributed worker process
```

## Core Components

### Game Logic (`go/`)
The fundamental Go game implementation:
- `game.py` - Base game interface
- `go_game.py` - Go-specific game implementation
- `go_logic.py` - Core game rules and logic

### Neural Network (`neural_network/`)
Deep learning models for position evaluation:
- `neural_net.py` - Base neural network interface
- `neural_net_wrapper.py` - PyTorch model wrapper
- `go_neural_net.py` - Go-specific neural network implementation
- `go_alphanet.py` - Main AlphaZero network architecture
- `go_alphanet_deprecated.py` - Deprecated network architecture

### Monte Carlo Tree Search (`mcts.py`)
The MCTS algorithm implementation for move selection, featuring:
- Tree search with UCB exploration
- Virtual loss for parallel search
- Dirichlet noise for exploration
- Tree reuse between moves

### Debug Tools (`debug/`)
Utility scripts for testing and debugging:
- `debug_self_play.py` - Test self-play functionality
- `debug_arena.py` - Test arena competitions
- `debug_scoring.py` - Test game scoring
- `debug_worker.py` - Test worker connections

### Training Pipeline (`training/`)
Components for the self-play training loop:
- `coach.py` - Main training coordinator
- `overseer.py` - Training overseer that manages iterations
- `self_play_manager.py` - Manages self-play game generation
- `arena.py` - Model comparison arena (class, not standalone script)
- `arena_manager.py` - Manages arena competitions
- `worker.py` - Distributed worker implementation

### GTP Interface (`gtp/`)
Go Text Protocol implementation for GUI integration:
- `engine.py` - Main GTP engine interface
- `engine_mcts.py` - MCTS implementation for GTP engine
- `heatmap_generator.py` - Visual heatmap generation for move analysis

### Distributed System (`distributed/`)
Infrastructure for distributed training:
- `ssh_connector.py` - SSH connection management
- `status_manager.py` - Worker status tracking
- `status.txt` - Worker status file

### Engine Interface (`engine/`)
Go engine implementation for playing against the model:
- `engine.py` - Main engine interface
- `run_engine.py` - Engine runner script (accepts -cli flag)
- `engine_legacy.py` - Legacy engine implementation
- `engine_config.yaml` - Engine configuration
- `build_engine.sh` - Engine build script (PyInstaller)
- `README.md` - Engine documentation

### Analysis Tools (`katago/`)
Integration with KataGo for move analysis:
- `katago_wrapper.py` - KataGo interface wrapper
- `katago_parameters.py` - KataGo configuration
- `run_katago.py` - Analysis runner (hardcoded to analyze sgf/figure_c1.sgf)
- `query_example.json` - Example query format for KataGo
- `response_example.json` - Example response format from KataGo
- `sgf/` - Sample game files for analysis
- `results/` - Analysis results storage

## Entry Points

- `start_main.py` - Main training orchestrator (no command-line arguments)
- `start_worker.py` - Distributed worker process (no command-line arguments)
- `engine/run_engine.py` - Standalone Go engine (accepts -cli flag only)
- `gtp/engine.py` - GTP interface for Go GUIs (no command-line arguments)
- `katago/run_katago.py` - KataGo analysis runner (hardcoded SGF file)

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
| `definitions.py` | Common path definitions and configurations |
| `go/go_logic.py` | Go game rules |
| `neural_network/go_alphanet.py` | Neural network architecture |
| `training/coach.py` | Training orchestration |
| `training/overseer.py` | Main training loop management |
| `distributed/ssh_connector.py` | Remote worker management |
| `lifecycle/neural_net_manager.py` | Model versioning |
| `logger/graph_logger.py` | Training visualization |
| `utils/config_handler.py` | Configuration file management |

## Development Guidelines

When modifying the codebase:
1. Game logic changes should be made in `go/`
2. Neural network modifications go in `neural_network/`
3. Training algorithm changes belong in `training/`
4. New analysis tools should integrate with `katago/`
5. Always update `configs/config.yaml` for new parameters