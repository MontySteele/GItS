# Sprint log — Salon UI legibility + measurement (2026-07-28)

Brief: `docs/sprint-salon-ui-2026-07-28.md`. Parent: `docs/playtest2-triage-2026-07-28.md` (Group 3).
All four tracks landed. Both hard sequencing constraints were already
satisfied when the sprint opened: B1–B5 shipped in the bug-fix batch and A12
shipped in the adjustment batch, so Track 1 could read a real per-player cap
instead of building an accessor against a constant.

**Everything visual in Tracks 1 and 2 is UNVERIFIED.** No Godot run is
available here, the mod has no C# test project, and co-op has no sim
backstop. The build compiles, the pck packs the scene and the glyphs, the
bite-check arms, and the structural claims are pinned by tests — but whether
the stage LOOKS right, and whether the new hover targets fight targeting
arrows or enemy intents, is a next-playtest question. Nothing below should be
read as "verified in game".

---

## Track 1 — Salon stage legibility (D1)

**§1 Accent hue per member.** The underglow pool and the chip edge carry
rose / gold / aqua (the mockup's #f0708c / #e8bb52 / #5fe0d2). Sprites are
untouched, per the ruling. Duplicates render as duplicate hues — the
slot-index Funnel Contract §1 is unchanged, so three Ushers are three gold
pools. Dry keeps the existing grey: "these numbers are not happening this
turn" outranks "this one is a Crabaletta".

**§2 Live tick chip.** Glyph + the member's current per-turn tick, under each
occupied member. The number comes from `SalonMemberPower.TickValue`, which is
now the expression the UPKEEP resolves through as well — the two are one
piece of code, not two that agree. A buffed value (Grand Salon, or the
Fanfare Focus term) renders in the game's modified-number green.

The glyphs are new procedural art: `tools/gen_salon_glyphs.py` draws a sword,
a shield and a droplet as white masters, registered in `art_lint`'s
`GENERATOR_OWNED` so no plan row can claim those out-paths. White because the
bridge tints them per member through `Modulate`, so one file per ROLE serves
every hue and the dry state greys the glyph by the same path that greys the
sprite.

**§3 No bow marker**, as ruled. The keyword text gained the sentence:
*"The leftmost member bows first."*

**§4 Per-slot hover tips.** A `Control` per slot owns an `NHoverTipSet`, and
the copy is `SalonMemberTips` — the same source B5's card keyword reads, not
a fork. Tip content is stashed as node metadata and read at hover time, so
the signal is connected once per node and the copy is never a snapshot of an
older stage.

**§5 Dynamic slot count.** The scene ships five slots now (3 base + Box Seats
upgraded = 5, the current ceiling), and the row is laid out from the LIVE cap
rather than from authored positions: gap tightens as the count grows, capped
at the shipped 62px pitch so a normal three-member stage is pixel-identical
to the one that shipped. This closes the sprint-2 gap where a fourth member
ticked, bowed and counted for every per-member rider while being invisible.

---

## Track 2 — Encore ribbon becomes RUNWAY (D7)

`RibbonVisualSpan = 20` is gone. A segment is one turn of upkeep at the
current stage (members × `TickEncoreCost`); five segments render, and past
that a "5+" cue. The last segment fills partially, so the bar drains
continuously rather than snapping a whole turn at a time. Deploying a member
visibly shortens the runway with Encore unchanged — correct, and the point.

**Judgment call (the brief asks for the least-weird rendering and a note).**
Zero members: the ribbon renders as one plain, muted, FULL-WIDTH bar carrying
the number. Full width because a partial plain bar would imply a fraction of
something and there is nothing to be a fraction of; muted because the bar is
not measuring anything right now.

---

## Track 3 — Encore saturation baseline (D8 prerequisite, MEASURE ONLY)

Instrument: `tier05/encore_telemetry.py`, fed by three new emit-only events
(`salon_upkeep`, `salon_tick`, `encore_end`). 200 realistic runs per arm,
seed 20260728, `RUNTEMPLATE` 7 world, constants `SALON_TICK_ENCORE_COST 1`,
`SALON_MEMBER_SLOTS 3`, `SALON_DRY_DAMAGE_MULT 0.75`.

*dry* = the upkeep arrives under ONE member's cost. *full* = it arrives
holding the whole stage's bill. *surplus* = held minus that bill.

| arm | acts | dry | full | all-ticked | surplus | held | end | gain/drain |
|---|---|---|---|---|---|---|---|---|
| salon | all | 49.4% | 45.7% | 45.2% | +1.4 | 3.5 | 4.0 | 1.49 |
| salon | act 1 | 54.0% | 42.6% | 42.4% | +0.6 | 2.3 | 2.5 | 1.52 |
| salon | act 2 | 49.9% | 44.2% | 43.6% | +1.2 | 3.4 | 4.5 | 1.40 |
| salon | act 3 | 37.8% | 56.6% | 55.6% | +4.0 | 6.6 | 8.3 | 1.62 |
| fanfare | all | 56.0% | 43.2% | 43.0% | +1.6 | 2.8 | 2.8 | 1.44 |
| generic | all | 61.7% | 36.6% | 36.4% | +0.6 | 2.1 | 2.2 | 1.47 |

n = 2589 combats / 9278 upkeeps on the salon arm.

**The read: the sim does NOT reproduce the playtest's "passively full free
block bar".** It reports close to the opposite. Half of all salon upkeeps
arrive unable to fund even one member, mean surplus is about one point, and
the meter ends combat holding 4. The only place the playtest's shape appears
at all is act 3, where the stage is biggest: dry falls to 37.8%, surplus
rises to +4.0, and the meter ends on 8.3.

This is the pass-4 divergence clause again, and it fires the same way: the
divergence IS the finding and goes to [USER] before any D8 remedy is
trusted. Three candidate explanations, none testable from here — (a) the
sim pilot spends Encore that a human hoards, since the pilot has no reason to
bank; (b) the playtest deck reached a generation density the drafted sim
decks do not; (c) **the playtest was CO-OP and tier 0.5 models one seat** —
the standing "co-op has no sim backstop" caveat, which here is not a caveat
about bugs but about the measurement itself: a second player changes how long
fights run and how much damage arrives per turn, and both feed the meter.
**No lever is proposed. Track 3 was measure-only and stays so.**

**An instrument bug caught mid-sprint, because the numbers did not
reconcile.** The first run reported gained/spent 3.07 against a mean end
level of 4.0 — figures that cannot both be true. The missing sink was
absorption: `absorb_into_encore` takes points off the meter and emits
`encore_absorb`, never `encore_spent`, so every point the buffer ATE was
being reported as a point it wasted — an exact inversion of what the buffer
is for. The denominator is `spent + absorbed` now, and gained − drained ==
end level holds, which is the arithmetic that makes the table credible. On
the salon arm absorption (4.2/combat) is the LARGER sink, ahead of upkeep and
cards (3.9); any D8 lever written against upkeep alone would be aiming at the
smaller half of the drain.

---

## Track 4 — Slip Backstage rider fire-rate (D4, MEASURE ONLY)

Instrument: `tier05/conditional_telemetry.py`, fed by an emit on every
conditional evaluation (card + predicate + fired). Generic on purpose — a
`graceful_retreat` counter would have to be rewritten for the next suspect.
Denominator is EVALUATIONS, not plays.

**`graceful_retreat` / `hp_lost_this_turn`: 2.9% (18/615) salon, 3.3%
(22/669) fanfare, 3.3% (14/426) generic — 58/1758 = 3.3% pooled across all
three arms with the upgraded copies folded in.** The suspicion is confirmed:
the rider is dead. Block resolves before the enemy swings,
so on the turn the card is played the condition describes damage that has
usually not happened yet. The printed card is a 9-block card that is a
5-block card ~97% of the time.

Two more dead riders surfaced that the brief did not ask about, and they are
worse:

Rates below are pooled across all three arms INCLUDING the upgraded copies,
which is the honest unit — an upgrade does not change either predicate.

| card | predicate | rate | evaluations |
|---|---|---|---|
| `the_final_verdict` | `reaction_triggered_by_this` | **0.0%** | 0/298 |
| `blocking_notes` | `spotlight_moved_this_turn` | 1.3% | 31/2471 |

`the_final_verdict` has never once fired in this world. **Out of scope to
fix** (any re-authoring is red-pen), but they belong in the same queue as D4
and are logged here rather than left for the next person to rediscover.

---

## Gates

- Full-repo `pytest` from root, before and after: **1330 passed, 1 skipped**
  (was 1318/1 at sprint start; +12 new tests, and 2 pre-existing tests were
  rewritten rather than added to — see below).
- `art_lint`: plan OK (three allowlisted PENDING/KNOWN rows unchanged).
- `build_pck` → contract `roster-pck-v3`, 117 resources, the three glyphs and
  the rebuilt scene present.
- `validate.ps1`: **OK**. Deployed `0.2-227`.
- Harmony bite-check: **14 patch class(es) armed**.

**Two shipped tests were rewritten, and both were honest catches, not
noise.** `test_the_stage_geometry_is_uniform_across_the_three_slots` pinned
three slots on a 62px pitch — a contract D1 deliberately replaces — so it now
sweeps every slot the scene ships and a second test pins the new rule (the
bridge lays out the row; 62 is the maximum gap, not the fixed one; a slot may
not overhang the arc). `lint_constant_parity` refused the four new bridge
constants until they were classified, and refused the two retired ones until
they were dropped.

**New gates were seen to FAIL before being trusted**, per house rule. Five
defects were reconstructed against the shipped source and each fired the gate
that covers it: a bridge that recomputes the Focus term instead of calling
`TickValue`; an upkeep loop that scales outside `TickValue`; a `LayOutSlots`
that is defined but never called; a widened `SlotSpacingMax`; a `SlotHalfSpan`
that overhangs the stage arc. The telemetry tests include a defect
reconstruction too — the absorption bug above is pinned as
`test_absorption_counts_as_drain_or_the_ratio_inverts`.

---

## For [USER] review

Everything below was decided without red-pen.

1. **The Track 3 divergence.** Sim says the Encore bar starves; playtest says
   it saturates. This needs a ruling on which world D8 is being designed for
   before any lever is picked.
2. **Absorption is the bigger sink** (4.2 vs 3.9 per combat on the salon
   arm). If D8 goes the "faster drain" route, upkeep is the smaller half.
3. **Two extra dead riders** (`the_final_verdict` at a flat 0%,
   `blocking_notes` at ~1%), found by an instrument built for a third.
4. **The zero-member ribbon rendering** (full-width muted plain bar) is my
   pick from the brief's "least weird" instruction.
5. **Five slots is the scene's ceiling.** Nothing today can exceed it —
   3 + Box Seats upgraded = 5 — but a future cap-raise card would go
   invisible above five. The loop clamps and this note is the record.
6. **The glyph shapes** are mine: sword/shield/droplet, drawn to the
   mockup's roles. They are geometry, not art direction, and cheap to redraw.
7. **Nothing visual is verified.** Track 1 and Track 2 both need eyes on a
   real combat, including the specific question the brief flagged: whether a
   per-slot hover target interferes with targeting arrows or enemy intents.
