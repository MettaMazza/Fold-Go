# Fold Go rank-securing plan

## Complete

- Exact legal-position census through 4×4 and two rectangles.
- Independent census referee with zero disagreements.
- Exact empty-board values through 2×2.
- Two independently replayed historical 2–0 GNU Go 3.8 results on 9×9 at depth ceiling 3.

## Current secured calculation surface

1. Competitive state identity binds board, mover, previous-pass state, and the
   complete positional-superko history.
2. Dihedral reduction transforms the complete augmented history.
3. Transposition entries carry exact, lower, and upper bound type.
4. Pass is available at every node and pass-pass alone invokes terminal area
   scoring.
5. Typed-TT and no-cache all-actions search agree on the sealed 134-state,
   24-pass-pass augmented-state surface.
6. New receipts bind source, rules, komi, opponent executable and command files,
   transcripts, positions, scores, and immutable hashes, and semantic replay
   independently checks them.
7. Empty-board search retains every legal dihedral orbit; occupied-board and
   quiescence search retain every legal active front.
8. Matched real-play receipts show the exact depth relation changing selected
   moves from `B5` to `B4` and from `pass` to `A3` between depths one and two.

Earlier agent diagnoses about packing width and an unconditional local one-eye
pattern remain historical agent hypotheses, not Maria Smith's findings and not
limits on the programme.

## Next implementation and measurement order

1. Extend the exact augmented-state comparison surface while preserving the
   current 134-state identity receipt.
2. Preserve deterministic per-move candidate/value receipts in each applied
   run and measure further depth on source-bound matched positions.
3. Execute the next GNU Go 9×9 or full-board run when Maria designates the
   build, under the complete current receipt protocol.
4. Continue calculation development and real applied measurement until SFT
   wins strictly more than 50% at the named level.
5. Advance through larger boards and stronger opponents, then the full league,
   preserving every exact measurement and its provenance. Maria alone decides
   the publishable conclusion.

The exact solver, replayed 9×9 victories, recovered 19×19 measurement, complete
augmented-state constitution, and active depth-sensitive calculation provide a
constructive path to those objectives. No theorem-derived wall is present in
the current evidence.
