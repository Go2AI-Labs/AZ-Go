---
layout: default
title: References
permalink: /references
---

# References and Related Work

## Core Papers

### AlphaGo and AlphaZero

**Silver, David, et al.** "Mastering the game of go without human knowledge." *Nature* 550.7676 (2017): 354-359.  
[https://www.nature.com/articles/nature24270](https://www.nature.com/articles/nature24270)
- Original AlphaGo Zero paper
- Introduces learning from self-play without human data
- Foundation for our implementation

### Implementation Guides

**Nair, Surag.** "A Simple Alpha(Go) Zero Tutorial." *Simple alpha zero*.  
[https://suragnair.github.io/posts/alphazero.html](https://suragnair.github.io/posts/alphazero.html)
- Excellent tutorial for understanding AlphaZero
- Clear explanations of MCTS and training loop
- Practical implementation advice

### Training Optimizations

**Wu, David J.** "Accelerating self-play learning in go." *arXiv preprint* arXiv:1902.10565 (2019).  
[https://arxiv.org/abs/1902.10565](https://arxiv.org/abs/1902.10565)
- Techniques for faster self-play
- Distributed training strategies
- Performance optimization methods

### Strategic Analysis

**Dou, Ze-Li, et al.** "Paradox of alphazero: Strategic vs. optimal plays." *2020 IEEE 39th International Performance Computing and Communications Conference (IPCCC)*. IEEE, 2020.  
[https://ieeexplore.ieee.org/document/9391562](https://ieeexplore.ieee.org/document/9391562)
- Analysis of AlphaZero's playing style
- Discussion of strategic choices vs optimal play
- Insights into model behavior

### Explainability Methods

**Selvaraju, Ramprasaath R., et al.** "Grad-cam: Visual explanations from deep networks via gradient-based localization." *Proceedings of the IEEE International Conference on Computer Vision*. 2017.  
[https://openaccess.thecvf.com/content_ICCV_2017/papers/Selvaraju_Grad-CAM_Visual_Explanations_ICCV_2017_paper.pdf](https://openaccess.thecvf.com/content_ICCV_2017/papers/Selvaraju_Grad-CAM_Visual_Explanations_ICCV_2017_paper.pdf)
- Grad-CAM methodology
- Application to understanding neural networks
- Visualization techniques

## Additional Resources

### Go Programming

- **Sensei's Library**: Comprehensive Go knowledge base
- **KataGo Papers**: Modern Go AI research
- **Computer Go Archive**: Historical development

### Machine Learning

- **PyTorch Documentation**: Framework reference
- **Deep Learning Book** (Goodfellow et al.): Theoretical foundations
- **Reinforcement Learning: An Introduction** (Sutton & Barto): RL fundamentals

### Related Projects

- **Leela Zero**: Open-source Go AI
- **KataGo**: Strong modern Go engine
- **MiniGo**: Simplified AlphaGo Zero implementation
- **ELF OpenGo**: Facebook's Go AI research

## Acknowledgments

This project builds upon the groundbreaking work of the DeepMind team and the broader computer Go community. Special thanks to:

- The AlphaGo team for revolutionizing computer Go
- Open-source contributors who made implementations accessible
- The Go community for centuries of strategic knowledge

## Contributing

If you have relevant papers or resources to add:
1. Fork the repository
2. Add references in appropriate sections
3. Submit a pull request

## Citation

If you use this project in your research, please cite:

```bibtex
@software{azgo2025,
  author = {Nguyen, Toan and Good, Blake and Leath, Harrison},
  title = {AZ-Go: Distributed AlphaZero Implementation for Go},
  year = {2025},
  url = {https://github.com/yourusername/AZ-Go}
}
```