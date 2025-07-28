---
layout: default
title: Model Analysis
nav_order: 4
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

# Configure KataGo for AZ-Go
cd katago/
./configure_katago.sh
```

### Running Analysis

Analyze specific positions:
```bash
python katago/run_katago.py --sgf katago/sgf/figure_c1.sgf
```

Compare model moves with KataGo:
```python
from katago.katago_wrapper import KataGoWrapper

analyzer = KataGoWrapper()
results = analyzer.analyze_position(board_state)
print(f"Best move: {results['best_move']}")
print(f"Win rate: {results['win_rate']:.2%}")
```

## Performance Metrics

### Training Progress Visualization

Monitor key metrics during training:

```python
# View training graphs
python logger/graph_logger.py --metrics all

# Specific metrics
python logger/graph_logger.py --metrics loss,elo,win_rate
```

Available metrics:
- **Loss**: Policy and value loss over iterations
- **ELO Rating**: Model strength progression
- **Win Rate**: Performance against previous versions
- **MCTS Statistics**: Visit counts, Q-values

### Model Strength Evaluation

#### ELO Rating System

Track model improvements:
```python
from training.arena import Arena

arena = Arena(model1, model2)
results = arena.play_games(num_games=100)
elo_diff = arena.calculate_elo_difference(results)
```

#### Game Analysis

Analyze model playing patterns:
```bash
# Generate analysis report
python analysis/generate_report.py --model iteration_50

# Output includes:
# - Opening preferences
# - Common patterns
# - Weakness analysis
# - Style characteristics
```

## Visualization Tools

### Board Position Heatmaps

Visualize model predictions:
```python
from gtp.heatmap_generator import HeatmapGenerator

generator = HeatmapGenerator(model)
heatmap = generator.generate_policy_heatmap(position)
heatmap.save("analysis/policy_heatmap.png")
```

### Move Probability Distributions

```python
# Show top move candidates
probabilities = model.predict(position)
top_moves = get_top_k_moves(probabilities, k=5)

for move, prob in top_moves:
    print(f"{move}: {prob:.2%}")
```

### Value Network Analysis

Understand position evaluation:
```python
value = model.evaluate_position(position)
print(f"Win probability: {value:.2%}")

# Track value changes through game
values = analyze_game_values("game.sgf")
plot_value_graph(values)
```

## Debugging Tools

### MCTS Tree Visualization

Examine search behavior:
```python
from debug.debug_mcts import MCTSDebugger

debugger = MCTSDebugger()
tree_info = debugger.analyze_tree(mcts, position)
debugger.visualize_tree(tree_info, "mcts_tree.png")
```

### Neural Network Inspection

Analyze network internals:
```python
# Feature visualization
from neural_network.visualizer import NetworkVisualizer

viz = NetworkVisualizer(model)
features = viz.extract_conv_features(layer=5)
viz.plot_features(features)

# Activation patterns
activations = viz.get_activations(position)
viz.analyze_patterns(activations)
```

## Comparative Analysis

### Model vs Model

Compare different training iterations:
```bash
python analysis/compare_models.py \
    --model1 iteration_30 \
    --model2 iteration_50 \
    --games 1000
```

Output includes:
- Head-to-head win rate
- Move agreement percentage
- Time per move comparison
- Strategic differences

### Model vs Human

Analyze games against human players:
```python
from analysis.human_comparison import HumanAnalyzer

analyzer = HumanAnalyzer()
report = analyzer.analyze_game("human_vs_ai.sgf")
print(report.summary())
```

## Statistical Analysis

### Move Prediction Accuracy

Evaluate on professional games:
```bash
python analysis/test_accuracy.py \
    --model iteration_50 \
    --test_set pro_games/ \
    --top_k 1,3,5
```

### Positional Understanding

Test specific Go concepts:
```python
# Ladder reading
ladder_accuracy = test_ladder_reading(model)

# Life and death
tsumego_score = test_tsumego(model, "problems/")

# Territory evaluation
territory_mae = test_territory_counting(model)
```

## Performance Profiling

### Speed Analysis

```bash
# Profile MCTS performance
python -m cProfile -o profile.stats mcts_benchmark.py
python analysis/analyze_profile.py profile.stats
```

Key metrics:
- Simulations per second
- Neural network inference time
- Tree expansion rate
- Memory usage

### GPU Utilization

Monitor training efficiency:
```python
from logger.gpu_monitor import GPUMonitor

monitor = GPUMonitor()
stats = monitor.get_training_stats()
print(f"GPU Utilization: {stats['gpu_util']}%")
print(f"Memory Used: {stats['memory_used']}GB")
```

## Export and Integration

### Model Export

Export for different platforms:
```bash
# ONNX format
python export/to_onnx.py --model iteration_50

# TensorRT optimization
python export/to_tensorrt.py --model iteration_50

# Mobile deployment
python export/to_mobile.py --model iteration_50 --quantize
```

### Analysis Reports

Generate comprehensive reports:
```bash
# Full analysis report
python analysis/full_report.py \
    --model iteration_50 \
    --output report.pdf \
    --include all
```

Report sections:
1. Training history
2. Performance metrics
3. Game analysis
4. Strength evaluation
5. Recommendations

## Best Practices

1. **Regular Checkpoints**: Analyze models every 10 iterations
2. **Diverse Testing**: Use various opponent styles
3. **Statistical Significance**: Run sufficient test games (>1000)
4. **Version Control**: Track analysis results with model versions
5. **Automated Testing**: Set up CI/CD for model evaluation

## Common Analysis Patterns

### Identifying Weaknesses

```python
# Find model blind spots
weaknesses = analyze_failure_patterns(model, test_games)
for pattern in weaknesses:
    print(f"Weakness: {pattern.description}")
    print(f"Frequency: {pattern.frequency}")
    print(f"Suggested training: {pattern.remedy}")
```

### Style Classification

```python
# Determine playing style
style = classify_playing_style(model)
print(f"Style: {style.type}")  # Aggressive, Territorial, Balanced
print(f"Characteristics: {style.traits}")
```