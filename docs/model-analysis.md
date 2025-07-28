---
layout: default
title: Model Analysis
parent: Analysis & Research
nav_order: 1
permalink: /model-analysis
---

# Model Analysis

This section covers tools and techniques for analyzing your trained AZ-Go models, understanding their behavior, and evaluating performance.

## KataGo Integration

AZ-Go integrates with KataGo for professional-level game analysis and model evaluation.

### Setting Up KataGo

```bash
# Install KataGo
brew install katago  # macOS
# or
sudo apt install katago  # Ubuntu
```

Note: KataGo must be configured manually with appropriate paths and parameters.

### Running Analysis

Analyze specific positions:
```bash
python katago/run_katago.py --sgf katago/sgf/figure_c1.sgf
```

Compare model moves with KataGo:
```python
from katago.katago_wrapper import KataGoWrapper

# Initialize with KataGo command
analyzer = KataGoWrapper("katago analysis -config your_config.cfg")
# Query positions with move history
response = analyzer.query(moves=["C4", "D4", "E5"])
print(f"Analysis: {response}")
```

## Performance Metrics

### Training Progress Visualization

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

The training system automatically generates graphs during training. After each iteration, three graphs are saved to `logs/graphs/`:

- **V-Loss Graph**: Value head loss over iterations
- **P-Loss Graph**: Policy head loss over iterations  
- **Win Rate Graph**: Arena performance against previous model

Graphs are automatically updated and saved as PNG files with timestamps.

### Model Strength Evaluation

#### Arena System

The training process includes an automatic arena evaluation:
```python
from training.arena import Arena

# Arena is used internally during training
# It plays games between current and previous models
# Models are accepted if win rate > acceptance_threshold (default: 0.54)
```

#### Game Analysis

Game records from arena matches are saved as SGF files in `logs/arena_game_history/`. These can be analyzed with standard Go software or the debug tools:

```bash
# Debug arena games
python debug/debug_arena.py

# Debug self-play games
python debug/debug_self_play.py
```

## Visualization Tools

### Board Position Heatmaps

Visualize board positions and moves:
```python
from gtp.heatmap_generator import MapGenerator

# Create heatmap generator
generator = MapGenerator(square_size=97, line_width=5)

# Generate board visualization
board_image = generator.generate_game_board(board, last_move)
# Also supports MCTS count and policy probability visualizations
```

### Neural Network Predictions

The neural network provides both policy (move probabilities) and value (win probability) outputs:

```python
from neural_network.neural_net_wrapper import NeuralNetWrapper

# Get predictions from the model
wrapper = NeuralNetWrapper(game)
wrapper.load_checkpoint(folder="logs/checkpoints", filename="best.pth.tar")
pi, v = wrapper.predict(board)

# pi: move probability distribution
# v: expected game outcome (-1 to 1)
```

## Debugging Tools

The codebase includes several debugging utilities:

### Available Debug Scripts

```bash
# Debug arena matches between models
python debug/debug_arena.py

# Debug self-play game generation
python debug/debug_self_play.py

# Debug distributed worker behavior
python debug/debug_worker.py

# Debug game scoring
python debug/debug_scoring.py
```

These tools help diagnose issues during training and game generation.

## Model Comparison

During training, models are automatically compared through the arena system. Each iteration plays games between the new and previous model to determine if the new model should be accepted.

For manual comparison, you can:
1. Load different model checkpoints
2. Play games between them using the Arena class
3. Analyze the resulting SGF files

## Model Evaluation

While comprehensive analysis tools are not included, you can evaluate models by:

1. **Training Metrics**: Monitor loss graphs and win rates
2. **Arena Performance**: Check acceptance rates against previous models
3. **Manual Testing**: Use the GTP interface to play against the model
4. **KataGo Comparison**: Use the KataGo integration to compare move choices

## Performance Monitoring

While dedicated profiling tools are not included, you can monitor performance through:

1. **Training Logs**: Check iteration times and game generation rates
2. **System Monitoring**: Use standard tools like `nvidia-smi` for GPU usage
3. **Debug Output**: Enable `debug_mode: true` in config.yaml for detailed timing

## Model Storage and Access

Trained models are saved in `logs/checkpoints/`:
- `best.pth.tar`: Current best model
- `current_net.pth.tar`: Latest trained model
- `previous_net.pth.tar`: Previous iteration model
- `checkpoint_X.pth.tar`: Specific iteration checkpoints

Models can be loaded for analysis or deployment using the NeuralNetWrapper class.

## Best Practices

1. **Regular Checkpoints**: Analyze models every 10 iterations
2. **Diverse Testing**: Use various opponent styles
3. **Statistical Significance**: Run sufficient test games (>1000)
4. **Version Control**: Track analysis results with model versions
5. **Automated Testing**: Set up CI/CD for model evaluation

## Practical Analysis Workflow

1. **Monitor Training Progress**:
   - Check loss graphs in `logs/graphs/`
   - Review win rates for model improvement
   - Examine arena game records

2. **Test Model Strength**:
   - Use GTP interface to play test games
   - Compare with KataGo analysis
   - Review self-play game quality

3. **Debug Issues**:
   - Use debug scripts for specific problems
   - Check training logs for errors
   - Verify game generation rates

## Model Explainability

### Grad-CAM Integration

The system supports Gradient-weighted Class Activation Mapping (Grad-CAM) for understanding neural network decisions. Grad-CAM helps visualize which board positions are most important for the neural network's move selection.

**How it works**:
- Highlights board positions important for move selection
- Visualizes which stones/patterns influence decisions
- Shows "unique" features for recognizing good moves

**Implementation**:
- Available through separate repository: https://github.com/ductoanng/AZ-Go-Grad-CAM
- Follow the steps in `AZ-Go-Grad-CAM.ipynb` for detailed analysis

**Use cases**:
- Understanding why the model chooses specific moves
- Identifying which board patterns the model has learned
- Debugging unexpected model behavior
- Teaching tool for understanding Go strategy

## Model Fine-Tuning

Model behavior can be adjusted through `configs/config.yaml`:

### Network Architecture Parameters
- Layer dimensions
- Residual block count
- Activation functions

### Training Hyperparameters
- Learning rate schedules
- Batch size
- Regularization strength
- Loss function weights

### MCTS Exploration Settings
- C_PUCT value for exploration/exploitation balance
- Dirichlet noise parameters
- Temperature settings for move selection

### Distributed Training Configuration
- Worker count
- Game generation rate
- Model distribution frequency

All configuration changes affect model behavior and training dynamics. See the [Training Process](training) documentation for detailed parameter descriptions.