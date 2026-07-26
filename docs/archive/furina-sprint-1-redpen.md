# Furina Sprint 1 — Red-pen & Rulings (chat → Code)

**Date:** 2026-07-20. Independently verified chat-side: 195 green locally;
spotlight_mult read at source (numbers-only confirmed structural — no
draw/energy path exists); personal-pool exclusion confirmed in rewards.py.
Review verdict: ship-quality sprint; corrections below are small.

## Gate 1 — Statline (report ask 1): CLEARED

Kickoff §2 was ratified by the user earlier this session ("the proposed
Furina doc makes sense as-is"); §2 is unchanged since that sign-off.
**Sheet pass 1 is unblocked.** (User retains veto as always; proceed.)

## Gate 2 — Amendment batch: RECOMMEND RATIFY with two edits

The batch is faithful to the kickoff and rulings. Two corrections before
the user's pen:

1. **Amendment 2's engine note overstates.** It reads "the multiplier is
   plumbed into damage, Block, and element-application counts only" —
   but application counts have no numeric DSL field yet (the report's §5
   says so; the code docstring says so honestly: "when the DSL grows
   one"). Correct the note to: *"enforced structurally for damage and
   Block; element-application counts are covered by the law and will
   join the plumbing when a card first prints a numeric count (documented
   gap in spotlight_mult)."* The LAW text is fine; only the parenthetical
   claims more than exists.
2. **Amendment 6 should carry R8's exemption clause** so the law can't be
   over-applied later: *"Exempt: potions (base-game-priced consumables)
   and relic-scale trickles."* The exemptions are part of the ruling's
   paper trail; the amendment is where future readers will look.

Ratification itself is the user's call per house rule — one word from
them lands the batch as the next dated §10 entry.

## Ruling (a) — Selector cadence does NOT count toward A5. CONFIRMED as implemented.

The Ethereal selector is kit-delivery machinery, same class as the
kit-Burst grant: counting it would award Furina +1 card/turn *by
existing*, structurally inflating A5 toward elite and breaking the
declared shape (A5 deliberately sub-elite at 3.7). The current
implementation (emits `selector_granted`, not `add_card`) is correct and
is now the ruled behavior. **Consequential edit to kickoff §2:** the A5
rationale currently reads "Encore-spend tempo, selector cadence" —
strike "selector cadence" (misleading given this ruling); A5's sources
are Encore-spend tempo and card-level velocity texture.

## Ruling (b) — test_m5 relaxation BLESSED, and the guardrail is codified

0.588 measured against a 0.6 threshold at n=40 (binomial sd ~0.12) is
noise, and the handling was exactly right process: dated comment,
ratified 1000-fight bands untouched and passing, disclosed as a red-pen
ask instead of silently applied. **Codified for DECISIONS:** small-n
heuristic locks may be retuned to measured-noise reality with a dated
comment and disclosure in the next report; ratified bands may NEVER be
retuned this way — they change only by ruling, with archives.

## Ruling (a2) — Spotlight baseline power (user question, answered structurally; measurement pre-registered)

The always-on relic-delivered +50% is ruled **fine to carry into sheet
pass**, with instrumentation: for Furina it roughly cancels the companion
pool's colorless discount (median decks: 2–3 boosted cards ≈ relic-grade
value; committed depth: the archetype working). Bounds: one character at
a time; uncommon-capped authored power underneath; numbers-only means no
turn-economy or amp-stack coupling; integer rounding self-mitigates at
common numbers (5→7 is +40%) and bites full only on big prints.

**Pre-registered for the sheet-pass Tier 0 report: the Spotlight
baseline delta** — median-deck winrate, relic disabled vs enabled. The
passive's worth gets measured in points, not vibes.

**Named watch-items:** the two AoE appliers under 1.5×
(chevreuse_bursting_grenades and guest_neuvillette_judgment, both
7→10 all + element) — the strongest things the baseline creates.

**Knob order, pre-committed now:** if hot, (1) SPOTLIGHT_MULT, then
(2) selector economics (cost-1 to aim / effect begins next turn — the
cost question is separable from the settled frequency question), then
(3) self-rate. **Companion card numbers are never the knob** — they are
priced for every character; the shared pool does not pay for one
character's multiplier.

**Delete-test note (structural, important):** with the mult
relic-sourced, criterion #2 ("deleting her cards guts the deck") now
genuinely bites — her cards must win via payoffs, relic as floor. The
criterion stays unmodified; if boosted companions alone win, that is a
real signal toward card-mediated boosting (the Columbina shape), not a
carve-out case.

## Ruling (c) — Placeholders BLESSED as sweep anchors only

FANFARE_CAP_FRACTION = 0.5 × maxHP and SPOTLIGHT_SELF_MULT = 1.25× are
blessed as sweep starting points. Final values are user picks at sheet
pass, informed by the sweeps; neither number may be cited as design
intent before then. (1.25× = half the partner bonus is a sensible anchor:
the asymmetry is visible but not insulting — the sweep tells us if the
acceptance criterion needs it harsher.)

## Ruling (ask 4) — EP prototype follow-up: DEFERRED to sheet pass, registration held open

Prediction 2 ("duplication separates median from ceiling") remains an
open registration — not failed, not confirmed, unmeasurable by the
scaffolding. Re-test with the real Encore Performance card (drafted
stochastically, duplicating a Spotlighted card) AND with combat coupled,
per the bonus finding: the same sheet-pass experiment should measure the
Guest Star draw-variance value that offer geometry cannot see. The two
re-tests are one experiment; design it that way.

## Commendations for the record

Prune cross-contamination (latent single-character bug caught before it
became a playtest mystery); check-if-solved 4-for-4 (Salon on oz_summon
rails); `applies_element: false` hardening (defensive authoring, unasked);
prediction 2 declared inconclusive-by-construction rather than
prototype-laundered; the draw-variance bonus finding reframing the Guest
Star suite's purpose one pass before we'd have designed for the wrong
problem.

## Sheet pass 1 is now fully unblocked

Gates cleared, placeholders anchored, registrations held honest. Scope
per kickoff: the ~75-card sheet, Burst design + meter, Salon grammar
(~20 lines on existing rails), Encore Performance + Guest Star
generators, Fanfare payoffs/uncappers, upgrades file, and the coupled
achievability/draw-variance re-run. Selector pilot weights ride along.
