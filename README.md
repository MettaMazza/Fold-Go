# Fold Go

> **Part of the [Smithian Fold Theory of Everything](https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything).** Sibling zero-parameter engines: [FoldBot Chess](https://github.com/MettaMazza/FoldBot-Chess) · [Fold Protein](https://github.com/MettaMazza/Fold-Protein).

A Go engine (Tromp-Taylor rules, area scoring) whose every quantity is **counted** — legality
is counted connectivity (groups and liberties over a flat board list), a point holds exactly the
**three** counted states (empty/black/white), and the search is exact. **Zero parameters. Zero
self-play training.** The incumbents climbed Go with thousands of TPUs and millions of self-play
games; this engine climbs it by counting.

Duplicated from the Smithian Fold Theory project as an independent workspace at the validated
state of the Go work.

## Quick start

```sh
# 1. Build the certification programs from source (ernos is on PATH)
cd tests
ernos fold_go_census.ep
ernos fold_go_solve33.ep

# 2. Certify the rules against the published Tromp oracle (halts on any mismatch)
./fold_go_census      # 1x1=1  2x2=57  3x3=12675  4x4=24318165  (4x4 takes ~2 min)

# 3. The solved endpoint: 3x3 empty board = +9 (the published record)
./fold_go_solve33

# 4. Independent referee cross-check (needs python3)
python3 ../tools/go_census_referee.py
```

## The rule that governs this workspace

**Read [`AGENT.md`](AGENT.md) first.** Every derivation and expansion of the corpus must route
through the engine and return to the one validated anchor with **no law or constraint violation** —
counted or forced values only, exact arithmetic, everything traced to the One, the `forced_to_be`
oracle checks and the honest node-budget abort left intact. Move ordering and symmetry must be
structural (counted), never a fitted or learned score. Validation is done in this directory
(see `AGENT.md` §3).

## Layout

| Path | What |
|------|------|
| `constants/fold_go.ep` | the engine (the corpus you expand): counted legality, census, exact solver |
| `foundation/*.ep` | exact integers/fractions, the One and the fold, the enforcement guards |
| `tests/fold_go_census.ep` | the census, certified against the Tromp oracle |
| `tests/fold_go_solve*.ep` | the exact solver and the 3×3 endpoint |
| `tools/go_*_referee.py` | independent Python cross-checks |
| `tools/measure_go.py`, `tools/GO_MATCHES.md` | the play harness + match record (findings) |
| `papers/` | the write-ups of the findings |
| `compiler/` | bundled ErnosPlain toolchain (incl. `src/transpile_go.rs`; `ernos` also on PATH) |

## Validated record (reproduced by the commands above)

- Census vs the published Tromp oracle, digit for digit, halts on mismatch: 1×1=1 · 2×2=57 · 3×3=12,675 · 4×4=24,318,165
- Rectangular boards cross-checked by an independent referee: 1×2=5 · 2×3=489
- 3×3 empty board solved to the published record **+9** · 5×5 refereed play (see `tools/GO_MATCHES.md`)

## Papers & findings

- [Symmetric Go: Solving Spatial Command on the 3D Lattice](papers/Symmetric_Go_Solving_Spatial_Command_on_the_3D_Lattice.md)
- [Zero-Parameter Geometric Go: Superhuman Performance](papers/Zero_Parameter_Geometric_Go_Superhuman_Performance.md)
- Full match record: [tools/GO_MATCHES.md](tools/GO_MATCHES.md)

---

Part of the **[Smithian Fold Theory of Everything](https://github.com/MettaMazza/Smithian-Fold-Theory-Of-Everything)** — one axiom, zero parameters, everything forced from the One.
