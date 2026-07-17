# Fold Go evidence index

**Release status:** exact substrate secured; competitive rank repair ongoing.

## Exact proof surface

- Census: 1×1=1, 2×2=57, 3×3=12,675, 4×4=24,318,165; 1×2=5, 2×3=489.
- Independent census referee: zero disagreements.
- Exact empty-board values: 1×1=0 (2 nodes), 1×2=0 (30 nodes), 2×2=+1 (17,038,501 nodes).
- Fresh 3×3 result: not completed during the bounded release audit.

## Accepted historical competitive evidence

### GNU Go 3.8 — 9×9 — depth ceiling 3 — batch 1

- Raw transcript: `batch_gnugo_9x9_d3.log`
- SHA-256: `868fc8f9314514c03f3206022b3a922443e6042552885f8e58747f9606ff78ff`
- Results: SFT Black 45–40; SFT White 49–38; aggregate SFT 2–0.
- Independent replay: every move legal under positional superko; both games ended pass-pass; scores reproduced.

### GNU Go 3.8 — 9×9 — depth ceiling 3 — v2

- Raw transcript: `v2_gnugo_9x9_d3.log`
- SHA-256: `b029188a50a2ea7c2231a24d975e4f55b53b6d609460a49fc786981a6586a770`
- Human ledger: `ledger_gnugo_9x9_d3.md`
- Results: SFT Black 46–40; SFT White 47–39; aggregate SFT 2–0.
- Independent replay: every move legal under positional superko; both games ended pass-pass; scores reproduced.

The reconstructed source SHA-256 for the producing `measure_go.py` is `62069645154e3454bd4057660598c61008dcd2464a8d6792db0f176e5c15c6ab`; the GNU Go 3.8 binary SHA-256 is `069c9400d5f2c9cb931c0960cf9266ac0cf90a93f5dce812b75d463a05f214a8`. The historical runs did not embed those identities at run time, so their binding is reconstructed rather than cryptographic.

The complete release record is `release/go_release_manifest_v2.1.json`.

## Other current results

- GNU Go 9×9 d2: 1–1.
- GNU Go 9×9 d4: 1–1.
- GNU Go 13×13 d3: 0–2.
- KataGo 9×9 d4: 0–4.
- KataGo 13×13 d3: 0–2.
- KataGo 9×9 d3 earlier batch: invalid because of illegal/desynchronized play.
- KataGo 9×9 d3 v2: correctly halted on desynchronization in round 5.
- 19×19: partial log only; no completed outcome.

## Withdrawn claims

No current repository evidence supports:

- a 7–3 GNU Go aggregate on 9×9;
- a 2–0 GNU Go result on 19×19;
- a 1–1 or 2–0 KataGo result on 19×19;
- a secured post-repair competitive rank.

These are corrected in the July 2026 release papers and Zenodo metadata.
