---
layout: default
title: Analysis Tools
parent: Analysis & Research
nav_order: 2
permalink: /analysis
---

# Analysis Tools

This section discusses methods to analyze trained models. The system automatically generates training graphs and stores model checkpoints for analysis.

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

### Neural Network Architecture

The neural network processes Go positions with:

**Input**: Board state encoded as multi-channel tensor
- Multiple planes representing current and historical positions
- Encodes stone positions, turn information, and game history

**Output**:
- **Policy (P)**: Probability distribution over all legal moves
  - Includes pass move option
  - Softmax normalized (sums to 1)
- **Value (V)**: Position evaluation score
  - Range: [-1, 1]
  - Represents expected game outcome from current position

## Theoretical Fine-Tuning

### Configuration Parameters

Key parameters in `config.yaml` for model tuning:

```yaml
# Network Architecture
num_channels: 128             # Width of convolutional layers
network_type: RES            # ResNet architecture

# Training Hyperparameters  
learning_rate: 0.0001        # Base learning rate
batch_size: 2048             # Training batch size
epochs: 10                   # Epochs per iteration

# MCTS Parameters
num_full_search_sims: 500    # MCTS simulations per move
c_puct: 1.0                  # UCT exploration constant
temperature_threshold: 4     # Moves before deterministic play
```

### Expected Outcomes

**Network Tuning**:
- `num_channels`: Increase for better pattern recognition
- `network_type`: RES (ResNet) or CNN options available
- Trade-off: Larger networks require more compute

**MCTS Tuning**:
- `num_full_search_sims`: More simulations = stronger play
- `c_puct`: Higher values encourage exploration
- `temperature_threshold`: Controls move randomness in early game

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

### Model Evaluation Methods

1. **Arena Win Rates**: Track improvement across iterations
2. **Self-Play Quality**: Review generated training games
3. **Manual Testing**: Play against model via GTP interface
4. **KataGo Comparison**: Use KataGo integration for analysis

## Practical Analysis Workflow

### Accessing Training Metrics

1. **View Training Graphs**: Check `logs/graphs/` for PNG files
   - Graphs are saved with timestamps
   - Updated after each training iteration

2. **Load Model Checkpoints**: Use saved models in `logs/checkpoints/`
   - `best.pth.tar`: Current best model
   - `checkpoint_X.pth.tar`: Specific iterations

3. **Review Game Records**: Analyze SGF files in `logs/arena_game_history/`
   - Contains games from arena evaluation
   - Can be opened with any SGF viewer

### Using the GTP Interface

Test models interactively:
```bash
# Launch GTP engine with trained model
python gtp/engine.py
```

This allows:
- Playing against the model
- Analyzing specific positions
- Testing model responses

## Next Steps

- [Training Guide](training) - Optimize training parameters
- [Usage Guide](usage) - Use analysis tools effectively