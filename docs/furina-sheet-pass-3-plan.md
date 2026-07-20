# Furina Sheet Pass 3 — Plan (pre-registered)

**Date:** 2026-07-20. **Authorized:** R32 (scope) + R33 (window zero),
furina-pass3-rulings.md. **Governing:** R16–R22, R26, R29–R33,
DECISIONS 69–88, kickoff v0.1, principles v1.10.
**Environment:** CONSTANTS_VERSION 2, DRAFTER_VERSION 2,
RUNTEMPLATE_VERSION 2, A6_INSTRUMENT_VERSION 2. SPOTLIGHT_BASE_MULT is
a PLACEHOLDER at 1.5 (R33 veto — see constants comment).
Seed 20260720. Registered BEFORE running; null results binding.
Experiments: tier05/exp_furina_pass3.py. Forced/dose cells are
diagnostics feeding rulings (R14): no acceptance targets on them.

Sequencing is R32's: **W0 runs first and is read before any design
window opens** — its outcome (rate asymmetry and/or selector v3) is
the world the windows measure in. Each window is one variable; A4/A6
re-measured after each.

## W0 — Ceiling designation experiment (R33; pre-registered verbatim)

**Question registered:** is outward (companion) designation EVER
value-rational under CURRENT content at ceiling depth, and at what
rate (SPOTLIGHT_BASE_MULT)? Both directions publishable: a clean "no"
means the ceiling fantasy needs CONTENT (the user's "director
offstage" shelf item), not tuning.

- **World:** fixed committed decks, E4-style. Depth-5 arm =
  starter + spotlight_weighted package (full Chevreuse kit ×4 +
  lynette_box_trick). Depth-3 slope arm = same minus one
  chevreuse_interdiction_fire and chevreuse_bursting_grenades,
  replaced by courtroom_drama + macaron_break (non-machinery Furina
  glue; keeps deck size and the machinery variable fixed).
- **Arms:** FORCED-self vs FORCED-companion designation via the
  engine's R33 oracle switch (heuristic v2 bypassed, not trusted; the
  companion arm has no self fallback).
- **Sweep:** SPOTLIGHT_BASE_MULT ∈ {1.25, 1.5} on the forced-companion
  arms. Forced-self arms run once per depth (the knob is unread there
  — asserted, see below). 6 cells × 4 encounters × 1000 fights.
- **Exercise-counter law applied (first use):** every cell publishes
  its SPOTLIGHT_BASE_MULT read count. REGISTERED VALIDITY GATE:
  forced-companion cells must show reads > 0 and forced-self cells
  reads == 0, else the cell is INVALID and the experiment stops — no
  silent E1 repeat.
- **Registered reading:** per-encounter winrate deltas
  (companion − self) published in full. Summary verdict per
  (depth, mult) dose: outward designation is VALUE-RATIONAL at that
  dose iff the battery-mean winrate delta ≥ 0. Any single encounter
  where companion beats self by ≥ 2pt is flagged as a NICHE even
  under a negative mean (content signal, not a verdict).
- **Registered consequences:** if any dose is value-rational →
  selector v3 (value-aware) is justified as a follow-on, built under
  full instrument discipline (banner, archive table, anchor — the A6
  v2 pattern). If a clean "no" everywhere → no selector work; the
  aim-outward half needs content; the shelf item goes to the user.
  Either way W1–W3 proceed (they are sheet work, not selector work).

## W1 — standing_ovation FLIP: generator → spend-payoff (R32.1)

The A4 lever AND the identity fix (R31 root cause: spotlight has ZERO
Encore spend lines; ovation-as-generator pools everything into
absorption → A4 8.0).

- **Shape (numbers PROPOSED, red-pen ratifies):** standing_ovation
  becomes "whenever you SPEND Encore, Spotlighted numbers +X% this
  turn (percentage points through the existing
  spotlight_mult_bonus_turn pipe — §2.2a numbers-only inherited)."
  The spotlight deck gains its first spend lines so the trigger is
  live (encore_cost / spend_encore on existing spotlight cards —
  smallest set that makes the flip real, each edit listed in the
  report).
- **Registered rule:** the flip SUCCEEDS if spotlight_weighted A4
  moves DOWN from 8.0 toward the 4.3 declaration (≤ 6.0 at minimum)
  while the §8 criterion-2 delete-test still passes on all four
  encounters. The recorded FALLBACK (rate-tune spotlight_encore 2→1
  no-stack) is used ONLY if the flip fails both directions; prefer
  the flip.

## W2 — Rider swap on shared_billing + stage_lights (R32.2)

Block riders → hydro-application / debuff riders: A4 down and A6 up
in one edit. **A3 rehoming check is part of the window:** A3 median
sits 2.4 vs ~2.5 target; the stripped block gets a home in
salon/generic glue or the axis dips — A3 re-measured in-window.
Freeze-cell steering applies to the NEW riders: nothing routes
through {undercurrent, rain_of_roses, guest_neuvillette_judgment}.

## W3 — Salon + spotlight A6 utility lift (R32.3)

The two-deck work the median math demands (v2 per-deck: salon 3.42 /
spotlight 3.31 / fanfare 3.24; the median is the MIDDLE deck, so A6
4.2 requires at least TWO decks ≥ 4.2). Levers: application uptime
(the 0.2 component), debuff texture (0.3), AoE (0.5) — in salon and
spotlight ONLY. **HARD constraint:** no new application texture
through the freeze cell; fix-by-buffing-other-routes, never freeze
fuel. Fanfare's saturated A4 10.0 and its 12.7% uptime are NOTED,
NOT IN SCOPE (R32.4 — no touch without a new ruling).

## Battery (after the windows)

1. **FANFARE_CAP re-check** {0.25, 0.5, 0.75} — E2's confirmation is
   only valid pre-flip (Fanfare counts Encore gained AND spent; W1
   changes both). Registered rule unchanged: ratified 0.5 stays
   unless fanfare punisher leaves [10%, 55%].
2. **Full character report** at 1000 fights: success for the pass =
   A4 4.3-shaped at median, A6 4.2 at median, A3 held ~2.5, A1/A7
   weaknesses intact, curve exponents sane, all RATIFIED bands hold
   (salon's remain law; spotlight A2 4.3 re-checked in the new
   world).
3. **Klee world verify** (shared engine touched: encore-spend hooks).
4. **Winrate band ratification stays DEFERRED** (R32 binding note):
   pass-3 report re-proposes; the user ratifies post-measurement.

## Non-goals

Fanfare sustain saturation (R32.4). Selector v3 (behind W0's verdict,
own discipline if built). Closing any OPEN [USER] item (EP
disposition, spotlight-rows red-pen, cap thumbs-up, naming/lore pass
— the rulings doc lists them; only the user closes them).
