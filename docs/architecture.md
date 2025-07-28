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


### 5. Game Engine (`go/go_game.py`)

Go game implementation:
- Legal move generation
- Capture detection
- Ko rule enforcement
- Territory scoring
- SGF export

## Training Pipeline Overview

The system implements an iterative self-improvement loop:

1. **Self-Play Generation** → Collect training data
2. **Neural Network Training** → Improve model
3. **Arena Evaluation** → Validate improvements
4. **Model Update** → Deploy better models

For detailed training process information, see [Training Process](training).

## Custom Communication Protocol

Workers communicate with overseer across nodes via:
- **Model Distribution**: Pickled PyTorch models
- **Game Collection**: Serialized training examples
- **Status Updates**: JSON progress reports

## Key Design Decisions

### 1. Distributed Architecture
- **Scalability**: Add workers dynamically
- **Fault Tolerance**: Workers can disconnect/reconnect

### 2. Memory Management
- **Example Buffer**: Fixed-size training history
- **Tree Reuse**: MCTS tree persistence between moves
- **Batch Processing**: Efficient GPU utilization

### 3. Model Versioning
- **Checkpointing**: Regular model saves
- **Best Model Tracking**: Automatic selection
- **Rollback Support**: Previous model recovery


## Next Steps

- [Training Process](training) - Detailed training pipeline
- [Usage Guide](usage) - Running the system
- [Model Analysis](model-analysis) - Analyze and understand models
- [Codebase Structure](codebase-structure) - Navigate the source code