---
layout: default
title: Usage
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

# Single machine training
python start_main.py --num-workers 0
```

### Play Against the Model

```bash
# Interactive game
python engine/run_engine.py --mode play

# GTP interface (for Go GUIs)
python gtp/engine.py --model logs/checkpoints/best_model.pth.tar
```

### Analyze Games

```bash
# Analyze SGF file with KataGo
python katago/run_katago.py --sgf game.sgf

# Generate heatmaps
python gtp/heatmap_generator.py --position "B[dd];W[pp]"
```

## Command Line Options

### Training Options

```bash
python start_main.py [OPTIONS]

Options:
  --config PATH           Config file (default: configs/config.yaml)
  --resume                Resume from last checkpoint
  --iterations N          Number of training iterations
  --episodes N            Self-play games per iteration
  --workers N             Number of parallel workers
  --no-arena             Skip arena evaluation
  --save-all             Save all models (not just best)
```

### Play Options

```bash
python engine/run_engine.py [OPTIONS]

Options:
  --model PATH           Model checkpoint to load
  --mode MODE            'play' or 'analyze'
  --mcts-sims N          MCTS simulations per move
  --thinking-time S      Time limit per move (seconds)
  --komi N               Komi value (default: 5.5)
  --board-size N         Board size (default: 7)
```

## Configuration Files

### Main Configuration (`configs/config.yaml`)

```yaml
# Customize training parameters
board_size: 7
komi: 5.5

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

### Engine Configuration (`engine/engine_config.yaml`)

```yaml
# KataGo integration
katago_path: /path/to/katago
model_path: /path/to/katago/model.gz

# Analysis settings
analysis_threads: 4
max_visits: 10000
```

## Common Workflows

### 1. Training a New Model

```bash
# Step 1: Configure parameters
vim configs/config.yaml

# Step 2: Start overseer
python start_main.py --iterations 100

# Step 3: Start workers (on each machine)
python start_worker.py

# Step 4: Monitor progress
tail -f logs/training.log
```

### 2. Resuming Training

```bash
# Automatic resume from last checkpoint
python start_main.py --resume

# Resume from specific checkpoint
python start_main.py --load-model logs/checkpoints/checkpoint_200.pth.tar
```

### 3. Running Tournaments

```bash
# Compare two models
python training/arena.py \
  --model1 logs/checkpoints/checkpoint_100.pth.tar \
  --model2 logs/checkpoints/checkpoint_200.pth.tar \
  --num-games 100
```

### 4. Batch Analysis

```python
# analyze_games.py
from katago.katago_wrapper import KataGoWrapper
import glob

analyzer = KataGoWrapper()
sgf_files = glob.glob("games/*.sgf")

for sgf in sgf_files:
    result = analyzer.analyze_game(sgf)
    print(f"{sgf}: {result['summary']}")
```

## Integration with Go GUIs

### Sabaki

1. Install Sabaki
2. Add engine:
   - Path: `/path/to/python`
   - Arguments: `/path/to/gtp/engine.py`
3. Configure time settings

### Lizzie

```bash
# Create wrapper script
echo '#!/bin/bash
python /path/to/gtp/engine.py "$@"' > azgo-gtp.sh
chmod +x azgo-gtp.sh

# Add to Lizzie engines
```

## Debugging and Analysis

### Debug Scripts

```bash
# Test self-play
python debug/debug_self_play.py

# Test arena
python debug/debug_arena.py

# Test scoring
python debug/debug_scoring.py

# Test worker connection
python debug/debug_worker.py
```

### Log Files

```
logs/
├── training.log          # Main training progress
├── arena.log            # Game results
├── worker_*.log         # Individual worker logs
└── error.log           # Error messages
```

### Performance Profiling

```bash
# Profile MCTS performance
python -m cProfile -o profile.stats mcts.py

# Analyze results
python -m pstats profile.stats
```

## Advanced Usage

### Custom Neural Networks

```python
# custom_net.py
from neural_network.neural_net import NeuralNet

class CustomNet(NeuralNet):
    def __init__(self, game, args):
        # Your implementation
        pass
```

### Modified MCTS

```python
# custom_mcts.py
from mcts import MCTS

class CustomMCTS(MCTS):
    def search(self, state):
        # Your modifications
        pass
```

### Distributed Setup

```yaml
# distributed_config.yaml
workers:
  - host: worker1.example.com
    user: azgo
    key: ~/.ssh/id_rsa
    gpu: 0
  
  - host: worker2.example.com
    user: azgo
    key: ~/.ssh/id_rsa
    gpu: 1
```

## Tips and Best Practices

### Training Tips

1. **Start Small**: Begin with fewer iterations to test setup
2. **Monitor GPU**: Use `nvidia-smi` to check utilization
3. **Backup Models**: Regular backups of best models
4. **Log Analysis**: Check logs for convergence issues

### Playing Tips

1. **Time Management**: Adjust MCTS sims based on time
2. **Opening Book**: Can integrate with opening databases
3. **Endgame**: May need position-specific tuning

### System Requirements

- **GPU Memory**: 4GB minimum, 8GB+ recommended
- **CPU**: Multiple cores for parallel MCTS
- **Storage**: 50GB+ for logs and checkpoints
- **Network**: Fast connection for distributed training

## Troubleshooting

### Common Issues

**Model not improving**
- Check learning rate decay
- Verify arena threshold
- Examine training examples

**Worker disconnections**
- Check SSH keys
- Verify network stability
- Monitor worker resources

**Out of memory**
- Reduce batch size
- Lower MCTS simulations
- Use gradient accumulation

## Next Steps

- Join our community discussions
- Contribute improvements
- Share your trained models
- Report issues on GitHub