> **MOVED 2026-08-06 — Clear the Stage, Track R-B (charter R119, rail 1).**
> Old path: `docs/sprint-fanfare-compensation-2026-07-28.md` — new path: `docs/archive/sprint-fanfare-compensation-2026-07-28.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Citers repointed in the move commit; see
> `review/stage-clear/rb-move-manifest.tsv`.

# Sprint brief — Fanfare compensation (self-payoffs + cap keyword everywhere, 2026-07-28)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Delegated sprint. Parent: `docs/sprint-fanfare-rework-2026-07-28.md` and its
log — the rework landed as ruled (a197294) and left two out-of-band numbers
that this pass exists to repair: the fanfare archetype at **0.5%** (below the
2.0% roster floor) and act-1 clear at **51.7%**. Both are REGISTERED here as
the before-numbers; the sprint's success question is whether they move, not
whether some other number looks nice.

Every card change ships with PROPOSED numbers unless marked RULED. All
tables run under the STOKER, greedy beside it, both labelled (standing rule).

## The diagnosis this brief is built on (Fable audit, 2026-07-28)

15 of the archetype's 28 cards read the meter, but the readers cluster at
rare (8 of 10) while the commons are almost uniformly blind Encore
generators. Before single-leg, every blind generator was IMPLICITLY a
Fanfare card — casting Hearts Swelling printed 7 on the way in. Track A
severed that: they are now batteries whose meter payoff is deferred until
the Encore leaves, and Encore held at combat end pays nothing. The
archetype kept its rare payoffs and lost its common-tier engine; a drafted
deck spends acts 1–2 generating a resource it has no reader density for.
That is the 0.5% and the act-1 widening in one sentence. The repair is
therefore reader density at the BOTTOM of the curve, not bigger rares.

## Track 1 — Fanfare Cap +X on ALL powers (RULED, reverses the short list)

[USER] ruling: **every Power prints `Fanfare Cap +X`; only a select few
print `Fanfare +X`** (the full floor grant). The rework's short-list
resolution (4 archon-register carriers, 12 Powers granting nothing) is
REVERSED — restore the keyword to all Powers, at values PROPOSED per card.
The register-lint R2 selector logic that produced the short list needs
re-deriving or relaxing to match; do not leave the lint fighting the ruling.

Known and accepted: the cap binds <1% of reads at current constants, so
this is mostly legibility/flavor today. State it in the log, don't tune
around it. `lasting_impression` remains the card most hurt by cap inertness
— if a small repricing of its line falls out naturally, PROPOSE it; do not
redesign it here.

## Track 2 — reader density at common/uncommon (RULED direction, numbers PROPOSED)

1. **2–3 NEW common cards** with low-slope Fanfare riders (the `1_per_4`
   tier — commons must not outscale the rares' `1_per_2`). At least one
   damage rider and one block rider, so both post-B1 rails carry archetype
   weight at common. Names/costs/numbers PROPOSED; register assignments
   must pass the register lint.
2. **Convert blind generators to dual-purpose** rather than deleting them:
   - `suffering_for_art` — thematically the flagship: it already
     self-damages and HP loss prints the meter. Give it a small Fanfare
     payoff clause (PROPOSED shape: a low-slope rider or a
     `fanfare_at_least` kicker), keeping the 0-cost identity.
   - `hearts_swelling` — the big battery gains a small reader clause so
     the 7 Encore it banks has a same-card reason to exist (PROPOSED).
   - Do NOT convert more than these two without flagging: mass conversion
     is a different sprint, and blind glue is allowed to exist.
3. **A common convert/spender in the fanfare register**: the Slip
   Backstage shape ("Convert N Encore into M Block") at common rarity —
   under single-leg the spend itself prints N Fanfare, which makes a
   convert card the archetype's cleanest act-1 engine piece. Numbers
   PROPOSED; watch distinctness vs `graceful_retreat` itself
   (card_distinctness_report — same shape at two rarities needs different
   rates or a second clause).
4. **The act-1 lever: the basic.** `aria_of_recompense` (starter, blind
   5-Encore battery) gets the most surgical fix available — PROPOSE ONE
   of: a small low-slope rider, or a tiny `Fanfare +X` grant (X ~2) as a
   front-load. Every deck starts with it, which is what makes it the
   act-1 lever; it is also what makes it dangerous — flag its number
   loudly for red-pen.

## Track 3 — re-measure (the gate)

- Full battery under stoker + greedy, before/after, same seed: the two
  registered numbers (fanfare 0.5%, act-1 51.7%) plus salon/generic arms
  to confirm the compensation does not leak sideways — salon landing on
  the real_ironclad anchor was ruled acceptable and should NOT move much.
- Fanfare source shares + reader fire-rates on every new/changed card
  (the conditional telemetry already exists) — a new reader that fires
  <10% is D4's mistake re-shipped; report it, don't tune it silently.
- Roster re-run for the quotable table.
- If the fanfare arm still sits below the 2.0% floor after this pass,
  REPORT AND STOP — a second round is a ruling, not a judgment call.

## Also recorded (RULED, no action)

- Negative-floor readers CLAMP; the StS inversion stays a one-line flip,
  revisit only if The Final Verdict misbehaves in play.
- The Verdict×Unheard-Confession interaction (crash pays flat-per-event
  block) is verified fine as-is.

## Gates (house standard)

Full-repo pytest green before/after; regen clean; structural lint (L3 rows
for any new invisible mechanic); register lint reconciled with Track 1;
constant parity; art_lint (new commons enter the art queue — casting_call
and take_your_bow are already owed); build + validate + bite-check; every
PROPOSED number and judgment call in the log.

## Out of scope

Any rare-tier redesign, mass conversion of blind glue beyond the two named
cards, the Spotlight-term rewrite and stoke sweep (still parked), the +9
phantom-count hunt (separate small task), co-op work, any second
compensation round (report-and-stop).
