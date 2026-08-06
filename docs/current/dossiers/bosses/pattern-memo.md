# Cross-Boss Pattern Memo — S9 Weekly-Boss Pool (Genshin Trounce/Weekly Bosses)

**Date:** 2026-08-05
**Scope:** Single Fable synthesis pass over all 11 dossiers (Dvalin, Andrius, Childe, Azhdaha, La Signora, Raiden Shogun, Shouki no Kami, Guardian of Apep's Oasis, All-Devouring Narwhal, The Knave, Lord of Eroded Primal Fire). Fable touchpoint 3 of 4, dispatch 2.
**Authority:** ZERO design authority. This memo catalogs patterns and flags translation risk as research input for Phase C's per-boss mini-sprints. It contains no card designs, no proposed numbers, and no verdicts on which bosses to build.

---

## 1. Recurring mechanics across the pool

### 1a. Phase advance by HP gate
- **Azhdaha** — 75% / 45% gates with explicit overkill clamps (damage floors at 65% / 35%).
- **Andrius** — interlude at ~half HP (sources disagree: 55% vs 51%), enrage at low HP (15% vs 20%); gate is burst-skippable.
- **La Signora** — cocoon at 20% of Phase 1 HP; Whirling Blaze at 20% of Phase 2 HP (dual HP-and-time trigger).
- **The Knave** — escalation at 70% of bar one; phase swap at 10% of bar one (widely misreported by guides as 70%).
- **Childe / Guardian of Apep** — sequential full-bar depletion: each phase is its own HP pool rather than a threshold on one bar.
- **Counter-examples worth tracking:** **Dvalin** (ward-break count OR wall-clock timer, no HP thresholds anywhere), **Raiden** (gauge-only, zero HP gates), **Narwhal** (Fury meter, plus a sub-20% *lockout* rather than a gate), **Eroded Primal Fire** (event-driven — first use of a use-capped scripted cast; no documented HP gates). The pool splits roughly half HP-gated, half counter/gauge/event-gated.

### 1b. Gauge- or counter-driven transitions (the non-HP clocks)
- **Dvalin** — cumulative ward-break counter (1/3/5/6) racing a wall-clock timer.
- **Raiden** — Ominous Destiny meter (fills on schedule, accelerates when the boss lands hits; 900 cap).
- **Narwhal** — Fury meter (per-second accrual with a permanent rate doubling at 80s, plus per-1%-HP-lost and per-Eye-destroyed increments; 120 cap).
- **Guardian of Apep** — bidirectional cleansing meter replacing the HP bar entirely in Phase 2 (win at 100%, hard fail at 0%).
- **La Signora** — Sheer Cold / Blazing Heat as a permanent second bar running parallel to HP.

### 1c. Counter-or-punish shields and break-gates
- **Dvalin** — regenerating non-elemental ward (20% Max HP) gating all real HP damage; break → long paralysis window.
- **Raiden** — Baleful Shadowlord shield: self-decaying on a timer, typed weakness (Cryo/Pyro/Dendro), break pays out stun + full party Energy refund.
- **La Signora** — Carmine Chrysalis cocoon: typed break (Pyro / moth pickups) at double gauge rate.
- **Shouki no Kami** — shield as +200% RES soft-immunity depleted by a second actor (the Terminal), not by player damage; break *triggers* the fail-check rather than rewarding directly.
- **Childe** — reactive element-matched shields with probabilistic drop-into-counter (13%) and a 150% counter keyed to *how* you hit it.
- **Eroded Primal Fire** — Void Wards: hit-count durability (1 per elemental hit, 3 per Nightsoul hit), tiered 50/40/24/3.
- **Andrius** — side-object variant: Cryo-shielded pillars broken by reactions (Pyro-weakest).
- **Narwhal** — Arkhe checks: 8-hits-or-1-aligned-hit on the Eye; aligned-hit interrupt on the charging sphere.

### 1d. Interrupt-the-channel checks (channel + supplied counter + payout)
- **The Knave** — Scarlet Nighttide Charged Attack cancels Bloodtide Banquet for 11.2% Max HP True damage.
- **Eroded Primal Fire** — four ward-gated channels; every break pays the identical contract (cancel + boss self-inflicts 10% Max HP + paralysis).
- **Narwhal** — Arkhe hit during the Pneumousia charge cancels and strips 25% of the Shadow's Max HP.
- **Raiden** — Flowers of Remembrance orb-charge race answering The Final Calamity.
- **Shouki no Kami** — Setsuna Shoumetsu: 40-second countdown answered by add-clear plus rebuilt Terminal shot.

### 1e. Scripted arena-wide execute with a supplied answer
- **Raiden** (Final Calamity — shield-piercing insta-kill; only the charged orb's bubble answers), **Shouki** (Setsuna insta-kill through DEF and shields), **Apep** (Aftershocks — 400% ATK full-arena; exactly 3 spawned shields answer), **Eroded Primal Fire** (Starscourge, once per fight), **Dvalin** (Rending Vortex — ground-plane execute answered by verticality).

### 1f. Add waves and kill-priority puzzles
- **Guardian of Apep** — an entire phase of role-typed adds (shield-source, invulnerable-buffer, cannibal, mobility-denial, timer-bomb) around a defended objective.
- **Shouki** — Nirvana Engines: typed-weakness add-clear that funds its own answer (drops charge the Terminal).
- **Raiden** — Illusions (find-the-real-one identification puzzle) and Magatsu Electroculi (hit-count timed bombs; kill → stun, ignore → nuke).
- **Andrius** — phantom-wolf spam as the enrage; pillars as destructible furniture.
- **Narwhal** — randomized 3-payload add table on a missed interrupt.
- **Eroded Primal Fire** — Mimiflora wave under a fog blackout.
- **Strict no-adds fights:** Dvalin, Childe, Azhdaha, La Signora, The Knave — a full third of the pool is deliberately 1v1.

### 1g. Arena denial / floor corruption
- **Dvalin** — permanent, escalating, never-cleansed platform corruption as the entire difficulty curve; terminal phase has no clean tile.
- **Eroded Primal Fire** — three-stage permanent floor *collapse* plus two grades of scorch.
- **La Signora** — Frosted Floor / Embered Earth left by nearly every attack, feeding the temperature gauge.
- **Azhdaha** — infusion-seeded ground hazards (burning marks, shard fields, drifting orbs).
- **Apep** — expanding corruption floor during the execute windup.
- **Shouki** — Raw Frost / Remnant Flame with a typed (opposite-matrix) cleanse; no cleanse in Phase 2.
- **Andrius** — two icy edge-rings with different numbers (interlude vs Phase 2).

### 1h. Enrage timers and soft enrages
- **Dvalin** (wall-clock phase gates + irreversible Energy Lightning), **Andrius** (add-frequency ramp), **La Signora** (Tsaritsa's Benevolence; Whirling Blaze on a drag), **Apep** ("Deadlier creatures incoming..." unlocks the timer-add), **Narwhal** (Fury rate doubling — an accelerating cycle rather than bigger numbers), **Raiden** (the gauge itself is the clock). **Explicitly no enrage:** Childe, Azhdaha, The Knave.

### 1i. Boss resists its own element (near-universal)
Andrius (immune to both of his own elements — the extreme case), Childe (50/50, then 70/70), La Signora (50% Cryo then 70% Pyro), Azhdaha (+60%/+50% to each infused element), Raiden (Electro shield near-immune to Electro), Apep (70% Dendro on a Dendro boss), Narwhal (70% Hydro outside, 70% Electro inside), The Knave (70% Pyro), Eroded Primal Fire (nominal Pyro boss whose real threat budget is Physical + shield-piercing drain). The pool-wide rule of thumb: the punishing element and the profitable element are opposed.

### 1j. Elemental identity shifts / infusion cycles
- **Azhdaha** — two-stage infusion at HP gates, pair fixed per week on a 4-variant rotation, readable before the fight.
- **Childe** — Hydro → Electro → both, per phase, with full moveset replacement.
- **La Signora** — hard Cryo→Pyro mirror-flip with mirrored gauge/floor/corner-object systems.
- **Narwhal** — Hydro outside / Electro inside, per arena.
- **Apep** — Physical Phase 1 → fully Dendro Phase 3 on the same skeleton.
- **Andrius** — Cryo baseline, Anemo *stacked on* (including a recolor of an existing move).

### 1k. Player-side status token as the fight's spine
- **Childe** — Riptide: the only status channel, gates the boss's own lethal tier, consume-vs-retain distinction, positional cleanse station.
- **The Knave** — Bond of Life (healing-hostage debuff), 250% amplifier vs marked targets, Corrosion rider piercing shields, heal-to-arm counter loop.
- **Azhdaha** — elemental mark DoT applied only through unshielded hits (shield = binary gate).
- **La Signora** — temperature gauges fed by hits taken.
- **Eroded Primal Fire** — Attrition: delayed-resolution stacking HP loss that bypasses shields.

### 1l. Boss HP as mechanical currency
- **The Knave** pays 1.5% Max HP to attack and lifesteals on connect; **Eroded Primal Fire** self-inflicts 10% Max HP per interrupted cast (~40% of the fight strippable via the contract); **Narwhal** loses scripted 20% chunks per interior clear; **Shouki** eats a 20% Max HP execute from the unshielded aimed shot.

### 1m. Resource refunds attached to mechanics
Raiden (full Energy on shield break; drain during the shield phase), Shouki (Energy Block economy paid out by the boss's own attacks; full refund on topple), Narwhal (full Energy on interior clear), Apep (20 Energy per Pernicious kill), Eroded Primal Fire (full party Energy per totem), La Signora (moth pickups as one-shot typed imbues).

### 1n. Positional intent conditionals
Azhdaha (flank/rear/range select the attack; Tail Slam baitable), Raiden (teleport-left/right as deterministic tells; behind-her punish), Shouki (published distance/angle-gated AI with anti-kite leash), Andrius (range-conditional Tail Sweep), The Knave (Turning Slash), Apep (behind/close conditionals), Childe (P3 range-split element selection).

### 1o. Anti-burst clamps
La Signora's Pain for Pain (per-instance cap, 30%→20%, with retaliation) is unique in kind; Azhdaha's damage floors and Dvalin's transition clamp are milder relatives. Andrius inverts it: burst is *rewarded* with a structure skip.

---

## 2. Patterns that translate naturally (StS2 vocabulary — observations, not proposals)

- **Discrete counters as phase clocks.** Dvalin's cumulative ward-break count, Raiden's Ominous Destiny, Narwhal's Fury (event-fed components), Apep's bidirectional meter — all are already visible accumulators with named thresholds. A boss meter that increments on events and resolves at a cap is native intent-adjacent grammar, and counter-driven advance survives burst turns in a way HP-percentage gates do not.
- **HP-gate phase triggers with overkill clamps.** Azhdaha's gates-plus-floors and the sequential-HP-pool structure (Childe, Apep, Shouki, Narwhal's interior, Knave's second bar) are the standard multi-form boss shape; clamps read as discrete-state constraints already.
- **Regenerating block gates + stun payouts.** The break-the-gate/cash-the-window loop (Dvalin, Raiden, Shouki, Narwhal, Eroded Primal Fire) is block/armor + a fixed vulnerable-window turn cycle — arguably the single most turn-legible structure in the pool.
- **Tell-then-heavy intent chains.** Tempestuous Barrage always preceding one of exactly two heavies (Dvalin); Fireball as a scripted follow-up beat (Signora); Abyssal Orbs always chaining into Downward Cleave, and rigid A-B-A structures (Eroded Primal Fire); deterministic successor scripting on Fall of Darkness (Knave); deterministic stance-switch moves and left/right teleport tells (Raiden). All are intent-preview mechanics stated in intent-table terms.
- **Countdown-or-die with a supplied answer.** Setsuna Shoumetsu, The Final Calamity, Aftershocks of the Apocalypse, Starscourge — a charging intent, a stated fail payload, and a specific condition that cancels it is one of the most portable set-piece shapes present.
- **Player-side status tokens gating and amplifying boss behavior.** Riptide restricting/unlocking the boss's move pool by player state; Bond of Life's 250% conditional amplifier; consume-vs-retain token rules; deterministic override rules (Childe P3). Intent selection conditioned on a visible player debuff is exactly how an intent table branches.
- **Stacking, discretely-incremented DoTs.** Attrition's per-attack stack counts, Azhdaha's on-unblocked-hit mark, Dvalin's per-instance-incrementing floor tick — stack counters with defined removal conditions, including binary shield-gating of application (Azhdaha) and shield-piercing drains (Corrosion, Attrition).
- **Add waves as kill-priority puzzles.** "These enemies are immune while X lives" (Apep's Protective), invulnerable-while-channeling with an indirect kill condition (Provender), typed add-clear races that fund their own answer (Nirvana Engines), find-the-correct-target puzzles with fixed hit costs (Raiden's Illusions), risk/reward timer adds (Pernicious). All are board-of-enemies constructions with no timing component.
- **Hit-count shields.** Void Wards and Signora's 8-hit corner objects count *actions*, not damage — already the unit a turn economy tracks; the published durability tiers are already a ladder.
- **Per-instance damage caps with retaliation.** Pain for Pain reads almost natively as a clamp-plus-punish rule, with a clean per-phase parameter change.
- **Boss-paid economies.** Shouki's enumerated per-attack Energy Block drops, the Knave's self-HP attack costs and hit/miss ledger, symmetric drain/refund swings attached to state changes (Raiden, Shouki, Narwhal) — resource generation attached to enemy actions and state transitions.
- **A literal published intent algorithm.** Shouki's AI is documented as priority + cooldown + gating condition with random tie-breaks and shared cooldown groups — the same statement a turn-based intent selector would be written in.
- **Per-phase resistance profiles.** Flat, knowable damage-type modifiers that swap at phase boundaries (every boss in §1i), including pre-fight-readable variant seeding (Azhdaha's weekly pairs).

---

## 3. Patterns that resist translation — the hard problems for Phase C mini-sprints

- **Wall-clock time blended into gates and economies.** Dvalin's 2/8/2/8-minute gates, Narwhal's per-second Fury with an 80-second rate doubling, Signora's 3.33%/sec gauges vs 12.5%/sec drains, Raiden's +20-per-2s meter, Corrosion's 2.5s tick, Attrition's 0.5s coalescing buffer. Turn count and elapsed seconds are different axes; every conversion rate is an invention that changes the difficulty curve, and several mechanics (Attrition's "stop getting hit or the bill compounds" buffer) lose their texture at any chosen resolution point.
- **Spatial positioning as the payload.** Safe pockets and geometric answers (God Arrow's center/edges, Rebuke's safe center, Musou no Hitotachi's safe rim), arena quartering and corner objects (Signora), shrinking/collapsing/corrupting floors as the difficulty axis itself (Dvalin, Eroded Primal Fire), adds physically pathing toward an objective (Apep's interception geometry), facing and behind-the-boss punishes, distance-gated intent forks and anti-kite leashes (Shouki), proximity-scoped auras. Without a board, "where you stand" — the majority of the pool's threat budget — has no referent, and raw ATK% values were balanced against sub-100% expected hit rates.
- **The dodge-i-frame taxonomy.** Nearly every dossier distinguishes attacks that can vs cannot be dodged through dash i-frames (and sometimes *can* via burst i-frames). The distinction only exists because a dodge verb exists; in discrete turns the entire category collapses into ordinary unmitigated damage.
- **Verticality.** Anemograna updrafts as combined traversal-and-defense resource (Dvalin), Upcurrent dodging Electrostreak (Shouki), attacks lacking vertical AoE (Childe), airborne adds. A third axis with no turn-based representation.
- **Aiming and sub-model hitboxes.** Weak points (Dark Shadow, the Knave), chest-only RES windows (Shouki), talon/head/back-crystal exposure hierarchies (Dvalin), manual aimed shots. "Where on the enemy your attack landed" is not a turn-based concept; the flat modifiers translate, the reasons they exist do not.
- **Forced movement and pure displacement.** Vacuum fields, knockbacks, pull-then-detonate setups, cage walls (Starscourge totems, Perch barriers). Effects whose entire payload is moving a body through space do nothing once space is abstracted.
- **Information denial.** Dvalin's fixed camera that hides the charging boss (load-bearing enough to ban co-op), Eroded Primal Fire's fog blackout. A turn interface shows intents by construction; hiding the boss is not something it can do without being unfair.
- **Foreign substrate systems.** The elemental aura/reaction gauge-unit layer (Azhdaha's cleanse matrix, bomb defusal, 8GU imbues), the energy-orb burst economy, the four-character standby-party layer (Corrosion drains off-field characters), and pre-fight roster gates (Arkhe alignment, Nightsoul 3x ward efficiency, region-specific fog clears). These are party-composition and simulation layers underneath the fights, not fight mechanics — a run-based deck has no guaranteed pre-fight roster slot, so any port either removes the check or converts it into draw variance.
- **Uptime and execution speed as the reward.** Submerge-gated targetability (Narwhal), paralysis windows whose value is how much rotation you physically execute (Shouki's ~20s, Dvalin's climb), interrupts that must land mid-animation (Knave, Raiden's reactive shield). A turn-based window grants fixed actions and cannot reward speed; forced transitions can never interrupt anything mid-action, which deletes the devour's specific drama (Narwhal).
- **Sub-turn damage cadence.** Ticks every 0.1–0.5s, dwell-time damage in beams/scorch/contact projectiles, per-second slows. The interesting quantity is how long you linger — a quantity turns cannot see.

---

## 4. Per-boss adaptation-difficulty notes (ranked easiest → hardest)

Ranking is a judgment call on the ratio of turn-legible spine to spatially/temporally load-bearing content, per each dossier's own natural/resistant analysis. It is research input only — not a build order, not a recommendation of which bosses to attempt.

1. **The Knave (Arlecchino).** The most compact state space in the pool: boss HP/phase, per-character Bond stacks, Corrosion ticks, Nighttide charges — fully enumerable, with no adds, no environmental hazards, no timers, and a plain arena by design. Bond of Life is already "a card-game status wearing an action-game costume" (stacking healing-hostage counter, conditional 250% amplifier, shield-piercing drain rider), and the heal-to-arm-the-counter loop is an economy decision, not an execution one. The hard residue is the ranged-immunity leash (a continuous proximity state with a "blocked in quick succession" counter), the animation-scoped Banquet interrupt window, facing-conditional Turning Slash, and the telegraph-then-delayed-eruption spatial puzzles that carry most big intents.

2. **Childe (Tartaglia).** The Riptide spine — a binary persistent token that gates the boss's own move pool, with consume-vs-retain and deterministic override rules — is intent-table branching stated in the game's own terms; three sequential stat blocks, no adds, no enrage, and a probabilistic reactive-shield/counter architecture round out a highly legible core. The mini-sprint's hard problems: the entire Ultima tier is defined by geometric safe-pocket telegraphs; Phase 2's identity is reaction-time and stamina; the cleanse station's real cost is travel time; and the shield is a mid-animation interrupt whose information-holder changes if it must be declared in advance.

3. **La Signora.** Pain for Pain (per-instance cap + retaliation, tightening per phase), the passively-filling temperature gauges, the typed cocoon interphase, moth pickup tokens, scripted openers/combos, and dual HP-or-time enrages all read nearly natively. The resistant core is concentrated in one subsystem: the corner objects — continuous proximity drain, arena quartering, hit-count durability entangled with a real-time respawn economy, and a consume-vs-preserve tension measured in wall-clock seconds — plus a kit that is mostly execution-defined projectile dodging.

4. **Guardian of Apep's Oasis.** Phase 2's bidirectional meter is literally arithmetic on a shared counter with discrete increments and win/loss thresholds, and the role-typed add roster (kill-priority shield source, invulnerable buffer with an indirect kill condition, risk/reward timer bomb) is native board vocabulary; the event-driven soft enrage and the telegraphed 400% execute with a limited-slot answer are clean shapes. What resists: the phase's *tension* is interception geometry (adds pathing toward the Heart), the boss's universal verb is emerge-at-your-position, the Perch is pure movement denial with no non-spatial meaning, and the shields-scramble only bites when locations are finite and contested.

5. **Raiden Shogun.** Zero HP gates anywhere — the gauge, the two-stance intent tables with deterministic switch moves and left/right teleport tells, the self-decaying typed shield with a payout on break, the Illusions/Electroculi hit-count puzzles, and the charge-the-orb-or-die set piece form an unusually complete turn-legible skeleton. The hard problems are real: the gauge runs on wall-clock seconds; the Follow-Up punish, safe-rim geometry, and movement-tracking eye spawns are purely positional; the melee shield's risk scales with attack *speed*; and The Final Calamity's "ignores all mitigation except one specific answer" plus its i-frame escapes are engine artifacts a turn frame can only flatten.

6. **Azhdaha.** HP gates with overkill clamps, pre-fight-readable weekly variant seeding, intent re-skinning (same skeleton, swapped element + rider), fixed multi-hit counts, a binary shield-gated mark DoT, and no adds — a strong discrete spine. But the fight's actual decision layer is positional intent selection (flank/rear/range choose the attack; baiting Tail Slam delays the Phase 3 ranged threats), and the mark's cleanse rules sit on the full aura-reaction simulation; the dodge-taxonomy and continuous DoT zones carry much of the remaining difficulty.

7. **Andrius.** Clean structure — HP-gated phases, a discrete attack menu with range-conditional branches, delayed-detonation mines, destructible typed pillars whose detonation is a two-way resource, add-ramp enrage, even a burst-skip rule. Yet the identity lives in movement: the interlude is a movement script that degenerates to "boss skips turns while a DoT ticks," Wolf King Roar's inverted distance scaling has nothing to read without position, the arena-edge squeeze and facing-cones are pure geometry, the dodge-proof category collapses, and the open-world engine layer (World Level scaling, despawn) plus the energy-orb economy are foreign systems.

8. **Shouki no Kami.** The biggest gift in the pool — a *published* priority/cooldown/range-gated AI table, an enumerated boss-paid resource economy, a two-step combo with stated window and miss cost, a countdown insta-fail with symmetric resource swings, and typed adds that fund their own answer. The equally big problem: nearly every player-side verb is spatial — matrices are floor tiles you stand on, the Terminal's shots are manually aimed, the vulnerability is a chest-only hitbox, Electrostreak is dodged by altitude, and the position/angle-gated AI presupposes kiting. The mechanics port; the solutions don't.

9. **Lord of Eroded Primal Fire.** Attrition and the Void Ward are the most card-native status/shield pair in the pool (delayed-resolution stack counter that pierces block; hit-count shields with a published durability ladder), and the four-gate interrupt-punish contract plus hard use-counters give a countable structural spine. But the fight's *signature* is geometric and informational: three permanent floor-collapse stages, an 80%-Max-HP fall penalty, a fog blackout answered by roster membership, vacuum setups, a cage you physically cannot leave, and Nightsoul/regional hooks reaching outside the fight — plus ATK% values balanced against real-time dodge rates.

10. **All-Devouring Narwhal.** Strong naturals — deterministic player-influenced devour, scripted 20% deductions, discounted sub-boss revisits, the Arkhe interrupt shape, the sub-20% lockout endgame. But the Fury meter blends wall-clock accrual (with an 80-second permanent doubling that has "no honest turn equivalent") into its counter; the surface fight's entire content is submerge-gated uptime prediction; Arkhe is a pre-fight roster guarantee a run-based deck can't replicate without changing the check's nature; the Weak Point is an aim check; and the fight-inside-a-fight presentation plus the devour's mid-action interruption are, per the dossier, partly unrecoverable in atomic turn resolution.

11. **Stormterror Dvalin.** The ward/paralysis loop and counter-driven (never HP-driven) phase gates are excellent turn grammar, and the fight is a clean 1v1 with a genuine intent-tell (Barrage → one of two heavies). Everything else is the hard problem list in concentrated form: the arena *is* the difficulty (permanent platform corruption, out-of-bounds as a live failure state that also cancels the reward window), verticality is the answer to multiple attacks via a shared traversal/defense resource, the fixed non-tracking camera is stated difficulty, the DoT's per-instance escalation lives at sub-turn granularity, the dual gates race a wall clock, and the burst-window target is reached by climbing the boss model. The most spatially/temporally load-bearing fight in the pool.

---

## Sources-quality note

All 11 dossiers arrived web-verified by the earlier research touchpoints: each cites Fandom wiki wikitext retrieved via the MediaWiki API as primary source, with cross-checks against KQM's Theorycrafting Library and/or independent guides (Game8, GameWith, TheGamer, ScreenRant, PlayerAssist, RaiderKing, ensigame, etc.). None is model-knowledge-only. Caveats the dossiers themselves flag, preserved here for Phase C: (a) **Andrius** — Fandom and KQM disagree on exact HP gates (55/15 vs 51/20, plus differing burst-skip conditions); treat "roughly half" and "low HP" as reliable, the precise percentages as unresolved. (b) **Dvalin** — the widely-circulated "25% HP meteor shower" claim is debunked by the wiki's break-count/timer table. (c) **The Knave** — Game Rant's "4.5" and "70% = phase 2" claims were identified as wrong and rejected in favor of the wiki. (d) **Eroded Primal Fire** — no source documents HP-percentage gates; any HP threshold beyond the self-inflicted 10% losses would be fabrication; TCG-card pages were explicitly excluded from boss data. (e) **Shouki** — the ~20-second Phase 1 paralysis duration is community-reported, not wiki-published. (f) Several dossiers note specific numbers deliberately omitted where two-source confirmation failed (Dvalin platform count, paralysis frame data) and sources that failed to load through the proxy (Game8/gamerguides 403s) counted only as snippet-level corroboration. This synthesis pass performed no new retrieval and adds no facts beyond the dossiers; the ranking in §4 is the only new judgment introduced.
