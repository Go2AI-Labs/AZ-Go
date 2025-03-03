# KataGo Analysis Results

## Overview

This document presents the results of 10 KataGo analysis runs for an empty board position. Each run evaluates potential moves and provides detailed statistics for each candidate move.

The board is from the perspective of Black, and White plays first (winrate is from black's perspective). The negative score and utility values indicate that White has an advantage in this position.

## Best Moves Summary

Across the 10 runs, three moves emerged as the strongest candidates:

| Run | Best Move | Second Best | Third Best |
|-----|-----------|-------------|------------|
| 1   | F1        | F9          | E7         |
| 2   | F9        | E7          | F1         |
| 3   | F9        | E7          | F1         |
| 4   | F9        | F1          | E7         |
| 5   | F1        | E7          | F9         |
| 6   | F1        | F9          | E7         |
| 7   | F1        | F9          | E7         |
| 8   | F9        | F1          | E7         |
| 9   | F9        | F1          | E7         |
| 10  | F1        | F9          | E7         |

**Frequency as top move:**
- F1: 5 times
- F9: 5 times
- E7: 0 times

## Move Analysis

### F1 Analysis
- Appeared as a top 3 move in all 10 runs
- Was the best move in 5 out of 10 runs
- Average scoreLead: around -6.52
- Average utility: around -1.062
- Average winrate: around 0.00034 (0.034%)
- Common follow-up sequences: E7→F9, F9→E7

### F9 Analysis
- Appeared as a top 3 move in all 10 runs
- Was the best move in 5 out of 10 runs
- Average scoreLead: around -6.50
- Average utility: around -1.062
- Average winrate: around 0.00033 (0.033%)
- Common follow-up sequences: E7→F1, F1→E7

### E7 Analysis
- Appeared as a top 3 move in all 10 runs
- Never ranked as the best move
- Average scoreLead: around -6.50
- Average utility: around -1.061
- Average winrate: around 0.00032 (0.032%)
- Common follow-up sequences: F1→F9, F9→F1

## Additional Strong Candidates

Beyond the top three moves, these moves consistently appeared in the analysis:

### D5
- Average scoreLead: around -6.42
- Average utility: around -1.061
- Average winrate: around 0.00038 (0.038%)

### F6
- Average scoreLead: around -6.30
- Average utility: around -1.057
- Average winrate: around 0.00036 (0.036%)

### E4
- Average scoreLead: around -6.01
- Average utility: around -1.049
- Average winrate: around 0.00040 (0.040%)

## Common Sequences

Looking at the principal variation (PV) across runs, these are the most common move sequences:

1. **F1 → E7 → F9** followed by E9→D5
2. **F1 → F9 → E7** followed by E1→D5/F6
3. **F9 → E7 → F1** followed by E9→F6
4. **F9 → F1 → E7** followed by E9→F6/D5
5. **E7 → F1 → F9** followed by E9→D5/F6
6. **E7 → F9 → F1** followed by E1/F6→D5/F6

This suggests that regardless of which of the top three moves is played first, the other two top moves are typically the next best responses, followed by moves like E9, D5, or F6.

## Statistical Analysis

### Average Values for Top Moves

| Move | Avg Prior | Avg Visits | Avg ScoreLead | Avg Utility | Avg Winrate |
|------|-----------|------------|---------------|-------------|-------------|
| F1   | ~0.30     | ~92        | -6.52         | -1.062      | 0.00034     |
| F9   | ~0.25     | ~90        | -6.50         | -1.062      | 0.00033     |
| E7   | ~0.28     | ~91        | -6.50         | -1.061      | 0.00032     |

### Board Position Statistics

Based on the rootInfo across all runs:
- Average scoreLead: around -6.49
- Average utility: around -1.061
- Average winrate: around 0.00034 (0.034%)

These metrics consistently indicate a clear advantage for White in this position (negative values represent Black's disadvantage), which is expected given that White plays first on an empty board.

## Run 1 Detailed Data

### Best move: F1
```json
{
  "edgeVisits": 93,
  "edgeWeight": 497.387578,
  "lcb": 0.00189966247,
  "move": "F1",
  "order": 0,
  "prior": 0.297016412,
  "pv": ["F1", "E7", "F9", "E9", "D5"],
  "scoreLead": -6.50007671,
  "scoreMean": -6.50007671,
  "scoreSelfplay": -6.73611462,
  "scoreStdev": 0.974447467,
  "utility": -1.06563744,
  "utilityLcb": -1.06122699,
  "visits": 93,
  "weight": 497.387578,
  "winrate": 0.00032450239
}
```

### Second best move: F9
```json
{
  "edgeVisits": 90,
  "edgeWeight": 480.860069,
  "lcb": 0.00199907904,
  "move": "F9",
  "order": 1,
  "prior": 0.292354226,
  "pv": ["F9", "E7", "F1", "E9", "D5"],
  "scoreLead": -6.47656572,
  "scoreMean": -6.47656572,
  "scoreSelfplay": -6.71750701,
  "scoreStdev": 0.98841952,
  "utility": -1.06493594,
  "utilityLcb": -1.06029853,
  "visits": 90,
  "weight": 480.860069,
  "winrate": 0.000342861096
}
```

### Third best move: E7
```json
{
  "edgeVisits": 87,
  "edgeWeight": 467.032415,
  "lcb": 0.0022504802,
  "move": "E7",
  "order": 2,
  "prior": 0.278253287,
  "pv": ["E7", "F1", "F9", "E9", "D5", "F6"],
  "scoreLead": -6.51034322,
  "scoreMean": -6.51034322,
  "scoreSelfplay": -6.65340235,
  "scoreStdev": 0.998081125,
  "utility": -1.06269839,
  "utilityLcb": -1.05730437,
  "visits": 87,
  "weight": 467.032415,
  "winrate": 0.000324042789
}
```

## Run 2 Detailed Data

### Best move: F9
```json
{
  "edgeVisits": 84,
  "edgeWeight": 446.204033,
  "lcb": 0.00190188585,
  "move": "F9",
  "order": 0,
  "prior": 0.231789708,
  "pv": ["F9", "E7", "F1", "E9", "F6"],
  "scoreLead": -6.45272193,
  "scoreMean": -6.45272193,
  "scoreSelfplay": -6.69601708,
  "scoreStdev": 0.971177282,
  "utility": -1.05868149,
  "utilityLcb": -1.05426949,
  "visits": 84,
  "weight": 446.204033,
  "winrate": 0.000326170026
}
```

### Second best move: E7
```json
{
  "edgeVisits": 97,
  "edgeWeight": 518.618489,
  "lcb": 0.00221627727,
  "move": "E7",
  "order": 1,
  "prior": 0.341070801,
  "pv": ["E7", "F1", "F9", "E9", "D5", "F6"],
  "scoreLead": -6.52181244,
  "scoreMean": -6.52181244,
  "scoreSelfplay": -6.66365499,
  "scoreStdev": 0.988982387,
  "utility": -1.05718397,
  "utilityLcb": -1.05184008,
  "visits": 96,
  "weight": 513.271906,
  "winrate": 0.000307745972
}
```

### Third best move: F1
```json
{
  "edgeVisits": 87,
  "edgeWeight": 464.649052,
  "lcb": 0.00194134062,
  "move": "F1",
  "order": 2,
  "prior": 0.297058433,
  "pv": ["F1", "E7", "F9", "E9", "F6"],
  "scoreLead": -6.51661356,
  "scoreMean": -6.51661356,
  "scoreSelfplay": -6.7018023,
  "scoreStdev": 0.976040159,
  "utility": -1.05819046,
  "utilityLcb": -1.05368666,
  "visits": 87,
  "weight": 464.649052,
  "winrate": 0.000332838388
}
```

## Recommendations

Based on the analysis of all runs, **F1** and **F9** appear to be equally strong moves, with **E7** as a close alternative. The corner moves (F1 and F9) are preferred in all runs and have slightly better metrics compared to the central move (E7).

The key factor in this position seems to be securing a strong position in the corners of the board, as the two top moves (F1 and F9) focus on corner positions. This aligns with traditional Go wisdom that recommends playing in the corners during the opening phase of the game. After the first move, the most advantageous follow-up would be to play the other two moves from the top three, typically followed by moves like E9, D5, or F6.

The consistency of the evaluations across all 10 runs demonstrates high confidence in these recommendations.