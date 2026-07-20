# Klee Errata Pass — Report (Frozen v2 + closeout of the ratification)

**Date:** 2026-07-19. **Input:** pass3-ratification.md + furina-predesign-notes.md Part 1. 107 tests (1 xfail, see the ask). The directive's re-run is done; **v0.1 is frozen and regression-locked** — with one pre-registered deviation coming back to you, per your own clause.

## Implemented

- **Frozen v2** (principles v1.5 §2.2): non-boss Frozen = next action −50% (`FROZEN_DAMAGE_MULT`), first Attack hit Shatters (`SHATTER_DAMAGE = 6`, removes Frozen; direct HP like splash; a hit cannot shatter the freeze it just applied). Boss path (Vuln 2) untouched.
- **`control_uptime` / SUPPORT_CARRY** (§2.2a): companion-sourced negation per enemy action (frozen attack = 0.5), flag on won fights >40%. Provenance tracked on the freeze-triggering card.
- **Companion errata v0.3.1**: Barbara/Bennett heals Exhaust — loaded, tested. The A4 barbara probe still clears its raw floor (2 melodies + idol ≈ 12 healing/fight even played once each), so no recalibration was needed.
- **Ratified bands codified**: `winrate_bands` in klee.yaml (demo 85–97 / spark 45–65 / reaction ≥35; gauntlet ≥75), enforced in `score_character` **only at ≥1000 fights** per your process fix, and regression-locked in tests at 1000/seed 42. The v0.1 median scorecard is snapshot-locked too (±0.3).
- **Process fix acknowledged** (verbatim lists in handoff docs) — no action needed repo-side; noting it so the log shows both sides adopted it.

## The re-run (reaction grid at 1000 fights, Frozen v2)

Your predictions, checked:

| Prediction | Result |
|---|---|
| boss 58% unchanged | **56.2%** ✓ (57.8 at 500 was the same number in noise) |
| elite/punisher winrates drop | **NULL — and instructive, see below** |
| floors hold via Shatter + Vuln | tank_boss 56.2 ≥ 35 ✓, gauntlet 92.5 ≥ 75 ✓ — **Shatter knob untouched** |

**The null:** punisher pre-errata hpΔ −38.5 → post −38.6; identical everywhere. Cause, measured: solo Frozen fires **0.01×/fight** on punisher — Klee's own pyro cadence eats every hydro/cryo aura (overload 2.4, vaporize 1.7, melt 0.8 per fight) before a freeze pair can meet. The stun you unpriced was never load-bearing *solo*; reaction's elite lines were earned by damage, not control. `control_uptime` reads ~0.1% across the grid. So the errata costs Klee nothing at Tier 0 — the mispricing was always a co-op/ecosystem exposure (hydro partner + cryo companions), which is exactly where the §2.2a pricing rule and the detector now stand guard. TIER2-VALIDATE marker extended to control_uptime in co-op.

**Median identity after errata:** A1 4.19 / A2 3.95 / A3 2.26 / A4 0.5 / A5 3.04 / A6 3.59 / A7 2.35 — every axis within 0.05 of the pass-3 scorecard. All constraints pass. Spark tank_boss sits at **~56% in its new 45–65 band** ✓.

## The one ask — demolition tank_boss, your pre-registered clause fired

You wrote: *"the demolition band widens to 85–97. If it exceeds 97 at 1000 fights, that's real and comes back."* At 1000 fights: **97.4%** (SE ≈ 0.5pt at this winrate — above the cap by slightly less than one SE, but I'm honoring the letter of the clause rather than re-litigating noise).

Empirical footing for the ruling, pre-measured:
- **Option A — accept 97.4** (boss specialist means specialist; the deviation is <1 SE over a cap you set from a 500-fight read of 96.8).
- **Option B — arm the dormant splash proc-cap at 3**: tank_boss → **96.5%** (in band), swarm 100% and gauntlet 99.4% unharmed. One constant flip; the armed behavior has been test-locked since pass 3. I did NOT arm it — its round-3 trigger condition was demolition median-A2 drag, not winrate, and re-purposing a knob without a ruling is how governors stop meaning things.
- The band test is `xfail(strict)` pointing at this report, so the suite is green and will *fail loudly the moment the ruling lands and the number moves* — flip the test with the ruling.

## Status

v0.1 scorecard: **frozen and regression-locked** (median snapshot + winrate bands + armed-knob behavior). Tier 0 is closed for Klee modulo the one-line demolition ruling above, which does not block anything downstream. Proceeding to **Tier 0.5 M5** per the sequencing recommendation.
