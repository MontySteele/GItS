# Atlas — tier05-economy

Scope: `tier05/events.py`, `rewards.py`, `shop.py`, `potions.py`, `relics.py`,
and the `tier05/content/` pools (`events.yaml`, `potions.yaml`, `relics.yaml`,
`act{1,2,3}_pool.yaml`).

## 1. Purpose

Everything a run gains or spends *outside* combat: post-fight reward screens and
the Featured Banner (`rewards.py`), the `$` node's card/companion shelf
(`shop.py`), Unknown-room events (`events.py`), and the run halves of the relic
and potion systems (`relics.py`, `potions.py`). Each owns only the **run** half
of a split — the combat half of every relic and potion lives in the frozen
`tier0/engine/` and its vocabulary is imported, never re-declared
(`relics.py:41`, `potions.py:36`). It is explicitly **not** a fidelity clone of
StS2: the house rule is *skip loudly, never approximate*, so an event whose
options are not all expressible with real ops does not ship
(`content/events.yaml:4-7`, `:273-280`) and a relic whose mechanic is missing
goes on the `skip:` list where `get_relic` refuses it (`relics.py:101-111`). It
is also **not** a player — the event option policy and the shop buy policy are
deliberately simple, readable confounders reusing `draft.score_offer` rather
than a second valuation, because a clever policy moves every run number
invisibly (`events.py:9-14`, `shop.py:13-20`).

## 2. Entry points

Run from the repo root with `PYTHONPATH=.`:

```sh
# the run model that drives all of this (--realistic turns on relics + potions)
PYTHONPATH=. python3 -m tier05.runner --character klee --realistic \
    --runs 500 --seed 42
# the §4.7 companion-channel measurement cell (R61; grades P1/P2/P3)
PYTHONPATH=. python3 -m tier05.exp_shop_companion_channel 500
# the economy test set
PYTHONPATH=. python3 -m pytest tier05/tests/test_events_acts23.py \
    tier05/tests/test_shop_economy.py tier05/tests/test_shop_companion_channel.py \
    tier05/tests/test_neow_and_shop.py tier05/tests/test_relic_granting.py \
    tier05/tests/test_relics_runlayer.py tier05/tests/test_potion_runlayer.py \
    tier05/tests/test_fontaine_rewards.py tier05/tests/test_extra_reward_screen.py -q
# content gates guarding this module's pools
PYTHONPATH=. python3 tools/lint_companion_shop_coverage.py
PYTHONPATH=. python3 tools/lint_ancient_coverage.py
PYTHONPATH=. python3 tools/lint_text_encoding.py
```

Library surface: `events.visit / option_value / resolve`, `rewards.roll_rewards /
roll_banner / character_pool`, `shop.visit_shop / companion_shop_offer`,
`relics.HeldRelics / roll_relic_reward / neow_offer / ancient_offer`,
`potions.roll_potion / PotionBag`. Every call site is in `tier05/model.py`
(`:313-341`, `:395-450`, `:490-511`, `:687`, `:739-741`).

## 3. Key invariants

- **Card ownership is REQUIRED, not merely non-conflicting.** A card with
  `character=None` is offered to nobody (`rewards.py:68`); the shop reuses the
  same pool so both doors admit the same cards (`shop.py:85-89`). An empty pool
  is a named error, never a `KeyError` (`rewards.py:226-231`).
- **Companions, kit cards and guest stars are never loot** (`rewards.py:50`,
  `:81`); `personal_pool` cards reach only their own character
  (`rewards.py:243-247`).
- **The banner's nation set is DERIVED from the sheets, never listed**
  (`rewards.py:101-121`); `nations=None` means every designed nation
  (`:143-144`) and 4-stars are never gated (`:156-161`). Forced *card* rarity
  falls rare→uncommon→common (`:235-236`); forced *companion* rarity omits the
  slot rather than substituting down (`:253-256`).
- **Event acts are 1-BASED in the YAML** (`events.py:99-100`, `:113`). A pool is
  the act's own + `all` + anything declaring the act in `also_acts`, minus
  `hidden` escalation stages (`events.py:115-127`); no event repeats within a
  run (`events.py:167-173`).
- **Option value is HP-equivalent and `GOLD_PER_HP = 7.5` is DERIVED** from the
  shop's own prices (60/8, 150/20), not chosen (`events.py:205-215`); pinned by
  `test_events_acts23.py::test_gold_rate_matches_the_shops_own_prices`.
  Escalation is valued *through* — immediate effect plus the best reachable next
  stage, depth-capped as a cycle guard (`events.py:224`, `:288-291`).
- **`resolve` order is fixed so a seed replays**: costs → `duplicate_deck` →
  removals/transforms/adds → downgrades → upgrades → picks/screens → grants →
  heals last (`events.py:365-500`). Three orderings are load-bearing:
  duplicate-before-add (`:388-391`), downgrade-before-upgrade (`:418-426`),
  heals after any max-HP change (`:493-498`).
- **Shop buys cards before removal and prices per shelf entry** — flat
  `SHOP_CARD_PRICE` for character cards, drawn-rarity price for companions
  (`shop.py:228-247`, `:270-277`). Removal only targets a known-dead card (curse
  or unupgradable basic glue) at a rising price (`shop.py:47-60`, `:72-74`).
- **Relic effects split by hook vocabularies imported from the engine**; a hook
  in neither set warns and is dropped from both, never approximated
  (`relics.py:41`, `:50-51`, `:264-284`). Acquisition is idempotent per id
  (`:327-328`) and owner-locked relics are gated at ROLL time (`:114-119`). The
  `event:` pool is closed — resolvable via `get_relic` but unreachable from
  `unowned_common` / `neow_offer` / `unowned_ancient` (`:90-98`), and a named
  event relic is never substituted (`events.py:482-487`).
- **Every potion id in the YAML must exist in `tier0.engine.potions.KNOWN`** or
  load raises (`potions.py:46-54`); tiers iterate in a fixed order so a seed
  replays (`potions.py:30-31`, `:86-111`). A full bag DISCARDS the drop and logs
  it — no swap prompt (`potions.py:131-139`).
- **Schema allowlists are enforced at load.** `events.EVENT_KEYS` /
  `OPTION_KEYS` raise on any unknown key (`events.py:51-91`); `acts.POOL_TIERS`
  / `ENCOUNTER_KEYS` / `ENEMY_KEYS` / `INTENT_KEYS` do the same for the act pools
  (`acts.py:54-78`). Adding a key to the grammar means adding it to **both** the
  reader and the allowlist. Encoding is declared on every read (`events.py:96`,
  `potions.py:45`, `relics.py:60`), gated by `tools/lint_text_encoding.py:43`.

## 4. Rulings that shaped it

- **R59** (`tier0/DECISIONS.md:1777`) — shop companion slot 2 is wildcard-nation
  at an **Uncommon floor** on renormalized reward odds; guaranteed-Rare rejected
  as brittle against banner thinning (`shop.py:171-179`).
- **R60** (`:1796`) — the C# `ColorlessCardPool` stays populated so its last
  fallback rung exists; tier 0.5 models no base colorless pool, so its ladder's
  last rung **drops the slot** instead — recorded, not faked (`shop.py:118-127`).
- **R61** (`:1813`) — "Tier 0.5 models economy channels." Companions become
  shoppable here because an unmeasured governor is a design claim with no
  instrument.
- **R63** (`:1842`) — execution record. Winrate delta was a NULL, slot-1 buy rate
  49.2% against a predicted 10-35%, relics bought −29.4%, unspent gold unchanged:
  **the purse does not bind**, so "price is the balance governor" is not
  currently true in the sim, and no knob was turned. Also records that buying
  cards before removal makes part of that buy rate an **ordering artifact**.
- **R64** (`:1922`) — the Featured Banner goes live; `roll_banner`'s old
  `("mondstadt",)` default had silently deleted every other nation's 5-stars from
  both reward slot and shop, so the nation set is now derived. `test_v18_banner`'s
  "roster <= cap" invariant is RETIRED. C# parity is structural, never numeric.
- **R65** (`:1961`) — unreleased-nation characters are placed in their nation of
  operation (Arlecchino → Fontaine); that is what `loader.character_nation`
  returns and what shop slot 1 and `SAME_NATION_REWARD_SHARE` key on.
- **R87** (`:2834`) — the current world is RUNTEMPLATE 7 / CONSTANTS 4 /
  DRAFTER 13; earlier drafter-layer numbers are archive. Both policies here call
  `draft.score_offer`, so archived economy figures are not readings of today's
  code.
- **D4** (`:2446`) — instrument-visibility law: a prediction must name an
  instrument that can see the changed object, and quantitative rationale carries
  a measurement or the `UNMEASURED` label. This is why
  `ShopOutcome.companion_offers` exists (`shop.py:187-192`).

## 5. Traps

- **`docs/run-model-rework-plan.md` is ARCHIVED — DO NOT QUOTE UNLABELLED** (its
  banner, lines 2-15). Same for `docs/sts2-map-and-events-research.md` §3–§3.6;
  only **§3.7** carries today's stamp (that doc's lines 11-15).
- **Skip lists are load-bearing and noisy by design.** Any access to
  `relics._pool()` emits a `UserWarning` per skipped relic (`relics.py:62-67`).
  `bronze_scales` and `oddly_smooth_stone` now have working mechanics and are
  *still* skipped: un-skipping arms a relic and moves the tier 0.5 measurement
  world, which is a **[USER] ruling** (`content/relics.yaml:284-309`). A stale
  skip *reason* is the quiet lie the list exists to prevent (`:311-318`).
- **`shop.grant_treasure_relic` is a deliberate no-op stub** (`shop.py:284-290`);
  the real treasure/elite/boss grants live in `model.py` gated on `grant_relics`.
- **`options_of` unions variants — right for valuation/validation, never for
  play**; `materialize` picks the one variant a visit sees (`events.py:138-164`).
- **`EventState.archetype` must be the deck's EMERGENT shape on adaptive runs**,
  never the assigned label — passing the label reintroduces the leak `test_m7`
  pins (`events.py:182-188`, applied at `model.py:490-505`).
- **`id()` keys in `visit_shop` are safe only because `loader.get_card` returns a
  fresh copy per call** (`shop.py:226-230`); `peek_card` there would collapse two
  shelf entries sharing an id.
- **The companion ladder widens the NATION before it drops the RARITY**
  (`shop.py:112-127`, `:151-168`). Every rung taken is a slot that silently
  stopped honouring §4.7; only `tools/lint_companion_shop_coverage.py` sees it —
  surviving is not the same as being right (that file's header, lines 1-30).
- **A lethal event option is refused here though the real game allows it**
  (`events.py:306-312`) — but an escalation ladder can still kill, and
  `model.py:513-521` treats that as a run death.
- **`companion_offers=0` means the slot is ABSENT, not empty** — none of the
  companion machinery, and none of its rng, runs (`rewards.py:238-240`).
- **Toggling `companions` / `grant_relics` / `grant_potions` changes the rng
  stream**, so on/off arms diverge downstream rather than being paired
  (`shop.py:210-216`, `potions.py:9-14`); byte-identity of the off arm is pinned
  by `test_relics_runlayer.py::test_relics_none_is_byte_for_byte_unchanged` and
  `test_potion_runlayer.py::test_grant_potions_false_is_byte_for_byte_unchanged`.

## 6. Reading order

1. `tier05/content/events.yaml:1-45` — the effect grammar and curation rule;
   `events.py` is only its interpreter.
2. `tier05/events.py` — pool selection, HP-equivalent valuation, resolve order.
3. `tier05/rewards.py` — the ownership rule and the banner, which `shop.py`
   reuses wholesale.
4. `tier05/shop.py` — the two channels and the fallback ladder.
5. `tier05/relics.py`, then `tier05/potions.py` — the run/combat split and the
   skip-list discipline.
6. `tier05/model.py:313-341, 395-450, 490-511, 687-741` — the call sites that
   thread all five together.
