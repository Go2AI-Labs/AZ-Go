---
layout: default
title: Training Process
parent: Training & Deployment
nav_order: 1
permalink: /training
---

# Training Process

The AZ-Go training pipeline implements the AlphaZero algorithm with distributed self-play and iterative improvement.

## Training Loop Overview

```
┌─────────────────────────────────────────────────┐
│                 Iteration Start                  │
│                                                 │
│  1. Self-Play ─────▶ 2. Train NN ─────▶ 3. Evaluate │
│       ▲                                     │    │
│       │                                     │    │
│       └─────────── 4. Update Model ◀────────┘    │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Phase 1: Self-Play Generation

### Overview

The most time-consuming phase of training. The model starts with zero knowledge other than Go rules. Beginning with randomly initialized weights, we generate training samples through self-play games using a reinforcement learning approach.

### Training Data Structure

Each training example consists of:
1. **Board State**: 18x7x7 stack representing current position
   - Layers 1-16: Past 16 board states from each player's perspective
   - Layer 17: Current player indicator (all 1s for black, all -1s for white)
   - Layer 18: Sensibility layer - encodes territory control
2. **Policy Target**: Length-49 vector with 1 at most-visited MCTS move
3. **Value Target**: Game result (-1 for loss, 1 for win)

### Data Collection

- **50,000 samples** per iteration
- Include **last 4 iterations** in training set
  - Iteration 1: 50,000 samples
  - Iteration 2: 100,000 samples  
  - Iteration 3: 150,000 samples
  - Iteration 4+: 200,000 samples (rolling window)

### Randomness for Exploration

**Temperature-based Selection**:
- First n moves: Select randomly (configurable temperature parameter)
- Remaining moves: More deterministic selection
- Reduces overfitting and ensures game variety

**Dirichlet Noise**:
- Applied to probability distribution at each tree node during MCTS
- Ensures variety in training games
- Prevents learning repetitive patterns

### MCTS Configuration

- **Simulations**: 500 per move
- **C_PUCT**: 1.0 (exploration constant)
- **Temperature**: Configurable for move randomness
- **Dirichlet α**: 0.25 at root node

## Phase 2: Neural Network Training

### Training Configuration

```yaml
optimizer: Adam
batch_size: 2048
learning_rate: 0.0001
epochs: 10
```

### Loss Function

Combined loss with equal weighting:
```
Loss = MSE(value_pred, value_target) + CrossEntropy(policy_pred, policy_target)
```

### Training Process

1. Load collected self-play samples
2. Shuffle and batch data
3. Train for 10 epochs using Adam optimizer
4. Monitor both policy and value losses
5. Save checkpoint after training

## Phase 3: Model Evaluation (Arena)

### Competition Setup

Previous best model vs newly trained model:
- **Total Games**: 50 matches
- **Acceptance Threshold**: 54% win rate (27/50 games)
- **Fair Comparison**: Same MCTS parameters for both models
- **Failure Case**: If threshold not met, new model discarded, previous best retained

### Arena Randomness

To add variation without modifying model output:
- Board states rotated by 90° random number of times before NN input
- Output transformed back to match original orientation
- All Go board rotations are equivalent
- Ensures diverse game positions during evaluation


### Evaluation Metrics

Tracked for each iteration:
- Win rate vs previous best
- Game length distribution
- Model acceptance decision

## Phase 4: Model Update

### Promotion Criteria

New model promoted if:
1. Win rate ≥ 55% in arena
2. OR iteration number is multiple of 10 (checkpoint)
3. OR this is the first iteration

### Model Management

```
logs/
├── checkpoints/
│   ├── best_model.pth.tar
│   ├── checkpoint_100.pth.tar
│   ├── checkpoint_200.pth.tar
│   └── current_model.pth.tar
└── train_examples/
    ├── iter_100/
    ├── iter_200/
    └── current/
```

## Training Configuration

### Standard Settings

```yaml
# 7x7 Go configuration
num_iterations: 500
num_episodes: 5000        # per iteration
num_mcts_sims: 500       # per move
num_epochs: 10           # NN training
batch_size: 512
num_games_arena: 40      # evaluation games
win_threshold: 0.55      # promotion threshold
```

### Memory Management

- **Example History**: 200,000 positions
- **Sampling**: Uniform from recent 10 iterations
- **Deduplication**: Remove duplicate positions

## Monitoring Progress

### Real-time Metrics

During training, monitor:
```
Iteration 42/500
Self-Play: 100%|████████| 5000/5000 [02:34:56]
Training Loss: 0.423
Arena: New Model Wins 24/40 (60.0%)
Model Updated: Yes
ELO Estimate: 1823 (+45)
```

### Visualization

Graphs generated in `logs/graphs/`:
- Loss curves (policy and value)
- Win rates over iterations
- Game length distributions
- Move prediction accuracy

## Distributed Training

### Worker Configuration

```yaml
num_parallel_workers: 4
worker_timeout: 3600  # seconds
episodes_per_worker: 1250  # 5000 total / 4 workers
```

### Load Balancing

- Dynamic work assignment
- Automatic failure recovery
- Progress synchronization

## Advanced Training

### Curriculum Learning

Start with simpler positions:
1. **Iterations 1-50**: Random opening positions
2. **Iterations 50-200**: Balanced middlegame
3. **Iterations 200+**: Full games

### Hyperparameter Tuning

Key parameters to experiment with:
- **C_PUCT**: Higher = more exploration
- **Temperature**: Lower = more deterministic
- **Learning Rate**: Affects convergence speed
- **MCTS Sims**: More = stronger but slower

### Training from Scratch vs Fine-tuning

```bash
# From scratch (default)
python start_main.py

# Fine-tune existing model
python start_main.py --load-model logs/checkpoints/best_model.pth.tar
```

## Troubleshooting

### Slow Convergence
- Increase MCTS simulations
- Lower learning rate
- More training epochs

### Overfitting
- Increase L2 regularization
- Add dropout layers
- Larger example buffer

### Worker Failures
- Check SSH connectivity
- Verify CUDA availability
- Monitor memory usage

## Next Steps

- [Usage Guide](usage) - Running trained models
- [Architecture](architecture) - System design details