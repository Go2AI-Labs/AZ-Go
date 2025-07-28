---
layout: default
title: Architecture Overview
parent: Technical Documentation
nav_order: 2
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

**Key Innovation**: The input to each Residual Block is added to the output of the final Convolutional Layer in the block, allowing the network to learn residual mappings rather than complete transformations from scratch. This allows gradients to flow more easily through the network during backpropagation, reducing vanishing gradient issues and enabling much deeper architectures.

**Why ResNet-18**: Despite being relatively shallow compared to larger versions like ResNet-50 or ResNet-152, ResNet-18 works well for our use case because the board size is relatively small (7x7 compared to standard 19x19 Go boards). It consists of 18 layers with learnable weights, structured into four major blocks, each containing two residual units.

**Input Structure** (18x7x7 stack):
- **Layers 1-16**: Past 16 board states from each player's perspective
  - 1 = black stones, -1 = white stones, 0 = empty
- **Layer 17**: Current player indicator (all 1s for black, all -1s for white)
- **Layer 18**: Sensibility layer - encodes intersections considered to be the current player's territory (reachable only by current player's stones)

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

**Training Parameters**:
- **Optimizer**: Adam
- **Batch Size**: 2048
- **Initial Learning Rate**: 0.0001
- **Epochs**: 10 per training iteration

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
- Add new child node when reaching non-terminal leaf that is not a terminal state
- Initialize node value using neural network evaluation
- Store win rate estimate and probability distribution with initial visit count of 1

**3. Rollout**:
- Traditional MCTS uses random playouts to terminal states
- We use neural network value estimate instead (more efficient)
- Node initialized with NN output values

**4. Backpropagation**:
- Update all traversed nodes with new information
- Propagate values up the tree
- Higher-level nodes reflect deeper exploration results

**Usage in Go**:
- Run MCTS for every move selection in every game
- Output: Vector containing visit counts for each node 1 level down from root
- Next move: Index with maximum visit count corresponds to board intersection

**Randomness for Training**:
- **Dirichlet noise**: Applied to probability distribution at each tree node
- **Temperature parameter**: Random moves for first n moves in game
- Ensures wider variety of training samples and prevents overfitting

### 5. Game Engine (`go/go_game.py`)

Go game implementation:
- Legal move generation
- Capture detection
- Ko rule enforcement
- Territory scoring
- SGF export

## Training Process

The training loop consists of three main phases:

### 1. Data Generation Phase (Self-Play)
- **Most time-consuming phase** - generates training data through self-play
- **Reinforcement learning approach** - model starts with zero knowledge except Go rules
- **Initial model**: Randomly initialized weights
- **Sample collection**: 50,000 individual samples per iteration
- **Training set**: Most recent 4 iterations of samples (iterations 1, 2, 3 contain 50k, 100k, 150k samples respectively)

**Training Example Components**:
- **Input**: 18x7x7 board state stack
- **Target 1**: Length-49 vector with 1 at index of most visited MCTS move
- **Target 2**: Game result (-1 for loss, 1 for win)

**Randomness Added**:
- Temperature parameter for random moves in first n moves
- Dirichlet noise during MCTS on probability distributions
- Prevents overfitting and ensures game variety

### 2. Neural Network Training Phase
- Standard neural network training process
- Uses collected samples from data generation
- Parameters listed in Neural Network section above

### 3. Model Evaluation Phase (Arena)
- **Games played**: 50 games between new model vs previous best
- **Acceptance threshold**: New model must win ≥54% (27/50 games)
- **Failure case**: If threshold not met, new model discarded, previous best retained
- **Randomness**: Board states rotated by 90° random times before NN input
  - Output transformed back to match original orientation
  - All Go board rotations are equivalent
  - Adds variation without modifying model output

## Data Flow

### Training Pipeline

1. **Self-Play Generation**
   ```
   Worker → MCTS → Neural Net → Game States → Training Examples
   ```

2. **Neural Network Training**
   ```
   Training Examples → Overseer → Adam Optimization → New Model
   ```

3. **Model Evaluation**
   ```
   New Model vs Best Model → Arena (50 games) → Win Rate ≥54% → Model Selection
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

## Model Analysis

### Training Metrics and Visualization

The system tracks three main graphs during training:

1. **V-Loss Graph**: Loss for the value head predictions
   - Tracks how well the network predicts game outcomes
   - Lower loss indicates better position evaluation

2. **P-Loss Graph**: Loss for the policy head predictions
   - Tracks how well the network predicts move probabilities
   - Lower loss indicates better move selection

3. **Win-Rate Graph**: Arena performance over iterations
   - Shows proportion of wins against previous best model
   - Blue line at 0.54 indicates acceptance threshold
   - Models above threshold become new best model

### Model Explainability

**Grad-CAM Integration**: The system supports Gradient-weighted Class Activation Mapping (Grad-CAM) for understanding neural network decisions:
- Highlights board positions important for move selection
- Visualizes which stones/patterns influence decisions
- Available through separate repository: https://github.com/ductoanng/AZ-Go-Grad-CAM

### Fine-Tuning

Model behavior can be adjusted through `configs/config.yaml`:
- Network architecture parameters
- Training hyperparameters
- MCTS exploration settings
- Distributed training configuration

## Next Steps

- [Training Process](training) - Detailed training pipeline
- [Usage Guide](usage) - Running the system
- [Model Archives](https://notion.so/ML@TCU/Model-Archives) - Historical model data and graphs