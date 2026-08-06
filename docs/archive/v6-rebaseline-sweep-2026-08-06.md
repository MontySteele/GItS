> **MOVED 2026-08-06 — Clear the Stage, Track R-B (charter R119, rail 1).**
> Old path: `docs/v6-rebaseline-sweep-2026-08-06.md` — new path: `docs/archive/v6-rebaseline-sweep-2026-08-06.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Citers repointed in the move commit; see
> `review/stage-clear/rb-move-manifest.tsv`.

# v6 re-baseline sweep — the standing batteries re-run under CONSTANTS 6 (Track M, wave 8)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

> **Run 2026-08-06, Track M (wave 8).** This sweep closes the v6 measurement
> window opened by R117/R118 (Q13 α Frozen scope, Q14 stamp bump, Q16 shop
> conditioning): per the window rule, nothing combat/shop was quotable until
> this sweep is green. **All numbers here are measured-under-v6 / DRAFTER 14**
> (paired v5 halves are labeled). Zero design authority: this document
> measures and reports; no lever is moved, no constant tuned, and nothing is
> graded against a band no ruling defines.

## Design — how the v5→v6 comparison isolates the batch

The archived surfaces were measured across several older worlds (C4 and
earlier), so archived-vs-fresh deltas would be confounded by everything since.
Following the D12→D13 pairing precedent (`docs/roster-anchor-v14-2026-08-05.md`
§1 "Pairing"; the sim-hygiene log's worktree recipe), the sweep runs **the
same recipe in two worktrees**: the v6 world at main `745139b` and the last
pre-v6 point on main, `09e0b56` (verified `RT7/D14/P3/C5`), same seeds, same
n. `run_many` seeds run *i* as `seed + i`, so run *i* in the two worlds is the
same world with different constants; the pair is a comparison, not two
measurements. (`game_ref/` was **copied** — not junctioned — into both trees,
read-only.)

What v6 changed, i.e. the expectation this sweep checks rather than assumes:
α narrowed the freezable set (boss-room non-minion helpers no longer freeze —
Frozen-touching arms may move) and Q16 conditioned
`SHOP_COMPANION_RARITY_ODDS` over the ≥Uncommon pool (tier-0.5 economy may
move). **One additional v6-batch change turns out to matter more than either
— the 10.2 rider's `ref_ironclad` archetype tags (Track V); see the verdict
table.**

## 1. The 12-arm standing battery, paired at n=3000 (seed 20260729)

Recipe of record (the D13 n=3000 standing table's): `python -m
tier05.exp_roster_anchors --runs 3000 --jobs 0 --seed 20260729`, driven
per-arm with one JSON checkpoint each (`review/v6-rebaseline/{v5,v6}-arm-*.json`;
harness body in the appendix). The v6 half **is** the quotable table —
`docs/roster-anchor-v14-v6-2026-08-06.md` (one run serves both, per the
wave-8 dispatch). Stamps: `seed=20260729 runs=3000 RT7/D14/P3/C5` vs
`…/C6`.

`z` is the two-proportion test on the difference. With 36 win/act-1/core
comparisons the Bonferroni bar is **|z| ≥ 3.1**; |z| ≥ 1.96 is nominal only.
Verdicts read the unquarantined columns (win, act-1); core-attainment deltas
are printed but carry the RA-G1 quarantine (interpretation gated on `Q18`),
and the `tto` columns are flagged-not-quarantined per the same rider.

| character | plan | win v5 | win v6 | Δ (pp) | z | act-1 v5 | act-1 v6 | Δ (pp) | z | core v5† | core v6† | Δ (pp)† | z† | tto v5‡ | tto v6‡ | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| klee | demolition | 6.67% | 6.67% | +0.00 | +0.00 | 82.53% | 82.53% | +0.00 | +0.00 | 91.13% | 91.13% | +0.00 | +0.00 | 5.21 | 5.21 | unmoved |
| klee | spark | 4.73% | 4.73% | +0.00 | +0.00 | 79.80% | 79.80% | +0.00 | +0.00 | 62.57% | 62.57% | +0.00 | +0.00 | 8.81 | 8.81 | unmoved |
| klee | reaction | 7.37% | 7.37% | +0.00 | +0.00 | 85.60% | 85.60% | +0.00 | +0.00 | 85.80% | 85.80% | +0.00 | +0.00 | 4.28 | 4.28 | unmoved |
| furina | salon | 11.30% | 11.20% | −0.10 | −0.12 | 60.60% | 60.60% | +0.00 | +0.00 | 63.97% | 63.97% | +0.00 | +0.00 | 5.85 | 5.85 | unmoved |
| furina | spotlight | 2.27% | 2.23% | −0.03 | −0.09 | 59.57% | 59.57% | +0.00 | +0.00 | 82.57% | 82.57% | +0.00 | +0.00 | 3.70 | 3.70 | unmoved |
| furina | fanfare | 2.20% | 2.23% | +0.03 | +0.09 | 58.17% | 58.17% | +0.00 | +0.00 | 43.53% | 43.50% | −0.03 | −0.03 | 7.77 | 7.77 | unmoved |
| kokomi | priest | 2.43% | 2.47% | +0.03 | +0.08 | 42.83% | 42.83% | +0.00 | +0.00 | 48.33% | 48.33% | +0.00 | +0.00 | 6.80 | 6.80 | unmoved |
| kokomi | commander | 3.03% | 3.00% | −0.03 | −0.08 | 51.33% | 51.33% | +0.00 | +0.00 | 28.27% | 28.23% | −0.03 | −0.03 | 8.49 | 8.47 | unmoved |
| kokomi | assist | 0.60% | 0.63% | +0.03 | +0.16 | 35.30% | 35.30% | +0.00 | +0.00 | 9.17% | 9.17% | +0.00 | +0.00 | 9.55 | 9.55 | unmoved |
| ref_ironclad | generic | 11.13% | 7.50% | **−3.63** | **−4.84** | 71.23% | 64.77% | **−6.47** | **−5.37** | 0.00% | 60.73% | +60.73 | +51.15 | — | 7.43 | **MOVED** |
| real_ironclad | generic | 8.53% | 8.53% | +0.00 | +0.00 | 69.87% | 69.87% | +0.00 | +0.00 | 69.23% | 69.23% | +0.00 | +0.00 | 8.33 | 8.33 | unmoved |
| real_silent | generic | 1.70% | 1.70% | +0.00 | +0.00 | 60.90% | 60.90% | +0.00 | +0.00 | 62.47% | 62.47% | +0.00 | +0.00 | 7.37 | 7.37 | unmoved |

† quarantined columns (RA-G1 banner). ‡ flagged-not-quarantined (Q18 rider).

**What actually moved, attributed:**

- **Eleven of twelve arms are statistically unmoved, and five of them
  (klee ×3, real_ironclad, real_silent) are bit-identical between the worlds
  in every printed column.** The expectation
  named in the dispatch — Frozen-touching arms may move; the shop
  conditioning touches the economy — resolves as: **neither α nor the shop
  conditioning produces a detectable outcome shift at n=3000.** The ±1–3-run
  jitter on the Furina/Kokomi arms is the shop-conditioning RNG divergence at
  its measured size (nominal |z| ≤ 0.16).
- **`ref_ironclad` is the one mover, and the cause is the 10.2 rider's tags,
  not α or the shop.** Both its shifts clear the Bonferroni bar (win
  −3.63 pp, z = −4.84; act-1 −6.47 pp, z = −5.37). Mechanism, stated as
  fact: `Card.archetypes` tags on the anchor's package do not only let the
  instrumentation read core attainment (0.00% → 60.73%, the rider's stated
  purpose, confirmed) — they also feed `draft.core_complete` →
  `_core_progress` → `score_offer`'s +3.0 core-advance bonus, so the anchor
  now **drafts differently**. The archived "salon and ref_ironclad
  co-leaders" ordering fact does not survive: under v6 the anchor sits at
  7.50%, below real_ironclad (8.53%). **What that means for the anchor's
  role is a question this sweep surfaces and does not answer** — it rides
  the hand-back, adjacent to (not inside) the Q18 quarantine.

## 2. The archived surfaces, one by one

The v5→v6 stamp put archive banners on seven publishing surfaces (six combat
docs + the shop-channel log). Disposition of each, per the dispatch's rule —
re-run if cheap, swept-by-table, or explicitly not-re-run:

| archived surface | disposition under this sweep |
|---|---|
| `docs/sprint-kokomi-instrument-log-2026-07-29.md` (D13 n=3000 standing table) | **RE-RUN — §1 above is its recipe under v6** (and the v6 half is the quotable successor per R118/10.2). |
| `docs/roster-anchor-v14-2026-08-05.md` (v14 n=1500 seed 11 table) | **SWEPT BY TABLE** — same twelve arms, same cell, larger n, †/‡ quarantine carried. Additionally its n=600/seed-11 sibling recipe was re-run outright (next row) and shows the same verdict pattern. |
| `docs/sprint-sim-hygiene-log-2026-07-29.md` — the 12-arm combat rows | **RE-RUN (cheap)** — `python -m tier05.exp_roster_anchors --runs 600 --jobs 0` in both worlds (`review/v6-rebaseline/{v5,v6}-n600-seed11.txt`). Same story at seed 11: every arm identical between worlds except kokomi/priest ±0.2 pp, kokomi/commander ±0.2 pp (nominal), and **ref_ironclad 11.2% → 8.2%** — the tag effect reproducing on an independent seed. |
| `docs/sprint-sim-hygiene-log-2026-07-29.md` — the 56-op static repricing table | **NOT-RE-RUN, stated:** it is a design-cost ledger discharged by R107(a) (S4-G8), not an outcome measurement; its authority is the ruling, not the world stamp. |
| `docs/sprint-fanfare-compensation-log-2026-07-28.md` | **SWEPT BY TABLE for its standing rows** (its roster-anchor n=600 half is the row above; its fanfare/salon headline arms are furina rows of §1). Its bespoke ablation arms (`exp_fanfare_compensation`, reader-density cells) are **not re-run**: diagnostic cells whose conclusions sit under the C2 escrow (PROVISIONAL), not standing surfaces; re-running them is on demand when the escrow opens. |
| `docs/sprint-fanfare-rework-log-2026-07-28.md` | Same treatment as the row above (its standing table half swept; `exp_pilot_gap` bespoke arms not re-run, same escrow). |
| `docs/furina-strength-findings-2026-07-28.md` | **NOT-RE-RUN, stated:** 150-run bespoke diagnostic cells (`exp_furina_strength`), findings-shaped, never a quotable standing surface; the quotable Furina numbers under v6 are §1's three furina rows. |
| `docs/archive/shop-companion-channel-sprint-log.md` (tier-0.5 shop maths — the surface the Q16 conditioning touched directly) | **RE-RUN (cheap), paired** — `python -m tier05.exp_shop_companion_channel` (500 runs/arm, seed 20260725) in both worlds; §3 below. |

## 3. The shop channel under the Q16 conditioning (paired v5 ↔ v6)

The one v6 change aimed squarely at a tier-0.5 surface. Both worlds, same
recipe, `review/v6-rebaseline/{v5,v6}-shop-channel.txt`:

| reading | v5 (`09e0b56`) | v6 (`745139b`) |
|---|---|---|
| klee/demolition, channel off → on | 5.0% → 5.8% (+0.80 pp) | 5.0% → 5.8% (+0.80 pp) |
| furina/salon, channel off → on | 11.8% → 11.6% (−0.20 pp) | 12.2% → 11.4% (−0.80 pp) |
| kokomi/priest, channel off → on | 4.0% → 2.6% (−1.40 pp) | 4.0% → 2.6% (−1.40 pp) |
| P1 slot-1 buy rate | 52.6% (1563/2973 visits) | 52.6% (1561/2969 visits) |
| P2 mean winrate delta | −0.27 pp | −0.47 pp |
| P3 slot-2 purchases uncommon-share | 97.3% of 619 | 97.3% of 619 |
| slot-2 OFFERED mix (c/u/r) | 1740 / 1085 / 148 | 1738 / 1084 / 147 |
| gold spent on companions | 88000 | 88000 |
| relics bought, off → on | 1008 → 699 (−30.7%) | 1011 → 696 (−31.2%) |
| gold left, off → on | 312695 → 307917 (−1.5%) | 312815 → 307327 (−1.8%) |

**Verdict: unmoved at this instrument's resolution.** The Q16 conditioning
renormalizes slot-1's rarity odds over the ≥Uncommon pool; the channel's
purchase behaviour, buy rate (identical at 52.6%), gold flow and crowd-out
shape are indistinguishable between the worlds — the paired divergence is
±1–4 shop visits of RNG drift and one Furina arm's ±0.4 pp. The July log's
P1/P2 out-of-band findings reproduce under v6 exactly as they stood under
the archive banner (P1 52.6% vs its 10–35% band; P2 negative) — carried as
description for `S4-G10`, which stays open and [USER]-gated.

Numbers are description, not grades: the P1–P3 bands are the 2026-07-25
sprint's own pre-registrations, quoted for continuity; §4.7's close-out
(`S4-G10`) remains open and [USER]-gated, and nothing here re-grades it.

## 4. Verdict — the v6 window CLOSES

- **Sweep verdict: GREEN.** Eleven of twelve standing arms unmoved by the v6
  batch; the shop channel re-measured under the conditioned odds; every
  archived surface either re-run, swept by the table, or explicitly listed
  not-re-run with its reason above. The v6 window's condition — "nothing
  combat/shop is quotable until the re-baseline sweep is green" — is
  satisfied; the quotable standing table is
  `docs/roster-anchor-v14-v6-2026-08-06.md`.
- **The one finding that outlives the sweep:** the `ref_ironclad` anchor
  moved (−3.6 pp win / −6.5 pp act-1, both past Bonferroni) and the cause is
  the 10.2 rider's tags reaching the drafter's scoring, not only the
  instrumentation. Surfaced for the hand-back; not this sweep's to resolve.
- Downstream unblocks, recorded plainly: the **"Clear the Stage" refactor
  swarm** (Document 5) is gated on exactly this sweep being green and may
  now run; the queue's v6 window notes are annotated CLOSED in the same
  commit as this document.

## Appendix — the per-arm harness body (v14 throwaway precedent, committed this time)

```python
"""Per-arm roster-anchor harness (Track M, wave 8).

The v14 precedent's throwaway harness, re-typed: drives ONE arm of
`tier05/exp_roster_anchors.py::ARMS` through `cells.CANONICAL.but(...)` and
reduces the same columns the v14/D13 tables printed -- win, act-1, acts,
deck, fights -- plus `core_complete` attainment and `tto` read off
`RunResult.time_to_online` (set by `tier05/model.py` on the first reward
screen where `draft.core_complete` passes). One JSON checkpoint per arm so
an interruption cannot lose the batch.

    python anchor_arm.py <repo_dir> <arm_index> <runs> <seed> <jobs> <out.json>
"""
import json
import sys


def main() -> int:
    repo, arm_index, runs, seed, jobs, out = sys.argv[1:7]
    sys.path.insert(0, repo)
    from tier05 import cells
    from tier05.exp_roster_anchors import ARMS

    character, archetype = ARMS[int(arm_index)]
    base = cells.CANONICAL.but(name="roster-anchors", runs=int(runs),
                               seed=int(seed), jobs=int(jobs))
    cell = base.but(character=character, archetype=archetype)
    a = cell.arm()
    results = a["results"]
    n = len(results)
    attained = [r for r in results if r.time_to_online is not None]
    row = {
        "character": character,
        "archetype": archetype,
        "stamp": cell.stamp(),
        "n": n,
        "win": a["win"],
        "act1": a["act1"],
        "acts": a["acts"],
        "deck": a["decksize"],
        "fights": a["fights"],
        "core_attain": len(attained) / n if n else 0.0,
        "tto": (sum(r.time_to_online for r in attained) / len(attained)
                if attained else None),
    }
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(row, fh, indent=2)
    print(json.dumps(row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
