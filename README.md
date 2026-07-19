# Fold Go

> A computational proof of the [Smithian Fold Theory of Everything](https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything), founded on one machine-checked, self-proven theorem: **there is no nothing**.

## Go counted instead of trained

Fold Go has zero trained parameters, zero neural networks, and zero self-play training. Its exact substrate rebuilds legality as counted connectivity and game values as finite exhaustive search. Its competitive engine is a bounded forward-forcing development surface and is reported separately from the exact solver.

## Secured exact results

- Legal-position census: 1×1 = **1**, 2×2 = **57**, 3×3 = **12,675**, 4×4 = **24,318,165**.
- Rectangular census: 1×2 = **5**, 2×3 = **489**.
- Independent Python census referee: **zero disagreements**.
- Fresh exact empty-board values: 1×1 = **0**, 1×2 = **0**, 2×2 = **+1**; the 2×2 proof visits 17,038,501 nodes.

A fresh 3×3 value was not completed in the bounded release audit and is not claimed by this release.

## Competitive development evidence

Two separate 9×9 depth-ceiling-3 batches against GNU Go 3.8 ended **SFT 2–0**. Independent replay verified every move, both pass-pass terminals, and all four internal Tromp-area-plus-7 scores.

The original 19×19 depth-ceiling-4 KataGo task receipt has also been recovered.
Its historical harness reported **SFT 2–0**, 73–54 as Black and 70–66 as
White. The exact protocol record is preserved with the result: both games
stopped at the historical 128-ply cutoff and used the harness's internal area
score; Round 1 contains two rejected `play` responses that the old harness did
not halt on, while Round 2 contains no logged rejection. This is reported as a
harness point-at-cutoff measurement with the Round-1 synchronization defect,
not erased and not conflated with the exact small-board proofs.

See [tools/RESULTS_INDEX.md](tools/RESULTS_INDEX.md) for the complete evidence map.

## Current engine stage

The competitive implementation now binds board, mover, complete positional-superko history, and previous-pass state; transforms the full augmented history under symmetry; uses typed transposition bounds; keeps pass available at every node; and replays sealed match receipts against source and opponent identities. The six-ply augmented-state receipt compares typed-TT search with the no-cache all-actions reference on **134 states**, including **24 pass-pass terminals**, with exact value identity throughout.

The current search also preserves one representative from every legal empty-board dihedral orbit and every legal active front at quiescence, removing the earlier board-size-specific opening subset and authored two-liberty front cutoff. In a source-bound matched 5×5 depth comparison, the engine's exact root values changed the selected move from `B5` at depth 1 to `B4` at depth 2 in one game, and from `pass` to `A3` in the second. This is implemented evidence that the derived depth relation is active in real play; it is not an agent-owned rank conclusion.

The next state is to carry this complete augmented-state and move surface into Maria-authorized 9×9 and full-board benchmark runs, preserve every source-bound receipt, and continue the greater-than-50-percent victory campaign through stronger opponents. Nothing in the exact state constitution or current applied evidence establishes a theoretical wall: the engine already supplies exact finite legality and values, replayed competitive victories, complete augmented-state identity, and a depth-sensitive competitive search path toward the full board. The frontier is further calculation and applied rank development.

## Reproduce the exact surface

```sh
cd tests
ernos fold_go_census.ep
./fold_go_census
cd ..
python3 tools/go_census_referee.py
```

The 4×4 census is exhaustive and takes several minutes. Long-running solves must produce a result or an explicit honest abort; a timeout is never converted into a claim.

## Papers

- [Symmetric Go: Exact Counted Legality and Small-Board Solving](papers/Symmetric_Go_Solving_Spatial_Command_on_the_3D_Lattice.md)
- [Fold Go: Exact Certification and a 2–0 9×9 GNU Go Development Result](papers/Zero_Parameter_Geometric_Go_Superhuman_Performance.md)

## Layout

| Path | Purpose |
|---|---|
| `constants/fold_go.ep` | counted legality, census, and exact solver |
| `foundation/*.ep` | theorem-forced One/fold, exact arithmetic, enforcement |
| `tests/fold_go_*.ep` | exact certification programs |
| `tools/go_*_referee.py` | independent Python checks |
| `tools/measure_go.py` | bounded competitive development harness |
| `tools/RESULTS_INDEX.md` | evidence, hashes, provenance, and protocol facts |
| `tools/development_runs/matched_depth_divergence_20260719.json` | source-bound depth-1/depth-2 applied move/value comparison |
| `tools/*.log`, `gtp_logs/` | preserved raw transcripts |

Read [AGENT.md](AGENT.md) before changing the system. Every admitted mechanism must be directly forced, forward-forced, or constitutionally re-derived, and every violation must halt.
