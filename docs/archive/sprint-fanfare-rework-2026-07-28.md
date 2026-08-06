> **MOVED 2026-08-06 — Clear the Stage, Track R-B (charter R119, rail 1).**
> Old path: `docs/sprint-fanfare-rework-2026-07-28.md` — new path: `docs/archive/sprint-fanfare-rework-2026-07-28.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Citers repointed in the move commit; see
> `review/stage-clear/rb-move-manifest.tsv`.

# Sprint brief — the Fanfare rework (single-leg + keywords + redesigns, 2026-07-28)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Delegated sprint. Parent findings: `docs/sprint-pilot-gap-log-2026-07-28.md`
and Opus's 38d7769 census. Every direction below is RULED by [USER]
(2026-07-28, post-playtest-3); every number marked PROPOSED returns at
review. This is the first BALANCE pass since playtest 3 — nothing here is
measure-only, and that is why the measurement discipline is strict:
**every table in this sprint runs under the STOKER pilot** (ruled: it
prices the nerf; greedy rows may appear beside it but never alone).

## Track A — single-leg Fanfare (RULED)

Fanfare prints when Encore goes DOWN, never when it goes up. All three
reduction paths qualify — salon upkeep ticks, explicit card spends, and
`absorb_into_encore` (ruled: absorbed Encore is deferred Block that will
never block a future hit, so cashing it is a real cost). `encore_gained`
generation is DELETED in both engines.

Design invariant to pin in a test (both engines): after this change, every
point of damage that gets past Block prints exactly 1 Fanfare — via
absorption if the buffer eats it, via `hp_lost` if HP does. Today absorbed
damage prints 0; that asymmetry is what Track A removes on the damage side.

Measured price at current constants: ~44% of stoker-arm generation
(pilot-gap P4; the priced −16% counterfactual was the OTHER leg — do not
quote it for this change). This is intended. Re-baseline, don't flinch.

## Track B — the Fanfare keywords, and the floor rule becomes visible (RULED)

The invisible FLOOR_PER_POWER rule (every power: floor/cap/current +5,
rares +8, printed nowhere) is REPLACED by printed keywords:

- **`Fanfare Cap +X`** — raises the cap only. Goes on powers generally and
  MAY go on some Exhaust skills (which ones is sheet judgment — PROPOSE a
  short list, do not scatter it).
- **`Fanfare +X`** — the full grant (current, floor and cap together), and
  it is a RARE POWER payoff only.

Spell it "Fanfare Cap", never bare "Cap" (ambiguous with the Salon cap).
The convention is safe because no card grants transient Fanfare directly —
all four generation sources are indirect. PIN THAT WITH A LINT: any sheet
row introducing a direct transient `gain_fanfare`-style op must be a
blocker, or the first such card makes "Fanfare +X" ambiguous forever.

FLOOR_PER_POWER (and the rare variant) retire as engine-side automatics;
the value moves onto the cards that print it. Which powers get `Fanfare
Cap` vs nothing, and every X, are PROPOSED. Note plainly in the log: this
track deletes most floor grants from non-Rares (~4% of her power by the
38d7769 measurement) and STACKS with Track A — the tracks are measured
together, never attributed separately without an ablation arm.

## Track C — three card redesigns + the rename (RULED, numbers PROPOSED)

1. **Slip Backstage** (`graceful_retreat`, fire-rate ~3%): becomes a
   spender — "Convert 5 Encore into 10 Block. Retain." (rate and Retain
   PROPOSED). Under Track A the spend itself prints 5 Fanfare; price it
   knowing that.
2. **The Final Verdict** (fire-rate 0%): becomes the Hyperbeam — "Deal
   damage equal to Fanfare. Fanfare falls to its floor, and the floor
   falls by X." X PROPOSED (start ~30). The floor MAY GO NEGATIVE
   (ruled): the engine must support a negative floor, decay clamps to it
   as today, generation climbs out of the hole. PROPOSED semantics:
   readers clamp — Focus term, riders, `fanfare_at_least` predicates all
   read max(0, fanfare) — so effects shut off rather than invert.
   Negative member ticks on the stage chips would read as a bug; if
   [USER] wants the harsher StS-style inversion it is a one-line flip,
   flag it at review.
3. **Blocking Notes** (fire-rate ~1%): becomes Companion tempo — "Gain 5
   Block. +2 (+3 upgraded) Block per Companion card played this turn."
   Count by `is_companion` on the played card, INCLUDING Guest Star token
   plays (that is the point here — the B2 printed-cost lesson does not
   apply, this is a payoff not a discount). New slope rail; the block-op
   rider lint class from B1 covers it, and the face must carry its
   scaling marker like every converted rider.
4. **Rename `box_seats` → `casting_call`** ("Casting Call", ruled). The
   id, the C# class, the power title, the loc row, and the art_coverage
   out-path all move; run the sheet-projections sweep — a rename is
   exactly the drift that family of hand-maintained projections exists to
   catch. Art is still owed either way; fetch under the new name only.

## Track D — the D6 probe (RULED direction, one card)

ONE card probing the on-demand bow: "the leftmost member takes their bow"
(Defect-evoke analogue). Under Track A it is an Encore-sink AND a bow
trigger, which is why it enters now. Cost, rarity, any rider: PROPOSED.
One card, not a family — it is a probe, and the next playtest is its
measurement.

## Measurement (the gate on the whole sprint)

- Before/after battery under the STOKER (and greedy beside it, labelled):
  winrate, act-1, turns-to-kill/hp-left (won fights only), the full
  Encore economy table, Fanfare source shares. Seeded, stamped, both
  pilots named in stamps.
- Roster re-run for the quotable table — every Furina row is invalidated
  by Track A regardless.
- If the stacked result lands outside a playable band (winrate collapses
  or barely moves), REPORT AND STOP — compensation is a [USER] ruling,
  not a sprint judgment. No compensating buff ships from this brief.

## Gates (house standard)

Full-repo pytest green before/after; regen clean; structural lint (add L3
rows for any new invisible mechanic — the negative floor and the keyword
grants qualify); constant parity re-classified for retired/new constants;
art_lint; build + validate + bite-check; every PROPOSED item and every
judgment call in the log.

## Out of scope

Any compensation buff (report the gap instead), the Spotlight-term
rewrite and stoke-constant sweep (separate pilot-infrastructure pass),
co-op work, the Encore-absorption verification pass ([USER]: "separate
pass, most likely") beyond the invariant test Track A itself pins.
