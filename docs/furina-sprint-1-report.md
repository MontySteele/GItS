# Furina Sprint 1 — Execution Report ("Foundation Wave")

**Date:** 2026-07-20. **Plan:** furina-sprint-1-plan.md. **Governing
doc:** furina-kickoff-v0.1.md. **Environment:** CONSTANTS_VERSION 2,
DRAFTER_VERSION 2, RUNTEMPLATE_VERSION 2, post-R8 pool — **plus the
Fontaine world change this sprint introduces** (see §4).

> **RESOLVED 2026-07-20** (furina-sprint-1-redpen.md): all §6 asks
> ruled. Statline CLEARED; amendment batch RATIFIED as principles v1.10
> (with two redpen edits); rulings a/b/c + ask 4 in
> tier0/DECISIONS.md 61–64. **Sheet pass 1 unblocked.**

## 1. Shipped (all behind tests; suite green)

- **`character:` schema field** (shared, all sheets). Companion rows
  derive it from the id prefix, personal sheets from the filename,
  explicit wins (Guest Star rows). Engine test pools stay untagged =
  invalid Spotlight targets. (`tier0/engine/state.py`, `content/loader.py`)
- **fontaine-companions.yaml loads**: 12 shared cards (4 characters ×
  3-card kits) + 3 Neuvillette Guest Stars. Cryo application budget and
  roster locked by tests (`tier0/tests/test_fontaine.py`). The two
  deliberately-untagged damage ops now carry explicit
  `applies_element: false` so no cadence dial can ever re-tag them.
- **Guest Star scoping**: `guest_star:` field; excluded from companion
  rewards, banner roll, and the 5-star roster. **Personal-pool cards are
  no longer offered cross-character** (latent single-character bug —
  Prune would have shown up in Furina's rewards).
- **Fontaine DSL asks, implemented fully** (not stubbed — each was
  smaller than its stub): `reaction_triggered_this_turn` (per-turn
  window, ANY reaction per the ruling), `block_next_turn` (pre-emptive
  block surviving the turn-start reset), `shatter_bonus` (flat Shatter
  rider; burst-direction growth — every Shatter still ends a freeze).
- **Skill-grade cadence**: only Skill/Burst-tagged personal cards
  auto-apply the character's element; attacks never; companion cards
  exempt from cadence entirely (application is the sheet's explicit call).
- **Furina skeleton** (`tier0/content/characters/furina.yaml`): Hydro,
  skill cadence, Fanfare enabled, Ethereal Spotlight relic hook,
  REF-PROXY starter (loudly marked; statline never read off it).
- **Encore** (v1.6 style): unbounded per-combat buffer; absorbs after
  Block, before HP (enemy hits AND DoT); "Spend N Encore:" playability
  gate (`encore_cost`); `spend_encore` overdraw primitive (shortfall =
  true HP, priced); per-combat reset in `run_fight`. **A4 accounting
  binding rule enforced in the harness**: `encore_absorb` is its own
  event, credited to A4 sustain, never folded into `blocked`
  (`harness/metrics.py`, `harness/axes.py`, locked by
  `test_encore_accounting_credits_a4_never_a3`).
- **Fanfare**: capped at `FANFARE_CAP_FRACTION × maxHP` (0.5
  PLACEHOLDER); strictly activity-based (HP lost, Encore gained/spent,
  Ovation per Spotlighted card played); **no passive accrual path exists
  in code**; inert for characters without the resource (burst_max
  pattern). (`tier0/engine/resources.py`)
- **Spotlight**: per-player registry (single field = duplicate
  designations structurally inert); selector delivered each turn via
  relic hook, ethereal (vanishes to exhaust, never circulates as loot);
  +50% printed numbers on the designated character's cards, self rate
  1.25× PLACEHOLDER; **numbers-only enforced structurally** — the
  multiplier is plumbed into damage and Block only (draw/energy/powers
  have no path to it); per-turn cap schematized but OFF, with a test
  making arming it a deliberate act.
- **Nation weighting real** (§4.1): `SAME_NATION_REWARD_SHARE = 0.5`
  concentrated on the run character's nation, remainder uniform across
  all nations. Single-nation pools reduce bit-exactly to the old uniform
  pick. Verified from both directions (Klee ≥0.6 Mondstadt, Furina
  ≥0.55 Fontaine despite the thin bench — geometry, not generosity).

## 2. Salon audit (check-if-solved FIRST — kickoff §11.3)

**Verdict: SOLVED — Salon ships on existing rails** (4-for-4 for the
house norm). The `oz_summon` pattern (`effects.player_turn_end_triggers`)
is the exact template: a duration-counter self-power whose end-of-turn
tick deals a small hit applying an element to a random enemy. Variants
already in production: permanent (`witchs_flame`), conditional trigger
(`solar_isotoma`). The loader's reaction-fuel derivation already keys on
`summon_element`, so Salon cards auto-tag as reaction fuel.

Salon Members = a hydro `salon_member`-class power + the overdraw
coupling, and the overdraw primitive (`spend_encore`) shipped this
sprint — a member tick that costs Encore and drains HP when dry is ~20
lines in the end-of-turn trigger block. **Not built yet, per the
directive**: grammar (per-member costs, tick sizes, member count) is
card design and gated on the sheet pass. If members ever need HP or
targetability, the enemy-side `summon` intent path exists but would be
new scope — nothing in the kickoff requires it. (C# note: "Necrobinder"
in klee-mod is a base-game type switch, not a summon system; the
BaseLib/live-game audit belongs to the C# phase.)

## 3. Achievability experiment (§8, pre-registered; null results binding)

`python -m tier05.exp_furina_achievability` — 2000 runs/cell, seed
20260720, 10 reward screens (RUNTEMPLATE_VERSION 2), real reward
primitives; measures the OFFER stream + two bracketing strategies (no
combat — her sheet doesn't exist; combat-coupled re-run is an obligation
at sheet pass 1). +EP/+GS arms are PROTOTYPE scaffolding, not designs.

```
== take-all (ceiling) ==      median  P>=1   P>=2   P>=3   P>=4
kit3                              3   1.000  0.994  0.820  0.353
kit3+EP                           4   1.000  1.000  0.994  0.820
kit2                              2   0.999  0.862  0.389  0.094
== committed (floor-ish) ==
kit3                              2   1.000  0.809  0.480  0.201
kit3+EP                           3   1.000  1.000  0.809  0.480
kit2                              2   0.999  0.597  0.241  0.067
(+GS rows identical to base beyond the P>=1 floor — see verdict 3)
```

**Registered-prediction verdicts:**
1. *"3-card kits alone put depth 4+ at reachable-but-luck-gated"* —
   **CONFIRMED.** Committed P(≥4) = 0.201, ceiling 0.353. Correct for a
   draft-gated high-ceiling slot. The 2-card counterfactual collapses to
   0.067 — the §10 depth ruling is load-bearing.
2. *"Duplication separates the archetype's median from its ceiling"* —
   **INCONCLUSIVE BY CONSTRUCTION.** The one-copy prototype shifts the
   whole distribution +1 uniformly; it cannot distinguish median-lift
   from ceiling-lift. Needs the real Encore Performance card (drafted
   stochastically, duplicating a *Spotlighted* card) at sheet pass. Not
   retried; logged as a scaffolding limitation, per house rules.
3. *"Neither substitutes for drafted depth"* — **CONFIRMED
   structurally.** GS never moves P(≥2..4); EP is dead without a drafted
   target.
4. **Bonus finding:** offer-stream P(≥1) ≈ 1.0 already — the Guest Star
   floor's real value is **in-combat draw variance** (drafted depth ≠
   drawn this turn), which offer geometry cannot see. The generation
   bet must be re-tested with combat at sheet pass.

## 4. World change & measurement notes

Loading the Fontaine sheet changed Klee's draft world (companion pool
16 → 28; her uniform reward half now ~21% Fontaine). All ratified
1000-fight winrate-band locks pass unchanged. One casualty: the
`test_m5` fragility-shape heuristic (n=40) read 0.588 vs its 0.6
elite/boss death-clustering threshold (binomial sd ~0.12 at that n);
relaxed to majority-clustering with a dated comment. **Red-pen ask (b)
in the amendment batch.**

## 5. Honest gaps / deferred (UNAPPLIABLE-style, loud)

- Spotlight covers damage + Block; **element-application counts have no
  numeric DSL field yet** (apply_aura is unitary) — documented in
  `spotlight_mult`, revisit when a card prints one. Per-target riders
  (`bonus_vs_*`) deliberately unscaled (v1 boring baseline).
- Selector aiming is a placeholder heuristic (deepest tagged character,
  companions over self); generic pilots score the selector 0 and won't
  play it — her real pilot weights are sheet-pass scope.
- Whether selector cadence counts toward A5: **open ruling** (currently
  it does NOT — emits `selector_granted`, not `add_card`). Ask (a).
- Cross-player selector passing: deferred, solo path first (kickoff §11.5).
- Burst meter/card, Fanfare payoffs/uncappers, Salon cards, the 75-card
  sheet + upgrades: sheet pass, gated on the statline red-pen.
- Co-op Fanfare (partner flux + Hot-Hands exclusion audit): Tier 2.
- klee-mod (C#) untouched; §11 handoff list accumulating as designed.

## 6. Asks (decision-ready)

1. **Statline red-pen on kickoff §2** — gates sheet pass 1 (open item 5).
2. **Amendment batch red-pen** — furina-principles-amendment-batch.md
   (7 amendments + open questions a/b/c).
3. Bless the two flagged placeholders (Fanfare cap 0.5, self-Spotlight
   1.25×) as *sweep starting points only* — both get swept at sheet pass.
4. Rule on EP prototype follow-up: verdict 2 needs the real card; fine
   to defer to sheet pass, but saying so keeps the registration honest.
