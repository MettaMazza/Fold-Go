# Fold Go: Exact Counted Legality, Small-Board Certification, and a 2–0 9×9 GNU Go Development Result

**Maria Smith (Ernos Labs)** — release-corrected preprint, July 2026
Companion to *The Smithian Fold Theory of Everything* — concept DOI [10.5281/zenodo.21182468](https://doi.org/10.5281/zenodo.21182468)

## Abstract

Fold Go is a computational proof programme derived from the Smithian Fold Theory (SFT), whose foundation is the machine-checked, self-proven theorem **there is no nothing**. It contains no trained policy network, value network, self-play training, or learned weights. The exact substrate expresses Go legality as counted connectivity and verifies finite board inventories and solved values by independent execution.

The current exact surface reproduces the legal-position census `1, 57, 12,675, 24,318,165` for boards 1×1 through 4×4, plus rectangular counts 5 and 489 for 1×2 and 2×3. Exact empty-board values are freshly secured through 2×2: 1×1 = 0, 1×2 = 0, and 2×2 = +1. Separately, the bounded competitive engine produced two independent two-game sweeps against GNU Go 3.8 on 9×9 at depth ceiling 3. Independent transcript replay accepted every move under positional superko and reproduced all four pass-pass terminals and internal Tromp-area-plus-7 scores.

These are different proof classes. The census and small-board solver are exact finite certifications. The 9×9 result is genuine historical competitive evidence, but it is not yet the post-repair secured rank: the current bounded search must still bind full superko history and previous-pass state in its transposition identity, store alpha-beta bound types correctly, search pass universally, and attach a common rules/komi and cryptographic provenance contract. No current repository receipt supports a 19×19 or KataGo victory or tie. Those earlier statements are withdrawn by this version.

## 1. Scientific position

This work does not treat prediction or benchmark victory as more valuable than proof. Its primary result is an inspectable construction: Go rules, finite position spaces, and solved values are rebuilt as counted objects whose checks halt on violation. Competitive play is the forward-forcing frontier that tests how far the same derived system has been carried under finite computation.

The current release therefore separates:

1. **Exact proof surface** — exhaustive census and exact small-board solving.
2. **Bounded competitive development** — finite-budget sparse search with preserved raw games.
3. **Open secured-rank gate** — the post-repair 9×9 rerun, followed by larger boards and stronger opponents.

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

The 2×2 proof visits 17,038,501 nodes. A fresh 3×3 result was not completed in the bounded release audit and is not promoted here.

## 3. Historical 9×9 competitive result

Two independent depth-ceiling-3 batches against GNU Go 3.8 ended 2–0:

| Receipt | SFT as Black | SFT as White | Aggregate |
|---|---:|---:|---:|
| `batch_gnugo_9x9_d3.log` | 45–40 | 49–38 | 2–0 |
| `v2_gnugo_9x9_d3.log` | 46–40 | 47–39 | 2–0 |

The repository preserves both raw transcripts and ledgers. Independent replay verified every move, both pass-pass endings, and the exact internal scores. The release index records the transcript, source, and opponent hashes available after the fact.

The match contract used the internal Tromp-area scorer with integer komi 7. It did not cryptographically bind a shared GTP rules/komi configuration at run time. That missing binding does not make the preserved games illegal or alter their reproduced scores; it limits the strength of the publication claim.

## 4. Why the competitive rank is not yet secured

The current competitive implementation has named, testable obligations:

- transposition identity must include board, mover, complete positional-superko history, and previous-pass state;
- cached values must distinguish exact, lower-bound, and upper-bound entries;
- pass must be searched whenever legal, not only when no stone candidate survives;
- symmetry must transform the entire augmented state, including history;
- sparse pruning must be described as bounded search rather than exact minimax;
- the referee must bind rules, komi, source commit, opponent binary/configuration, and immutable transcript hashes, and halt on every protocol error.

The next secured-rank result will be measured only after these obligations pass an exhaustive small-state reference gate. The existing 2–0 records remain historical evidence and will not be rewritten as the post-repair result.

## 5. Reproducibility

Run the census and independent referee from the repository:

```sh
cd tests
ernos fold_go_census.ep
./fold_go_census
cd ..
python3 tools/go_census_referee.py
```

The release evidence map is `tools/RESULTS_INDEX.md`. Raw logs are preserved verbatim. Current and refused results are reported together so the development cannot be reconstructed from headlines alone.

## 6. Conclusion

Fold Go already demonstrates that a non-trivial part of computational Go can be forced into transparent counted law: legality, finite inventories, and exact small-board values. It also demonstrates genuine zero-trained-quantity competitive play through two independently replayed 9×9 GNU Go sweeps. The stronger full-board and neural-opponent claims remain open. That boundary is not a retreat from the programme; it is the proof discipline the programme requires.
