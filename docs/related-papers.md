---
layout: default
title: Related Papers & Resources
nav_order: 5
permalink: /related-papers
---

# Related Papers & Resources

This section provides a curated list of research papers, articles, and resources that form the theoretical foundation of AZ-Go and provide context for understanding AlphaZero-style reinforcement learning.

## Foundational Papers

### AlphaGo Zero (2017)
**"Mastering the game of Go without human knowledge"**  
*David Silver, Julian Schrittwieser, Karen Simonyan, et al.*  
[Nature 550, 354–359 (2017)](https://www.nature.com/articles/nature24270)

Key contributions:
- Tabula rasa reinforcement learning
- Dual-headed neural network (policy + value)
- Self-play training without human games
- Simplified MCTS without rollouts

### AlphaZero (2018)
**"A general reinforcement learning algorithm that masters chess, shogi and Go through self-play"**  
*David Silver, Thomas Hubert, Julian Schrittwieser, et al.*  
[Science 362, 1140-1144 (2018)](https://www.science.org/doi/10.1126/science.aar6404)

Key contributions:
- Generalization to multiple games
- Unified algorithm architecture
- No domain-specific augmentations
- Superhuman performance in hours

### MuZero (2020)
**"Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model"**  
*Julian Schrittwieser, Ioannis Antonoglou, Thomas Hubert, et al.*  
[Nature 588, 604–609 (2020)](https://www.nature.com/articles/s41586-020-03051-4)

Key contributions:
- Model-based reinforcement learning
- Learning without knowing game rules
- Planning in learned latent space

## Technical Deep Dives

### Neural Network Architecture

**"Residual Networks Behave Like Ensembles of Relatively Shallow Networks"**  
*Andreas Veit, Michael Wilber, Serge Belongie*  
[NeurIPS 2016](https://arxiv.org/abs/1605.06431)

Understanding ResNet architectures used in AlphaZero.

**"Batch Normalization: Accelerating Deep Network Training"**  
*Sergey Ioffe, Christian Szegedy*  
[ICML 2015](https://arxiv.org/abs/1502.03167)

Critical for stable training of deep networks.

### Monte Carlo Tree Search

**"A Survey of Monte Carlo Tree Search Methods"**  
*Cameron Browne, Edward Powley, Daniel Whitehouse, et al.*  
[IEEE TCIAIG 2012](https://ieeexplore.ieee.org/document/6203567)

Comprehensive overview of MCTS variants and applications.

**"Bandit based Monte-Carlo Planning"**  
*Levente Kocsis, Csaba Szepesvári*  
[ECML 2006](https://link.springer.com/chapter/10.1007/11871842_29)

Original UCT algorithm that MCTS is based on.

## Implementation Details

### Distributed Training

**"Distributed Deep Reinforcement Learning: Learn how to play Go"**  
*Yuandong Tian, Jerry Ma, Qucheng Gong, et al.*  
[ICLR 2018](https://arxiv.org/abs/1803.01242)

Facebook's ELF OpenGo implementation insights.

### Optimization Techniques

**"Fixing Weight Decay Regularization in Adam"**  
*Ilya Loshchilov, Frank Hutter*  
[ICLR 2019](https://arxiv.org/abs/1711.05101)

AdamW optimizer used in modern implementations.

## Go-Specific Research

### Computer Go History

**"Deep Blue and Beyond: Chess and Go"**  
*Murray Campbell*  
[AI Magazine 2002](https://ojs.aaai.org/aimagazine/index.php/aimagazine/article/view/1642)

Historical context of computer game playing.

### Position Evaluation

**"Teaching Deep Convolutional Neural Networks to Play Go"**  
*Christopher Clark, Amos Storkey*  
[ICLR 2015](https://arxiv.org/abs/1412.3409)

Early work on using CNNs for Go position evaluation.

## Related Implementations

### Open Source Projects

1. **Leela Zero**  
   Community implementation of AlphaGo Zero  
   [GitHub](https://github.com/leela-zero/leela-zero)

2. **KataGo**  
   Improvements over AlphaZero with additional features  
   [GitHub](https://github.com/lightvector/KataGo)  
   [Paper](https://arxiv.org/abs/1902.10565)

3. **MiniGo**  
   Simplified Python implementation  
   [GitHub](https://github.com/tensorflow/minigo)

## Theoretical Background

### Reinforcement Learning

**"Reinforcement Learning: An Introduction"**  
*Richard Sutton, Andrew Barto*  
[Book (2018)](http://incompleteideas.net/book/the-book.html)

Foundational RL concepts and algorithms.

### Game Theory

**"Combinatorial Game Theory"**  
*Aaron N. Siegel*  
[AMS (2013)](https://bookstore.ams.org/gsm-146)

Mathematical foundations of perfect information games.

## Recent Advances

### Efficient Training

**"Accelerating Self-Play Learning in Go"**  
*David J. Wu*  
[arXiv 2019](https://arxiv.org/abs/1902.10565)

KataGo's improvements to training efficiency.

### Analysis Tools

**"Analyzing Deep Neural Networks for Game AI"**  
*Tom Schaul, et al.*  
[ICML 2022](https://proceedings.mlr.press/v162/schaul22a.html)

Methods for understanding learned representations.

## Practical Resources

### Tutorials and Guides

1. **"AlphaZero from Scratch"**  
   Step-by-step implementation guide  
   [Blog Series](https://web.stanford.edu/~surag/posts/alphazero.html)

2. **"Understanding AlphaGo"**  
   Visual explanations of key concepts  
   [Interactive Guide](https://www.alphagomovie.com/learn)

### Video Lectures

1. **David Silver's RL Course**  
   UCL Course on Reinforcement Learning  
   [YouTube Playlist](https://www.youtube.com/playlist?list=PLqYmG7hTraZBiG_XpjnPrSNw-1XQaM_gB)

2. **AlphaGo Documentary**  
   Behind the scenes of the historic match  
   [DeepMind Film](https://www.youtube.com/watch?v=WXuK6gekU1Y)

## Community and Discussion

### Forums and Communities

- [Computer Go Reddit](https://www.reddit.com/r/cbaduk/)
- [Leela Zero Discord](https://discord.gg/leelazero)
- [KataGo Discord](https://discord.gg/katago)
- [DeepMind Blog](https://deepmind.com/blog)

### Competitions

- **Computer Go Tournaments**
  - [CGOS](http://www.yss-aya.com/cgos/)
  - [KGS Bot Tournaments](https://www.gokgs.com/)

## Citation Format

When referencing AZ-Go in academic work:

```bibtex
@software{azgo2025,
  author = {Nguyen, Toan and Good, Blake and Leath, Harrison},
  title = {AZ-Go: Distributed AlphaZero Implementation for Go},
  year = {2025},
  url = {https://github.com/yourusername/AZ-Go}
}
```

## Contributing to Research

If you use AZ-Go for research:
1. Consider sharing your findings
2. Submit improvements via pull requests
3. Report interesting discoveries in Issues
4. Join our research discussion forum

## Further Reading

For those wanting to dive deeper:

1. **Mathematical Foundations**
   - Markov Decision Processes
   - Multi-armed Bandit Problems
   - Function Approximation in RL

2. **Advanced Topics**
   - Curriculum Learning
   - Transfer Learning in Games
   - Explainable AI for Game Playing

3. **Related Domains**
   - General Game Playing (GGP)
   - Real-time Strategy Games
   - Imperfect Information Games