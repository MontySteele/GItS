# Klee — Character Design Doc (v0.1)

**Files:** `klee-cards.yaml` (75-card pool), `mondstadt-companions.yaml` (16 companion cards). Governed by `teyvat-spire-design-principles.md`; tested per `tier0-simulator-spec.md`.

## 1. Identity
The Spark Knight. Pyro, **catalyst-grade cadence** (every attack applies Pyro — maximum reaction fuel, so base numbers run low). Delayed explosives, random targeting, gleeful fragility. She enables any reaction instantly and can trigger none alone.

## 2. Declared statline (Ironclad = 3.0; declare BEFORE tuning, sim validates)
| Axis | Target | Rationale |
|---|---|---|
| A1 Frontload | **4.5** | Bombs + spray; her signature strength |
| A2 Scaling | 3.0 solo → 4.0 drafted | Grand Finale/Workshop are linear; real ceiling is draft-gated (companions/artifacts) |
| A3 Block | **2.0** | Reluctant, conditional defense |
| A4 Sustain | **1.5** | Declared weakness. 62 HP. Barbara is the drafted answer |
| A5 Velocity | 3.5 | Sparks = free plays; modest draw |
| A6 Utility | **4.0** | Excellent AoE / poor precision (random targeting is the tax) |
| A7 Setup tax | 3.5 | Online turn 1–2; folds to sustained pressure (see A3/A4) |
Companion appetite: **Standard**. Balance check: 4–5 on exactly two primary axes (A1, A6) ✓, ≤2 on at least one (A3, A4) ✓.

## 3. Core mechanics (numbers = sim starting points)
- **HP 62, energy 3, draw 5.** Starting deck: 4× Kaboom!, 4× Duck and Cover, 1× Jumpy Dumpty, 1× Pop!
- **Bombs:** charge on an enemy. Detonates at start of Klee's next turn for its damage + Pyro; detonates **early** if the enemy is hit by an Attack card. Multiple bombs stack independently. Detonations fire relic/power hooks.
- **Sparks:** at **3 Sparks**, next Attack costs 0 (consumes 3). Starting relic **Pounding Surprise** (talent-relic): +1 Spark per Bomb detonation.
- **Burst Energy:** meter 60. +5 per Skill-tagged card (`tags: [skill_tag]`), +5 per reaction triggered. **Sparks 'n' Splash** requires full meter, empties it.
- Loop: place turns → detonation turns → Sparks smooth the energy curve → any off-element companion ignites the reaction layer.

## 4. Archetypes (tag matrix validated by `validate.py` output)
1. **Demolition** (28 cards, enabler-rich) — default plan. Setup/payoff rhythm; payoffs: Blazing Delight, Chained Reactions, Grand Finale.
2. **Spark Spray** (21 cards, even role mix) — velocity plan; zero-cost volume, Gleeful Barrage as the scaler. Structural Shiv-analogue.
3. **Reaction** (14 personal cards, **payoff-heavy by design**) — DELIBERATE ASYMMETRY: this archetype's *enablers live in the companion pool* (Xingqiu/Fischl/Kaeya appliers, Sucrose/Prune triggers, Durin amp). Her personal cards only reward auras (Sizzle, Perfect Timing, Flame Dance) or accelerate Burst. Aura-starvation detector (Tier 0 §8) is this archetype's health metric; target <15% zero-reaction fights in a Reaction-weighted deck.
Bridges: Sorry Jean (block↔demolition), Sparkly Explosion (demolition↔spark), Friendly Visit / Study Buddy / Best Friends Forever (anything↔companions).

## 5. Relics & potions (v0.1 sketch — design after sim pass 1)
- Starting: **Pounding Surprise** (above). Character relics (~8): bomb-count+, spark-threshold, burst-energy-carryover (Favonius-flavored), companion-slot upgrade, detonation lifesteal (patches A4 at relic rarity, not card rarity — deliberate), etc.
- Potions: Bottled Fireworks (place 3 bombs), Spark Cider (gain 3 Sparks), Warm Milk (heal; Jean insists).

## 6. DSL extensions required (Tier 0 M4 scope — beyond spec §4.2 v1 ops)
`detonate`, `move_bombs`, `modify_bombs`, `burst_energy`, `swirl`, `refresh_all_auras`, `buff_next_attack`, `cost_mod`, `conditional` (predicates: this_cost_zero, has_spark, target_has_nonpyro_aura, reaction_triggered_by_this, killed_target), `repeat_this`, formula amounts (`times_formula`, `bonus_formula`, `X_plus_1`), companion ops (`copy_companion_in_hand`, `replay_next_companion`, `copy_companions_played_this_combat`), and powers: bomb_damage_up, zero_cost_attacks_up, spark_per_turn, detonation_splash, detonation_vuln, spark_threshold_down, amp_reaction_up, bomb_and_spark_per_turn, sparks_n_splash, plus companion powers (oz_summon, solar_isotoma, witchs_flame, celestial_gift). Implement lazily — a stubbed op that logs UNIMPLEMENTED is fine for pass 1; prioritize whatever the Demolition/Spark decks need first.

## 7. Sim test plan (order matters)
1. Starter-deck Klee vs battery → confirm A1/A3/A4 shape vs REF_IRONCLAD before any archetype packages.
2. Demolition-weighted, Spark-weighted, Reaction-weighted (12 companions injected at realistic draft rates) → axis scorecards + degeneracy detectors.
3. Watchlist: Vermillion Pact + Durin + Melt stacking vs the 4× amp cap; Gleeful Barrage + spark engines for runaway; Playtime Forever + Blazing Delight loop density.
4. Dream-team config (Prune + Durin + Nicole + Albedo forced into deck) — should be strong, NOT dominant vs a focused Demolition deck. If it dominates, nerf the Rares' numbers, not the structure.

## 8. Asset punch list (for eventual art pass)
75 card portraits (500×380), ~24 power icons, ~10 relic icons, 16 companion portraits, char select art, energy icon, map marker, combat visual (layered-PNG Godot scene, Hexaghost-style — no Spine needed for v1), ~4 SFX. All original/commissioned per principles §9.
