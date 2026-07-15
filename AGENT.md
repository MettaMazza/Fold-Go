# AGENT.md — the law this workspace is held to

You are working on **Fold Go**: a Go engine (Tromp-Taylor rules, area scoring) whose
every quantity is **counted** — legality is counted connectivity (groups, liberties over
a flat board list), a point holds exactly the **three** counted states (empty/black/white),
and the search is exact. It carries **zero parameters, zero self-play training**. This file
is binding. Read it before you change anything, and route every change back through the
validation in **this directory**.

---

## 0. The one validated anchor (do not regress it)

There is exactly one validated state, and it is the baseline every derivation and
expansion must return to. In this folder it is **proven, reproducibly, by the commands
in §3**. As validated, the engine holds:

- **Rules substrate — the census, certified digit-for-digit against the published Tromp
  oracle** (`tromp.github.io/go/legal`), the engine **halting** (`forced_to_be`) on any mismatch:
  1×1 = **1**, 2×2 = **57**, 3×3 = **12,675**, 4×4 = **24,318,165**.
- **Rectangular boards** (no published oracle) enumerated and **cross-checked by an independent
  Python referee** (`tools/go_census_referee.py`): 1×2 = 5, 2×3 = 489.
- **Solved endpoint:** the 3×3 empty board reaches the **published record +9** (whole board to
  Black under exact minimax with counted greedy ordering + root symmetry, a hard node budget,
  and an honest abort — never a hang), certified by `forced_to_be`.
- **Refereed play:** SFT Type Zero Go (zero parameters, iterative-deepening ceiling 4, 2^19-node
  budget) on 5×5, every position legal under the counted rules. Record in [`tools/GO_MATCHES.md`](tools/GO_MATCHES.md).

If any change makes any of the above stop reproducing, the change is wrong until proven
otherwise. **The anchor is the arbiter, not your intent.**

---

## 1. The zero-parameter law (inherited from the Smithian Fold Theory)

Every derivation in the corpus obeys these constraints — the same standard the main theory is
held to (`OneFoldMaster.md` / `STANDARDS.md` in the parent project). A violation is not a style
issue; it makes a "forced" number a fitted one, and it must halt.

1. **Zero parameters.** No hand-tuned constant, no fitted heuristic, no trained weight, no
   learned policy/value net. Every quantity is **counted** (from the rules / the board geometry)
   or **forced** (assembled from already-derived quantities). If you cannot say *what counts it*,
   it does not belong. Move ordering and symmetry reductions must be **structural** (counted), not
   scored by a fitted function.
2. **Exact arithmetic only.** No decimal ever enters a derivation. Everything is an exact whole
   number or exact fraction (`foundation/exact_integers.ep`, `foundation/exact_fractions.ep`).
3. **Every value traces back to the One.** The only assumed thing is the One; everything else is
   built by the two moves (fold and take) and the two counted generators **`b = 2`, `c = 3`**
   (Go's three point-states are the colour count `c`). No borrowed numbers, no forward references.
4. **The form is forced, not just its parts.** Assembled values are minimal and unique over a
   *generated* candidate space (`foundation/assembly_enumeration.ep`, `foundation/form_enforcement.ep`);
   the `forced_to_be` guard **halts** on any un-forced value. Every census count and every solved
   value passes through `forced_to_be` against the oracle — a mismatch is a hard stop, never a warning.
5. **Measured/oracle values are sealed.** An oracle target is read only on the **comparison side**
   (`forced_to_be(label, engine_count, oracle)`) to take a yes/no difference; it never feeds the
   engine's enumeration. The engine's counts are always its own forward enumeration.

**The guards and the honest abort are the point, not obstacles.** If the engine halts, a constraint
fired; if a search hits its node budget it **aborts honestly** rather than guessing. You fix the
derivation or raise the budget with reason — you never edit, weaken, or route around `forced_to_be`,
the census oracle checks, the referee cross-check, or the abort.

---

## 2. The routing rule (this is the instruction)

**Every derivation and every expansion of the corpus must route through the engine and return to
the one validated anchor with no law or constraint violation.** For any change — a bigger board, a
deeper solve, a new rule detail, a play heuristic:

1. Express the new quantity as **counted or forced** in the `.ep` source (`constants/fold_go.ep`,
   using only `foundation/`). No literal you cannot justify by a count or a forcing; no fitted
   ordering or evaluation.
2. **Rebuild through the engine** (`ernos`, §3) — if it halts, a guard rejected an un-forced value.
   That is the engine doing its job; fix the derivation, do not bypass the guard.
3. **Re-run the full validation in this directory** (§3): the census must still match the Tromp
   oracle digit-for-digit, the 3×3 solve must still reach +9, and the independent Python referees
   must still agree with zero disagreements.
4. Only a change that **passes every check and preserves the anchor** is admissible. Anything else
   is reverted.

There is no "temporarily fit it and clean up later." A learned heuristic that plays well is a
regression, because the entire claim of this engine is that it carries none.

---

## 3. How to validate — in THIS directory

All commands run from this folder (`/Users/mettamazza/Desktop/Fold Go`). `ernos` is on PATH
(`~/.local/bin`); the ErnosPlain toolchain is bundled in `compiler/` (with `compiler/src/transpile_go.rs`).

**A. Build the engine's certification programs from source:**
```sh
cd tests
ernos fold_go_census.ep     # -> ./fold_go_census
ernos fold_go_solve.ep      # -> ./fold_go_solve
ernos fold_go_solve33.ep    # -> ./fold_go_solve33
```
If `ernos` halts on a forced-value guard, that is the constraint firing — see §1/§2.

**B. Run the certification (the census halts on any oracle mismatch):**
```sh
./fold_go_census      # 1x1=1, 2x2=57, 3x3=12675, 4x4=24318165; ends "matches the oracle digit for digit"
./fold_go_solve33     # 3x3 empty board = +9 (the published record); or an HONEST abort at budget
```
The 4×4 census enumerates ~43M colourings and takes a couple of minutes — that is expected, not a hang.

**C. Independent referee cross-check (needs `python3`):**
```sh
python3 tools/go_census_referee.py    # an independent Tromp implementation vs ./tests/fold_go_census
python3 tools/go_solve_referee.py     # an independent solver vs ./tests/fold_go_solve
```
Zero disagreements is the pass condition. The referees `cwd` into this folder — keep them pointing here.

---

## 4. Where things live

- `constants/fold_go.ep` — the engine (the corpus you expand): counted Tromp-Taylor legality,
  group/liberty flood, census, and the exact solver. Self-contained substrate.
- `foundation/*.ep` — exact integers/fractions, the One and the fold, and the enforcement guards
  (`enforcement.ep` carries `forced_to_be`). Treat as fixed substrate.
- `tests/fold_go_census.ep` — the census, certified against the Tromp oracle.
- `tests/fold_go_solve.ep`, `tests/fold_go_solve33.ep` — the exact solver / the 3×3 endpoint.
- `tools/go_census_referee.py`, `tools/go_solve_referee.py` — independent Python cross-checks.
- `tools/measure_go.py`, `tools/GO_MATCHES.md` — the play harness and the match record (the findings).
- `papers/` — the write-ups of the findings.
- `compiler/` — the bundled ErnosPlain toolchain (`ernos` is also on PATH).

The finding this workspace exists to protect: **a Go engine whose legality and search are pure counted
connectivity — census exact to the published oracle at every board through 4×4, the 3×3 solved to the
record, zero parameters, zero self-play.** Keep it that way.
