---
layout: default
title: Home
permalink: /
---

# AZ-Go: AlphaZero for Go

A distributed AlphaZero implementation specifically designed for training Go models. This project implements the AlphaGo Zero algorithm with distributed training capabilities, neural network management, and comprehensive logging.

**Authors:** Toan Nguyen, Blake Good, Harrison Leath  
**Date:** May 5, 2025

<div style="text-align: center; margin: 30px 0;">
  <img src="https://img.shields.io/badge/Python-3.x-blue.svg" alt="Python 3.x">
  <img src="https://img.shields.io/badge/PyTorch-Latest-orange.svg" alt="PyTorch">
  <img src="https://img.shields.io/badge/Board-7x7-green.svg" alt="7x7 Board">
</div>

## Key Features

### 🎯 Go Game Implementation
- Complete Go game logic with proper rule handling
- Configurable board sizes (default 7x7)
- Full support for captures, ko rule, and scoring

### 🚀 Distributed Training
- Train across multiple worker nodes
- SSH connectivity for remote workers
- Automatic synchronization and model distribution

### 🧠 Neural Network Architecture
- ResNet-18 based architecture
- Configurable channels and layers
- Policy and value heads for move prediction

### 🌳 MCTS Integration
- Monte Carlo Tree Search with configurable parameters
- C_PUCT exploration control
- Efficient tree reuse between moves

### 📊 Comprehensive Analysis
- KataGo integration for move analysis
- Training progress visualization
- Game history tracking with SGF export

## Quick Navigation

- [**Installation Guide**](installation) - Get started with AZ-Go
- [**Architecture Overview**](architecture) - Understand the system design
- [**Training Process**](training) - Learn about the training pipeline
- [**Usage Guide**](usage) - Run training and analysis

## Recent Updates

- **Komi adjusted to 5.5** - Better game balance
- **Training temperature lowered** - More focused exploration
- **Simulations increased to 500** - Stronger play quality
- **New analysis tools** - Figure C2 analysis added

## Getting Started

```bash
# Clone the repository
git clone https://github.com/yourusername/AZ-Go.git
cd AZ-Go

# Install dependencies
pip install -r requirements.txt

# Start training
python start_main.py
```

## Performance

Current model achieves:
- **500 MCTS simulations** per move
- **ResNet-18** with 128 channels
- **Distributed training** across multiple GPUs
- **5000 self-play games** per iteration

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/yourusername/AZ-Go/blob/main/LICENSE) file for details.