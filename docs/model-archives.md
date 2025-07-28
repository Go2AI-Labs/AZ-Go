---
layout: default
title: Model Archives
nav_order: 4
parent: Analysis & Research
permalink: /model-archives
---

# Model Archives

## 📦 Accessing Trained Models

All trained model checkpoints and associated training data are hosted on our Notion workspace.

<div style="background-color: #f0f8ff; border: 2px solid #1e90ff; border-radius: 8px; padding: 20px; margin: 20px 0;">
  <h3 style="margin-top: 0; color: #1e90ff;">🔗 Notion Model Repository</h3>
  <p>Our Notion workspace contains:</p>
  <ul>
    <li><strong>Model Checkpoints</strong> - PyTorch .pth files for each iteration</li>
    <li><strong>Training Histories</strong> - Loss curves, ELO progression, win rates</li>
    <li><strong>Hyperparameter Configs</strong> - Exact settings used for each model</li>
    <li><strong>Evaluation Results</strong> - Performance benchmarks and analysis</li>
    <li><strong>SGF Game Records</strong> - Sample games from each model version</li>
  </ul>
  <a href="https://harrisonleath.notion.site/ML-TCU-d58eaa8cde34425fae64342f42cc8f67" target="_blank" style="background-color: #1e90ff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Access Model Archives →</a>
</div>

## Available Models

### Complete Model Archive

Below is a comprehensive list of all trained models, their training parameters, and performance characteristics:

| Model | Games Played | Date | Key Features | Notes |
|-------|--------------|------|--------------|-------|
| **Model K** | 23,500 | Aug 1, 2023 | First SGD model, 9x7x7 input | Moderately competent early game, weak mid/late game |
| **Model L** | 13,525 | Aug 8, 2023 | 18x7x7 input, 200 MCTS sims | First model with expanded input size |
| **Model M** | 49,525 | Sep 4, 2023 | Stable training, temp=15 | Modified random move selection after iteration 40 |
| **Model N** | 21,025 | Sep 17, 2023 | Same as M, temp=8 | Reduced temperature for more focused play |
| **Model O** | 15,525 | Sep 17, 2023 | Progressive move cap | Started with 25 moves, gradually increased |
| **Model P** | 17,830 | Oct 25, 2023 | Playout cap randomization | 6000 episodes/gen, batch size issue (64 instead of 2048) |
| **Model Q** | 146,586 | Nov 15, 2023 | Playout randomization enabled | Improved training stability |
| **Model R** | 79,256 | Feb 5, 2024 | Sensibility layer added | Queue-based game loading, unusual V loss |
| **Model S** | 360,984 | Feb 15, 2024 | Cosine annealing enabled | Neural network handicapped by unmasked pi vectors |
| **Model T** | 57,709 | Feb 21, 2024 | Same as Q + sensibility | Issues with losses and win rates discovered |
| **Model U** | 400,000 | Feb 28, 2024 | Rerun of Model T | Fixed runtime errors from Model T |
| **Model V** | 115,647 | Apr 3, 2024 | Corrected loss function | Major bug fix improving training |
| **Model W** | 750,000 | Dec 12, 2024 | MCTS fix proposed | Arena games duplicated (no MCTS randomization) |
| **Model X** | 965,000 | Feb 10, 2025 | Arena game fix | Corrected winrate graph |
| **Model Y** | 905,000 | Feb 14, 2025 | CPUCT 1.0→1.5 | Increased exploration parameter |
| **Model Z** | 1,340,000 | Feb 24, 2025 | 400 MCTS sims, no fast sims | Built on Model X base |
| **Model AA** | 995,000 | Mar 3, 2025 | 500 MCTS sims | Fresh start with increased simulations |
| **Model AB** | 475,000 | Mar 24, 2025 | temp=4, 500 sims | Reduced temperature for more deterministic play |
| **Model AC** | 500,000 | TBD | In development | Details pending |

### Latest Stable Release
- **Model AB** (March 2025)
- **Training**: 475,000 self-play games
- **Key Parameters**: 500 MCTS simulations, temperature=4
- **Performance**: Latest iteration with reduced randomness
- **Recommended for**: Production use, tournament play

### Key Training Evolution
1. **Early Models (K-O)**: Experimentation with input sizes, MCTS parameters
2. **Mid Development (P-U)**: Introduction of advanced features (playout randomization, sensibility layer)
3. **Bug Fix Phase (V-W)**: Correcting loss functions and arena evaluation
4. **Modern Era (X-AC)**: High-quality models with 400-500 MCTS simulations

## Detailed Model Specifications

### Recent High-Performance Models

#### Model AB (Latest Release)
- **Configuration**: 500 MCTS simulations, temperature=4
- **Network**: ResNet architecture, 128 channels
- **Training**: SGD optimizer, batch size 2048
- **Special Features**: Extremely low temperature for deterministic play
- **Use Case**: Best for tournament play and production deployments

#### Model AA
- **Configuration**: 500 MCTS simulations, standard temperature
- **Network**: Fresh training from scratch
- **Training**: No fast simulations, pure quality focus
- **Special Features**: Clean training run without legacy issues
- **Use Case**: High-quality baseline model

#### Model Z
- **Configuration**: 400 MCTS simulations, no fast sims
- **Base**: Built on Model X improvements
- **Training**: 1.34M games, extensive experience
- **Special Features**: Removed fast simulation shortcuts
- **Use Case**: Strong strategic play with depth

### Training Configuration Details

All recent models use these core parameters:
- **Board Size**: 7x7
- **Network Type**: ResNet (RES)
- **Input Channels**: 18 layers (board states + game features)
- **Hidden Channels**: 128
- **Learning Rate**: 0.0001 (SGD) or with cosine annealing
- **Batch Size**: 2048 (except Model P with 64)
- **Temperature Threshold**: Varies by model (4-15 moves)

## Using Downloaded Models

### Loading a Model

```python
from neural_network.neural_net_wrapper import NeuralNetWrapper
from utils.config_handler import ConfigHandler

# Load configuration
config = ConfigHandler().load_config()

# Initialize neural network
nn = NeuralNetWrapper(config)

# Load downloaded checkpoint
nn.load_checkpoint("path/to/downloaded/model.pth")

# Use for inference
board_state = ...  # Your game state
policy, value = nn.predict(board_state)
```

### Model Compatibility

Ensure compatibility between model and code versions:

```python
# Check model metadata
import torch

checkpoint = torch.load("model.pth")
print(f"Model version: {checkpoint['version']}")
print(f"Training iteration: {checkpoint['iteration']}")
print(f"Board size: {checkpoint['board_size']}")
```

### Converting Models

For different deployment scenarios:

```bash
# Convert to ONNX
python export/to_onnx.py --model downloaded_model.pth

# Optimize for mobile
python export/to_mobile.py --model downloaded_model.pth --quantize
```

## Model Versioning

Our models follow semantic versioning:
- **Major**: Significant architecture changes
- **Minor**: Training improvements, hyperparameter tuning
- **Patch**: Bug fixes, minor adjustments

Example: `azgo_v2.3.1_iter300.pth`
- Version 2.3.1
- Trained for 300 iterations

## Contributing Models

If you've trained interesting variants:
1. Document training configuration
2. Include evaluation results
3. Provide sample games
4. Submit via GitHub issue

## Troubleshooting

### Common Issues

**Model won't load:**
```python
# Check PyTorch version compatibility
import torch
print(torch.__version__)

# Try loading with map_location
model = torch.load("model.pth", map_location='cpu')
```

**Size mismatch:**
- Verify board size matches (7x7 default)
- Check number of channels in config
- Ensure architecture version matches

**Performance issues:**
- Use GPU if available
- Consider quantized models for CPU inference
- Batch multiple predictions

## Archive Structure & Resources

### Model Files Available

Each model in the archive includes:
- **Configuration File** (`config.yaml`): Complete training parameters
- **Training Graphs**: Loss curves and win rate progression
- **Model Checkpoint**: PyTorch `.pth` file (available on Notion)
- **Commit Hash**: Exact code version used for training

### Accessing Model Resources

The complete model archive with downloadable checkpoints, configuration files, and training graphs is available on our Notion workspace:

<div style="background-color: #e6f3ff; border-left: 4px solid #1e90ff; padding: 15px; margin: 20px 0;">
  <strong>📁 Model Archive Contents:</strong>
  <ul style="margin-top: 10px;">
    <li>Full configuration files for all models</li>
    <li>Training result graphs showing loss and win rate progression</li>
    <li>Detailed notes on each model's characteristics</li>
    <li>Git commit hashes for reproducibility</li>
    <li>PyTorch checkpoint files (.pth)</li>
  </ul>
</div>

### File Organization

```
Model Archives/
├── Model K-O (Early Development)/
│   ├── config.yaml
│   ├── training_graph.png
│   └── notes.txt
├── Model P-U (Feature Introduction)/
│   ├── config.yaml
│   ├── training_graph.png
│   └── notes.txt
├── Model V-W (Bug Fixes)/
│   ├── config.yaml
│   ├── training_graph.png
│   └── notes.txt
└── Model X-AC (Modern Era)/
    ├── config.yaml
    ├── training_graph.png
    └── notes.txt
```

Each model directory contains:
- Complete training configuration
- Visual training progress (loss/win rate graphs)
- Detailed implementation notes
- Performance benchmarks