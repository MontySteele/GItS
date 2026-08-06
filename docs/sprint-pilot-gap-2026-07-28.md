# Sprint brief — the pilot gap (Furina power ceiling, 2026-07-28)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Delegated sprint. MEASURE ONLY: no lever, no card change, no constant change.
Every lever this sprint informs is [USER] red-pen and out of scope.

## Why this sprint exists

Playtest 3 (2026-07-28): ascension 0 beaten effortlessly on the first try;
the Encore runway sat saturated. The sim, on the same build, reports the
OPPOSITE — 49.4% dry upkeeps and a 15% winrate on the salon-assigned arm
(`tier05/exp_salon_ui.py`, seed 20260728). The engines' arithmetic is not in
question (constant parity, both mirrors reviewed); the divergence is in the
PILOT. Furina's kit is a flywheel — every Encore point prints Fanfare twice
(gained and spent), Fanfare feeds the Focus term on member numbers,
Chevalmarin's bow converts the boosted stage back into Encore, and
center_stage pays 2 per card while she holds the Spotlight. A human who
banks Encore, deploys early and keeps the Spotlight runs the wheel; the
greedy pilot demonstrably does not (a stage dry half the time is a stage
nobody is stoking).

Consequence if this is right: every quoted Furina row is a FLOOR, not a
ceiling, and any nerf priced against the current pilot is priced against the
wrong Furina. This sprint builds the pilot that runs the wheel and measures
the gap. THE GAP IS THE DELIVERABLE.

## Pre-registered readings (recorded before any run)

- **R-A** stoker salon winrate rises ≥ +25 points over greedy AND dry rate
  falls below ~25%: the loop is pilot-shaped. The playtest is reproduced in
  sim, and all nerf pricing moves to the stoker arm.
- **R-B** winrate moves < +10 points: the loop is NOT pilot-skill-shaped.
  The co-op seat dynamic becomes the leading hypothesis for the playtest
  power level, and the next sprint instruments that instead.
- **R-C** anything between: report both worlds; the ruling decides.

Winrate may saturate (Opus's floor experiment already hit 100% on the
power-heavy deck): register turns-to-kill and hp-left as the re-cut metrics
UP FRONT, not after saturation is discovered.

## Track 1 — the stoker pilot

A NEW pilot id (`salon_stoker` or similar), built the way `_charge_value`
was for Kokomi: a machinery term in `tier0/pilot/policy.py` gated on a
weight that every other pilot zeroes, plus a weights yaml. The standard
pilots and their weights are UNTOUCHED — pin this by re-running one anchor
arm and diffing its numbers (must be identical; the anchor tables are
byte-frozen).

Behaviors to encode, as WEIGHTED HEURISTICS, not lookahead:

1. **Deploy early**: salon_member deploys score high while the stage is
   below the live cap (`salon_slots`), decaying once full — a full stage
   makes further deploys bow-triggers, which is a different decision.
2. **Fuel the stage**: Encore gains are worth more when the held Encore is
   below ~2 turns of the current upkeep bill (members ×
   `SALON_TICK_ENCORE_COST`) — the runway the D7 ribbon now draws is the
   exact quantity to keep positive.
3. **Hold the stage's Spotlight**: the existing `spotlight` term already
   values designation; the stoker may re-weight it, not rewrite it.
4. **Nothing else**: no new valuation of damage/block — the point is a
   pilot that runs the engine, not a better pilot generally.

**Binding null result to respect** (`policy.py:64`, Kokomi v0.4 W1): a
"bank Charge before playing a Charge reader" rule with this same shape
MEASURED WORSE (priest act-1 33%→27%) and is documented do-not-retry. That
result binds Kokomi's Charge, not Furina's Encore — the economies differ
(Charge is spent by readers; Encore is a per-turn upkeep with a passive
absorb floor). It is cited here as the reason this sprint MEASURES the
stoker instead of assuming it: **a stoker that comes back WORSE than greedy
is a reportable result, not a failed sprint** — it would be strong evidence
for R-B.

## Track 2 — the dual-pilot battery

Re-run under BOTH pilots, same seed, version-stamped, side by side:

- The full Encore battery (`exp_salon_ui` T3 shape): dry / full / surplus /
  held / end / gain-drain, per act.
- Add one derived column: fraction of upkeeps at runway ≥ 5 turns
  (encore ≥ 5 × members × cost) — the direct sim analogue of the saturated
  bar the playtesters SEE, quotable against the next playtest's watch brief.
- The salon-assigned roster rows (3-act, current world). This DOUBLES as
  the owed post-box_seats salon re-measure — stamp it as such, so that debt
  retires with this sprint.
- Fanfare per-source shares (Opus's 38d7769 census instrument) under the
  stoker, next to the greedy shares.

Never quote a stoker row against a greedy row without both labels; from
this sprint on, any Furina table that shows one pilot must say which.

## Track 3 — loop decomposition (log arithmetic only, no engine change)

Under the stoker arm, from the existing event log:

- Fanfare share attributable to the Encore DOUBLE-COUNT: total from
  `encore_gained` + `encore_spent`, and the counterfactual "single-count"
  total (drop the smaller leg). Pure accounting on emitted events.
- center_stage share (was 39.8% under greedy — does the stoker push it up?).

These are the first two nerf candidates' price tags, computed WITHOUT
implementing either. The lever pick is red-pen.

## Gates (house standard)

- Full-repo pytest from root, green, before and after.
- Anchor-arm reproduction diff proving the standard pilot is untouched.
- Version stamps on every table; both-pilot labeling as above.
- Sprint log lists every judgment call made without red-pen.

## Out of scope

Any balance lever (Fanfare sources, Encore economy, member numbers,
FLOOR_PER_POWER — idea 1 included), any card or text change, any co-op
modeling (R-B routes there via a FUTURE brief, not this one), any change to
existing pilots or their weights.
