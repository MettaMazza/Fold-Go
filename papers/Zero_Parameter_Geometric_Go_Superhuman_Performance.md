# Fold Go: Exact Counted Legality, Small-Board Certification, and Recorded Zero-Parameter Match Results

**Maria Smith (Ernos Labs)** — publication edition v2.4, 22 July 2026
Companion to *The Smithian Fold Theory of Everything* — concept DOI [10.5281/zenodo.21182468](https://doi.org/10.5281/zenodo.21182468)

## Abstract

Fold Go is a computational proof programme derived from the Smithian Fold Theory (SFT), whose foundation is the machine-checked, self-proven theorem **there is no nothing**. It contains no trained policy network, value network, self-play training, or learned weights. The exact substrate expresses Go legality as counted connectivity and verifies finite board inventories and solved values by independent execution.

The current exact surface reproduces the legal-position census `1, 57, 12,675, 24,318,165` for boards 1×1 through 4×4, plus rectangular counts 5 and 489 for 1×2 and 2×3. Exact empty-board values are freshly secured through 2×2: 1×1 = 0, 1×2 = 0, and 2×2 = +1. Separately, the bounded competitive engine produced two independent two-game sweeps against GNU Go 3.8 on 9×9 at depth ceiling 3. Independent transcript replay accepted every move under positional superko and reproduced all four pass-pass terminals and internal Tromp-area-plus-7 scores. The recovered 19×19 depth-ceiling-4 KataGo task receipt records a further harness-reported 2–0 measurement, 73–54 as Black and 70–66 as White. The current engine additionally binds complete augmented state, typed transposition bounds, universal pass, complete empty-board orbits, complete active fronts, and immutable source/opponent receipts; typed-TT and no-cache values agree on a sealed 134-state surface with 24 pass-pass terminals.

These are different evidence classes. The census and small-board solver are exact finite certifications. Match transcripts are measured implementation results. The recovered 19×19 receipt stopped both games at the historical 128-ply harness cutoff and used the harness's internal area score. Round 1 contains two rejected `play` responses that the old harness failed to halt on, creating a possible board-state divergence; Round 2 contains no logged rejection. The exact statement supported by the receipt is therefore a **harness-reported 2–0 point-at-cutoff measurement with a Round-1 synchronization defect**. The measurement is retained with its protocol facts rather than withdrawn or conflated with the exact solver.

## 1. Scientific position

Fold Go pursues both executable proof and benchmark victory. Go rules, finite
position spaces, and solved values are rebuilt as counted objects whose checks
halt on violation; the competitive campaign then carries that derived system
through increasing board sizes and opponent strength until the declared victory
criterion is secured. Development runs are preserved as measurements of their
named builds. An AI agent does not get to promote an early run into Maria's
finding or loss, set the campaign endpoint, or undercut the active victory
programme.

The current release therefore separates:

1. **Exact proof surface** — exhaustive census and exact small-board solving.
2. **Bounded competitive development** — finite-budget sparse search with preserved raw games.
3. **Forward competitive work** — registered matches on increasing board sizes and opponent strengths under Maria's greater-than-50-percent victory criterion.

## 2. Exact counted surface

Under the declared Tromp-Taylor legality grammar, a position is legal only when every maximal same-colour group has at least one liberty. Fold Go enumerates the board directly; published counts are used only on the comparison side.

| Board | Exact legal positions |
|---|---:|
| 1×1 | 1 |
| 2×2 | 57 |
| 3×3 | 12,675 |
| 4×4 | 24,318,165 |
| 1×2 | 5 |
| 2×3 | 489 |

An independently written Python referee reports zero disagreements. The exact solver freshly secures:

| Empty board | Exact value for Black |
|---|---:|
| 1×1 | 0 |
| 1×2 | 0 |
| 2×2 | +1 |

The 2×2 proof visits 17,038,501 nodes. The next exact state extends this same finite exhaustive method to 3×3; the current secured claim remains the exact surface through 2×2.

## 3. Recorded competitive results

Two independent depth-ceiling-3 batches against GNU Go 3.8 ended 2–0:

| Receipt | SFT as Black | SFT as White | Aggregate |
|---|---:|---:|---:|
| `batch_gnugo_9x9_d3.log` | 45–40 | 49–38 | 2–0 |
| `v2_gnugo_9x9_d3.log` | 46–40 | 47–39 | 2–0 |

The repository preserves both raw transcripts and ledgers. Independent replay verified every move, both pass-pass endings, and the exact internal scores. The release index records the transcript, source, and opponent hashes available after the fact.

The match contract used the internal Tromp-area scorer with integer komi 7. It did not cryptographically bind a shared GTP rules/komi configuration at run time. Report that exact protocol with the reproduced scores.

The recovered 19×19 KataGo receipt is SHA-256
`b26eda8f0c82cfad7a6d4fb8ca28e62c48b7919c59512c71d37327cb99fd3b18`.
The historical command was
`python3 -u tools/measure_go.py --size 19 --depth 4 --rounds 2 --engine katago gtp`.
The harness emitted 73–54 with SFT as Black and 70–66 with SFT as White, then
`Final Score: SFT 2 - 0 Opponent`. Both games stopped at 128 plies and were
scored internally. Round 1 includes two rejected `play` responses that the old
harness ignored; Round 2 has no logged rejection. The evidence index preserves
the full provenance and result wording.

## 4. Current competitive measurement protocol

The current competitive implementation records the following testable protocol properties for new measurements:

- transposition identity must include board, mover, complete positional-superko history, and previous-pass state;
- cached values must distinguish exact, lower-bound, and upper-bound entries;
- pass must be searched whenever legal, not only when no stone candidate survives;
- symmetry must transform the entire augmented state, including history;
- sparse pruning must be described as bounded search rather than exact minimax;
- the referee must bind rules, komi, source commit, opponent binary/configuration, and immutable transcript hashes, and halt on every protocol error.

These properties make later matches replayable and expose protocol defects. They do not authorize an AI agent to define rank or publication. Maria's declared criterion is a score strictly above 50% at the point of victory.

The current implementation has now executed those repairs. A sealed six-ply receipt gives typed-TT/no-cache equality on 134 augmented states and 24 pass-pass terminals. The empty board retains every legal dihedral orbit and the occupied/quiescence surface retains every legal active front. In a matched 5×5 development comparison, exact root fractions change the selected move `B5 → B4` between depths one and two in one game and `pass → A3` in the other. This is source-bound applied evidence that the depth relation is active in real play, not Maria Smith's official game or rank conclusion.

The game receipt now also preserves the calculation itself at every SFT move: exact augmented-state address, complete candidate order, exact fraction for every candidate at every completed depth, node-budget status, and final deterministic argmax. A matched two-game 5×5 depth-2 GNU Go development execution sealed 28/28 SFT decisions, 56 completed depth passes, and 444 candidate-value rows; independent replay verified both complete games and the hash chain. The named 1/1/0 tally remains development data, not an agent declaration of rank, victory, loss, or endpoint.

The next state is a Maria-authorized 9×9 or full-board campaign on this secured calculation and receipt surface, followed by continued development until the strictly-over-50-percent criterion is attained at each named level. The exact solver, replayed 9×9 victories, recovered 19×19 measurement, complete augmented-state constitution, and active depth-sensitive search provide an executable route; no theorem-derived wall has been established.

## 5. Reproducibility

Run the census and independent referee from the repository:

```sh
cd tests
ernos fold_go_census.ep
./fold_go_census
cd ..
python3 tools/go_census_referee.py
```

The release evidence map is `tools/RESULTS_INDEX.md`. Raw logs are preserved verbatim. Engine proofs, implementation measurements, Maria's declared conclusions, and agent-authored probes remain separately attributed.

## 6. Conclusion

Fold Go demonstrates that a non-trivial part of computational Go can be forced into transparent counted law: legality, finite inventories, exact small-board values, complete augmented-state identity, exact cache/reference agreement, and a depth-sensitive competitive calculation. It also records zero-trained-quantity competitive play through two independently replayed 9×9 GNU Go sweeps and the recovered 19×19 KataGo point-at-cutoff measurement with its exact protocol facts. Competitive development proceeds toward the declared victory campaign without redefining proof as prediction or converting development artifacts into limits.
