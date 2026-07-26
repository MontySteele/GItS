# Furina pass 3 — chat ratifications + design-pass scope (2026-07-20)

**Provenance:** written in chat with the user after the pass-2 wrap; every
ruling below is USER-RATIFIED in conversation. This is v2 of the chat
notes — v1 recommended ratifying the SPOTLIGHT_BASE_MULT record and
treated "rational self-Spotlight" as settled; both were wrong (user
catch). The correction is on record in R33, banner-style, per the M7
precedent. v2 fully supersedes v1.

**RENUMBERING NOTE (cross-session convention):** the chat draft numbered
these rulings R28–R32 on the assumption that R28 was the next free
number. It is not — tier0/DECISIONS.md holds R28 as the pass-2 GO
(entry 79 block). Per the convention ("if a collision exists, renumber
and note it"), every ruling here is shifted +1:

| chat draft | this doc / DECISIONS |
|---|---|
| R28 | **R29** |
| R29 | **R30** |
| R30 | **R31** |
| R31 | **R32** |
| R32 | **R33** |

All internal references below use the renumbered ids.

---

## R29 — DECISIONS 75 veto window CLOSED (with one amendment)

User ratifies (a) commanding_gaze KEPT (Spooked! parity), (b) blood
4→6 (kickoff §4 + self-subsidy argument; upgrade never lowers it),
(c) house_call KEPT at 5+3 (threshold-family grammar, A7 tax pricing).

(d) is AMENDED, not ratified: strike "Naming/lore audit CLEARED" from
the DECISIONS 75 record. Replace with: "audit prepared; user eyes-on
naming/lore pass owed before ship." A document citing another document
cannot close a [USER] gate (the v1.7 lesson). The pass itself is the
closure; nothing else is.

## R30 — star_of_the_show errata RATIFIED

The +3/3 re-encoding is ratified as what the sheet always said. The
convention is codified with it: max_stacks counts POWER UNITS;
single-application rows encode max_stacks == amount; the upgrade
applier bumps max_stacks alongside amount. The user has seen the
corrected pass-1 numbers (self_carry punisher 38.0% → 49.3%, same
constants) and accepts that no sweep is invalidated.

## R31 — Instrument gaps: PATH 2. The declarations are DEFENDED.

Report asks 1 and 2 are resolved together, against the
accept-the-world option. User ruling, verbatim intent: "good at
surviving" is a valid archetype but not the whole identity — it's
boring, and it clashes with the spend-buffer-for-power intention of
Encore/Fanfare. The two-elite-axes identity (A4 4.3, A6 4.2) STANDS.
The R16 world's measurements are design defects to fix, not a new
shape to ratify.

Root cause, established from the sheet (recorded — it drives the
scope):

- standing_ovation is a generator in the one archetype with no sinks.
  Encore spend-line census: fanfare 7, salon 2, **spotlight 0**. Under
  self-Spotlight (structurally guaranteed — see R33, which corrects
  v1's "rational, load-bearing" framing), "whenever you play a
  Spotlighted card" ≈ "whenever you play a card" — 2–4 Encore per
  card, spend rate zero, everything pools into absorption, and the
  harness (correctly, kickoff binding note) credits absorption to A4.
  That is the 8.0.
- Secondary: the R16 re-author gave the spotlight glue commons BLOCK
  riders (shared_billing 4, stage_lights 3) — the boost cards
  themselves are defensive texture.
- A6 median math (why "just fix fanfare" cannot work): v2 per-deck is
  salon 3.42 / spotlight 3.31 / fanfare 3.24; the statistic is the
  MIDDLE deck, so lifting fanfare alone caps the median at 3.42.
  Reaching 4.2 requires at least TWO decks ≥ 4.2.

## R33 — SPOTLIGHT_BASE_MULT 1.0 record VETOED (errata-grade); the self-Spotlight finding is RE-SCOPED; ceiling experiment pre-registered

User catch (their 6th, and the first to catch a MEASUREMENT record
rather than a card or a law): "every deck self-Spotlights" was
presented (by pass 2's E1, and by chat-Claude, who wrongly called the
knob record "genuinely free") as a discovered rational strategy. It is
not. It is a foregone conclusion, three ways at once:

1. **Selector heuristic v2 cannot pick a companion.** It designates
   the character with the most tagged cards; ~20+ Furina cards vs
   3–5-card companion kits (drafted median 2, ceiling ~5) makes the
   companion branch unreachable. v2 was an overcorrection from v1's
   companions-always rule (which WAS measured harmful: a 1-card guest
   hijacked a 20-card kit, halving Ovation throughput). The
   honest-gaps line already admitted it: "raw depth, not value."
2. **E1 was circular.** The {1.0, 1.25} sweep ran at committed-median
   under this selector, where the companion rate never enters any
   computation — identical cells are guaranteed, not informative. E1
   is hereby RE-SCOPED to what it proved: a valid median-depth null.
   The "dead knob" generalization and the recorded 1.0 are struck.
   Never summarize E1 as "the knob is dead."
3. **Recording 1.0 inverted a ratified lever.** Pass-1 geometry:
   companion ×1.5 > self ×1.25, with the reduced self rate PROVEN
   load-bearing (R17: "the reduced rate IS the anti-self-buff lever").
   At base 1.0, self > companion — outward designation is worthless at
   the base layer and the degenerate play becomes optimal BY CONSTANT,
   not by content.

Stakes named: self-Spotlight was kickoff-declared as the FALLBACK;
companion-directed play is the draft-gated ceiling and the entire
Columbina driver grammar Furina exists to beta-test. Pass 2 proved
card-mediated empowerment aimed at SELF; the aim-outward half is
unproven. Pass 1 filed this as a red-pen framing question; pass 2
hardened it into "load-bearing." That hardening is reverted.

**Execution items:**

- tier0/constants.py: SPOTLIGHT_BASE_MULT returns to PLACEHOLDER
  status; rewrite the comment to carry the re-scoped E1 record and
  cite R33. The DECISIONS 79 entry gets a correction note (M7 banner
  precedent).
- Lint candidate (catch → lint, per the standing pattern): dead-knob
  claims require an exercise counter. A sweep that concludes "no
  effect" must show the swept constant was READ ≥ once per cell
  (instrument-side counter). E1 would have failed this lint loudly.

**Pre-registered ceiling experiment (WINDOW ZERO of pass 3 — runs
before all other windows):**

- World: fixed deep-committed decks, E4-style (full Chevreuse kit +
  Lynette; depth 5). Optionally a depth-3 arm for the slope.
- Arms: FORCED-self designation vs FORCED-companion designation
  (oracle-style direct comparison; the v2 heuristic is bypassed, not
  trusted).
- Sweep: SPOTLIGHT_BASE_MULT ∈ {1.25, 1.5} on the forced-companion
  arm (1.5 restores the pass-1 asymmetry candidate).
- Question registered: is outward designation EVER value-rational
  under current content at ceiling depth, and at what rate? Both
  directions are publishable: a clean "no" means the ceiling fantasy
  needs CONTENT (a unique aim-outward payoff — "director offstage"
  shape, user's shelf), not tuning.
- Forced arms are diagnostics feeding a ruling — R14 applies; no
  acceptance targets on dose cells.

**Follow-on (behind window zero, not before):** selector v3
(value-aware or reachable-threshold), treated as an INSTRUMENT change
with full discontinuity discipline — banner, archive table, anchor —
exactly like A6 v2. Content-side "director offstage" hook stays on the
user's shelf pending window-zero results.

## R32 — Pass-3 design-pass SCOPE (user-approved plan; RESEQUENCED under R33)

Window zero (the R33 ceiling experiment) runs FIRST: the items below
all measure against a world where designation behavior is load-bearing
background, and window zero may change that world (selector v3 and/or
a restored rate asymmetry). Each subsequent item is its own
measurement window (one variable; dose cells stay diagnostics per
R14):

1. **standing_ovation FLIP: generator → spend-payoff.** Target shape:
   rewards SPENDING Encore with Spotlighted power (e.g. "whenever you
   spend Encore, Spotlighted +X this turn"), and/or spotlight payoffs
   gain encore_cost lines. Spotlight becomes a PULLER from the buffer
   the salon/fanfare build. This is the A4 lever AND the identity fix
   — prefer it over rate-tuning (2→1 no-stack is recorded as fallback
   only). NOTE post-R33: if window zero makes outward aim rational,
   the trigger density of anything keyed to "Spotlighted card played"
   changes — measure in the post-window-zero world only.
2. **Rider swap on shared_billing + stage_lights:** block riders →
   hydro-application / debuff riders. Moves A4 down and A6 up in one
   edit. A3 rehoming check is part of the window: A3 median sits 2.4
   vs ~2.5 target; stripped block needs a home in salon/generic glue
   or the axis dips.
3. **Salon + spotlight utility lift** (the two-deck A6 work the median
   math demands). Freeze-cell steering is a hard constraint: new
   application texture must not route through the named hydro+cryo
   cell (undercurrent, rain_of_roses, guest_neuvillette_judgment);
   fix-by-buffing-other-routes, never freeze fuel.
4. **Fanfare sustain saturation (10.0, pre-R16) is NOTED, NOT IN
   SCOPE.** Flagged to the user as a possible re-open; they did not
   take the expansion. Do not touch it without a new ruling.

**Interaction notes (binding on the windows):**

- The flip changes Encore flux, and Fanfare generation counts Encore
  gained AND spent — so E2's FANFARE_CAP 0.5 confirmation is only
  valid for the pre-flip world. Schedule a cap re-check inside the
  pass-3 battery; do not carry E2 forward silently.
- The kickoff harness note stands: Encore absorption credits A4,
  never A3. No instrument-side relief; the fix is content-side.
- §7 winrate band proposals are for the R16 world and that world is
  about to change again (twice, counting window zero): band
  ratification is DEFERRED to post-pass-3 measurement. Salon's
  already-ratified bands remain law.
- A4/A6 re-measured after each window; success criterion for the pass
  is the declared statline (A4 4.3-shaped at median, A6 4.2 at
  median) with A3 held and A1/A7 weaknesses intact.

## OPEN [USER] ITEMS (not closed by this doc — only the user closes them)

- Report ask 3: registration (i) disposition + Encore Performance
  re-cost. Chat recommendation on the table (close as
  measured-negative now, fold the re-cost into pass-3 windows) — NOT
  yet user-confirmed; the spotlight catch interrupted the closeout.
- Report ask 4: red-pen of the re-authored spotlight rows — chat
  recommendation: defer into pass 3 (three of the cards are being
  re-authored again anyway). NOT yet user-confirmed.
- FANFARE_CAP 0.5 thumbs-up — NOT yet user-confirmed (and now carries
  the scheduled pass-3 re-check regardless).
- SPOTLIGHT_BASE_MULT: no longer a thumbs-up item — VETOED per R33.
- The eyes-on naming/lore pass (R29d) — before ship, no substitute.
