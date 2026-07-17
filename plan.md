# Fold Go rank-securing plan

## Complete

- Exact legal-position census through 4×4 and two rectangles.
- Independent census referee with zero disagreements.
- Exact empty-board values through 2×2.
- Two independently replayed historical 2–0 GNU Go 3.8 results on 9×9 at depth ceiling 3.

## Current blockers

1. Augmented superko state is absent from the competitive transposition identity.
2. Transposition entries do not distinguish exact, lower, and upper bounds.
3. Pass is omitted while stone candidates exist.
4. Current symmetry reduction does not transform the complete history.
5. Sparse competitive search is bounded, not exact minimax.
6. The referee does not yet hash-bind common rules, komi, source, opponent configuration, and transcripts.

The previous “16-bit fraud” and “geometric eye equals unconditional life” diagnoses are refused. The current packing base already exceeds the provable 19×19 denominator bound, and a local one-eye pattern is not an unconditional-life theorem.

## Next implementation order

1. Build an all-actions, no-cache reference search over small reachable augmented states.
2. Implement complete state identity and bound-typed transposition entries.
3. Make pass universal and transform complete history under symmetry.
4. Add immutable referee manifests, protocol-error halts, and transcript replay.
5. Require worker-count and move-order identity on the registered gate set.
6. Rerun GNU Go 3.8 on 9×9 at the current depth/rank gate.
7. Secure the rank only if SFT wins strictly more than 50% at the point of victory.
8. Then advance to larger boards and stronger opponents, preserving every negative run.
