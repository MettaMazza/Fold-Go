# Symmetric Go: Exact Counted Legality and Small-Board Solving with Zero Trained Parameters

**Maria Smith — Ernos Labs, Scotland — July 2026**

## Abstract

This paper presents the exact substrate of Fold Go, a computational proof of the Smithian Fold Theory. The system is founded on the machine-checked, self-proven theorem **there is no nothing**, which forces the One and its fold rather than assuming them. Go positions are represented as finite three-state coordinate fields; groups and liberties are counted connected components; every reported finite census is generated forward by the engine and independently checked.

The release reproduces the exact legal-position inventory for boards 1×1 through 4×4 and two rectangles, with zero disagreements from an independent referee. Its exact game solver freshly secures empty-board values through 2×2. Competitive measurements are reported separately in the companion paper, including two replayed 9×9 GNU Go sweeps and the recovered 19×19 KataGo task receipt with its exact cutoff, scoring, and synchronization facts.

## 1. Counted legality

Each intersection has exactly three rule states: empty, Black, or White. A board is accepted only when every maximal same-colour connected component has a liberty. The engine uses an explicit visited ledger and stack; no learned classifier or statistical legality approximation enters.

The engine's census is compared against published Tromp counts only after enumeration. A mismatch calls the enforcement layer and halts.

| Board | Engine count | Independent check |
|---|---:|---:|
| 1×1 | 1 | 1 |
| 2×2 | 57 | 57 |
| 3×3 | 12,675 | 12,675 |
| 4×4 | 24,318,165 | 24,318,165 |
| 1×2 | 5 | 5 |
| 2×3 | 489 | 489 |

## 2. Exact solver

The exact `.ep` solver and the bounded Python competitive harness are distinct systems and must not share a headline. Fresh exact empty-board results are:

- 1×1 = 0, 2 visited nodes;
- 1×2 = 0, 30 visited nodes;
- 2×2 = +1, 17,038,501 visited nodes.

The release audit did not finish a fresh 3×3 proof and therefore makes no current 3×3 claim. The stale Python solve referee also expects fields the current solver no longer emits; repairing that structured result contract is part of the next exact release.

## 3. Symmetry and proof obligations

Dihedral reduction is valid only when it preserves the complete state on which legality and value depend. For simple finite census states, board symmetry is sufficient. For positional-superko competitive states, the history must be transformed with the board. The current competitive code binds board, mover, previous-pass state, and the complete positional-superko history under a history-wide symmetry transform. Its transposition entries carry exact/lower/upper bound types.

The current 11-test implementation suite includes optimized-versus-no-cache comparisons on reachable augmented small-board states. This remains a bounded competitive search rather than the exhaustive `.ep` small-board solver.

## 4. Reproducibility

```sh
cd tests
ernos fold_go_census.ep
ernos fold_go_solve.ep
./fold_go_census
cd ..
python3 tools/go_census_referee.py
```

Long-running endpoints must terminate with a result or an explicit honest abort. No timeout is converted into a victory.

## 5. Conclusion

Finite Go legality and small-board game values are executable counted objects
with independent checks. Larger-board benchmark victory is the active
forward-forcing campaign. Both are reported on their own evidence, and agents
do not declare development batches to be Maria's findings, losses, or endpoint.
