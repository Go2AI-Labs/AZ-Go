---
layout: default
title: Model Analysis
permalink: /analysis
---

# Model Analysis

This section discusses methods to analyze trained models. All configuration information and graphs for every model are stored for reference.

## Loss Graphs and Win-Rate Visualization

### Understanding the Training Metrics

Three main graphs are recorded for every model:

#### 1. V-Loss Graph (Value Loss)
- Tracks the loss for value prediction (win probability)
- Lower values indicate better position evaluation
- Should decrease over iterations as model improves

#### 2. P-Loss Graph (Policy Loss)  
- Tracks the loss for move prediction
- Measures how well the model predicts expert moves
- Convergence indicates consistent move selection

#### 3. Win-Rate Graph
- Shows proportion of wins against previous best model
- Blue line at 0.54 (54%) indicates acceptance threshold
- New model accepted only if win rate exceeds threshold

### Neural Network I/O Analysis

**Input Structure**:
- 18x7x7 tensor containing last 18 board states
- Each 7x7 layer represents one historical position

**Output Components**:
- **P Vector**: 50x1 probability distribution
  - 49 board intersections + 1 pass move
  - Values between 0 and 1 (sum to 1)
- **V Value**: Single scalar in [-1, 1]
  - Indicates position evaluation
  - -1 = likely loss, +1 = likely win

## Theoretical Fine-Tuning

### Configuration Parameters

Key parameters in `config.yaml` for model tuning:

```yaml
# Network Architecture
num_channels: 128      # Width of residual blocks
num_blocks: 9          # Depth of network

# Training Hyperparameters  
learning_rate: 0.0001  # Initial learning rate
batch_size: 2048       # Samples per batch
epochs: 10             # Training epochs per iteration

# MCTS Parameters
num_mcts_sims: 500     # Simulations per move
cpuct: 1.0            # Exploration constant
```

### Expected Outcomes

**Increasing Network Capacity**:
- More channels → Better pattern recognition
- More blocks → Deeper strategic understanding
- Trade-off: Slower inference time

**Adjusting MCTS**:
- Higher simulations → Stronger play
- Higher C_PUCT → More exploration
- Trade-off: Longer move generation

## Model Explainability with Grad-CAM

### Understanding Neural Network Decisions

Grad-CAM (Gradient-weighted Class Activation Mapping) visualizes which board regions influence the neural network's decisions.

#### How Grad-CAM Works

1. **Forward Pass**: Input board state through network
2. **Backward Pass**: Calculate gradients for target move
3. **Heat Map**: Highlight important board regions
4. **Interpretation**: See what the model "focuses on"

#### Application to Go

For a given board position:
- **Bright regions**: Critical for move decision
- **Dark regions**: Less influential areas
- **Pattern recognition**: Identifies learned Go concepts

### Using Grad-CAM Analysis

Access the Grad-CAM implementation:
- Repository: [https://github.com/ductoanng/AZ-Go-Grad-CAM](https://github.com/ductoanng/AZ-Go-Grad-CAM)
- Jupyter Notebook: `AZ-Go-Grad-CAM.ipynb`

Steps for analysis:
1. Load trained model checkpoint
2. Select interesting game positions
3. Run Grad-CAM visualization
4. Interpret attention patterns

### Example Insights

Common patterns revealed by Grad-CAM:
- **Corner focus**: Early game emphasis on corners
- **Group safety**: Attention to endangered stones
- **Territory boundaries**: Recognition of territorial lines
- **Ko situations**: Heightened attention during ko fights

## Performance Metrics

### Training Progress Indicators

Monitor these metrics across iterations:

1. **Loss Convergence**
   - Both losses should decrease
   - Plateaus indicate learning limits

2. **Win Rate Trends**
   - Gradual improvement expected
   - Sudden drops may indicate overfitting

3. **Game Length Distribution**
   - Shorter games → More decisive play
   - Very short games → Possible issues

### Model Strength Estimation

Approximate ELO can be calculated:
- Compare against known engines
- Track relative improvements
- Account for board size differences

## Advanced Analysis Tools

### Position-Specific Analysis

```python
# Analyze specific board positions
analyzer.analyze_position(board_state)
# Returns: Move rankings, win probabilities
```

### Comparative Analysis

```python
# Compare models on test positions
compare_models(model1, model2, test_set)
# Returns: Agreement rate, strength difference
```

### Strategic Pattern Detection

Identify learned patterns:
- Common opening sequences
- Tactical motifs
- Endgame techniques

## Next Steps

- [Training Guide](training) - Optimize training parameters
- [Usage Guide](usage) - Use analysis tools effectively