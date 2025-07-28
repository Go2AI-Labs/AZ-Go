---
layout: default
title: Model Archives
nav_order: 6
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

### Latest Stable Release
- **Model**: `azgo_v1.0_iter500.pth`
- **Training**: 500 iterations, 2.5M self-play games
- **Performance**: ~2000 ELO
- **Notes**: Best overall performance, recommended for most use cases

### Experimental Models
- **Strong Style Models**: Aggressive tactical play
- **Positional Models**: Territory-focused strategy
- **Speed-Optimized**: Reduced channels for faster inference

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

## Archive Structure

In the Notion workspace, models are organized as:
```
Model Archives/
├── Stable Releases/
│   ├── v1.0/
│   ├── v0.9/
│   └── ...
├── Experimental/
│   ├── High-Temperature/
│   ├── Large-Network/
│   └── ...
└── Historical/
    ├── Early Iterations/
    └── Benchmarks/
```

Each model entry includes:
- Download link
- Training configuration
- Performance metrics
- Known limitations
- Recommended use cases