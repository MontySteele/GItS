# Brief — Kokomi pool fill, 15 proposals (2026-07-29)

**PROPOSALS ONLY. NO YAML SHEET IS EDITED BY THIS DOC.** Nothing here is
ratified and nothing here is in the measured pool — an unratified card in
`docs/kokomi-cards.yaml` would silently enter every drafting arm and change
every Kokomi number in the repo, which is the opposite of what a proposal is
for. Card rows are given in the sheet's effect grammar so that a [USER]
approval is a paste, not a re-authoring.

**World the diagnosis was measured in: `RT7 / D13 / P3 / C4`.**

---

## 1. The gap, counted

| character | total | basic | common | uncommon | rare |
| --- | --- | --- | --- | --- | --- |
| furina | 82 | 5 | 23 | 35 | 19 |
| klee | 76 | 4 | 32 | 25 | 15 |
| **kokomi** | **61** | **5** | **27** | **19** | **10** |

Kokomi is 15 short of Klee and 21 short of Furina, and the shortfall is
top-heavy: **10 rares against Klee's 15**, 19 uncommons against 25.

**This fill proposes exactly Klee's shape** — `+4 common / +6 uncommon /
+5 rare` — landing her at **76 (5 / 31 / 25 / 15)**. Rares are the priority the
brief names; the count is capped at +5 rather than +7 because overshooting
Klee's rare count while still trailing his commons would build a pool whose
best cards are easier to find than its filler.

### Where the holes actually are

By archetype (a card counts once per archetype it lists):

| archetype | cards | of which rare | rare-exclusive |
| --- | --- | --- | --- |
| generic | 32 | 1 | 1 (`ceremonial_garment`) |
| priest | 25 | 7 | 5 |
| assist | 17 | 2 | **0** |
| commander | 11 | 2 | 2 |

- **The assist lane has no rare of its own.** Its only two rares
  (`moonlit_offering`, `epiphany_of_the_deep`) are shared with priest and are
  priest cards wearing an assist tag. The kickoff §3 designed assist as "honest
  glue no archetype warps around" with "low internal payoff by design" — the
  measurement says that intent overshot: **assist wins 0.5% [0.3, 0.8] at
  n=3000** against a roster floor of 2.1%, the worst arm on the roster by a
  factor of four. A lane with no payoff at its top rarity has no reason to be
  drafted after the third pick.
- **Commander has 11 cards**, less than half of priest's 25, and its whole
  identity (conscript) is printed on 9 of them. It is thin rather than broken —
  it wins 2.9%, the best Kokomi arm.
- **Priest is the finished lane.** No priest-exclusive card is proposed here.

### Three ops and one runtime count that no card in the repo prints

Found while auditing the grammar for this brief. Each is implemented, tested,
priced by DRAFTER 13 — and unreachable, because no card row uses it. This is
the `surging_shoal` vigil defect (a card in no package is unreachable) one level
down: **a verb in no card is unreachable.**

- **`grant_sly_this_turn`** — HandTrick's shape: give a Skill in hand Sly for
  the turn. Kokomi's Sly lane is the assist lane, and nothing in her pool can
  *make* a card Sly. Printed by proposals **A1** and **A5**.
- **`recall_to_draw`** — Headbutt's shape: a chosen card from discard to the top
  of draw. The assist lane throws its own payoffs away and has no way to get one
  back. Printed by **A9**.
- **`discards_this_turn`** (an `amount_formula` count, MementoMori's) — the
  assist lane has **no attack that reads its own engine**; its damage cards read
  the *exhaust* pile, which is priest's resource. Printed by **A4**.
- (`block_next_turn` and `metallicize` *are* printed — twice and once — which is
  the flatness problem in §4, not an unreachability one.)

---

## 2. Constraints every proposal below is checked against

1. **LAW 2 — no direct heals, ever** (R52 ask 1: "NO amendment — and none
   planned, ever"). **No proposal prints `heal`.** `gain_max_hp` is also
   excluded: it heals by the same amount it raises the cap, so it is a heal
   wearing a different op name.
2. **R51 debuff texture** — Weak and Vulnerable only as riders on exhaust / Sly
   engine pieces, never a cheap standalone AoE debuff (the `commanding_gaze`
   pattern is explicitly excluded from her pool). **No proposal applies Weak or
   Vulnerable at all**, which is the safest form of compliance; the two cards
   that do (`exposing_current`, `sango_prayer`) already cover the texture.
3. **Deck-size law** (kickoff §1 law 4, gated by `tools/lint_kokomi_decksize.py`)
   — Commons and basics may not net a positive card delta. The four proposed
   commons net **0, 0, 0, 0**; `conscript` in default transform mode is delta
   zero, which is what makes it legal at Common.
4. **Existing ops only** — the op-parity lint (`tools/lint_op_parity.py`) fails
   an op with no price, and DRAFTER 13 priced all 56. **14 of 15 proposals use
   only registered ops.** The one exception is flagged in §3 and in §6.
5. **No Furina grammar.** `salon_bow`, `gain_encore`, `spotlight_*`,
   `generate_guest_star` are hers. The `copy_*` family is deliberately avoided
   too: the kickoff draws the line explicitly — Furina's companion grammar is
   *additive and empowering*, Kokomi's is *transformative and consumptive*. The
   one existing exception (`shoulder_to_shoulder`, a common that copies a
   companion) is not extended.
6. **No Klee grammar** — no bombs, no Sparks.
7. **Names** — none of the 15 ids or names collides with an existing card in any
   `docs/*-cards.yaml`, and none appears in `docs/reserved-card-names.txt`
   (which includes the Silent's full 88-name base-game pool). Names are still
   [USER]-gated for lore, as always.
8. **Upgrades not proposed.** `docs/kokomi-upgrades.yaml` has a rest-smith
   dependency and every card needs one; that is a second pass, deliberately not
   bundled with 15 unratified rows.

---

## 3. The five rares

### A1 — Orders from the Shrine
- **id** `orders_from_the_shrine` · **rare** · skill · **cost 1** · Exhaust
- **archetypes** `[assist]`
```yaml
- id: orders_from_the_shrine
  name: Orders from the Shrine
  rarity: rare
  type: skill
  cost: 1
  exhaust: true
  archetypes: [assist]
  effects:
    - {op: grant_sly_this_turn, card_type: skill}
    - {op: grant_sly_this_turn, card_type: skill}
    - {op: grant_sly_this_turn, card_type: skill}
    - {op: discard, amount: 3, select: chosen}
```
- **Rationale.** The assist lane's first rare of its own, and it pays off the
  cards the lane already drafted instead of adding a new engine: three Skills in
  hand become Sly, then a chosen discard-3 fires all three riders at once.
  `grant_sly_this_turn` filters to Skills not already Sly this turn, so the three
  ops pick three different cards rather than stacking on one. Exhaust and cost 1
  keep it a one-shot detonation of a hand, not a loop.
- **Feeds** assist. **Ops** all registered; first printed use of
  `grant_sly_this_turn`.

### A2 — Beat to Quarters
- **id** `beat_to_quarters` · **rare** · skill · **cost 2** · Exhaust
- **archetypes** `[commander]`
```yaml
- id: beat_to_quarters
  name: Beat to Quarters
  rarity: rare
  type: skill
  cost: 2
  exhaust: true
  archetypes: [commander]
  effects:
    - {op: conscript, amount: 2, mode: create}
    - {op: cost_mod, scope: companion_cards, delta: -1, duration: this_turn}
    - {op: gain_charge, amount: 2}
```
- **Rationale.** Commander's best turn currently needs two rares in hand:
  `grand_conscription` makes the bodies and `honor_guard` discounts them, and
  nothing does both. This is the lane's single-card payoff turn. `mode: create`
  is Uncommon+ only by the deck-size law and Exhaust pays one card back, so the
  net is +1 on a Rare, which is what the law prices Rares for.
- **Feeds** commander. **Ops** all registered.

### A3 — Tideborne Discipline — ⚠ NEEDS ENGINE WORK
- **id** `tideborne_discipline` · **rare** · power · **cost 2**
- **archetypes** `[assist]`
```yaml
- id: tideborne_discipline
  name: Tideborne Discipline
  rarity: rare
  type: power
  cost: 2
  archetypes: [assist]
  effects:
    - {op: apply_power, power: discard_dividend, amount: 1, target: self}
    # discard_dividend: whenever a card is discarded from your hand by a card
    # effect, gain 1 Block and 1 Charge per stack.
```
- **Rationale.** The structural hole, stated as a card: the assist lane has **no
  persistent payoff power at any rarity**. Priest has three
  (`mercy_of_the_deep`, `epiphany_of_the_deep`, `vigil_of_the_deep`), commander
  has its cost engine, assist has nothing that rewards running the engine across
  turns — which is why its curve is a pile of 0-cost cyclers that win 0.5%.
  `dark_embrace` (already on `epiphany_of_the_deep`) is the exhaust-side mirror
  of this; this is the discard side.
- **⚠ FLAG.** `apply_power` is registered, but **`discard_dividend` is a NEW
  POWER** — engine work in `tier0/engine/powers.py` plus a trigger at the
  `_op_discard` Sly site, plus a C# mirror before it can ship in the mod. It is
  proposed anyway, and proposed as the *only* one of the fifteen that costs
  engine work, because every no-new-power version of "reward the discard engine
  across turns" is a rider on a single card and therefore not the thing the lane
  is missing. If the answer is no, **A4 + A6 are the fallback** and the lane
  stays a tempo lane with no long game.
- **Feeds** assist.

### A4 — Everything the Current Took
- **id** `everything_the_current_took` · **rare** · attack · **cost 2**
- **archetypes** `[assist]`
```yaml
- id: everything_the_current_took
  name: Everything the Current Took
  rarity: rare
  type: attack
  cost: 2
  archetypes: [assist]
  effects:
    - {op: damage, amount_formula: {base: 6, per: 3, count: discards_this_turn},
       target: enemy}
```
- **Rationale.** The assist lane's only self-reading attack. Every damage card it
  can draft either reads the **exhaust pile** (`undertow`, `pearl_barrage`,
  `depths_judgment` — priest's resource) or is flat (`scattering_spray`,
  `driftglass`). A lane whose whole verb is discarding has no card that asks how
  much it discarded. Cost 2 and Rare are the rate limit: on the lane's real big
  turn (three discards) it is 15 for 2, roughly `read_the_current`'s charged
  ceiling, and it is 6 for 2 when drawn early — deliberately bad without the
  engine, which is what makes it a payoff rather than a staple.
- **Feeds** assist. **Ops** all registered; first printed use of the
  `discards_this_turn` count.

### A5 — The Deep Holds the Line
- **id** `the_deep_holds_the_line` · **rare** · skill · **cost 2**
- **archetypes** `[generic, priest]`
```yaml
- id: the_deep_holds_the_line
  name: The Deep Holds the Line
  rarity: rare
  type: skill
  cost: 2
  archetypes: [generic, priest]
  effects:
    - {op: block, amount: 6, bonus_formula: 1_per_2_charge}
    - {op: block_next_turn, amount: 6}
```
- **Rationale.** **The flatness card, and the one this brief would defend
  hardest.** The 2026-07-29 stability reading (see
  `docs/sprint-kokomi-instrument-log-2026-07-29.md`) found that on the
  instrument R51 made the entire home of her healer fantasy, Kokomi reads
  **mid-pack to worst on every column**, and that Klee — her declared opposite
  on the volatility axis — reads flatter than she does. Her pool's reason is
  visible: pre-emptive Block is printed on exactly two commons (`slack_water`
  4/4, `tideline_watch` 8-next) and per-turn Block on one uncommon
  (`pearl_current`, `metallicize` 3). This card is the two flatness verbs at
  rare rate, with the Charge bank finally buying *defence* instead of only
  damage — which is the kickoff's stated identity ("her HP bar doesn't move; her
  deck does") expressed as arithmetic rather than as flavour. It is the only
  proposal here whose case is a measurement.
- **Feeds** generic (all three plans) and priest. **Ops** all registered;
  `block` already accepts `bonus_formula` (`_resolve_block`, effects.py:623).

---

## 4. The six uncommons

### A6 — War Council
- `war_council` · **uncommon** · skill · **cost 1** · Exhaust · `[commander, assist]`
```yaml
- id: war_council
  name: War Council
  rarity: uncommon
  type: skill
  cost: 1
  exhaust: true
  archetypes: [commander, assist]
  effects:
    - {op: conscript, amount: 1, mode: create}
    - {op: draw, amount: 2}
    - {op: discard, amount: 1, select: chosen}
```
- **Rationale.** The kickoff says assist "feeds both other lanes" and no card
  actually bridges them. This one does it in one direction: velocity in, a body
  out, and the chosen discard means the card it draws into can be thrown to a Sly
  rider. Net delta 0 (create +1, Exhaust −1). **Feeds** commander and assist.

### A7 — Hand Over Hand
- `hand_over_hand` · **uncommon** · skill · **cost 0** · `[assist]`
```yaml
- id: hand_over_hand
  name: Hand Over Hand
  rarity: uncommon
  type: skill
  cost: 0
  archetypes: [assist]
  effects:
    - {op: discard, amount: 1, select: chosen}
    - {op: draw, amount: 2}
  sly:
    - {op: block, amount: 4}
```
- **Rationale.** The lane's four 0-costs (`moon_signal`, `whispered_word`,
  `ebb_tide`, `steady_the_line`) are all commons and all at common rate, so a
  big-energy assist turn has nothing to spend on. A chosen discard into draw-2
  at 0 is the uncommon rate, and the Sly rider makes it pay when it is itself
  the card thrown. **Feeds** assist.

### A8 — Low Water Mark
- `low_water_mark` · **uncommon** · skill · **cost 1** · `[assist, priest]`
```yaml
- id: low_water_mark
  name: Low Water Mark
  rarity: uncommon
  type: skill
  cost: 1
  archetypes: [assist, priest]
  effects:
    - {op: discard, amount: 2, select: chosen}
    - {op: gain_charge, amount: 4}
  sly:
    - {op: exhaust_from, amount: 1, select: chosen}
```
- **Rationale.** The assist→priest bridge in the other direction from A6: it
  converts a discarded hand into Charge, the only currency both lanes read. Two
  chosen discards fire two Sly riders, and its own Sly rider feeds the exhaust
  funnel, so the card pays whether it is played or thrown. **Feeds** assist and
  priest.

### A9 — What the Tide Gives Back
- `what_the_tide_gives_back` · **uncommon** · skill · **cost 1** · `[assist]`
```yaml
- id: what_the_tide_gives_back
  name: What the Tide Gives Back
  rarity: uncommon
  type: skill
  cost: 1
  archetypes: [assist]
  effects:
    - {op: recall_to_draw, amount: 1}
    - {op: block, amount: 4}
  sly:
    - {op: recall_to_draw, amount: 1}
```
- **Rationale.** The lane's structural downside, answered: it discards at
  volume and cannot get a payoff back. Uncommon rather than common because
  recursion plus a lane built on random discards is a real engine, and the Sly
  rider deliberately makes the *thrown* copy the better one. **Feeds** assist.
  First printed use of `recall_to_draw`.

### A10 — Signal Flags
- `signal_flags` · **uncommon** · skill · **cost 0** · `[assist, commander]`
```yaml
- id: signal_flags
  name: Signal Flags
  rarity: uncommon
  type: skill
  cost: 0
  archetypes: [assist, commander]
  effects:
    - {op: grant_sly_this_turn, card_type: skill}
    - {op: draw, amount: 1}
```
- **Rationale.** A1 at uncommon rate and the reason A1 is draftable: one card
  becomes Sly, one card is drawn, free. Without something at this rarity the
  "make a card Sly" verb exists on exactly one Rare and the lane's rare payoff
  has no on-ramp. **Feeds** assist and commander.

### A11 — Close Ranks
- `close_ranks` · **uncommon** · skill · **cost 1** · `[commander]`
```yaml
- id: close_ranks
  name: Close Ranks
  rarity: uncommon
  type: skill
  cost: 1
  archetypes: [commander]
  effects:
    - {op: block, amount: 6}
    - {op: cost_mod, scope: companion_cards, delta: -1, duration: this_turn}
```
- **Rationale.** Commander's only discount is a Rare (`honor_guard`), so the
  lane cannot defend on the turn it musters — it either plays bodies or plays
  Block. Block-plus-discount at uncommon is the lane's missing tempo turn.
  **Feeds** commander.

---

## 5. The four commons

Each nets card delta **0** and is checked against the deck-size law.

### A12 — Pass the Word
- `pass_the_word` · **common** · skill · **cost 0** · `[assist]`
```yaml
- id: pass_the_word
  name: Pass the Word
  rarity: common
  type: skill
  cost: 0
  archetypes: [assist]
  effects:
    - {op: discard, amount: 1, select: chosen}
    - {op: draw, amount: 1}
    - {op: gain_charge, amount: 1}
```
- **Rationale.** Every existing assist 0-cost discards at **random**
  (`moon_signal`, `whispered_word`, `ebb_tide`, `steady_the_line`,
  `tactical_retreat`), so the lane's glue is a coin-flip on its own payoffs and
  the Sly riders it drafted fire on whatever came up. One chosen-discard cycler
  at common rate is what makes the lane a decision instead of a shuffle.
  **Feeds** assist. Delta 0.

### A13 — The Hollow Wave
- `the_hollow_wave` · **common** · attack · **cost 1** · `[assist, generic]`
```yaml
- id: the_hollow_wave
  name: The Hollow Wave
  rarity: common
  type: attack
  cost: 1
  archetypes: [assist, generic]
  effects:
    - {op: damage, amount: 5, target: all_enemies}
  sly:
    - {op: damage, amount: 4, target: random_enemy}
```
- **Rationale.** The lane's only AoE is `scattering_spray` (5 AoE plus a
  random discard). This is the same rate with the payoff moved onto the Sly
  rider, so it rewards being thrown rather than charging for it — and R56's "no
  one starts the game with AoE; if you need it, you draft it" is respected
  because it is a draft-in, not a starter. **Feeds** assist and generic.
  Delta 0.

### A14 — Hold the Shallows
- `hold_the_shallows` · **common** · skill · **cost 1** · `[commander]`
```yaml
- id: hold_the_shallows
  name: Hold the Shallows
  rarity: common
  type: skill
  cost: 1
  archetypes: [commander]
  effects:
    - {op: block, amount: 5}
  sly:
    - {op: conscript, amount: 1}
```
- **Rationale.** The only card in the pool where the commander verb fires off
  the assist verb, at the rarity where the two lanes actually meet in a deck.
  `conscript` in default transform mode is delta **zero**, which is precisely
  why the law lets it sit on a Common. **Feeds** commander (and assist decks
  that splash it). Delta 0.

### A15 — Slackwater Drill
- `slackwater_drill` · **common** · skill · **cost 1** · `[generic]`
```yaml
- id: slackwater_drill
  name: Slackwater Drill
  rarity: common
  type: skill
  cost: 1
  archetypes: [generic]
  effects:
    - {op: block, amount: 3}
    - {op: apply_power, power: metallicize, amount: 1, target: self}
```
- **Rationale.** The flatness texture at common rate, and the cheapest possible
  answer to the §3-A5 measurement: per-turn Block is printed on exactly one card
  in her pool (`pearl_current`, uncommon, `metallicize` 3). One stack for 1 is
  under-rate as a Block card on purpose — it is bought for the trajectory, not
  for the turn, which is the distinction the stability instrument exists to make
  visible. **Feeds** generic (all three plans). Delta 0.

---

## 6. Summary and what a [USER] pass has to decide

| # | id | rarity | cost | archetypes | flags |
| --- | --- | --- | --- | --- | --- |
| A1 | `orders_from_the_shrine` | rare | 1 | assist | first `grant_sly_this_turn` |
| A2 | `beat_to_quarters` | rare | 2 | commander | — |
| A3 | `tideborne_discipline` | rare | 2 | assist | **⚠ new power `discard_dividend`** |
| A4 | `everything_the_current_took` | rare | 2 | assist | first `discards_this_turn` |
| A5 | `the_deep_holds_the_line` | rare | 2 | generic, priest | the measurement's card |
| A6 | `war_council` | uncommon | 1 | commander, assist | — |
| A7 | `hand_over_hand` | uncommon | 0 | assist | — |
| A8 | `low_water_mark` | uncommon | 1 | assist, priest | — |
| A9 | `what_the_tide_gives_back` | uncommon | 1 | assist | first `recall_to_draw` |
| A10 | `signal_flags` | uncommon | 0 | assist, commander | — |
| A11 | `close_ranks` | uncommon | 1 | commander | — |
| A12 | `pass_the_word` | common | 0 | assist | — |
| A13 | `the_hollow_wave` | common | 1 | assist, generic | — |
| A14 | `hold_the_shallows` | common | 1 | commander | — |
| A15 | `slackwater_drill` | common | 1 | generic | — |

**By rarity:** 5 rare, 6 uncommon, 4 common → pool 61 → **76**, matching Klee's
`5 / 31 / 25 / 15` shape.
**By archetype fed:** assist **10**, commander **5**, generic **3**, priest
**2** (cards counted once per archetype listed).

### Machine-checked before publication

The fifteen rows above were extracted from this document's own YAML blocks and
run through the real gates, so a [USER] approval is not also a debugging
session:

- **`tools/lint_kokomi_decksize.py`** — clean, exit 0. All four commons net 0.
- **Op registry** — every op appears in `tier0.engine.effects.OPS`; no `heal`,
  no `gain_max_hp`, no Furina or Klee verb, no unpriced op (so
  `tools/lint_op_parity.py` cannot be tripped by these rows).
- **Id / name collisions** — none against any `docs/*-cards.yaml`, none against
  `docs/reserved-card-names.txt`.
- **Engine resolution** — 13 of 15 resolve clean against a hand-built
  `CombatState`, including the two novel reads (`discards_this_turn` as an
  `amount_formula` count and `1_per_2_charge` as a `bonus_formula` on `block`).
  The two that raise are `everything_the_current_took` and `the_hollow_wave`,
  both plain `damage` ops — and an existing card (`waters_edge`, `damage 6`)
  raises identically in the same harness, because `damage` reads a state field
  that `resolve_card` sets up and a bare `_resolve_effects` call does not. It is
  a harness artifact, verified as such, not a card defect.
- **A3 is the exception and is meant to fail** anything that checks powers:
  `discard_dividend` does not exist. That is the flag, not an oversight.

### The decisions this needs

1. **A3, the one engine ask.** A new power `discard_dividend` — Python engine,
   trigger site, C# mirror. Everything else is paste-and-measure. If it is a no,
   the assist lane keeps no long game and A4 + A6 are the declared fallback.
2. **Whether assist should be rescued at all.** The kickoff designed it as
   deliberately low-payoff glue; the measurement says 0.5% at n=3000. Ten of
   these fifteen cards assume the answer is "raise it to the floor". The
   alternative ruling — that assist is a splash lane and its 0.5% arm number is
   an artifact of measuring it as a *plan* — is a legitimate reading of the same
   evidence and would cut this brief roughly in half.
3. **Names.** All fifteen are placeholders pending the lore/naming audit, as
   always. `slackwater_drill` deliberately echoes the existing `slack_water` and
   may want to not.
4. **Nothing may be measured until it is ratified.** The moment a row lands in
   `docs/kokomi-cards.yaml` it enters the drafter's pool for every arm, and
   every Kokomi number in the repo becomes a pre-fill number. The fill should
   land as one batch with a fresh roster-anchor reading beside it, not
   card-by-card.

---

# REWORK INPUT (NOT LINTED) — the support gap, from Track A (2026-08-04)

**Filed by R92/3c.** Carried here rather than into a gate, and the distinction
is load-bearing: **this is never linted.** The sim is one-seat (charter A0's
D4 clause, written in at birth), so a `support` cell can only be graded by a
play session and no coverage lint may ever fail a pool for it. It arrives as
input to the fill above, not as a bar it has to clear.

**The finding, in one line.** `support` reads **0% on all three GItS sheets**
— Klee, Furina and Kokomi — against **2.3% in every one of the five canon
pools** (`docs/role-tempo-baseline.md` §1).

**It is a structural absence, not a mis-tagging.** The classifier finds
support in canon three independent ways, all of them the game's own spellings:
an ally `TargetType` (`AnyAlly` / `AllAllies`), a `MultiplayerOnly` card
constraint, and a power that walks the owner's teammates (`GetTeammatesOf`).
**No GItS row has any of the three.** There is nothing for a classifier to
find, so no amount of re-tagging closes this — a card has to be authored.

**Why it lands in THIS brief.** §5's assist lane is where those cards belong.
The lane's declared job is helping the other two seats, the co-op playtest is
the only instrument that can see it, and the fill above is the next batch that
will author Kokomi cards at all. Canon concentrates its own support in the two
newest characters, so a support-carrying Assist would be following canon
practice rather than inventing a category.

**How this interacts with open question 2 above** ("whether assist should be
rescued at all"). It does not settle it and must not be read as settling it.
If assist stays a splash lane, the support gap stays open and becomes a
roster-level question for whoever authors slot 4. If assist is rescued to the
floor, this is the shape the rescue should take, because a lane whose cards
only ever help the seat that plays them is not an assist lane.

**Not a gate. Not a floor. Not a number.** Track A carries this and stops.
