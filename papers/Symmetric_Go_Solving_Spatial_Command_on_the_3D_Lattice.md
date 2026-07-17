# Symmetric Go: Exact Counted Legality and Small-Board Solving with Zero Trained Parameters

**Maria Smith — Ernos Labs, Scotland — July 2026**

## Abstract

This paper presents the exact substrate of Fold Go, a computational proof of the Smithian Fold Theory. The system is founded on the machine-checked, self-proven theorem **there is no nothing**, which forces the One and its fold rather than assuming them. Go positions are represented as finite three-state coordinate fields; groups and liberties are counted connected components; every reported finite census is generated forward by the engine and independently checked.

The release reproduces the exact legal-position inventory for boards 1×1 through 4×4 and two rectangles, with zero disagreements from an independent referee. Its exact game solver freshly secures empty-board values through 2×2. A previously stated 3×3 value and claimed 9×9/19×19 tournament aggregates are not promoted without a completed current receipt. Competitive evidence is reported separately in the companion Fold Go development-result paper.

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

Dihedral reduction is valid only when it preserves the complete state on which legality and value depend. For simple finite census states, board symmetry is sufficient. For positional-superko competitive states, the history must be transformed with the board. Current competitive code canonicalizes the current board only, so its transposition cache is not an exact solver for the augmented rule state.

This distinction is constructive: it identifies the next theorem-to-code bridge precisely. The optimized search will be admitted only when an all-actions, no-cache reference agrees exhaustively on small reachable augmented states.

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

The exact Fold Go result is already substantive: finite Go legality and small-board game values are executable counted objects with independent checks. Larger-board competitive strength remains a forward-forcing programme, not the criterion by which the exact surface is judged.
