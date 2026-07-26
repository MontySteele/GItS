# Relic + Potion + Ancient-Reward Layer: making the run "realistic"

Status: **DRAFT — awaiting red-pen 2026-07-21.** Successor to
`run-model-rework-plan.md`, which built the realistic Act-1 *gauntlet* (roster,
template, gold economy) but deliberately deferred relics, potions, and the
treasure/ancient relic reward (§1 of that doc: "Relics — **Skip** for now.
Treasure/shop grant/spend **gold only**; relic slot is a stub.").

---

## 0. The reframe (why this exists, why now)

The realistic gauntlet floored every character at ~0% winrate. That is not a
bug — the fights are winnable in isolation — it is the **missing power budget**.
Real StS2 enemy numbers assume the player is carrying relics, drinking potions,
and upgrading. We modeled the enemies faithfully and the player impoverished, so
the scale collapsed. The ratified sequence is:

> **Once the runs are "realistic," THEN we calibrate the sim difficulty.**

Relics and potions ARE the missing realism. Until they exist, any difficulty
knob we turn is compensating for an absence, not calibrating a system. This
layer closes the last two major player-side subsystems (relics, potions) plus
the reward step that delivers them (the treasure/"ancient" chest). After it, the
only major subsystem still unmodeled is **events**.

Second reason, forward-looking: **the artifacts chunk of the design space needs
a relic layer anyway.** Klee's mod ships relics (Pounding Surprise, and the
artifact-set work is queued). Building the relic engine now means artifacts land
on a real substrate instead of a stub.

---

## 1. Scope & the three-workflow split

Three subsystems, but they are **not independent** and **cannot run in
parallel** — all three write `tier05/model.py` (the run loop), `constants.py`,
and the reward/combat plumbing, and two concurrent workflows editing the same
files clobber each other. They also have a hard dependency: you cannot grant a
relic at a treasure chest before the relic engine exists. So: **sequential,
relics first.**

| # | Workflow | What it delivers | Depends on |
|---|----------|------------------|------------|
| **W1** | **Relic engine** | The relic data model, the hook vocabulary, guarded combat + run-layer application, the tiered relic pool, run-state wiring (gained relics persist and apply every fight). *No new granting sites yet* — relics are exercised via tests + one seeded grant. | — |
| **W2** | **Ancient / reward cadence** | Turns the treasure `T` stub into a real relic grant, adds the boss + elite relic rewards, stocks the shop with relics, and wires the run economy so gained relics ride through the run. This is the "add in that step" workflow. | **W1** |
| **W3** | **Potions** | Potion data model, 3 potion slots, drop/shop delivery, and a bounded mid-combat use policy (guarded so battery players — which never hold potions — are untouched). | W1 plumbing (parallel-safe conceptually, but sequenced after W2 to avoid `model.py` collisions) |

Each workflow ends at a **green full suite** (`pytest` at repo root) and a
checkpoint commit on `klee/real-ironclad-baseline`. I run them one at a time,
report results, and only start the next once the prior is green.

---

## 2. Layer boundary — the load-bearing invariant

The tier0 battery (every ratified axis score, the anchor lock pinning
`ref_ironclad` to winrate 0.525 / avg_turns 9.585 at abs 1e-9) **stays frozen.**
The mechanism that guarantees it already exists and is the whole reason this is
tractable:

- Relics and potions are read off `player.relic_hooks` / a new
  `player.potions`. **Battery players carry neither** (they are built from
  character yaml, whose only `relic_hooks` entry is the post-fight starter relic
  — `heal_after_won_fight` for Ironclad, which never touches combat). Every new
  combat effect is gated `if <hook present>` / `if player.potions`, so on the
  battery it is a dead branch. Same guard pattern `frail` and `spark_on_detonation`
  already use.
- Run-**gained** relics/potions live in the run layer (`tier05/`) and are never
  seen by tier0 encounters, which never invoke the run loop.
- **W1 ships a test that re-asserts the anchor lock and
  `test_baseline_scores_are_exactly_three` AFTER the relic engine lands.** A new
  lock is only trusted once seen to fail against its bug: each combat-start relic
  test is first run against a battery player to prove it changes nothing.

If any relic/potion effect cannot be expressed without touching the battery, it
is **skipped and logged UNIMPLEMENTED**, never approximated (house rule; same
line `refpowers` draws for Stampede/Hellraiser).

---

## 3. Relic engine (W1)  ⟵ RED-PEN

### 3.1 Data model

Relics become a tier0.5 yaml sheet, `tier05/content/relics.yaml`. A relic is an
id + tier + a list of typed effects, each mapping to a **known application
site**. No free-form code in the sheet — an effect type the engine doesn't know
is a loud load error.

```yaml
- id: anchor
  name: Anchor
  tier: common
  effects: [{hook: combat_start_block, amount: 10}]
- id: coffee_dripper
  name: Coffee Dripper
  tier: boss
  effects: [{hook: energy_per_turn, amount: 1}, {hook: disable_heal}]
```

### 3.2 Hook vocabulary (the codeable surface)

Every hook maps to an existing seam in `combat.py` / `refpowers.py` /
`model.py`. This is the "cherry-pick the codeable ones" line from the enemy
roster, applied to relics.

| Hook | Fires at | Site (already exists) |
|------|----------|-----------------------|
| `combat_start_block: N` | fight start | new: apply block when run_fight builds the player |
| `combat_start_power: {name: N}` | fight start | reuse `powers.apply_power` (strength/etc.) |
| `combat_start_heal: N` | fight start | player.hp bump, capped |
| `combat_start_energy: N` | turn 1 only | `combat._player_turn` energy set |
| `combat_start_draw: N` | turn 1 only | `CombatState.draw` |
| `energy_per_turn: N` | every turn | `refpowers.energy_for_turn` (Pyre already lives here) |
| `turn_n_block: {turn: T, amount: N}` | turn T | `refpowers.side_turn_start_early` |
| `on_attack_count: {every: 3, gain: {...}}` | Nth attack | `state.attacks_played_this_turn` (Juggling already counts) |
| `status_immunity: [frail, weak]` | on-apply | `powers.apply_power` guard |
| `post_fight_heal: N` | won fight | `model.run_one` (where Burning Blood already lands) |
| `on_pickup_maxhp: N` | pickup | `model` run-state |
| `gold_per_fight: N` / `gold_on_pickup: N` | won fight / pickup | `model` economy |
| `disable_heal` / `disable_potion` | run-wide | boss-relic downsides, flags read at the heal/potion sites |

Existing special string hooks (`spark_on_detonation`, `heal_after_won_fight`)
are **preserved verbatim** — they keep working, and the starter relics keep
declaring them in character yaml.

### 3.3 The Common relic pool (wiki-grounded, red-penned to Common)

RATIFIED: take **the Common pool** (`slaythespire.wiki.gg`, EA v0.10x) —
"around 30 of these." 25 shared + 5 character-specific. Both characters draw the
**shared** pool (relics carry no element/reaction leakage, so the card-parity
concern that bans companions for the refs does not apply — a shared relic pool
is the honest StS2 model and keeps Klee/Ironclad on one scale). Starter relics
(Burning Blood / Pounding Surprise — already modeled) stay character-specific
and are **never** offered as loot. Numbers below are the real wiki numbers.

Every relic maps to a hook site or is **skipped and logged** (house rule: no
silent approximation). Codeable = ✓; skip = ✗ with the missing mechanic named.

| Relic | Effect | Hook / disposition |
|-------|--------|--------------------|
| Anchor | start combat w/ 10 Block | `combat_start_block` ✓ |
| Vajra | start combat w/ 1 Strength | `combat_start_power` ✓ |
| Blood Vial | heal 2 at combat start | `combat_start_heal` ✓ |
| Lantern | +1 Energy on turn 1 | `combat_start_energy` ✓ |
| Bag of Preparation | draw 2 extra on turn 1 | `combat_start_draw` ✓ |
| Bag of Marbles | apply 1 Vulnerable to all at combat start | `combat_start_enemy_power` ✓ |
| Red Mask | apply 1 Weak to all at combat start | `combat_start_enemy_power` ✓ |
| Festive Popper | deal 9 to all enemies at combat start | `combat_start_aoe` ✓ |
| Gorget | start combat w/ 4 Plating | `combat_start_power` (Plating exists in refpowers) ✓ |
| Happy Flower | every 3 turns, gain Energy | `every_n_turns_energy` ✓ |
| Pendulum | every 3 turns, draw 1 | `every_n_turns_draw` ✓ |
| Centennial Puzzle | first HP loss each combat → draw 3 | `on_first_hp_loss` (on_damage seam) ✓ |
| Strike Dummy | 'Strike' cards deal +3 | `card_name_damage_bonus` ✓ |
| Strawberry | +7 Max HP on pickup | `on_pickup_maxhp` ✓ |
| Amethyst Aubergine | enemies drop +15 Gold | `gold_per_fight` ✓ |
| Meal Ticket | heal 15 on entering shop | run-layer at `$` ✓ |
| Regal Pillow | heal +15 on Rest | run-layer at `R` ✓ |
| Venerable Tea Set | +2 Energy on first combat after a Rest | `post_rest_energy` (stateful) ✓ |
| War Paint | upgrade 2 random Skills on pickup | run-layer deck op ✓ |
| Whetstone | upgrade 2 random Attacks on pickup | run-layer deck op ✓ |
| Book of Five Rings | every 5 cards added, heal 20 | run-layer counter ✓ |
| Red Skull (IC) | HP ≤ 50% → +3 Strength | `conditional_power` ✓ (Ironclad-only) |
| Bronze Scales | start combat w/ 3 Thorns | ✗ Thorns power not in tier0 |
| Oddly Smooth Stone | start combat w/ 1 Dexterity | ✗ Dexterity power not in tier0 |
| Juzu Bracelet | no normal fights in ? rooms | ✗ no events/? rooms in the model |
| Potion Belt | +2 potion slots | deferred to **W3** (potions) |

Char-specific commons for un-simmed characters (Snecko Skull, Fencing Manual,
Bone Flute, Data Disk) are out of scope — only Ironclad's Red Skull and the
shared pool are reachable by our two characters.

### 3.5 Neow / run-start relic (answer 5)  ⟵ scope note

RATIFIED: model the run-start special-relic pick. Real StS2: **offered 1
curse-pool relic + 2 positive-pool relics, choose 1.** Many Neow relics are
one-time *deck* effects (add a Rare card, Transform, Scroll packs) or
**curse-adders** — curses are not shipped in the sim (`shop.is_known_dead`
already flags `curse` as a not-yet-shipped tag). So the codeable subset:

| Neow relic | Effect | Disposition |
|------------|--------|-------------|
| Booming Conch | Elite combats: draw 2 + 1 Energy | ✓ `elite_combat_start` |
| Fishing Rod | every 3 normal combats, upgrade a random card | ✓ run-layer counter |
| Golden Pearl | +150 Gold | ✓ `gold_on_pickup` |
| Strawberry-class / Max-HP boons | +Max HP | ✓ `on_pickup_maxhp` |
| Arcane Scroll / card-add boons | add a Rare/Uncommon to deck | ✓ run-start deck op (own pool) |
| Curse-pool relics (Precarious Shears, Neow's Sacrifice, curse-adders) | add curse / lose Max HP | ✗ curses unshipped — logged |
| Cross-character / colorless card boons (Kaleidoscope, Lead Paperweight) | foreign/colorless cards | ✗ no colorless/foreign pool |

v1 offer = **3 codeable positive boons, pick 1** (pilot takes the best). The
curse-pool downside branch is logged as UNIMPLEMENTED until curses ship. This is
W2 work (granting); W1 defines the persistent-hook Neow relics (Booming Conch,
Fishing Rod) as data in the pool.

### 3.4 Run-state wiring

`RunResult` gains `relics: list[str]`. `build_player_from_ids` gains a
`relic_ids` param that merges each relic's combat hooks into `relic_hooks` for
that fight. Max-HP relics adjust the run's `max_hp` variable at pickup;
`disable_heal` suppresses rest/post-fight heals for the rest of the run. All
seeded through the run's single `random.Random` — same determinism contract.

---

## 4. Ancient / reward cadence (W2)  ⟵ RED-PEN

"Ancient" = the treasure-chest step (real StS Act 1, node 9 = a guaranteed
relic). Right now the `T` node grants gold and calls a no-op
`shop.grant_treasure_relic`. W2 makes the reward cadence real:

| Site | Real StS2 | Model |
|------|-----------|-------|
| Treasure `T` | guaranteed relic (+ gold) | roll 1 relic (common-weighted) from the unowned pool; add to run |
| Each won `N`/`E` | card reward (already) + **relic on elite** | **elite** grants a relic (uncommon-weighted); normal fights unchanged |
| Boss `B` | boss relic + card | boss grants a **boss-tier** relic |
| Shop `$` | 3 cards + relic(s) + removal | add 1–2 relics for sale (priced) alongside the card shelf |

**Relic reward pool = "not already owned," tier-weighted per site.** Rarity
weights (common/uncommon/rare split at treasure vs elite vs boss) are the
red-pen numbers. Defaults proposed: treasure = common 50 / uncommon 40 / rare
10; elite = uncommon 70 / rare 30; boss = boss-tier only; shop = common/uncommon.

**Pickup policy:** relics are almost always strictly good in StS, so the default
policy is **take every offered relic** except when a boss relic's downside is
deck-hostile (e.g. Coffee Dripper's no-heal on a heal-reliant deck — a real
skip). A single valuation stub the pilot can veto through; conservative default =
always take. Flagged for red-pen: whether v1 just auto-takes everything (simplest,
faithful enough for Act 1) or runs the veto.

---

## 5. Potions (W3)  ⟵ RED-PEN

### 5.1 Data model & slots

`tier05/content/potions.yaml`; `POTION_SLOTS = 3` (StS default). A potion is an
id + tier + effect drawn from the **already-implemented** power/effect
vocabulary, so payloads are nearly free:

| Tier | Potion | Effect |
|------|--------|--------|
| common | Block Potion | gain 12 block |
| common | Fire Potion | 20 damage to one enemy |
| common | Blood Potion | heal 20% max HP |
| common | Strength Potion | +2 strength this combat |
| common | Swift Potion | draw 3 |
| common | Weak Potion | apply 3 Weak |
| uncommon | Fear Potion | apply 3 Vulnerable |
| uncommon | Energy Potion | +2 energy |
| rare | Fairy in a Bottle | on lethal, revive at 30% max HP |

### 5.2 Delivery

- **Drop:** `POTION_DROP_CHANCE` after a won normal/elite fight (StS default
  ~40%, slot permitting).
- **Shop:** 1–2 potions for sale.
- Overflow (slots full) = drop discarded, logged.

### 5.3 Use policy (the one genuinely invasive piece)  ⟵ RED-PEN

Potions are used **mid-combat**, which means the pilot loop in `combat.py` sees
them. Guarded on `player.potions` being non-empty → **battery players never
enter the branch**, anchor lock safe. A bounded greedy heuristic (not a solver):

- **Defensive:** if predicted incoming this turn ≥ current HP and a
  block/heal/Fairy potion is held → drink it (Fairy auto-triggers on lethal
  regardless, as a revive).
- **Offensive:** on elite/boss, drink a damage/strength/Weak/Fear potion when it
  meaningfully advances the kill or blunts a telegraphed big hit.
- Otherwise hold.

This is "good enough to stress the character," matching the enemy-roster
philosophy — not optimal potion sequencing. The heuristic thresholds are the
red-pen surface.

---

## 6. Measurement — what "done" proves

For each workflow, and cumulatively:

1. **Full suite green** at repo root; anchor lock + `baseline_scores_are_exactly_three`
   still exact (the layer-boundary proof).
2. **Effects are real, not inert:** a run WITH a relic/potion measurably differs
   from one without (the Burning-Blood-was-silently-inert lesson — every hook
   ships with a test that fails if the effect no-ops).
3. **Winrate moves toward realistic:** the ~0% floor should rise as the power
   budget arrives. We do **not** calibrate difficulty here — we just confirm the
   direction is right and report the new curve for `real_ironclad`, `ref_ironclad`,
   and `klee` at a fixed seed set. Calibration is the **next** pass, on top of a
   now-realistic run.

---

## 7. Decisions — needs red-pen before W1 fires

1. **Relic pool (§3.3):** the ~18-relic representative set and the hook
   vocabulary. Add/drop any; confirm the shared-pool-for-both-characters call.
2. **Relic reward cadence & weights (§4):** treasure/elite/boss/shop relic
   sites and the rarity splits. Auto-take-all vs veto pickup policy.
3. **Potion set, slots (3), drop chance (~40%) (§5.1–5.2).**
4. **Potion use heuristic (§5.3)** — the defensive/offensive thresholds, and
   whether Fairy-in-a-Bottle revive is in scope for v1.
5. **"Ancient" = the treasure-chest relic step** — confirm that's the reading,
   or tell me what you meant.
6. **Sequencing:** relics → ancient → potions, one at a time (not parallel).
   Confirm, or reprioritize.

Nothing schematized here is armed until you've penned it. On your go I fire W1.
