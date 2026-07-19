# Fold Go competitive measurement status

## Completed on 2026-07-18

- State identity binds the current board, mover, previous-pass flag, and the
  complete positional-superko history.
- A dihedral transform is admitted only when the same transform preserves the
  current board and every historical board.
- Transposition entries verify the exact augmented state and carry `EXACT`,
  `LOWER`, or `UPPER` bound type.
- Pass is available at every search node and at the root. Two consecutive
  passes alone invoke terminal area scoring.
- The referee and GTP boundary now carry the previous-pass state into root
  selection. A root pass after an opponent pass is scored immediately as the
  terminal area position rather than being searched as a first pass. The SFT
  move is locally legality-checked before it is sent to the opponent.
- Pass and resign are distinct protocol outcomes.
- Equal literal area scores are recorded as draws; they are no longer assigned
  to White and they do not increment either side's win count.
- The tournament client fails closed on rejected commands, malformed replies,
  opponent EOF, illegal/desynchronized moves, and move-cap truncation.
- A tournament now requires an explicit new output directory. Before play it
  records the source commit/hash, opponent command and executable hash, literal
  rules, board size, integer komi, search ceiling, node budget, colour schedule,
  and hardware. Every completed game carries its moves, GTP transcript, final
  position, complete-history hash, score, and result; the final match receipt
  hash-binds every game receipt. Existing receipt directories are never replaced.
- A halted match is sealed as `void` rather than being turned into a result.
- The receipt verifier now independently replays every recorded move through
  the local rules, rechecks alternating colours, pass-pass/resignation,
  positional-superko history, final position, literal area score, draw/winner
  attribution, and the aggregate tally in addition to the outer hash chain.
  The preserved 5×5 GNU Go smoke receipts pass this semantic replay.
- On boards through 3×3 the optimized path uses all legal point actions plus
  pass. Focused verification matches the typed-TT search against the same
  no-cache all-actions search.
- The focused suite now also enumerates the reachable 2×2 augmented states
  through five plies and compares typed-TT with no-cache all-actions search at
  every retained state, including pass history.
- The sealed six-ply receipt extends that boundary to 134 distinct augmented
  states and 24 pass-pass terminals. All 134 typed-TT values equal their
  no-cache all-actions values at the registered comparison depth.
- The external receipt path was exercised against the installed GNU Go binary
  on 5×5, integer komi 0, depth-zero infrastructure mode, alternating colours.
  Both games completed and the receipt verifier confirms both transcripts,
  game hashes, source hash, and opponent executable hash. The harness emitted
  0–2 in this depth-zero infrastructure measurement. It is not Maria's finding
  or loss and does not define playing strength.

These are engine and referee corrections. The evidence record also contains
the exact census/solve surface, two replay-verified 2–0 GNU Go 9×9 batches, and
the recovered 19×19 KataGo point-at-cutoff measurement with its disclosed
Round-1 synchronization defect. Maria determines the conclusions and next run.

## Agent-recommended measurement strengthening

- Extend the reachable augmented-state census beyond the sealed six-ply boundary.
- Re-run the complete local exact and referee anchors after the receipt layer is
  implemented.
- Add deterministic per-move search-decision receipts bound into each game.
- Register the next rank opponent, settings, output directory, and stopping
  rule when Maria orders the run.

These recommendations improve replayability and engine coverage. They do not
authorize, refuse, delay, or veto a real match and cannot define rank or the
project conclusion. Maria alone decides when the next build runs and what the
result establishes.

## Complete empty-board orbit surface

The development engine now retains one representative from every legal
dihedral orbit on an empty board. The former hand-listed 9x9 and 19x19
star-point subsets are removed, so no board-size-specific opening preference
can exclude a legal orbit before exact search. This is a completeness
correction, not an official match or rank conclusion.

## Complete active-front quiescence surface

The development engine no longer uses a hand-selected two-liberty cutoff to
decide which occupied-board fronts exist at a quiescence leaf. Both ordinary
search and bounded quiescence now retain one augmented-symmetry representative
of every legal liberty adjacent to every live group. The existing quiescence
depth remains the stopping rule. A focused test constructs a four-liberty group
and proves that every legal active-front orbit survives selection. This is an
engine-completeness correction, not an official game, result, or rank claim.

## Applied depth-sensitive move evidence

The committed matched 5×5 development receipts hold opponent, rules, komi,
colours, source, and starting conditions fixed while changing the search depth
from one to two. Exact replay locates two first divergences:

- game 1 changes from `B5` at depth 1 to `B4` at depth 2 on the empty board;
- game 2 changes from `pass` at depth 1 to `A3` at depth 2 after a shared
  23-ply prefix.

`tools/development_runs/matched_depth_divergence_20260719.json` preserves the
complete candidate fractions at both depths and binds the producing receipts.
This proves that the implemented depth relation changes real-play selection
through exact computed values. It is source-bound development evidence, not
Maria Smith's official game, rank conclusion, loss, or campaign endpoint.

## Current stage and next state

The current engine has complete augmented-state identity, typed TT bounds,
universal pass, complete empty-board orbit retention, complete active-front
retention, source/opponent-bound immutable receipts, and applied depth-sensitive
move evidence. The next state is to use this secured calculation surface in
Maria-authorized 9×9 and full-board runs and continue development until the
strictly-over-50-percent victory criterion is attained at each named level.
Exact finite proofs, two replay-verified 9×9 victories, the recovered 19×19
point-at-cutoff measurement, and the completed search-state constitution give
an executable route forward; no theorem-derived obstruction has been produced.
