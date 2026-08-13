# Atlas — tier0-pilot-roster

> **Lifecycle: LIVING** — expected to change; read it to work on the project.

Scope: `tier0/pilot/policy.py`, `tier0/roster.py`, `tier0/constants.py`,
`tier0/content/` (`loader.py`, `upgrades.py`, `local_reference.py`, and the
`cards/`, `characters/`, `encounters/`, `pilots/` YAML trees).

## 1. Purpose

The **content and decision layer** the engine runs on: who exists
(`roster.py`), what they play (`content/` YAML + the docs sheets it reads),
what every tunable number is (`constants.py`), and how a card gets chosen each
turn (`pilot/policy.py`). Its job is to feed `combat.run_fight` a `Player`, a
list of `Enemy`, and a `(state) -> Card | None` pilot, so that numbers taken in
different sessions are comparable. The pilot is explicitly **not** a good
player and must not become one: "Deliberately dumb; both Klee and reference
decks use the same pilot" (`pilot/policy.py:1-9`) — it is the constant that
makes card comparisons mean something, so improving it retroactively moves
every tier-0.5 number in the repo (R93). The roster is explicitly **not** a
place for balance numbers — HP, decks and bands stay in the ratified character
YAML (`roster.py:26-35`), and reference anchors are **not** roster members
(`roster.py:165-171`).

## 2. Entry points

Run from the repo root with `PYTHONPATH=.`:

```sh
# the battery: build_player + make_pilot + run_fight, per encounter
PYTHONPATH=. python3 -m tier0.harness.runner --character klee \
    --deck reaction_package --pilot reaction --fights 1000
# the roster gate (dual-wired: lint + test)
PYTHONPATH=. python3 tools/lint_roster_registry.py
PYTHONPATH=. python3 -m pytest tier0/tests/test_roster_registry.py \
    tier0/tests/test_roster_runtime_contracts.py -q
# content / pilot / upgrade guards
PYTHONPATH=. python3 -m pytest tier0/tests/test_content_boundaries.py \
    tier0/tests/test_upgrades.py tier0/tests/test_upgrade_delta_ops.py \
    tier0/tests/test_pilot_reaction_value.py \
    tier0/tests/test_pilot_stoke_value.py -q
PYTHONPATH=. python3 tools/lint_constant_parity.py   # C# mirrors vs constants
PYTHONPATH=. python3 tools/lint_upgrade_coverage.py
```

In-process (the four doors everything else uses):

- `loader.build_player(character_id, deck="starter")` — battery path
  (`loader.py:420`); `loader.build_player_from_ids(...)` — tier05 run path
  (`loader.py:445`).
- `loader.build_encounter(id)` / `loader.encounter_stages(id)`
  (`loader.py:536`, `loader.py:529`).
- `policy.make_pilot(loader.pilot_weights(pilot_id))` (`policy.py:25`,
  `loader.py:570`) — the exact pair `harness/runner.py:29` uses.
- `runner.resolve_plan(character, archetype) -> (plan, pilot)` in
  `tier05/runner.py:62` — the R68 single source of truth for plan→pilot; do not
  index `roster.Character.plans` directly.

Live inventory today: 300 cards, 5 character sheets (3 roster + 2 reference),
6 encounters, 15 pilot weight sets.

Recipe (recount with `loader._card_index()`, then subtract the side sheet):
220 personal rows (`docs/klee-cards.yaml` 76, `docs/furina-cards.yaml` 82,
`docs/kokomi-cards.yaml` 62) + 51 companion rows (17 / 19 / 15) + 29 shared and
reference rows under `tier0/content/cards/` (curses 10, ironclad_package 6,
silent 6, ironclad_starter 3, colorless_event 2, tokens 2) = 300. The loader
index reads **303** — the extra 3 are `ancients.yaml`, acquisition-only.

## 3. Key invariants

- **One roster row per character; append, never reorder** — the order is ship
  order and reports print it (`roster.py:108-110`). `roster.get()` raises and
  names the whole roster rather than returning `None` (`roster.py:147-162`).
- **`archetypes` is declared, then cross-checked** against the tags the
  character's cards actually carry, minus `generic` — declared so a typo'd card
  tag cannot invent an archetype, cross-checked so a registry tag on zero cards
  cannot survive (`roster.py:57-69`;
  `test_roster_registry.py:74`).
- **The registry is enforced where it cannot be imported.** C# and PowerShell
  get swept by `tools/lint_roster_registry.py`; its `CLOSED_LISTS` tokens are
  *functions* of the character so a new row needs no edit there
  (`lint_roster_registry.py:52`, `:75`, `:118`).
- **Pilot decision order is fixed: lethal → block-panic → weighted score**
  (`policy.py:41-53`), and `damage`/`block`/`incoming` are computed **once** per
  decision and shared by all three consumers (`policy.py:37-39`).
- **Ties break to the earliest playable index** — the scorer sorts on
  `(score, -i)` (`policy.py:51-53`), and a non-positive best score means *pass*
  (`policy.py:54-55`).
- **`chosen_i` is passed, never looked up**: `Card` is a value-equality
  dataclass, so `playable.index(card)` finds the first *equal* card
  (`policy.py:88-93`).
- **Character-machinery terms default to 0.0 and are skipped when zero**, so
  every older pilot is arithmetically unchanged and the frozen anchor tables
  cannot move (`policy.py:646-654`; weights in `content/pilots/archetypes.yaml`).
- **The pilot must not disagree with the engine.** Every formula it forecasts
  goes through the engine's own helper — `effects.flat_attack_bonus`,
  `effects._calc_amount`, `effects._bonus_formula`, `effects.spotlight_mult`,
  `resources.readable`, `powers.modify_damage_dealt`, `e.ramped_amount`
  (`policy.py:177`, `:190`, `:208-212`, `:155`, `:669`).
- **Content validates at LOAD, not at play.** Every `op:` must be in
  `effects.OPS` and every `if:` a real predicate, recursing through
  `then`/`else` (`loader.py:251-283`); duplicate card ids raise
  (`loader.py:241-245`).
- **Ownership is a property of the sheet, not a per-row field**: `character`
  from the sheet name, `nation` from the sheet name, both `setdefault` so an
  explicit row wins (`loader.py:217-231`). Ownership is tagged **only for
  draftable rarities** — `character` is also Furina's Spotlight key, so tagging
  basics would change a shared engine path (`loader.py:90-101`).
- **`get_card` always returns a fresh deep copy; `peek_card` returns the shared
  prototype and must not be mutated** (`loader.py:345-365`).
- **Upgrade deltas are per-key, and an unknown key is a loud error** — the
  applier and the sheet drifting apart must fail the suite
  (`upgrades.py:9-13`, `:517-523`); a key that matches no effect also raises
  (`upgrades.py:521-523`).
- **Nothing in `engine/` may hard-code a balance number** (`constants.py:1-6`),
  and knobs are read as module attributes only — `from tier0.constants import X`
  binds at import and slips the sweep hook (`constants.py:979-989`).
- **All text I/O declares `encoding=`** — the loader carried five bare
  `read_text()` calls that produced mojibake on cp1252
  (`loader.py:86`; `tier0/tests/test_encoding_gate.py:1-22`).

## 4. Rulings that shaped it

- **R66** — the ratified card sheet is canonical for a character's archetype
  vocabulary; a registry naming tags that exist on zero cards produced numbers
  "indistinguishable from correct numbers" and archived every adaptive Kokomi
  reading (`tier0/DECISIONS.md:1989-2035`; `roster.py:133-139`).
- **R68** — plan→pilot resolves **only** through `runner.resolve_plan`; the
  bypass path is gone, and version stamps are read live rather than stored
  (`DECISIONS.md:2122-2160`; `roster.py:32-33`, `tier05/runner.py:43-62`).
- **R20** — `*-upgrades.yaml` sheets win; inline `upgrade:` on a card sheet is
  deprecated and the loader's tolerance is a loud per-sheet `UserWarning`, not
  silence. Same entry carries the standing agreement that **schema changes to
  shared loaders require a cross-session note BEFORE landing**
  (`DECISIONS.md:424-431`; `loader.py:199-211`).
- **R92-3b** — the card schema has *two* readers, `loader.py` (via
  `Card.from_dict`, which hard-fails on unknown fields) and
  `tools/gen_klee_cards.py::CARD_FIELDS`; that makes any field addition a
  shared-surface change that files its note first (`DECISIONS.md:3141-3165`).
- **R8** — the conjunctive healing law killed card-based A4 probing, so the
  sustain probe is the anchor's exempt relic trickle injected via
  `package_relic_hooks`: never on `starter`, never in tier05 runs
  (`DECISIONS.md:305-317`; `loader.py:427-431`).
- **R37 / R24** — an upgrade must be sim-expressible: Catalytic Converter's
  delta became `{innate: true}` and left `UNAPPLIABLE`, satisfying the
  no-unmeasured-upgrades law rather than waiving it
  (`klee-mod/DECISIONS.md:992-1004`; `upgrades.py:77-99`, `:155-160`).
- **R36** — `discard_for_sparks` grammar: forced discard, 1 spark per card
  *actually* discarded, kit cards exempt; upgrade deltas `{discard, sparks}`
  (`klee-mod/DECISIONS.md:975-990`; `upgrades.py:356-384`).
- **R80** — Charge is never spent; upgrades may move a summon's duration but
  never Charge or conscript counts (`klee-mod/DECISIONS.md:2161-2163`;
  `upgrades.py:426-433`).
- **R67 (with R33)** — nine dead constants DELETED, each leaving a tombstone
  comment; a swept knob must record a real read through the PEP 562
  `__getattr__` hook, and the gate "may not be satisfied by adding artificial
  reads" (`DECISIONS.md:2065-2118`; `constants.py:562-567`, `:960-1013`).
- **R83** — `real_silent`'s pilot weights stay **PLACEHOLDER** (measured a dead
  lever, 24.2% vs 24.5% over 1000 runs), no poison term is added, and the
  authorized lever is the draft scorer, not this file
  (`DECISIONS.md:2623-2656`; `content/pilots/archetypes.yaml`, `silent` entry).
- **R93** — the block-panic rung's known weakness (it fires on
  incoming-vs-HP ratio alone and "will buy 4 block against 39 incoming every
  time") is **filed to the backlog, not fixed**: "Nobody changes
  `tier0/pilot/policy.py` for it now" (`DECISIONS.md:3179-3216`;
  `policy.py:45-49`, `docs/archive/backlog-2026-07-29.md`).

## 5. Traps

- **`_est` is the only legal way to read an `amount` field in the pilot.** Raw
  arithmetic on a formulaic amount crashed every tier05 run an X-cost card was
  drafted into (Malaise) — `policy.py:105-120`, and the same warning repeated at
  `policy.py:324-329`.
- **`_active_effects` reads only an enumerated predicate list**; anything else
  (`reaction_triggered_by_this`, `killed_target`) keeps top-level-only valuation
  and silently falls through (`policy.py:123-165`). A new predicate the pilot
  cannot read makes it price the whole conditional branch at zero.
- **Two documented binding NULL results live in comments and must not be
  retried**: "bank Charge before playing a Charge reader" measured *worse*
  (priest act-1 33%→27%) — `policy.py:64-70`; and the `salon_stoker` arms exist
  only so a win is attributable, with `salon_stoke_only` / `salon_spot_only`
  as ablations (`content/pilots/archetypes.yaml`, salon_stoker block).
- **The `STOKE_*` constants are deliberately NOT in `constants.py`** — that file
  is the surface `tools/lint_constant_parity.py` compares to C# by value, and a
  pilot heuristic has no C# counterpart because the mod ships no bot
  (`policy.py:554-565`).
- **Two "known understatement" lists are on the record** in the pilot weights
  file so a low anchor score is not read as a finding about the pool: Demon Form
  scoring as a one-shot, Vulnerable priced flat at `amount*2`, poison priced
  blind (`content/pilots/archetypes.yaml`, `ironclad` and `silent` entries).
- **`game_ref/` absence is TOTAL and intentional** — cards *and* character YAML
  are gitignored, so `real_ironclad` simply does not exist on a fresh clone
  (`loader.py:30-44`). When present it is atomic: a missing layer, a stale
  merged pool, or one missing upgrade raises rather than loading a partial pool
  (`loader.py:162-188`). `GITS_REFERENCE_MODE=committed-only` forces the
  absent-path behaviour (`local_reference.py:20-38`).
- **`character` is forced, not `setdefault`-ed, on external rows** — without it
  every Klee reward screen could offer a Bash (`loader.py:143-151`).
- **Frozen files that read like tunables**: `content/encounters/battery.yaml:3`
  is marked `*** FROZEN 2026-07-19 — do not retune; all comparisons depend on
  it ***`, and `block: 1.2` is frozen in *every* pilot entry
  (`content/pilots/archetypes.yaml:1-3`, and each `# FROZEN. do not tune.`).
- **Always `loader.reset_caches()`, never a single `cache_clear()`** —
  `_card_prototype` is derived from `_card_index`, so clearing one serves
  prototypes built from a content tree that no longer exists
  (`loader.py:556-567`).
- **The `kit:` list and the sheet's `kit_card:` flag must agree** — a kit card
  the sheet does not mark would silently dodge the draft-pool exclusion, so it
  is a loud error (`loader.py:381-395`).
- **A gate that sweeps nothing reports the same clean line as one that sweeps
  everything** — hence `test_the_gate_is_not_vacuous` and the "slot 4 with
  nothing wired" test asserting ≥15 findings by name
  (`test_roster_registry.py:39-71`).
- **`UNAPPLIABLE` is an empty `frozenset` on purpose**, kept so the next
  unexpressible delta has somewhere to be named instead of being tolerated
  silently (`upgrades.py:77-99`; the module docstring says the same).

## 6. Reading order

1. `tier0/roster.py` — the whole file; the docstring is the argument for the
   module's existence.
2. `tier0/content/loader.py:192-283` — `_card_index` and the load-time
   vocabulary validator: where sheets become `Card`s and what is rejected.
3. `tier0/pilot/policy.py:1-120` — the decision order, the shared valuations,
   and `_est`.
4. `tier0/content/pilots/archetypes.yaml` — every pilot's weights plus the
   frozen/placeholder/understatement notes.
5. `tier0/constants.py:521-568` — the pilot-policy knobs, then
   `constants.py:960-1013` for the sweep hook.
6. `tier0/content/upgrades.py:1-96` — the delta grammar contract, before
   touching any `*-upgrades.yaml` row.
