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

Two separate 9×9 depth-ceiling-3 batches against GNU Go 3.8 ended **SFT 2–0**. Independent replay verified every move, both pass-pass terminals, and all four internal Tromp-area-plus-7 scores. These are genuine historical results.

They are not yet the secured post-repair rank. The competitive search still needs an augmented-state proof gate for complete positional-superko history, previous-pass state, transposition bound types, universal pass search, and a cryptographically bound referee contract. No current receipt supports a 19×19 or KataGo victory or tie.

See [tools/RESULTS_INDEX.md](tools/RESULTS_INDEX.md) for the complete evidence map.

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
| `tools/RESULTS_INDEX.md` | evidence, hashes, accepted/refused claims |
| `tools/*.log`, `gtp_logs/` | preserved raw transcripts |

Read [AGENT.md](AGENT.md) before changing the system. Every admitted mechanism must be directly forced, forward-forced, or constitutionally re-derived, and every violation must halt.
