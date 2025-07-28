
# AZ-Go: A Custom AlphaGo Zero Implementation for Compact Board Configurations

A distributed AlphaGoZero implementation specifically designed for training Go models. This project implements the AlphaGo Zero algorithm with distributed training capabilities, neural network management, and comprehensive logging.

📚 **[Read the Documentation](https://go2ai-labs.github.io/AZ-Go/)**

## Features

- **Go Game Implementation**: Complete Go game logic with proper rule handling on configurable board sizes (default 7x7)
- **Distributed Training**: Support for training across multiple worker nodes with SSH connectivity
- **Neural Network Architecture**: ResNet and CNN architectures with configurable parameters
- **MCTS Integration**: Monte Carlo Tree Search with configurable simulation counts and exploration parameters
- **KataGo Integration**: Interface with KataGo engine for analysis and evaluation
- **Comprehensive Logging**: Training progress, game history, and performance metrics
- **GTP Protocol Support**: Integration with Go Text Protocol for engine communication

## Quick Start

### Main Training (Distributed)
Start the main overseer node:
```bash
python start_main.py
```

### Worker Training
Start worker nodes for distributed training:
```bash
python start_worker.py
```

## Configuration

All training parameters are configured in `configs/config.yaml`:

- **Board Size**: 7x7 Go board (configurable)
- **Training**: 500 iterations with 5000 self-play episodes per iteration
- **MCTS**: 500 simulations with C_PUCT of 1.0
- **Neural Network**: ResNet architecture with 128 channels, SGD optimizer
- **Distributed**: Support for multiple parallel workers

## Project Structure

```
├── go/                     # Go game implementation
│   ├── go_game.py         # Main game interface
│   ├── go_logic.py        # Go rules and board logic
│   └── game.py            # Abstract game interface
├── training/              # Training infrastructure
│   ├── overseer.py        # Main training coordinator
│   ├── coach.py           # Training loop management
│   ├── arena.py           # Model evaluation
│   └── worker.py          # Distributed worker nodes
├── neural_network/        # Neural network implementations
│   ├── go_alphanet.py     # AlphaZero network architecture
│   └── neural_net.py      # Network interface
├── mcts.py                # Monte Carlo Tree Search
├── distributed/           # Distributed training support
├── katago/               # KataGo integration
├── gtp/                  # Go Text Protocol support
├── engine/               # Game engine integration
└── configs/              # Configuration files
```

## Training Process

1. **Self-Play**: Workers generate training games using MCTS
2. **Neural Network Training**: Overseer trains the network on collected games
3. **Arena Evaluation**: New models compete against current best
4. **Model Selection**: Better performing models are promoted

## Logging and Analysis

- **Checkpoints**: Model saves in `logs/checkpoints/`
- **Training Examples**: Game data in `logs/train_examples/`
- **Game History**: SGF files in `logs/arena_game_history/`
- **Performance Graphs**: Training metrics in `logs/graphs/`
- **KataGo Analysis**: Detailed game analysis in `katago/results/`

## Requirements

- Python 3.x
- PyTorch
- NumPy
- PyYAML
- SSH access for distributed training
- KataGo binary (optional, for analysis)
