# Tier 0 Balance Simulator — Design Spec & Handoff

**Project:** Genshin Impact character mod for Slay the Spire 2 (working title: "Teyvat Spire")
**Deliverable:** A standalone Python Monte Carlo combat simulator for validating card designs *before* any in-game implementation.
**Audience:** Claude (in Claude Code). This doc is written by Claude (in claude.ai chat) as a handoff. Read the commentary section first — it explains why this exists and what to avoid.

---

## 0. Commentary from your chat-instance self (read this first)

Hey — context you need, since you weren't in the room:

**What this project is.** The user and I are designing a StS2 mod that adds Genshin Impact characters, starting with Klee. StS2 is Godot 4.5 + C# ("MegaDot" engine, .NET 9, ships with HarmonyLib and an official mod loader). We analyzed the Downfall StS2 port (github.com/lamali292/Downfall) as our reference: one character ≈ 5–7k LOC of C#, ~75–90 cards, ~20 powers, ~10 relics. The expensive engineering piece in our design is an **elemental aura + reaction system** (details in §4.4). Everything else is assembly-line card work.

**Why Tier 0 exists.** We committed to "framework first, cards second." Before writing any C#, we want to validate card designs numerically: does Klee's damage curve resemble a fair StS character, or is she Watcher 2.0? The full testing plan is tiered: Tier 0 = this simulator (design-time, thousands of fights/min, models only OUR numbers); Tier 1 = the game's built-in `AutoSlay` bot for crash testing (yes, MegaCrit shipped their test bot in the binary — a Nexus mod unlocks it); Tier 2 = HTTP-bridge bots on the real game (precedents: STS2MCP, auto-spire) for run-level winrate stats; Tier 3 = headless reimplementation (only if Tier 2 throughput is insufficient — precedent exists in zhiyue/sts2-rl-agent).

**What Tier 0 is NOT.** It is not a StS2 reimplementation. It is disposable design tooling — a spreadsheet with a combat loop. Resist the urge to model relics we haven't designed, the map, potions, shops, intents-as-AI, or multiplayer netcode. Every hour spent making the simulator "more faithful" beyond this spec is an hour not spent on the mod. If a design question can't be answered by this sim, the answer is "test it in Tier 1/2," not "extend Tier 0."

**Known epistemic gaps.** Exact StS2 enemy statlines are not reliably known to us and change with EA patches anyway. That's why §5 defines the encounter battery *behaviorally* (calibrated so reference decks hit target outcomes) rather than as copied game data. All numeric constants in this doc are **tunable starting points**, not gospel. Put them all in one `constants.py` / YAML file.

**The user's workflow quirk that matters to you:** they will iterate card designs as data rows and re-run the battery constantly. Fast iteration loop > elegance. Single command, CSV out, summary table in terminal.

---

## 1. Goals & non-goals

**Goals**
1. Score any character design on the seven evaluation axes (§2) via simulated combat against a fixed encounter battery (§5).
2. Compare candidate Klee card pools against two calibrated reference characters (simplified Ironclad, simplified Silent) so results read as "relative to baseline," never absolute.
3. Validate the elemental reaction system's math (amplification stacking, aura economy) under realistic play.
4. Detect degenerate loops: infinite detection, runaway multiplicative scaling.
5. Support archetype-tagged sub-pool testing: simulate "Demolition-weighted deck" vs "Reaction-weighted deck" vs "Spark-weighted deck" separately.

**Non-goals (v1)**
- No map/pathing, events, shops, potions, gold.
- No multiplayer (co-op reactions are validated in Tier 2; the reaction *math* is identical solo).
- No upgrade paths (model upgraded cards as separate rows if needed).
- Relics: ONLY as simple passive hooks (needed for Klee's starting relic). No relic pool.
- No exact StS2 fidelity. Simplifications are fine if applied equally to Klee and the reference decks.

---

## 2. The seven evaluation axes (scoring output)

Each simulated character/deck configuration produces a 7-axis scorecard, each axis normalized so **simplified starter-deck Ironclad = 3.0**:

| Axis | Metric (from sim logs) |
|---|---|
| A1 Frontload | Avg total damage dealt turns 1–3, per energy spent |
| A2 Scaling | Avg damage per turn at turns 8–10 ÷ turns 1–3 (curve shape logged separately: fit linear vs superlinear) |
| A3 Block economy | Effective mitigation per energy (block used + damage prevented by kills/debuffs) |
| A4 Sustain | Net HP delta per fight (healing − chip taken) |
| A5 Velocity | Cards drawn + energy generated above base, per turn |
| A6 Utility | Composite: AoE coverage (swarm-fight TTK vs single-target TTK ratio), debuff uptime |
| A7 Setup tax | Turns until DPT exceeds 1.5× starter-deck baseline; folds-under-pressure = winrate delta between Punisher and Attrition encounters |

Balance heuristic (report should flag violations): a healthy character scores **4–5 on exactly two axes and ≤2 on at least one**. Flat 3s = boring; no weakness = broken.

---

## 3. Architecture

```
tier0/
  constants.py          # ALL tunable numbers live here
  engine/
    state.py            # CombatState, Player, Enemy, Deck/Hand/Discard/Exhaust piles
    effects.py          # atomic effect resolvers (the DSL)
    powers.py           # counter-based powers with hook points
    reactions.py        # elemental aura + reaction resolver  ← the important one
    combat.py           # turn loop
  content/
    cards/*.yaml        # card definitions as data (schema §4.1)
    characters/*.yaml   # character defs: HP, starting deck, relic hooks
    encounters/*.yaml   # encounter battery (schema §5)
    pilots/*.yaml       # pilot policy weights per archetype (§6)
  pilot/
    policy.py           # rule-based card-play pilot
  harness/
    runner.py           # CLI: run N fights × battery × configs, seeded
    metrics.py          # axis computation, degeneracy detectors
    report.py           # terminal summary table + CSV/JSON dump
  tests/                # pytest: effect resolution, reaction table, determinism
```

- Python 3.11+, stdlib + PyYAML; numpy optional. No other deps.
- Fully deterministic per seed. `--seed`, `--fights N` (default 1000/encounter), `--config`.
- Target throughput: ≥500 fights/sec on one core for a 12-turn fight. If you can't hit that, simplify — don't optimize cleverly.

## 4. Core model

### 4.1 Card schema (this schema IS the design deliverable — the mod's card sheet will use the same columns)

```yaml
id: jumpy_dumpty
name: "Jumpy Dumpty"
cost: 2                  # int, or "X"
type: attack             # attack | skill | power
rarity: common           # basic | common | uncommon | rare
element: pyro            # pyro|hydro|electro|cryo|anemo|geo|dendro|none
solve: [frontload, utility]      # primary axes served (A1..A7 names)
archetypes: [demolition]         # demolition | reaction | spark | generic
role: enabler                    # enabler | payoff | glue
effects:
  - {op: damage, amount: 7, target: random_enemy, times: 2, applies_element: true}
  - {op: place_bomb, amount: 2, target: random_enemies, bomb_damage: 6}
exhaust: false
tags: [companion?]       # companion cards get companion: {nation: mondstadt, unit: xingqiu}
```

### 4.2 Effect DSL — atomic ops (v1 complete list; extend only when a designed card demands it)

`damage` (target: enemy|all_enemies|random_enemy, times, applies_element), `block`, `draw`, `energy`, `apply_power` (self or enemy: strength, weak, vulnerable, poison-like DoT), `apply_aura` (element, no damage), `place_bomb` (delayed damage charge, see below), `gain_spark`, `heal`, `add_card` (token to hand/discard), `exhaust_from` (hand random/choice-as-random), `scry_discard` (look N, discard worst by pilot heuristic).

**Bombs (Klee signature):** a Bomb is a charge on an enemy: detonates at start of owner's next turn for `bomb_damage` + applies Pyro; detonates early if that enemy is hit by an Attack card. Detonation triggers relic hooks.

**Sparks (Klee resource):** counter on player. At 3 Sparks: next Attack costs 0 (consume all 3). Starting relic hook: +1 Spark per Bomb detonation.

### 4.3 Powers
Counter-based with four hooks: `on_turn_start`, `on_turn_end`, `on_deal_damage(mod)`, `on_take_damage(mod)`. Implement only: Strength, Weak (−25% dealt), Vulnerable (+50% taken), a generic DoT, Metallicize-like, and the elemental auras (§4.4). Nothing else until a card needs it.

### 4.4 Elemental auras & reaction resolver — validate this carefully
- Auras are enemy-side flags with a duration (default: 2 owner-turns; tunable).
- One aura per enemy in v1 (new same-element hit refreshes; new different-element hit = check reaction table).
- Damage tagged with element E hitting enemy with aura A ≠ E: consume A, apply reaction:

| Trigger on aura | Reaction | v1 effect (tunable) |
|---|---|---|
| Pyro on Hydro / Hydro on Pyro | Vaporize | that hit ×1.5 |
| Pyro on Cryo / Cryo on Pyro | Melt | that hit ×1.75 |
| Pyro on Electro (either) | Overload | +6 damage to ALL enemies |
| Electro on Cryo (either) | Superconduct | apply Vulnerable 2 |
| Hydro on Electro (either) | Electro-Charged | apply DoT 4 (2 turns) |
| Hydro on Cryo (either) | Frozen | enemy skips next intent |
| Anemo on any aura | Swirl | copy aura to all enemies |
| Geo on any aura | Crystallize | player gains 4 Block |

- **Critical property to preserve:** amplifiers (Vaporize/Melt) affect ONE hit and consume the aura. They must never become a persistent multiplier. Add a pytest asserting this.
- Instrumentation: log reactions/fight, damage share from reactions, aura wasted (expired unconsumed). Klee's reaction-archetype health = reaction damage share 25–45% in a Reaction-weighted deck; >60% means amp numbers are carrying too hard.

### 4.5 Enemies
Enemies are statlines + a fixed rotating intent script (no AI): each intent = attack(N×times) | block(N) | buff(strength+N) | debuff(weak/vulnerable) | summon(wave). Scripts defined per-encounter in YAML.

## 5. Encounter battery (behaviorally calibrated)

Six fights. Numbers below are starting points; calibrate per §7 and then FREEZE for all comparisons.

1. **SWARM** — 5 × (14 HP, attack 4). Tests AoE (A6). Target: starter Ironclad clears in 5–7 turns, loses 8–14 HP.
2. **PUNISHER** — 1 × (90 HP, attacks 9×1 ramping +2/turn after turn 3; punishes slow starts). Tests A1. Target: starter Ironclad wins ~50–60%, avg −18 HP.
3. **ATTRITION** — 2 × (45 HP, alternating attack 6 / block 8 / debuff weak). 12+ turn grind. Tests A3/A4.
4. **BURST CHECK** — 1 × (60 HP, sleeps 3 turns then attacks 24). Deal 60 by turn 4 or eat the hit. Tests burst-on-demand (A6).
5. **TANK BOSS** — 1 × (240 HP, attack 12 / buff strength+2 / multi-attack 6×3 rotation). Tests A2 scaling shape.
6. **GAUNTLET** — SWARM then PUNISHER back-to-back, HP carries over. Tests A4/A7 composite.

## 6. Pilot policy
Rule-based greedy with two hard rules, then weighted scoring:
1. If lethal is playable this turn, play it.
2. Else if incoming damage ≥ threshold (config: 40% of remaining HP), prioritize block until covered.
3. Else score each playable card: `w_damage·expected_damage + w_block·block + w_scaling·scaling_value + w_reaction·reaction_setup_or_trigger + w_tempo·(draw+energy) − w_cost·cost`, weights from `pilots/*.yaml`. One weight file per archetype (demolition/reaction/spark/generic) so archetype comparisons aren't confounded by pilot behavior.
- Deliberately dumb is fine; both Klee and reference decks use the same pilot. Log a `pilot_regret` sample (random 1% of turns: was a strictly-better single play available?) as a sanity metric, don't chase it.

## 7. Calibration & references
Implement two reference characters from public StS knowledge, simplified:
- **REF_IRONCLAD:** 80 HP, 5×Strike(6), 4×Defend(5), Bash(8+Vuln2). Plus a 10-card "archetype package" (strength ramp: Inflame-like +2 STR, Heavy-Blade-like STR×3, etc.).
- **REF_SILENT:** 70 HP, starter equivalent + Shiv package (0-cost 4-dmg tokens, +damage-per-shiv scaler) — the multiplicative reference.
Procedure: tune §5 statlines until REF_IRONCLAD starter hits the behavioral targets → freeze battery → REF_IRONCLAD = 3.0 on all axes by construction → score REF_SILENT (expect: A1≈2, A5≈4.5, superlinear A2) as the validity check. If Silent doesn't look like Silent, the axes are miscomputed — fix before touching Klee.

## 8. Degeneracy detectors (run always, report loudly)
- **Infinite detector:** any turn where cards played > 25 or a (hand,piles,energy) state repeats within a turn → flag INFINITE, log the loop's card sequence.
- **Runaway scaling:** DPT turn 10 > 8× DPT turn 3 → flag SUPERLINEAR with fitted exponent.
- **Amp stacking:** any single hit > 4× its base damage → log multiplier provenance.
- **Aura starvation (Klee-specific):** Reaction-deck fights with 0 reactions triggered → % reported (draft-gating health check).

## 9. Milestones (each independently runnable)
1. **M1 Engine core:** state, effects DSL, powers, combat loop, one encounter, REF_IRONCLAD starter, pytest green, determinism test (same seed = identical log).
2. **M2 Battery + calibration:** all six encounters, calibration procedure run, battery frozen, axis computation, terminal report.
3. **M3 References validated:** REF_SILENT scores sane. Ship the scorecard format.
4. **M4 Klee systems:** reactions module + bombs + sparks + companion tagging, degeneracy detectors, pilot weight files. Smoke-test with ~10 placeholder Klee cards (I'll deliver the real card sheet separately — build the schema, not the cards).

## 10. Open questions (decide yourself, note decisions in a DECISIONS.md)
- Hand size / draw-per-turn: use 5-draw/10-hand StS defaults unless something breaks.
- Aura duration & reaction magnitudes: starting values above; expose all in constants.
- Whether Frozen on bosses needs a resistance rule (probably yes: bosses consume Frozen for 50% less effect or immunity — your call, log it).

*— end of spec. Have fun. Don't gold-plate it.*
