---
layout: default
title: Architecture
permalink: /architecture
---

# Architecture Overview

AZ-Go implements the AlphaZero algorithm with a distributed training architecture designed for efficiency and scalability.

## System Components

### Core Components

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│    Overseer     │────▶│   Workers    │────▶│    Arena    │
│  (Coordinator)  │     │ (Self-Play)  │     │ (Evaluation)│
└────────┬────────┘     └──────┬───────┘     └──────┬──────┘
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│  Neural Network │     │     MCTS     │     │  Game Logic │
│   (ResNet-18)   │     │ (Tree Search)│     │  (Go Rules) │
└─────────────────┘     └──────────────┘     └─────────────┘
```

### 1. Overseer (`training/overseer.py`)

The central coordinator that:
- Manages the training loop
- Distributes models to workers
- Collects self-play games
- Trains neural networks
- Evaluates model improvements

### 2. Workers (`training/worker.py`)

Distributed nodes that:
- Generate self-play games
- Run MCTS simulations
- Execute neural network inference
- Send training data back to overseer

### 3. Neural Network (`neural_network/go_alphanet.py`)

#### ResNet-18 Architecture

At the core of this program is a neural network used to get move probabilities and win rate estimates for every board state. We use a Residual Neural Network (ResNet-18) which addresses the "vanishing gradient problem" through residual connections (skip connections).

**Key Innovation**: The input to each Residual Block is added to the output of the final Convolutional Layer in the block, allowing the network to learn residual mappings rather than complete transformations from scratch.

**Input Structure** (18x7x7 stack):
- **Layers 1-16**: Past 16 board states from each player's perspective
  - 1 = black stones, -1 = white stones, 0 = empty
- **Layer 17**: Current player indicator (all 1s for black, all -1s for white)
- **Layer 18**: Sensibility layer - territory control encoding

**Output Components**:
- **Policy Head**: 49-element probability distribution (one per board intersection)
- **Value Head**: Win rate estimate in [-1, 1] (-1 = loss, 1 = win)

```python
Input (18x7x7)
    │
Conv Block
    │
ResNet Blocks (x9)
    │
    ├─── Policy Head ──▶ 49 move probabilities
    │
    └─── Value Head ───▶ Position evaluation [-1, 1]
```

This is effectively an image classification network where:
- Input "channels" are board states instead of RGB
- Output "classes" are possible next moves instead of object categories

### 4. MCTS (`mcts.py`)

#### Monte Carlo Tree Search Implementation

MCTS is a heuristic search algorithm that combines tree search with random sampling to make optimal decisions in Go's vast decision space. It operates through four main steps:

**1. Selection**:
- Navigate through the tree selecting nodes with highest Upper Confidence Bound (UCB)
- UCB balances:
  - **Exploitation**: Following promising paths (high win rate)
  - **Exploration**: Visiting less-explored nodes (low visit count)
- C_PUCT parameter controls exploration vs exploitation balance

**2. Expansion**:
- Add new child node when reaching non-terminal leaf
- Initialize node value using neural network evaluation
- Store win rate estimate and probability distribution

**3. Rollout**:
- Traditional MCTS uses random playouts
- We use neural network value estimate instead
- Initial visit count set to 1

**4. Backpropagation**:
- Update all traversed nodes with new information
- Propagate values up the tree
- Higher-level nodes reflect deeper exploration

**Usage in Go**:
- Run MCTS for every move selection
- Output: Visit counts for each possible move
- Next move: Index with maximum visit count

### 5. Game Engine (`go/go_game.py`)

Go game implementation:
- Legal move generation
- Capture detection
- Ko rule enforcement
- Territory scoring
- SGF export

## Data Flow

### Training Pipeline

1. **Self-Play Generation**
   ```
   Worker → MCTS → Neural Net → Game States → Training Examples
   ```

2. **Neural Network Training**
   ```
   Training Examples → Overseer → SGD Optimization → New Model
   ```

3. **Model Evaluation**
   ```
   New Model vs Best Model → Arena → Win Rate → Model Selection
   ```

### Communication Protocol

Workers communicate with overseer via:
- **Model Distribution**: Pickled PyTorch models
- **Game Collection**: Serialized training examples
- **Status Updates**: JSON progress reports

## File Organization

```
lifecycle/                  # Model and data lifecycle management
├── lifecycle_manager.py    # Coordinates all lifecycle operations
├── neural_net_manager.py   # Model versioning and storage
└── train_example_manager.py # Training data management

distributed/               # Distributed training infrastructure
├── ssh_connector.py      # SSH connection handling
└── status_manager.py     # Worker status tracking

logger/                    # Logging and visualization
├── graph_logger.py       # Training metrics plotting
└── gtp_logger.py        # Game protocol logging
```

## Key Design Decisions

### 1. Distributed Architecture
- **Scalability**: Add workers dynamically
- **Fault Tolerance**: Workers can disconnect/reconnect
- **Load Balancing**: Automatic work distribution

### 2. Memory Management
- **Example Buffer**: Fixed-size training history
- **Tree Reuse**: MCTS tree persistence between moves
- **Batch Processing**: Efficient GPU utilization

### 3. Model Versioning
- **Checkpointing**: Regular model saves
- **Best Model Tracking**: Automatic selection
- **Rollback Support**: Previous model recovery

## Performance Optimizations

### Neural Network
- Batch inference for multiple MCTS simulations
- FP16 training support
- Gradient accumulation for large batches

### MCTS
- Virtual loss for parallel simulations
- Tree reuse between moves
- Cached neural network evaluations

### Distributed Training
- Asynchronous game generation
- Compressed model transfer
- Parallel worker execution

## Extension Points

### Adding New Features

1. **New Network Architectures**: Implement in `neural_network/`
2. **Alternative Search**: Replace MCTS in game generation
3. **Different Games**: Implement game interface in `go/`
4. **Analysis Tools**: Add to `katago/` or `gtp/`

### Configuration Options

All major parameters configurable via `configs/config.yaml`:
- Network architecture
- Training hyperparameters
- MCTS settings
- Distributed configuration

## Next Steps

- [Training Process](training) - Detailed training pipeline
- [Usage Guide](usage) - Running the system