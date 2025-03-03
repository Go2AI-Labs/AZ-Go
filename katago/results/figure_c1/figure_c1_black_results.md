# KataGo Analysis Results

## Overview

This document presents the results of 10 KataGo analysis runs for the Figure C1 board position. Each run evaluates potential moves and provides detailed statistics for each candidate move.

The board is from the perspective of Black, and Black plays first (winrate is from black's perspective). The negative score and utility values indicate that White has an advantage in this position.

## Best Moves Summary

Across the 10 runs, three moves emerged as the strongest candidates:

| Run | Best Move | Second Best | Third Best |
|-----|-----------|-------------|------------|
| 1   | E7        | F1          | F9         |
| 2   | E7        | F1          | F9         |
| 3   | F1        | E7          | F9         |
| 4   | E7        | F1          | F9         |
| 5   | E7        | F1          | F9         |
| 6   | E7        | F9          | F1         |
| 7   | E7        | F1          | F9         |
| 8   | E7        | F9          | F1         |
| 9   | F9        | F1          | E7         |
| 10  | E7        | F1          | F9         |

**Frequency as top move:**
- E7: 8 times
- F1: 1 time
- F9: 1 time

## Move Analysis

### E7 Analysis
- Appeared as a top 3 move in all 10 runs
- Was the best move in 8 out of 10 runs
- Average scoreLead: around -4.75
- Average utility: around -1.053
- Average winrate: around 0.0006 (0.06%)
- Common follow-up sequences: F1→F9, F9→F1

### F1 Analysis
- Appeared as a top 3 move in all 10 runs
- Was the best move in 1 out of 10 runs
- Average scoreLead: around -4.78
- Average utility: around -1.055
- Average winrate: around 0.00054 (0.054%)
- Common follow-up sequences: F9→E7, E7→F9

### F9 Analysis
- Appeared as a top 3 move in all 10 runs
- Was the best move in 1 out of 10 runs
- Average scoreLead: around -4.82
- Average utility: around -1.053
- Average winrate: around 0.00056 (0.056%)
- Common follow-up sequences: F1→E7, E7→F1

## Additional Strong Candidates

Beyond the top three moves, these moves consistently appeared in the analysis:

### F6
- Average scoreLead: around -4.92
- Average utility: around -1.055
- Average winrate: around 0.00048 (0.048%)

### D5
- Average scoreLead: around -4.88
- Average utility: around -1.056
- Average winrate: around 0.00053 (0.053%)

### E4
- Average scoreLead: around -5.08
- Average utility: around -1.061
- Average winrate: around 0.00047 (0.047%)

## Common Sequences

Looking at the principal variation (PV) across runs, these are the most common move sequences:

1. **E7 → F1 → F9** followed by D5/F6
2. **E7 → F9 → F1** followed by D5/F6
3. **F1 → F9 → E7** followed by D5/F6
4. **F1 → E7 → F9** followed by D5/F6
5. **F9 → F1 → E7** followed by D5/E1

This suggests that regardless of which of the top three moves is played first, the other two top moves are typically the next best responses, followed by moves like D5 or F6.

## Statistical Analysis

### Average Values for Top Moves

| Move | Avg Prior | Avg Visits | Avg ScoreLead | Avg Utility | Avg Winrate |
|------|-----------|------------|---------------|-------------|-------------|
| E7   | 0.247     | 84.5       | -4.75         | -1.053      | 0.00060     |
| F1   | 0.285     | 87.4       | -4.78         | -1.055      | 0.00054     |
| F9   | 0.213     | 79.6       | -4.82         | -1.053      | 0.00056     |

### Board Position Statistics

Based on the rootInfo across all runs:
- Average scoreLead: around -4.82
- Average utility: around -1.055
- Average winrate: around 0.00055 (0.055%)

These metrics consistently indicate a clear advantage for White in this position (negative values represent Black's disadvantage).

## Recommendations

Based on the analysis of all runs, **E7** appears to be the strongest move, with **F1** and **F9** as close alternatives. The move E7 is preferred in most runs and has slightly better metrics compared to the alternatives.

The key factor in this position seems to be securing a strong position in the upper-central area of the board, as all top three moves (E7, F1, F9) focus on this region. After the first move, the most advantageous follow-up would be to play the other two moves from the top three, typically followed by moves like D5 or F6.