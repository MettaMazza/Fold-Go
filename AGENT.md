# Fold Go development constitution

Fold Go is a computational proof of the Smithian Fold Theory. Its foundation is one machine-checked, self-proven theorem—**there is no nothing**—which forces the One and its fold. Neither the author nor an agent decides whether a derivation is valid: the engine's trace, closure, enforcement, and halt conditions do.

## Admissible routes

Every mechanism must enter by one named route:

1. direct forcing from the SFT corpus;
2. forward forcing created to secure a required Go/computational operation;
3. constitutional re-derivation of established computer science inside SFT mathematics and constraints.

An unexplained imported algorithm, learned weight, fitted number, or heuristic literal is outside the forced claim until closed. Preserve it as engineering work rather than relabeling it.

## Secured anchor

- Census: 1×1=1, 2×2=57, 3×3=12,675, 4×4=24,318,165; rectangles 1×2=5 and 2×3=489.
- Independent census referee: zero disagreements.
- Fresh exact values: 1×1=0, 1×2=0, 2×2=+1; 2×2 nodes=17,038,501.
- Historical competitive evidence: two independent GNU Go 3.8, 9×9, depth-ceiling-3 batches at 2–0, independently replayed as legal with reproduced scores.

Do not claim a fresh 3×3 exact value, 19×19 win/tie, KataGo win/tie, or secured competitive rank without a new immutable receipt satisfying the gates below.

## Exact-surface gate

From the project root:

```sh
cd tests
ernos fold_go_census.ep
ernos fold_go_solve.ep
./fold_go_census
cd ..
python3 tools/go_census_referee.py
```

The engine must halt on census disagreement. Long solves must end in a completed result or explicit honest abort.

## Competitive-proof gate

Before the 9×9 rank is rerun and secured:

- state identity binds board, mover, complete positional-superko history, and previous-pass state;
- transposition entries carry exact/lower/upper bound type;
- pass is always an available legal action;
- any symmetry transforms the entire augmented history;
- optimized search agrees exhaustively with a no-cache/all-actions reference on small reachable states;
- the referee sets and records a common rules and komi contract;
- opponent errors, illegal moves, desynchronization, or truncation halt and void the game;
- source commit, source hash, opponent binary/configuration hash, hardware, transcript, and result manifest are immutable and hash-bound.

Only after this gate may a new result be called the secured rank. Preserve prior raw games as historical evidence.

## Repository discipline

- Standalone Fold Go controls active development.
- Main SFT receives a synchronized release only after the standalone result passes its gates and Maria declares the publishable conclusion.
- Commit locally by project; push only on Maria's request.
- Never overwrite or delete a negative, voided, partial, or desynchronized run. Index it with its status.
