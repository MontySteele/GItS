# Rulings R23–R25 + companion scoping note (2026-07-20, chat → Code)

Ruled after the post-worknote inventory of remaining Klee cards/mechanics.
The inventory's suggested build order is APPROVED as the standing plan:
aura application → Burst-energy spike (CustomResource) → power cards (the
Burst last) → bomb-manipulation ops → codegen widening → companions.

## R23 — Aura application pass: GO

Highest-leverage next step: turns on the already-shipped reaction stack AND
the ratified Pyro-on-detonation — the moment the demolition deck starts
feeding reactions (the mod's core loop, live).

Burst-energy note for the upcoming spike: the sim's particle economy is LAW
(skill tags 5, reactions 5; Klee meter 60). Whatever CustomResource shape
wins the spike, the numbers come from tier0 constants, not re-derivation.

**Execution (this session):**
- `KleeElementalHooks` (Powers/ElementalApplication.cs): standing combat-hook
  listener via `ModHelper.SubscribeForCombatStateHooks` — the game's
  first-party mod-subscriber API, verified in the CombatState decompile
  (IterateHookListeners ends by yielding subscribed mod models). No Harmony.
- Application happens in `BeforeDamageReceived` (pre-hit), mirroring tier0
  resolve_hit's mid-pipeline application: a blocked hit still applies its
  element, and — ordering-safety — AuraPower consumes auras post-hit
  (AfterDamageReceived), so the listener can never mistake a just-consumed
  aura for "no aura" and wrongly stick the trigger element.
- `AuraCmd` (same file): Find / Apply / Refresh shared plumbing; Apply is the
  port of tier0 apply_aura (trigger-only Anemo/Geo never stick).
- BombPower.Detonate: each detonation is now a Pyro-tagged hit resolved
  explicitly before the damage lands (tier0 parity: detonate_bombs →
  deal_damage_to_enemy(element="pyro")). Pyro applies/refreshes on no-aura /
  Pyro-aura enemies; on off-element auras it consumes and reacts — Vaporize
  and Melt amplify the detonation itself. Detonation damage stays Unpowered
  with no card source, so it cannot be elementally resolved twice.
- Unblocked, hand-written (registered in KleeCardPool; pool now 37):
  - **Sizzle** — 7 + 5 if the target has a non-Pyro aura. Predicate
    snapshotted before the first hit (tier0 `target_has_nonpyro_aura`): the
    card's own hit consuming the aura is exactly what the bonus rewards.
  - **Flame Dance** — 7 ALL, +4 vs aura'd enemies, via ModifyDamageAdditive
    on the card (cards in piles are hook listeners; Strength/Vigor idiom, so
    previews show the bonus per enemy).
  - **Kaboom Beetle Swarm** — 5 ×3 random, +3 per hit vs Bombed enemies
    (same idiom; bomb state read at hit time, so an early detonation ends
    the bonus mid-card, as in the sim).
  - **Elemental Ecstasy** — refresh all auras, draw 1 per aura (tier0
    _op_refresh_all_auras + per_aura draw).
- Art: sizzle/flame_dance had picks already; kaboom_beetle_swarm ←
  Tomato Pepper Jumpy Dumpty AoE, elemental_ecstasy ← Klee Birthday 2025 —
  both shortlist-grade from already-fetched raws (L1 rejected the first
  picks as duplicates), FLAGGED for red-pen with the other residuals.
- Not yet reachable in mono-Klee play: off-element auras need companions, so
  Sizzle's bonus, Vaporize/Melt on detonation, and Frozen paths are dormant
  until then — but Pyro application, refresh, aura expiry, and the
  aura-reading cards are all live.

## R24 — Upgrade-delta wiring: RULED, sheets are the single source of truth

Wire ALL delta keys from *-upgrades.yaml through codegen. Codegen defaults
are ABOLISHED, not demoted: a generated card whose sheet has no ratified
delta gets NO upgrade path and a loud manifest flag (tier0 UNAPPLIABLE
discipline applied to C#) — silent defaults are how CCM shipped +3 block
against a ratified +2. One regen fixes every existing mismatch.

**Execution:** gen_klee_cards.py UPGRADE_* constants deleted; build_upgrade
consumes damage/block/draw/spark/bomb_damage/cost (cost via
`EnergyCost.UpgradeBy`, the idiom CardModel.OnUpgrade's own doc comment
prescribes). Partial application is forbidden — an inexpressible key blocks
the whole upgrade path. Regen changed every card where sheet ≠ default
(cant_catch_me +3→+2 block and dropped the unruled draw bump; crackle
+3→+2; rapid_fire +2→+1; bombs_away and all_my_treasures swapped wrong
damage bumps for cost −1; etc.). Sole flag: hot_hands (`remove:
self_damage` is structural — no upgrade path until hand-finished or
re-ruled numeric), recorded in manifest.json `upgrades.no_upgrade_path`.

## R25 — dodge_roll domination errata: QUEUED

Delta: `dodge_roll: {block: -2}` (8 → 6; status-exhaust rider unchanged).
Hide and Seek stays the bigger flat block at common; dodge_roll becomes the
utility trade at uncommon. Rides in the CCM errata batch — same sheet, same
window discipline; neither touches spark generation, so they may land
together, but only AFTER the R10 Crackle measurement window runs.

**Execution:** QUEUED ERRATA comment above the dodge_roll row in
klee-cards.yaml, mirroring CCM's. No code change (dodge_roll is blocked on
`exhaust_from`).

## Companion-system scoping note (pre-ruling)

"Playing a companion card" is NOT a new mechanic — companion cards are
ordinary cards in a colorless-style shared pool (principles §4.1;
CustomCardPoolModel.IsColorless is first-class in the StS2 API); their
effects are normal card effects; Oz-style summons are powers, same as
Klee's own. The genuine engineering is ACQUISITION: the 4th reward slot,
nation weighting (constants from tier05.rewards), and pool registration.
Full spec when companions reach the front of the queue.
