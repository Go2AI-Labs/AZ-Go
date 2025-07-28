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

## 📚 Project Resources

<div style="background-color: #f0f8ff; border: 2px solid #1e90ff; border-radius: 8px; padding: 20px; margin: 20px 0;">
  <h3 style="margin-top: 0; color: #1e90ff;">🔗 Notion Documentation & Model Archives</h3>
  <p style="margin-bottom: 10px;">Access our comprehensive Notion workspace containing:</p>
  <ul style="margin-bottom: 15px;">
    <li><strong>Model Archives</strong> - Download trained model checkpoints</li>
    <li><strong>Training Logs</strong> - Detailed experiment records</li>
    <li><strong>Performance Benchmarks</strong> - Model comparison data</li>
    <li><strong>Research Notes</strong> - Implementation insights and findings</li>
  </ul>
  <a href="https://harrisonleath.notion.site/ML-TCU-d58eaa8cde34425fae64342f42cc8f67" target="_blank" style="background-color: #1e90ff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Visit Notion Workspace →</a>
</div>

## Documentation Structure

### 📁 Getting Started
- [**Installation Guide**](installation) - Set up AZ-Go on your system
- [**Usage Guide**](usage) - Run training and play games

### 🏗️ Technical Documentation
- [**Codebase Structure**](codebase-structure) - Navigate the source code
- [**Architecture Overview**](architecture) - System design and components

### 🚀 Training & Deployment
- [**Training Process**](training) - Understanding the training pipeline
- [**Distributed Training**](distributed-training) - Scale across multiple machines

### 📊 Analysis & Research
- [**Model Analysis**](model-analysis) - Evaluate and understand your models
- [**Analysis Tools**](analysis) - Built-in analysis capabilities
- [**Related Papers**](related-papers) - Research foundation and references

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