# Furina Sheet Pass 2 — Plan ("The R16 World")

**Date:** 2026-07-20. **Authorized:** R28 (GO, full queued scope).
**Governing:** R16–R22 (furina-pass1-rulings.md), R26 (adjacent-rarity
domination law), DECISIONS 69–78, kickoff v0.1, principles v1.10.
**Environment:** CONSTANTS_VERSION 2, DRAFTER_VERSION 2,
RUNTEMPLATE_VERSION 2. Suite baseline: 223 green.
**Official numbers:** 1000 fights/encounter, seed 20260720, unless a
cell says otherwise. Null results binding, as always.

## 1. Scope (all previously ruled; nothing new is being decided here)

1. **R16 re-author** — Spotlight empowerment moves from the relic's
   passive into her cards, through the existing `spotlight_mult` pipe.
2. **SPOTLIGHT_BASE_MULT sweep** {1.0, 1.25} — pre-registered (R16.2).
3. **§8 criterion-2 delete-test** re-run in the R16 world (must pass).
4. **FANFARE_CAP_FRACTION re-sweep** {0.25, 0.5, 0.75} with the 6-blood
   uncapper (R17 note + DECISIONS 75b).
5. **A6 instrument v2** — application-uptime component (R18).
6. **Graded-encounter EP battery** — registration (i) instrument (R21).
7. **pit_orchestra/macaron_break** domination fix (R28; then the pair
   leaves the lint's KNOWN set).
8. **spotlight_weighted A2 band** — landed per R19's schedule ("it gets
   banded at pass 2"), number from the measured world, red-pen may
   adjust.

## 2. Engine: the card-mediated pipe (R16.3 — no new keyword)

Two powers, both read INSIDE the existing empowerment path, so §2.2a
numbers-only enforcement is inherited structurally (the helper is
plumbed into damage/Block and nowhere else):

- `spotlight_mult_bonus` — combat-duration percentage points added to
  the Spotlighted character's multiplier (25 = +0.25x). Granted only by
  her cards via apply_power.
- `spotlight_mult_bonus_turn` — same, this-turn (cleared at end of
  turn like other `_turn` windows).
- `spotlight_flat_damage_turn` — this-turn variant of the existing
  Star-of-the-Show flat rider (R16.3 authorizes "flat Spotlighted
  riders for the turn/combat").

`SPOTLIGHT_MULT` is renamed **`SPOTLIGHT_BASE_MULT`** (R16.2 language):
the relic's residual passive, swept not guessed. `SPOTLIGHT_SELF_MULT`
1.25 stays the ratified self baseline (R17) — the anti-self-buff lever
remains the BASE rate asymmetry; card-granted bonuses apply to whoever
is designated (the cards are the power; the lever is the baseline).

Pilot: damage estimation already reads `effects.spotlight_mult`, so
card-granted bonuses flow into play decisions automatically;
`_spotlight_value` gains terms for the three new powers so boost cards
are drafted/played when a stage exists.

## 3. Sheet: the re-authored Spotlight list

Counts preserved (6 commons / 7 uncommons / rares unchanged): 76 cards
stays 76. KEEP (unchanged): an_invitation, blocking_notes, curtain_cue;
leading_role, supporting_cast, guest_list, directors_cut, duet,
standing_ovation; all Spotlight rares (encore_performance,
star_of_the_show, prima_donna, command_performance). The generators and
ratified texture lines survived §3A — they were never the problem; the
draw/economy administration commons were.

- **limelight** (NEW common, replaces warm_reception): 1c skill —
  Spotlighted character's numbers +25% this turn; draw 1. The
  bread-and-butter boost.
- **stage_lights** (NEW common, replaces props_department): 1c skill —
  Spotlighted cards' damage +2 this turn; block 3. Flat-rider texture.
- **shared_billing** (REWORK): block 4 + Spotlighted numbers +25% this
  turn (was: conditional Encore rider). Defend the stage while the
  star shines.
- **top_billing** (NEW uncommon, replaces constant_star): 1c power —
  Spotlighted character's numbers +25% for the rest of combat, max 2
  stacks. The archetype's core scaling engine; delete it and the mult
  goes with it.

Upgrades sheet: entries for the four changed slots re-authored under
the mined grammar; removed cards' entries removed. spotlight_weighted
package swaps in the new cards (courtroom_drama draft-in cedes its
slot to top_billing — a human drafting this deck takes the scaling
engine first). Probes unchanged: spotlight_companions_only carries no
her-machinery by construction; self_carry is untouched.

**pit_orchestra fix** (flag from DECISIONS 76 KNOWN set): effects
become block 5 + gain Encore 1 (was block 5 + Encore 2). Strictly
tankier / strictly less flux than macaron_break (2 block / 2 Encore) —
neither dominates, and it stops dominating graceful_retreat comparisons
too. The pair leaves KNOWN; the lint then guards the fix.

## 4. Pre-registered experiments (null results binding)

### E1 — SPOTLIGHT_BASE_MULT sweep x delete-test (R16.2, §8c2)

For m in {1.0, 1.25}: full battery, spotlight_weighted +
spotlight_companions_only (+ salon/fanfare spot-checks for
non-interference). **Criterion 2 (delete-test): spotlight_weighted
winrate >= companions_only on ALL four core encounters.** Decision
rule, registered now: if exactly one m passes, it wins; if BOTH pass,
pick 1.0 unless spotlight_weighted's hard floors (punisher, tank_boss)
at 1.0 fall more than 2pt below their 1.25 values — R16's spirit is
"power in the cards, not the relic", so the clean world is the
default and the residual passive must buy its keep. If NEITHER passes,
the card numbers (not the base mult) iterate — §2.2a knob order.

### E2 — FANFARE_CAP_FRACTION re-sweep (R17 note, 6-blood uncapper)

Under the E1-chosen world: fanfare_weighted at cap fraction
{0.25, 0.5, 0.75}. The ratified 0.5 STAYS unless its punisher winrate
leaves the sane band [10%, 55%] (pass-1: 37.6%) — this is a
confirmation re-run, not a re-pick; any change is red-pen material,
not executable here.

### E3 — A6 instrument v2 (R18)

New component: **application uptime** = fraction of enemy intents
taken while the actor carries an elemental aura (the `intent` event
gains an `aura` flag; ref_ironclad applies nothing, so his uptime is
0 by construction). Composite, anchor-preserving:

    A6v2 = 3.0 * (0.5*aoe_ratio + 0.3*debuff_ratio + 0.2*(1 + uptime - uptime_baseline))

At baseline, every term is 1 → 3.0 exactly (anchor preserved without
dividing by a zero-baseline uptime). Weights 0.5/0.3/0.2 keep AoE the
headline while giving uptime real credit. `A6_INSTRUMENT_VERSION = 2`
stamped with the CONSTANTS_VERSION archive discipline; v1 numbers
(Klee A6, Furina 3.6 measured) archived in the pass-2 report table;
never compare v1/v2 unlabeled. Klee re-derived under v2; Furina's
declared 4.2 re-scored. Co-op value stays Tier-2-invisible (accepted
scope, R18).

### E4 — Graded-encounter EP battery (R21, registration (i))

Pass-1's instrument quantized (median AND P90 pinned 0.500).
Graded instrument: tank_boss at enemy-HP grades {0.6, 0.8, 1.0, 1.2,
1.4}; per seed, play ascending grades until first loss; score =
highest grade cleared (0-5). Arms: spotlight_weighted WITH
encore_performance (as shipped) vs the same deck with
encore_performance swapped for courtroom_drama (warm-body control,
same cost). 400 seeds/arm. **Registration (i): duplication should
lift the CEILING (P90 of graded score) more than the median.** If the
graded instrument still cannot separate the arms, the registration
STAYS OPEN and that is the reported result — never "EP showed no
effect."

### E5 — Scorecard + bands

Full `--report-character` at 1000 fights in the chosen world: statline
vs declaration, identity constraints, ratified bands (salon 7.6 /
fanfare 4.2 must hold — they were ratified against the pass-1 world;
drift is reported, not silently absorbed). spotlight_weighted A2
banded at measured + 0.3 (the R19/Klee margin convention). Winrate
bands for spotlight/fanfare PROPOSED in the report (ratification is
red-pen's).

## 5. Out of scope

Selector aiming remains heuristic v2 (open scope, pass-1 honest gap).
A5/A7 shortfalls stay deliberately un-spent until the R16 world is
measured (R19). No salon/fanfare card changes beyond pit_orchestra.
Adaptive-drafter integration for her archetypes: tier05 milestone
scope. The strict-domination lint's dodge_roll pair: Klee session's
sheet, awaiting ruling — not touched here.
