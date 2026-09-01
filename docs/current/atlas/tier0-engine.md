# Atlas — tier0-engine

> **Lifecycle: LIVING** — expected to change; read it to work on the project.

Scope: `tier0/engine/` — combat, effects, powers, statuses, reactions,
resources, relics, potions, refpowers, state.

## 1. Purpose

The combat kernel of the Tier 0 Monte Carlo balance simulator: it runs a single
fight (`combat.run_fight`) over YAML-authored cards, and everything else in the
repo (harness batteries, tier05 run model, C# codegen) sits above it or is
generated from it. Its job is *comparable numbers* — content is scored as a ratio
against `ref_ironclad/starter = 3.0` (`tier0/README.md`, "Frozen calibration"),
so its first duty is stability of the divisor, not richness. It is explicitly
**not** a game: no UI, no reward screen, no run layer, no draft — combat is
**emit-only** toward the run layer, stating facts (`extra_card_screens`,
post-fight heal events) and never rolling, offering or drafting anything
(`state.py:606-619`, `combat.py:826-829`). Nor is it a fidelity clone of StS2:
`refpowers.py:20-22` is "PARITY, NOT FIDELITY" — the real Ironclad is scored in
the same impoverished world Klee is.

## 2. Entry points

From the repo root with `PYTHONPATH=.` (the README's `.venv/bin/python` is
equivalent to `python3` here; pyyaml/pytest already import):

```sh
# battery summary; add --score for the 7-axis card (runs the baseline alongside)
PYTHONPATH=. python3 -m tier0.harness.runner --character klee \
    --deck reaction_package --pilot reaction --fights 1000
PYTHONPATH=. python3 -m tier0.harness.runner --score --character klee \
    --deck demolition_package --pilot demolition
PYTHONPATH=. python3 -m pytest tier0/tests -q                    # whole suite
PYTHONPATH=. python3 -m pytest tier0/tests/test_combat.py \
    tier0/tests/test_effects.py tier0/tests/test_refpowers.py -q  # engine only
```

CLI flags: `--character --deck --encounter --pilot --fights --seed --csv --score
--report-character` (`tier0/harness/runner.py:159-175`).

In-process: `combat.run_fight(player, enemies, pilot, seed) -> CombatState`
(`tier0/engine/combat.py:788`). A pilot is `(state) -> Card | None`
(`combat.py:20-21`). Test fixtures for hand-built states live in
`tier0/tests/conftest.py`.

## 3. Key invariants

- **All randomness flows through `CombatState.rng`**; nothing may import the
  global `random` functions — `state.py:4-6`.
- **Pile removal is by identity, never by value.** `Card` is a dataclass, so two
  copies compare equal; every remove goes through `remove_instance`
  (`state.py:55-69`), and the hand flush compares `id(c)` (`combat.py:571-578`).
- **Card schema is closed.** `from_dict` raises on unknown fields and names
  retired ones (`fanfare_cost`) with their reason — `state.py:247-264`,
  `state.py:44-52`. Two readers share the surface: the loader and
  `tools/gen_klee_cards.py::CARD_FIELDS` (R92-3b).
- **Unknown card ops raise**, never skipped — `effects.py:2217-2218`. Gaps that
  cannot raise emit a loud `UNIMPLEMENTED` event instead (`refpowers.py:72-100`,
  `refpowers.py:147-149`; relics and potions do the same).
- **Damage clamps at zero at both ends of the modifier chain**
  (`powers.py:26-45`); otherwise negative Strength makes an attacked player
  *gain* block.
- **One aura per enemy; amplifiers (Vaporize/Melt) multiply exactly one hit and
  consume the aura — never persist** (`reactions.py:7-9,84-87`). Anemo/geo
  trigger but never stick.
- **X-cost cards bypass every cost modifier** and spend the whole bank, mirroring
  `CardEnergyCost.GetAmountToSpend` (`combat.py:124-141`); spark-free is checked
  *before* FreeAttack/Corruption (`combat.py:171-179`).
- **Fanfare is read-only** — activity-generated, decayed, never spent
  (`resources.py:12-20`; no playability gate, `combat.py:120`). Decay runs at the
  true top of the player turn, before block clear/draw/upkeep, so it taxes
  inventory not income (`combat.py:419-424`, `resources.py:117-140`).
- **Player turn order is the StS2 site mapping A/B/C/D/E/F/G/I/M**, documented
  once in `refpowers.py:26-46`, implemented in `combat.py:411-472`. Load-bearing
  part: `player_turn_start_late` is *after* the draw, while
  `powers.on_turn_start` is a PRE site.
- **Status cards are unplayable** (`combat.py:102-104`) and each injected copy is
  a fresh `Card` — pile membership is object-based (`statuses.py:38-41`).
- **Degeneracy is bounded** by a per-turn card cap plus a hand/pile/energy
  snapshot-repeat check (`combat.py:505-518`); per-combat rewind is a *snapshot*,
  not a subtraction — `fanfare_cap` restores from `fanfare_cap_base`
  (`combat.py:799-807`, `state.py:361-374`).
- **Text I/O must declare `encoding=`** — structural gate, because the defect
  only shows on a cp1252 host (`tier0/tests/test_encoding_gate.py:1-22`).

## 4. Rulings that shaped it

- **R14** — engine diagnostics (`fanfare_turn`, `engine_closure`,
  `cards_created_this_turn`) are report-only; never acceptance targets
  (`tier0/DECISIONS.md:632`; sites `combat.py:495-533`).
- **R16** — Spotlight empowerment lives in cards via the existing
  `spotlight_mult` pipe; `*_turn` powers are windows cleared at turn end, not
  stacks (`DECISIONS.md:386-401`; `powers.py:20-22`).
- **R20** — inline `upgrade:` on card rows is DEAD (`*-upgrades.yaml` is the one
  convention); the field survives only so the loader never hard-fails
  (`state.py:233-241`).
- **R33/R67** — dead-knob deletion + the KNOB_READS gate: a swept constant must
  record ≥1 real read, and knobs are served by a PEP 562 module `__getattr__`,
  so **never** write `from tier0.constants import X` (it binds at import and
  slips the hook) — `tier0/DECISIONS.md:2065-2118`, `tier0/constants.py:979-989`,
  `effects.py:298-305`.
- **R34** — X-cost cards are exempt from spark spend (a spark-freed X card would
  resolve at X=0) — `klee-mod/DECISIONS.md:963-967`; `combat.py:186-201`.
- **R36** — `discard_for_sparks`: forced discard, 1 spark per card *actually*
  discarded, kit cards exempt (`klee-mod/DECISIONS.md:975-990`; `effects.py:1474`).
- **R37** — Innate cards surface to the top of the shuffled draw pile
  (`klee-mod/DECISIONS.md:992-1000`; `combat.py:748`, `state.py:114-117`).
- **R39** — spark-reading effects see the bank as it was at play time, before the
  card's own spend (`tier0/DECISIONS.md:739-760`; `combat.py:190-197`).
- **R52** — Kokomi heals no HP; the healing law translates would-be heals to
  Block (`DECISIONS.md:1314-1340`; `effects.py:2259`, `effects.py:2544`).
- **R72** — bombed-state is snapshotted **at cast**, so hit 1's detonation cannot
  strip the rider off hits 2-3 (`DECISIONS.md:2313-2340`; `effects.py:570`).
- **R82** — enchantments are a per-*instance* rider only, no registry, no
  subsystem (`DECISIONS.md:2594-2620`; `state.py:215-223`, `effects.py:2280`).
- **R85** — "Curtain Call": `register` joins the shared card schema (engine-inert)
  and five *activity*-triggered powers land — never per-turn, per the accrual law
  (`DECISIONS.md:2699-2750`; `state.py:134-140`, `resources.py:304`,
  `refpowers.py:729`, `reactions.py:135`).
- **R92-3b** — `tempo_band` is inert metadata on both readers, and a shared-schema
  change files its cross-session note *before* it lands
  (`DECISIONS.md:3149-3168`; `state.py:83-99`).

## 5. Traps

- **The battery is the divisor; do not make it feel anything new.** `relics.py`,
  `potions.py` and much of `refpowers.py` are *dead branches* there, guarded by
  empty `Player.relic_effects` / `Player.potions` (`relics.py:5-16` + guards at
  `relics.py:86,105,184,243,259`; `potions.py:5-15` + `potions.py:169`).
  `tier0/tests/test_anchor_lock.py:52-60` pins the anchor's exact winrate/turns
  at seed 7. The battery and the pilots' block weight (1.2) are frozen by
  calibration, not by file permission (`tier0/README.md`, "Frozen calibration").
- **`refpowers.UNIMPLEMENTED` is a real exclusion list** — Stampede and
  Hellraiser are NOT approximated; their cards stay out of the pool
  (`refpowers.py:54-55,72-100`).
- **Funnel granularity is an approximation with a tripwire**: card-caused
  self-damage is a delta across one CardPlay, so a card with several distinct
  self-damage ops fires Inferno once and emits `refpower_funnel_collapse` — that
  card must not enter the pool unreviewed (`refpowers.py:39-52`).
- **`refpowers.bind()` is a module-global seam**, not a preference: `effects.py`
  cannot pass attacker identity, so state is bound try/finally around
  `_run_rounds` (`refpowers.py:152-171`, `combat.py:817-824`).
- **Inert-looking fields are load-bearing.** `register`, `solve`, `tempo_band`,
  `archetypes` are read by *nothing* in the engine and must stay that way — they
  exist because `from_dict` refuses unknown fields and the codegen whitelists
  them (`state.py:83-99,134-140`).
- **One `sly` field, two behaviours** (EB-71, R174 — the unification of what
  used to be `sly` vs `sly_keyword` vs `sly_this_turn`). `Card.sly` is an
  effect list; the reserved rider `{op: sly_autoplay}` in it means the
  base-game keyword (auto-play the discarded card for free), and everything
  else is Kokomi's authored Assist lane. Authored riders resolve inline in the
  discard loop, the auto-plays are batched after it, and both are handled at
  the one trigger site in `effects._op_discard`. `sly_autoplay` is deliberately
  **not** in `OPS` and is never dispatched — registering it would demand a
  drafter price (`lint_op_parity`), and `draft._static_power` reads
  `sly_riders()`, so the marker is worth exactly zero: the price the keyword
  already carried. Hand Trick grants the rider with `until: turn_end` (swept in
  `refpowers.reset_turn_counters`); Master Planner grants it with no expiry.
  The C# side speaks the same grammar since the parity leg (2026-08-12): the
  marker emits as `CardKeyword.Sly` on the CanonicalKeywords rail, the authored
  riders emit as the `AfterCardDiscarded` hook, and `tools/lint_sly_grammar.py`
  is the standing guard. Equivalence pins:
  `tier0/tests/test_eb71_sly_unification.py`, `test_eb71_cs_parity.py`.
- **Phase revives fire at every HP-dropping site**, before `state.over` is
  re-read; kill predicates observe the pre-revive `hp <= 0` but Fatal
  (`counts_for_fatal`) does not — otherwise Feed farms phase-downs and minions
  for permanent max HP (`combat.py:63-99`, `state.py:427-434`).
- **`Card.__deepcopy__` is hand-rolled** and copies exactly `_MUTABLE_FIELDS`; a
  new mutable field not added there is silently shared between copies
  (`state.py:35-39,266-287`).
- **Encore absorption is credited to A4 sustain, never A3 block** — without the
  rule Furina grows a phantom third elite axis (`resources.py:6-11`).

## 6. EB-118 surfaces — merged, and INERT

Merged into `main` 2026-08-23 on the settled Route-1 precedent: the ops, the
field and the context exist in HEAD, **no card on any sheet reaches any of
them**, every drafter price is PROPOSED, and no live `RT/D/P/C` integer moved.
Activation is Phase 2 (`review/ruled/eb118-richness-phase0-2026-08-23.md`
§3). Each entry says what the surface *is*, because the thing a reader will
trip over is assuming it is dead code.

- **`spend_spark` — ALL OR NOTHING, and the price is visible** (`effects.py:672`
  `spend_spark_amount`, `:689` `spend_sparks`, op at `:1339`). The amount is a
  literal positive int and raises otherwise, because `combat.spark_cost` reads
  the same number off the printed effect with no state in hand — a price the
  playability gate cannot read is a price that fires without being shown. A
  short bank pays **nothing** and emits `spend_spark_refused`: Sparks have no
  overdraw currency (the shortfall-drains-HP grammar is Furina's Encore alone,
  `resources.spend_encore_or_hp`), and a partial spend leaves the payer
  believing it was paid. Dropping under the free-Attack bar is a legal landing
  — `combat.spark_threshold` reads the LIVE bank at every site.
- **`choose_one` / `modes` — the modal surface, and the chooser is a marked
  PLACEHOLDER** (`effects.py:2030-2087`). A `choose_one` carries `modes:`, a
  list of 2+ `{label, effects}` dicts; it is **not** a keyword — the label is
  that mode's plain card text and the bodies are the ordinary op vocabulary.
  The distinction from `conditional` is WHO decides: a conditional reads a
  predicate off the board, a modal asks the player, which puts it at the
  chooser seam beside `_worst_card` / `_best_card`. `_chosen_mode`
  (`:2051`) always returns index 0 — a fixed index, not a heuristic, chosen so
  the seam exists and stays deterministic. `pilot.policy._active_effects`
  calls that same function for its forecast, so the pilot's read and the mode
  that resolves cannot disagree. Replacing that body is `POLICY_VERSION` work.
  Emits `mode_chosen(card, index, label)`, mirrored in
  `KleeCode/Cards/ModalChoice.cs`.
- **`recall_to_draw` gained a SOURCE, not a parallel op family**
  (`effects.py:2512-2589`). `from: exhaust` reads the exhaust pile through
  `recall_exhaust_pool` (`:2530`), whose filter *is* the constraint set: no kit
  card, no `is_junk` Status/Curse, no card that itself retrieves from Exhaust
  (`retrieves_from_exhaust`, `:2516`, read off the printed effect tree), and
  never the resolving card's own instance — that last exclusion is what keeps
  the pile from closing into a cycle. Destination is top-of-draw in both
  branches, **never the hand**; the returned card gains `exhaust` per
  INSTANCE for the rest of combat, so it rotates again and pays Charge again
  at the ordinary funnel. Card-shape constraints (Uncommon-or-Rare,
  self-Exhausting) live at `loader._validate_recall_shape` and
  `gen_klee_cards.blocked_reason`; `tools/lint_recall_exhaust.py` sweeps both
  halves plus the closure.
- **Salon `rotate` / `perform` — two verbs over ONE member-action path**
  (`effects.py:1495` `_op_salon_rotate`, `:1519` `_op_salon_perform`,
  `salon_member_act` at `:3199`). Rotate is a pure reorder: identity kept, no
  tick, no Encore drained, no bow or replacement triggered, and
  `powers['salon_member']` untouched by construction. Perform resolves through
  `salon_member_act` — the same function turn-start upkeep calls — so the
  Encore upkeep, the dry three-quarters, the Focus/Grand-Salon scaling and the
  `salon_tick` row are inherited, not restated; that sharing is the contract.
  The member STAYS on stage, so `amount: N` performs the leftmost member N
  times. Both whiff **loudly** on an empty stage (`salon_rotate_whiffed` /
  `salon_perform_whiffed`), the `conscript_whiffed` pattern. Reads come from
  the `leftmost_salon_member_*` predicate prefix (`:2135`), closed on
  `SALON_MEMBERS` so a typo fails at load.
- **`ethereal:` on the BASE card, and ONE predicate for both spellings**
  (`state.py:212` the field, `:381` `is_ethereal`). Until now the keyword was
  reachable only through `tags: [ethereal]`, which is the Status/Curse/token
  spelling; the field is the personal-sheet spelling of the same keyword, and
  `is_ethereal` is the single predicate combat reads at all three seams (retain
  split, flush filter, ethereal sweep). **Orthogonal to `is_junk`** — an
  Ethereal *personal* card is still one of Kokomi's own cards and still pays
  her Charge funnel when it burns. The `remove: ethereal` upgrade delta
  (`content/upgrades.py:188-204`) is guarded where `remove: exhaust` is not: a
  delta removing a keyword the base never printed is a sheet error. The
  drafter scales the whole card by `draft.STATIC_ETHEREAL_SHARE` (0.6) — a
  lifecycle discount, not an op price — and no offerable row prints the field,
  which is why `D` did not move.
- **`CombatState.exhaust_selection` — an identity CONTEXT, not a combat-global
  `last_exhausted`** (`state.py:808-819`; `effects.py:117-195`;
  `_op_exhaust_from` `:1845-1912`). One printed descriptor per victim the
  CURRENT `exhaust_from` took — `id, cost, type, rarity, companion, upgraded`,
  printed identity only, which is what lets `Powers/ExhaustSelection.cs` record
  the same row off the same facts. Three facts do the scoping: `resolve_card`
  opens an empty selection per card play; `combat._FREE_PLAY_CONTEXT`
  (`combat.py:489`) saves and restores the list OBJECT, so a free play landing
  mid-resolution cannot hand its victims to the outer card; and a second
  `exhaust_from` REBINDS rather than clearing in place. `exhaust_selection_counts`
  (`:161`) is one definition with three consumers — the
  `exhaust_selection_*` amount tokens (`:313`), the predicates, and the emitted
  parity row (`EXHAUST_SELECTION_ROW_KEYS`, `:189`) — so a formula can never
  report a different number from the row the parity test compares. X-costs
  contribute 0 to the derived total rather than being coerced. Vocabulary:
  names `exhaust_selection_has_companion` / `_has_personal` (`:2117`),
  prefixes `exhaust_selection_has_type_` / `_cost_at_least_` / `_size_at_least_`
  (`:2138`). Deliberately **no** "Status exhausted" reward grammar — the
  context reports rarity and C11 keeps Kokomi's pool free of junk.

## 7. `block_at_turn_start` — merged, and INERT (EB-83)

Built FIRST AND ALONE on the `EB-82` admission rule — an engine surface is
never invented inline inside a conversion — so it lands with **no carrier at
all**: no card on any sheet prints it, and no live `RT/D/P/C` integer moved.
The two replacement cards (*Tengu Flurry*, *Chinju Ward* — names ruled at
R231, 2026-08-30) and the Wood Carvings conversion are still [USER]-gated on
the `RT` window.

- **What it is.** `{op: block_at_turn_start, amount: <int|count>, turns: <int>}`
  — "gain `amount` Block at the start of each of your next `turns` turns"
  (`effects.py::_op_block_at_turn_start`). The **duration-scoped** twin of
  `block_next_turn`, which is a one-shot bank popped whole at the next turn
  start. Same seam, same raw payout, deliberately adjacent in
  `player_turn_start_triggers` so the two cannot acquire different hooks by
  accident: **pay, then tick, then expire**, which is why a power applied on
  turn N with `turns: 2` pays at N+1 and N+2 and never on the turn it was
  played.
- **Where the second number lives, and why it is not a new object graph.**
  `powers` is `name -> int`, so a power carrying *(amount, turns)* needs one
  more field. It gets the sidecar the engine already uses for exactly that —
  `Player.timed_power_amounts`, keyed by power name, the shape
  `Player.power_payloads` established. `powers[name]` holds **turns
  remaining** (the engine's own stacks-are-turns grammar: `kurage_summon`,
  `colossus`, `intangible`, `double_damage`, `ceremonial_garment`) and the
  sidecar holds the amount those turns pay, so every existing reader of
  `powers` keeps working and only the payout consults the sidecar. Both
  entries are deleted together at expiry. **Lifetime is exactly `powers`'
  lifetime** — default-empty on a fresh `Player`, one built per fight by
  tier 0.5, neither swept in `run_fight`.
- **The amount is snapshotted at play time; the duration may not be.**
  `amount` goes through `_amount` (so `block_gained_this_card` is
  expressible) and is scaled by Spotlight and the salon multiplier once, at
  play. `turns` is a **literal positive int** and raises otherwise
  (`effects.block_at_turn_start_turns`, the `spend_spark_amount` precedent),
  checked at LOAD by `loader._validate_effect_vocabulary`: a duration
  resolved against combat state is printed text that means something
  different every time it is played.
- **Stacking is a PLACEHOLDER** — additive on amount, `max` on turns, so a
  second casting can never shorten a standing one. No ratified rule for
  same-name *(amount, turns)* effects exists to inherit; the engine's
  ratified duration rules are all single-field refreshes and settle only the
  turns half. **[USER]'s pick whenever the first carrier is printed.**
- **Nimble does not ride it**, for `block_next_turn`'s reason verbatim (EB-85
  divergence 4): the Block arrives from a POWER, so there is no `cardSource`
  for the enchantment hook to read. `enchantments._BLOCK_OPS` is an allowlist,
  so the exclusion is structural.
- **Registered where an op has to be registered:** `effects.OPS`, the loader's
  load-time vocabulary check, `card_connectivity_report.OP_HOOKS` (same hook
  as its one-shot sibling — the vocabulary asks what state an op moves, not
  how often), and `draft.STATIC_OP_PRICING` / `_op_price` (the delayed-Block
  share, once per printed turn; PROPOSED, and unreachable).
- **Named still-owed, for whoever prints the first carrier:** there is no
  `block_at_turn_start` upgrade-delta key in `content/upgrades.py`, so an
  upgraded row (Toric Toughness' published 5→7) cannot yet spell its bump.
  Deliberately not added here — the delta keys are a shared schema with
  `tools/gen_klee_cards.py`'s C# emitter, and a shared-schema change lands
  atomically with every consumer (R20/R92) or not at all.

## 8. Reading order

1. `tier0/README.md` — what the sim is for, and what is frozen.
2. `tier0/engine/state.py` — data model, determinism contract, card schema.
3. `tier0/engine/combat.py` — `run_fight` / `_player_turn` / `_enemy_turn`: the
   ordering every other file plugs into.
4. `tier0/engine/refpowers.py:1-56` — site mapping, parity stance, UNIMPLEMENTED.
5. `tier0/engine/effects.py` — the card DSL: `_amount` / `_bonus_formula` /
   `_predicate` / `OPS` / `resolve_card`.
6. `tier0/DECISIONS.md` (and `klee-mod/DECISIONS.md` for R34-R37 / C# parity) —
   search the R-number before changing any behaviour.
