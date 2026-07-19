# Symmetric Go: Exact Counted Legality and Small-Board Solving with Zero Trained Parameters

**Maria Smith — Ernos Labs, Scotland — July 2026**

## Abstract

This paper presents the exact substrate of Fold Go, a computational proof of the Smithian Fold Theory. The system is founded on the machine-checked, self-proven theorem **there is no nothing**, which forces the One and its fold rather than assuming them. Go positions are represented as finite three-state coordinate fields; groups and liberties are counted connected components; every reported finite census is generated forward by the engine and independently checked.

The release reproduces the exact legal-position inventory for boards 1×1 through 4×4 and two rectangles, with zero disagreements from an independent referee. Its exact game solver freshly secures empty-board values through 2×2. The competitive implementation now carries complete augmented-state identity, typed transposition bounds, universal pass, complete empty-board orbit retention, complete active-front retention, and independent receipt replay. A sealed six-ply comparison gives exact typed-TT/no-cache identity on 134 augmented states and 24 pass-pass terminals. Competitive measurements are reported separately in the companion paper, including two replayed 9×9 GNU Go sweeps, the recovered 19×19 KataGo task receipt, and source-bound depth-sensitive move evidence.

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

The secured exact value surface currently extends through 2×2. Extending the same exhaustive engine to 3×3 is the next exact-solver state; it is a larger execution of the established finite method, not evidence of a theoretical obstruction.

## 3. Symmetry and proof obligations

Dihedral reduction is valid only when it preserves the complete state on which legality and value depend. For simple finite census states, board symmetry is sufficient. For positional-superko competitive states, the history must be transformed with the board. The current competitive code binds board, mover, previous-pass state, and the complete positional-superko history under a history-wide symmetry transform. Its transposition entries carry exact/lower/upper bound types.

The current implementation suite includes optimized-versus-no-cache comparisons on reachable augmented small-board states. Its sealed six-ply receipt covers 134 distinct states and 24 pass-pass terminals with exact value identity. Empty-board selection preserves every legal dihedral orbit, and ordinary and quiescence selection preserve every legal active front. This remains a bounded competitive search rather than the exhaustive `.ep` small-board solver; the distinction identifies the two executable proof surfaces without reducing either.

Competitive receipts now bind every SFT move to its pre-move augmented state, complete ordered root surface, exact candidate fractions at each completed depth, node-budget status and deterministic argmax. The first applied two-game receipt contains 28/28 such decisions, 56 completed depth passes and 444 exact candidate rows, and passes independent semantic replay. This strengthens the trace from exact state constitution to real-play selection without assigning an agent-owned rank conclusion.

## 4. Applied calculation continuation

Matched 5×5 development receipts hold the opponent, rules, komi, colours, source, and starting conditions fixed while changing depth from one to two. Exact candidate fractions change the selected move from `B5` to `B4` on the empty board and from `pass` to `A3` after a shared 23-ply prefix. This demonstrates that the derived depth relation is active in real play. It is applied development evidence, not an agent-owned official result, loss, or rank conclusion.

The next state is to carry the complete augmented-state and move surface into Maria-authorized 9×9 and full-board runs, then continue calculation development through the strictly-over-50-percent victory criterion. Exact finite legality and solving, replayed competitive victories, complete augmented-state identity, and active depth-sensitive calculation provide a constructive route forward; no theorem-derived wall has been produced.

## 5. Reproducibility

```sh
cd tests
ernos fold_go_census.ep
ernos fold_go_solve.ep
./fold_go_census
cd ..
python3 tools/go_census_referee.py
```

Long-running endpoints must terminate with a result or an explicit honest abort. No timeout is converted into a victory.

## 6. Conclusion

Finite Go legality and small-board game values are executable counted objects
with independent checks. The competitive engine now preserves the complete
augmented state and current move surface, with exact cache/reference identity
and source-bound depth-sensitive applied evidence. Larger-board benchmark
victory is the active forward-forcing campaign. These results establish the
current stage and next calculation route without creating a theoretical wall;
agents do not declare development batches to be Maria's findings, losses, or
endpoint.
