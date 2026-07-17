# Fold Go

> **Part of the [Smithian Fold Theory of Everything](https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything).** Sibling zero-parameter engines: [FoldBot Chess](https://github.com/MettaMazza/FoldBot-Chess) · [Fold Protein](https://github.com/MettaMazza/Fold-Protein).

## A Go engine that **counts instead of training** — zero parameters, zero self-play.

The incumbents climbed Go with thousands of TPUs and millions of self-play games. This engine
climbs it by counting: legality is counted connectivity (groups and liberties), a point holds
exactly the three counted states, and the search is exact. There is no policy net, no value net,
no learned anything.

### What it does — measured, and reproducible

- ✅ **Rules certified digit-for-digit against the published Tromp oracle**, the engine **halting**
  on any mismatch: 1×1 = **1** · 2×2 = **57** · 3×3 = **12,675** · 4×4 = **24,318,165**. An
  independent Python referee cross-checks every count.
- 🎯 **3×3 solved to the published record, +9** — exact minimax with *counted* move ordering and
  root symmetry, a hard node budget, and an honest abort (never a hang).
- 🔢 **Zero parameters, zero self-play training.** Move ordering and symmetry are structural
  (counted), never a fitted or learned score.

```sh
# see it for yourself
cd tests
ernos fold_go_census.ep && ./fold_go_census     # counts vs the Tromp oracle, digit for digit
ernos fold_go_solve33.ep && ./fold_go_solve33    # 3x3 empty board = +9
python3 ../tools/go_census_referee.py            # an independent referee agrees
```
*(The 4×4 census enumerates ~43M colourings — a couple of minutes, not a hang.)*

## How it works

- **Legality is counted connectivity** — Tromp-Taylor rules: a position is legal iff every maximal
  same-colour group has a liberty. Groups are counted connected components (breadth-first flood over
  the flat board, a visited ledger, an exact stack — no recursion, no heuristics).
- **A point is the colour count** — three states, empty/black/white — `c = 3` itself.
- **The census is the engine's own forward enumeration**; the oracle lives on the comparison side
  only, and any disagreement halts the run.

## The rule that governs this workspace

**Read [`AGENT.md`](AGENT.md) first.** Every derivation and expansion must route through the engine
and return to this validated state with **no law or constraint violation** — counted or forced
values only, everything traced to the One, the `forced_to_be` oracle checks and the honest
node-budget abort left intact. A learned heuristic that plays well is a regression, because the
whole point is that this engine carries none.

## Papers & findings

- **[Symmetric Go: Solving Spatial Command on the 3D Lattice](papers/Symmetric_Go_Solving_Spatial_Command_on_the_3D_Lattice.md)**
- **[Zero-Parameter Geometric Go: Superhuman Performance](papers/Zero_Parameter_Geometric_Go_Superhuman_Performance.md)**
- Full match record: [`tools/GO_MATCHES.md`](tools/GO_MATCHES.md)

## Layout

| Path | What |
|------|------|
| `constants/fold_go.ep` | the engine: counted legality, census, exact solver |
| `foundation/*.ep` | exact integers/fractions, the One and the fold, the enforcement guards |
| `tests/fold_go_census.ep` | the census, certified against the Tromp oracle |
| `tests/fold_go_solve*.ep` | the exact solver and the 3×3 endpoint |
| `tools/go_*_referee.py` | independent Python cross-checks |
| `tools/measure_go.py`, `GO_MATCHES.md` | play harness + match record |
| `compiler/` | bundled ErnosPlain toolchain (incl. `src/transpile_go.rs`; `ernos` also on PATH) |

---

Part of the **[Smithian Fold Theory of Everything](https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything)** — one machine-checked, self-proven theorem (*there is no nothing*), zero parameters, with the One and fold forced rather than assumed.
