# Atlas — klee-mod-cards

> **Lifecycle: LIVING** — expected to change; read it to work on the project.

Scope: `klee-mod/KleeCode/Cards/` (handwritten + `*/Generated/`), the three
`Generated/manifest.json` ledgers, and the codegen contract with
`docs/{klee,furina,kokomi}-cards.yaml`, `docs/*-companions.yaml`,
`docs/*-upgrades.yaml`.

## 1. Purpose

The **C# card layer the shipped mod loads**, plus the machinery keeping it
equal to the ratified YAML sheets. Almost all of it is emitted:
`tools/gen_klee_cards.py` turns each character's sheet into one `.cs` per card,
a roster class, and a manifest, so the sheet stays the single source of truth
through implementation. The generator is explicitly **not** an approximator —
"Any effect, card-level cost, condition, or lifecycle rule without an
implemented runtime is NOT emitted... A generator that emits a
plausible-looking wrong body is worse than one that emits nothing"
(`tools/gen_klee_cards.py:11-18`). `Generated/` is **not** editable source: every
file carries a DO-NOT-EDIT header and the directory is deleted and rewritten on
each regen (`_write_plan`). The handwritten cards in `Cards/` and
`Cards/{Furina,Kokomi}/` exist only because their lifecycle is machinery rather
than ops; they are the one place sheet↔C# drift is possible, hence their lint.

## 2. Entry points

From the repo root with `PYTHONPATH=.` (validate.ps1 pins the same via
`Invoke-RepoPython`, `klee-mod/build/validate.ps1:274-296`):

```sh
PYTHONPATH=. python3 tools/gen_roster_cards.py            # regen all 3 profiles
PYTHONPATH=. python3 tools/gen_roster_cards.py --check    # CI guard (S6a)
PYTHONPATH=. python3 tools/gen_klee_cards.py --character furina   # one profile
PYTHONPATH=. python3 tools/lint_generated_structure.py    # L1/L2/L3 on emitted .cs
PYTHONPATH=. python3 tools/lint_handwritten_parity.py     # handwritten vs sheets (S6)
PYTHONPATH=. python3 tools/lint_pool_membership.py        # every class pooled (S6b)
PYTHONPATH=. python3 tools/lint_unique_names.py docs/klee-cards.yaml \
    docs/furina-cards.yaml docs/kokomi-cards.yaml docs/mondstadt-companions.yaml \
    docs/fontaine-companions.yaml docs/inazuma-companions.yaml
PYTHONPATH=. python3 -m pytest tier0/tests/test_roster_codegen.py \
    tier0/tests/test_generated_structure.py tier0/tests/test_sheet_lints.py -q
```

In-process: `gen.blocked_reason(card, profile)` (`gen_klee_cards.py:961`),
`gen.emit(card, profile)` (`:5052`), `gen.upgrade_plan(card)` (`:2279`),
`gen.pascal(id)` (`:881`), profiles in `gen.PROFILES` (`:168`); the one driver
is `gen._run_profile(profile, check)` (`:5997`), planning through
`gen.PLAN_BUILDERS`.
Live inventory: klee 68 generated + 48 companions + 8 blocked; furina 81/82 +
3 Guest Stars; kokomi 70/76; 287 card classes, all pooled.

## 3. Key invariants

- **Sheet in, C# out, one direction.** Each file's header names script and
  sheet, "DO NOT EDIT. Edits are lost on the next regen"
  (`gen_klee_cards.py:20-22`; e.g. `Cards/Generated/QuickFuse.cs:1-7`).
- **`--check` compares three things**: per-card content, *extra* `.cs` files in
  the out dir, and the manifest bytes (`_check_plan`) — one implementation for
  all three profiles since F3, reading the same `ProfilePlan` the write path
  writes.
- **`CARD_FIELDS` is deliberately total** — an unknown card-level field blocks
  the card by name rather than being ignored (`:790-837`, `card_level_reason`
  `:840-847`). It caught `innate` and `retain` (`:791-813`); `tempo_band` had to
  be added or every personal row would block (`:827-831`) — **234** today
  (76 / 82 / 76), and the count is read from the sheets, not from this line.
- **`MECHANICAL_OPS` is a whitelist backed by verified C# call sites**; an op
  outside it blocks (`:200-227`, refused `:996-998`). Per-op field whitelists
  apply the same rule one level down (`:244-268`).
- **Partial upgrades are forbidden** — a card gets its whole ruled delta or no
  `OnUpgrade` body plus a manifest entry (`:2194-2202`); deltas come only from
  `docs/*-upgrades.yaml` (`:46-49`, `:678-684`).
- **A card's `sly` (discard) branch is re-run through `blocked_reason`** via
  `_sly_view`; an unchecked branch is the same surface with the alarm off
  (`:928-939`, `:4442`).
- **`sly:` is one list carrying two things** (EB-71, R174, C# leg 2026-08-12).
  The authored riders (`effect_walk.sly_riders`) become the
  `AfterCardDiscarded` hook and the `[gold]Sly[/gold]:` line on the face; the
  reserved `{op: sly_autoplay}` marker is the base game's own `CardKeyword.Sly`
  and rides `CanonicalKeywords` beside Exhaust/Innate/Retain — no body, no
  description line, because the game resolves the auto-play itself and a hook
  beside it would resolve the discard twice. A marker carrying any other key
  (Hand Trick's `until: turn_end` grant) is runtime state with no C# rail and
  BLOCKS. Guard: `tools/lint_sly_grammar.py`; pins:
  `tier0/tests/test_eb71_cs_parity.py`.
- **`EB-118`'s new C# surfaces are merged and UNREACHED** (2026-08-23). Four
  ops joined `MECHANICAL_OPS` with verified call sites — `spend_spark`
  (`:217`), `salon_rotate` / `salon_perform` (`:226`), `recall_to_draw`
  (`:252`), `choose_one` (`:260`) — and **no committed sheet row prints any of
  them**, so `--check` output and every manifest are byte-identical to the
  pre-branch tree. Landing sites: `recall_to_draw` rides
  `Powers/RecallFromExhaust.cs` (`Recall`), whose `Recallable` pool filter *is*
  §6.4 constraints 3–6 while constraints 1–2 are card SHAPE checked in
  `blocked_reason` (`:1530-1545`) — the generator reads the sheet directly and
  never passes through `loader._validate_recall_shape`, so a row that reaches
  the emitter has been checked on both sides of the wall; the `IExhaustRetriever`
  marker is stamped from the same printed shape tier0 reads. `salon_perform`
  rides `SalonMemberPower.PerformLeftmost` (`:3339`, `:3663`), which loops
  `PerformMember` — the one body the turn-start upkeep also runs, mirroring
  `effects.salon_member_act`; a second copy of it is the defect the shape
  exists to prevent. `salon_rotate` rides `RotateLeftmost`, a pure reorder.
  Chosen `exhaust_from` now brackets its selector with
  `ExhaustSelection.Open` / `Record` / `Close` (`:4203-4216`), the twin of
  tier0's `CombatState.exhaust_selection`, keyed on the resolving card INSTANCE
  and the seat (a tracker keyed on anything shared is right solo and wrong in
  co-op).
- **`choose_one` INVENTS NO UI** — `Cards/ModalChoice.cs` is a thin wrapper over
  the base game's own card-level choice: `CardSelectCmd.FromChooseACardScreen`
  (the ≤3-option screen Splash/Discovery/Quasar and the generation Potions
  already use), sequenced by the `PlayerChoiceContext` every `OnPlay` receives
  and co-op-synced as `PlayerChoiceType.Index`; `CardSelectCmd.Selector` keeps
  a modal card answerable by the understudy bot rather than a wall. The
  mode-taken record mirrors tier0's `mode_chosen` emit field for field
  (`tier0/tests/test_eb118_modal_parity.py` reads it out of the source).
  **Two `choose_one` effects on one card BLOCK** — one `modeIndex` local and
  one screen per play, so they would collide on both (`:1631-1633`).
- **Ethereal is a keyword REUSE, not a new rail.** `ethereal: true` on a base
  row joins `CARD_FIELDS` (`:1019` — without the entry the first card ruled
  Ethereal from print would BLOCK on an unknown field) and emits
  `CardKeyword.Ethereal` **first** in the `CanonicalKeywords` array, beside
  Exhaust/Innate/Retain, because the canon pairing spells it that way
  (Apparition: `{ Ethereal, Exhaust }`) — `:5924-5933`. The keyword is the
  whole implementation: the game's own end-of-turn sweep reads `Keywords` and
  exhausts the card (`causedByEthereal: true`), so there is no body and no hook,
  and the description string never hand-writes the word. The
  `remove: ethereal` upgrade delta emits `RemoveKeyword(CardKeyword.Ethereal)`
  in `OnUpgrade` (`:5527-5532`), the canon shape verbatim (Apparition,
  EchoForm, VoidForm each print it and each remove it, changing nothing else).
  Precedent already shipping in the mod: Furina's `EtherealSpotlight` token.
- **Two handwritten sets, not interchangeable**: `HAND_WRITTEN` is Klee-only
  (guarded by `profile is KLEE_PROFILE`), `HAND_WRITTEN_ROSTER` is
  Furina/Kokomi (`:653-676`, `:941-945`).
- **A blocked companion or Guest Star is a build failure**, not a manifest row
  — `SystemExit` (`_plan_klee`'s companion loop, `_plan_roster`'s Guest Star
  loop).
- **Generated classes are `autoAdd: false`; pool classes own membership**
  (`:5384-5389`, `:5474`); every `CustomCardModel` must be reachable from a
  character pool or `CardModel.Pool` falls through to `MockCardPool` and throws
  "You monster!" on draw (`tools/lint_pool_membership.py:1-27`, ledger `:41-58`).
- **Cadence is profile business, never per-card**: Klee/Kokomi
  `catalyst_attack`, Furina `skill_grade` (`gen_klee_cards.py:96-108`, `:110-157`).
- **Encoding + naming gates**: every text read/write declares `encoding=` or a
  Windows regen ships mojibake into the mod's Localization strings
  (`tools/lint_text_encoding.py:1-14`); display names are unique across cards
  AND relics plus the reserved list (`tools/lint_unique_names.py:1-42`,
  `docs/reserved-card-names.txt:1-20`).

## 4. Rulings that shaped it

- **R23** — the aura batch stays handwritten; its per-target bonuses live in
  `ModifyDamageAdditive`, which codegen does not emit
  (`docs/archive/klee-r23-r25-rulings.md:8-56`; `gen_klee_cards.py:655-659`).
- **R24** — `*-upgrades.yaml` is the only source of upgrade deltas; codegen
  defaults ABOLISHED, partial application forbidden, no-delta cards ship with
  none plus a manifest flag (`docs/archive/klee-r23-r25-rulings.md:57-80`;
  `gen_klee_cards.py:678-684`, `:4788`; `Cards/Generated/manifest.json:134`).
- **R20** — inline `upgrade:` on a card sheet is deprecated, so a stray inline
  key blocks (`tier0/DECISIONS.md:424-431`; `gen_klee_cards.py:985-988`).
- **R34** — X-cost cards are exempt from spark spend; the codegen X-guard keeps
  drift loud (`klee-mod/DECISIONS.md:963-967`; `gen_klee_cards.py:877-908`).
- **R36** — `discard_for_sparks` = forced player-chosen discard, 1 Spark per
  card actually discarded, kit cards exempt via `KitGrant.NotKitCard`
  (`klee-mod/DECISIONS.md:975-990`; `gen_klee_cards.py:186-193`).
- **R37** — an upgrade must be sim-expressible; `{innate: true}` emits
  `AddKeyword(CardKeyword.Innate)` in `OnUpgrade`
  (`klee-mod/DECISIONS.md:992-1004`; `gen_klee_cards.py:699-703`).
- **R52 (ask N1)** — Kokomi's cadence is CATALYST, structural in the profile
  rather than authored per card (`tier0/DECISIONS.md:1318-1320`;
  `gen_klee_cards.py:141-146`).
- **R69** — the uniqueness namespace is "names the player sees", so relics are
  in it and both sides of a settled clash are reserved
  (`tier0/DECISIONS.md:2190-2205`).
- **R85** — `register` joins the SHARED card schema, inert on both readers; C#
  parity for twelve cards was deferred by name (`tier0/DECISIONS.md:2699-2745`;
  `gen_klee_cards.py:821-826`).
- **R86** — that deferral was paid off and the set **deleted, not emptied**:
  "an empty set is an invitation" (`tier0/DECISIONS.md:2757-2772`;
  `tier0/tests/test_roster_codegen.py:53-61`).
- **R87** — GrandFinale silently lost `new DynamicVar("BonusPer", 2m)` to an
  indentation bug with 1296 tests green; hence `lint_generated_structure.py`
  parses the emitted `.cs` rather than calling back into the generator
  (`tier0/DECISIONS.md:2834`; `tools/lint_generated_structure.py:5-27`).
- **R92-3b** — the sheet schema has TWO readers (`tier0/content/loader.py` via
  `Card.from_dict`, and `gen_klee_cards.CARD_FIELDS`), so a field addition is a
  shared-surface change that files a cross-session note BEFORE landing
  (`tier0/DECISIONS.md:3149-3161`; mirror `docs/roster-codegen.md:118-134`).

## 5. Traps

- **`Cards/*/Generated/` is wiped on every regen** — anything hand-added there
  vanishes silently (`gen_klee_cards.py::_write_plan`).
- **Klee's manifest has a different SHAPE**: `generated`/`companions`/`blocked`/
  `upgrades`, with no `profile`, `coverage`, or `runtime_clusters`
  (`_plan_klee` vs `_plan_roster`) — code reading `coverage` KeyErrors on Klee.
  F3 unified the *driver*, not the schemas: those bytes are committed output.
- **`Cards/Generated/` holds Klee's cards AND all 48 companions** from three
  `*-companions.yaml` sheets, plus `CompanionRoster.cs`; only the manifest
  separates them (`_plan_klee`).
- **`"hand-written"` in a `blocked` map is a finished decision, not a gap** —
  checked first so completed work never re-reports as an open workstream
  (`_furina_runtime_cluster`, `_kokomi_runtime_cluster`).
- **Text-identical mechanism loss is the standing defect class**: `exhaust`,
  `innate`, `retain`, literal `times`, `bonus_formula`, the fanfare keyword
  grants and `crash_fanfare` render the same face with or without the
  mechanism, so the curated L3 table is the only catcher
  (`tools/lint_generated_structure.py:134-231`). New invisible mechanic ⇒ new row.
- **L2's orphan exemption is conditional**: `CalculationBase`/
  `CalculationExtra`/`ExtraDamage` are exempt only when a `Calculated*Var`
  consumes them, else they are "half a rider" (`lint_generated_structure.py:96-104`).
- **A `kit_card` row must override `GetResultPileTypeForCardPlay` to
  `PileType.None` on every sheet** — the C# default is type-derived, so an
  Attack/Skill-shaped Burst recirculates into the deck; that is how
  `let_the_people_rejoice` shipped broken while `sparks_n_splash` looked fine
  (`tools/lint_handwritten_parity.py:241-262`).
- **Parity coverage = `HAND_WRITTEN` + `HAND_WRITTEN_ROSTER` − `ROSTER_DEFERRED`,
  checked in BOTH directions**: a deferred row that now parses fails as a STALE
  DEFERRAL (`lint_handwritten_parity.py:297-331`, `:388-402`), and `Unparseable`
  is always loud, never a skip (`:22-27`, `:53-55`).
- **`docs/roster-codegen.md` is partly stale by its own admission** — a
  2026-07-26 correction block up top, and it still quotes "75 of 76" Furina
  cards against the live 81/82 (`:5-16`, `:71-76`). The manifests are the
  coverage ledger; the doc is the contract prose.
- **`Confiscated.cs:16` names `KleeExtraCardPool`, which no longer exists** —
  the off-pool ledger is `KleeOffPoolCards.cs`, whose docstring also records
  that its "a second pool could never work" paragraph is now FALSE and was
  nearly acted on as true (`klee-mod/KleeCode/KleeOffPoolCards.cs:24-45`).

## 6. Reading order

1. `tools/gen_klee_cards.py:1-160` — the refusal contract, sheet/out-dir
   constants, and the three `CharacterProfile`s.
2. `tools/gen_klee_cards.py:821-1020` — `CARD_FIELDS`, `card_level_reason`, top
   of `blocked_reason`: everything that decides *not* to emit.
3. `klee-mod/KleeCode/Cards/Generated/manifest.json` then
   `Cards/Furina/Generated/manifest.json` — the two manifest shapes side by side.
4. `tools/lint_generated_structure.py:1-134` — the three laws, and why the lint
   is generator-independent.
5. `tools/lint_handwritten_parity.py:1-56` and `:241-262` — the only drift-prone
   path, and the kit invariant that already burned us.
6. `docs/roster-codegen.md` — the prose contract (read its correction block
   first), before touching a profile or the sheet schema.

## 7. The prototype surface — a fourth emitter that is not a fourth character

`EB-147` (R213 B) added `docs/prototype-surface.yaml` and
`tools/gen_prototype_cards.py`, emitting into
`klee-mod/KleeCode/Cards/Prototype/Generated/`. Four facts a reader of §1–§6
would otherwise get wrong:

- **It is NOT a `CharacterProfile` in `PROFILES`.** `--character all` means
  `PROFILES.values()`, so registering it there would put prototypes in the
  DEFAULT run by definition — which is the one thing R213 B forbids. It is a
  separate script with its own out dir, manifest and namespace, and
  `lint_roster_registry` (which reads `def _plan_<id>(`) still sees exactly
  three characters. `PLAN_BUILDERS` is untouched.
- **The emitter is the SAME emitter.** `gen_prototype_cards` owns no templates:
  it calls `blocked_reason` and `emit` with the OWNING character's profile,
  `dataclasses.replace`d on the four location fields only. `character_id`,
  `native_element`, `cadence`, `art_loader` and `emit_character_identity` stay
  the owner's, so a Kokomi prototype keeps the catalyst cadence and its
  `CharacterId`. (Side effect worth knowing: `profile is KLEE_PROFILE` is
  FALSE for a replaced Klee profile, so the `HAND_WRITTEN` short-circuit and
  the Klee header shape do not apply to prototype rows. Neither should.)
- **A blocked prototype row is a `SystemExit`, not a manifest entry** — the
  opposite of the character profiles. A sheet may legitimately run ahead of
  the runtime; this surface exists to be played at the real game this week.
- **`PrototypeRoster.cs` is committed even when the surface is EMPTY**, because
  `KleeMod.PrototypeCards` names it under `#if PROTOTYPE_CARDS` and a dev build
  of an empty surface must still compile. It is in
  `lint_pool_membership.MEMBERSHIP_FILES`: the quarantine covers measurement,
  never runtime legality, and a poolless prototype would throw "You monster!"
  the first time a staged turn drew it.

Commands and the deletion rule: `docs/current/OPERATIONS.md`, "Prototype
surface". Packet: `review/active/eb147-prototype-surface-2026-08-27.md`.
