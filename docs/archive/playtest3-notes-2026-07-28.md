> **MOVED 2026-08-06 — Clear the Stage, Track R-B (charter R119, rail 1).**
> Old path: `docs/playtest3-notes-2026-07-28.md` — new path: `docs/archive/playtest3-notes-2026-07-28.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Citers repointed in the move commit; see
> `review/stage-clear/rb-move-manifest.tsv`.

# Playtest 3 notes — Furina, ascension 0 (2026-07-28)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Build `0.2-230` (the merged salon-UI sprint). Solo, salon build heavy on
powers, picking up Fanfare scaling cards late.

This file is RAW INPUT for the next triage, not a triage. Nothing here is
ruled and nothing here has been acted on except the one defect in §2.

---

## The headline: she is too strong

> "Furina is quite strong now and trivially crushed ascension 0. I usually
> had 80-90 Fanfare per turn by the end, could play through 6-7 cards per
> turn with all the cost reducers active, and had no trouble slaughtering
> everything."

**Not diagnosed, not fixed.** What follows is the shape of a hypothesis for
whoever picks this up, and it should be measured before it is believed.

The Fanfare number is the part that stands out, because Fanfare is not just a
resource in a salon deck — it is a MULTIPLIER on the whole stage.
`SALON_FOCUS_PER = 10` gives every member number +1 per 10 Fanfare held, with
no cap on the term. At 80-90 held that is **+8 or +9 on every tick and every
bow**, before Grand Salon, and it applies to three-to-five members every turn.
A Crabaletta printed at 6 is ticking for 14-15.

Three threads worth pulling, in the order they can be measured:

1. **Is the Focus term the engine?** It is the only multiplicative-feeling
   term in the kit and it is uncapped. A sweep on `SALON_FOCUS_PER` is cheap.
2. **Did the cost reducers make the turn unbounded?** "6-7 cards per turn"
   is a velocity claim, and velocity times a per-member slope is the
   compounding shape. The A13/A14 slopes shipped this cycle; they are
   per-member on a stage that A12 also made bigger.
3. **`FANFARE_CAP_FRACTION` is 0.5 × maxHP.** 80-90 held implies a large
   maximum, so the cap may not be binding late — which is worth checking
   against the pass-4 saturation work rather than re-deriving.

**Caution on the sim's opinion.** Track 3 of the salon UI sprint measured the
Encore economy as STARVED where the previous playtest read it as saturated;
that divergence is still unruled. A tier 0.5 sweep that says Furina is fine
should not overrule a playtest that says she trivially crushed A0 — the same
way round as before.

---

## Answers to the four playtest questions

**1. Hover targets vs targeting arrows — NOT ANSWERED.** The question did not
reach the playtest. It is still open: each occupied slot carries an invisible
`Control` inside Furina's own bounds, and whether it interferes with picking
an attack target is the one thing the sprint brief flagged and the build
cannot answer for itself.

**2. Stage at cap 4-5 — DEFECT, FIXED.**

> "Box Seats did add new salon members, but the salon pictures stacked over
> each other and became unreadable."

The mechanic worked; the rendering did not. Cause was older than the cap: the
member art is cut at 144px tall and ~121-129 wide and was drawn at **1:1** on
a 62px pitch, so members have always overlapped by about half. That is
missed-requirements sec.4.3, which shipped as a knowingly recorded gap with a
test asserting it. A12 made the pitch as tight as 39.5px and turned "ugly"
into "unreadable".

Fixed by fitting the art to the slot at runtime, capped at 0.5 — exactly half
the master and exactly the 72px beam — so a three-member stage is a clean 2x
downscale and only a RAISED cap goes below it. The pool/beam/ghost
decorations are squashed horizontally on the same rule, because the pool is
what carries the accent hue and overlapping pools blur the identity signal
the hue exists to provide.

The old house rule of "pre-scaled art, no runtime minification" is amended:
the pitch is a function of a per-player stat now, so no single cut size can
serve it. The gap test was replaced with the arithmetic check it always said
it should become.

**3. Runway ribbon — PASS.** "Yes, that worked."

**4. Exhaust legibility (B3) — PASS.** "All cards tagged Exhaust in the list
did Exhaust." B3's in-game eyeball is closed; it was owed since batch 1.

---

## What this leaves open

- **The strength problem**, undiagnosed and unruled. Above.
- **Hover vs targeting arrows**, unanswered for a second cycle.
- **The D8 Encore divergence**, unruled — and now with a second data point
  that the sim and the table disagree about how strong this kit is.
- Two dead riders found by the D4 instrument (`the_final_verdict` 0/298,
  `blocking_notes` 31/2471) that nobody has ruled on.
