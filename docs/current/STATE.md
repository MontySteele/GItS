# STATE

> **What currently ships** — roster, systems, versions, and active workstreams.
> Snapshot only: how a stamp reached its current value lives in the commit
> messages that carry it, not here. Open decisions live in
> [`docs/current/QUEUE.md`](QUEUE.md); engineering tasks in
> [`docs/current/BACKLOG.md`](BACKLOG.md); normative rules in
> [`docs/current/LAW.md`](LAW.md); measurement law and active registrations in
> [`docs/current/EXPERIMENTS.md`](EXPERIMENTS.md); how-to commands in
> [`docs/current/OPERATIONS.md`](OPERATIONS.md).

## Live cell

**`RT12 / D17 / P10 / C19`**, read live via `tier05/cells.py`, with
`PILOT_WEIGHTS_VERSION` **5**. Numbers are never comparable across a stamp
boundary unless labeled, and a report without a stamp is not citable
(`EXPERIMENTS.md`).

| stamp | value | source | what this value covers |
|---|---|---|---|
| `RT` `RUNTEMPLATE_VERSION` | **12** | `tier0/constants.py` | The run-layer half of the window-2 correctness batch (`EB-104`): the shop receives the run's Featured Banner, potion capacity is derived from held relics on read, the rest-site heal floors, Book of Five Rings counts event deck-adds through one door, and event card-reward screens roll rarity through `RARITY_ODDS`. |
| `D` `DRAFTER_VERSION` | **17** | `tier0/constants.py` | **`EB-118` Phase-3 Window 3's two new pricing terms** (R211, [USER] 2026-08-25), and the first bump in the series where the drafter learns a **cost** rather than a value. **(a) `STATIC_SPARK_SPEND_COST = 2.5`** — the `spend_spark` branch of `_op_price` stops reading the dead GAIN dial with the sign flipped and reads its own live one. The bump is **UNCONDITIONAL and was owed in writing**: that branch carried an explicit no-bump licence naming what would spend it — "the first sink card that prints it" — and `powder_charge` is that card. The value is **DERIVED, not picked** (three routes; two converge on 2.50 from opposite directions) and taken at the TOP of the convergent range under R194's direction rule, so the residual error under-values the sink rather than over-valuing it. **(b) `spotlight_moved_this_turn` joins `STATIC_STATE_CONDITIONS`** at share **`STATIC_SPOTLIGHT_MOVED_SHARE = 0.167`**, the measured spotlight-arm rate; R211 ratified the rider but not the share, and 0.167 is the conservative end of the defensible band (0.167–0.5). **BOTH VALUES ARE [USER]-OVERRIDABLE and each lives in exactly one constant.** **The archive scope is unusually small and that is the point: FOUR ROWS, three of them new.** The spend dial re-prices the three new sinks (`powder_charge` 7.0000/10.0000 → **2.0000/5.0000**, `hold_the_line` 5.0000/8.0000 → **0.0000/3.0000**, `smoke_and_sparks` 6.0000/8.0000 → **1.0000/3.0000**) and NOTHING ELSE — R211 kept `STATIC_SPARK_VALUE` at 0.0, so all eleven shipped Klee Spark rows and `prune_witch_hunt` are unchanged to four decimals. The rider re-prices `take_it_from_the_top` (5.0000/5.0000 → **6.6700/7.3380**, which is the whole reason it was taken: the upgrade was invisible on both faces) and `curtain_cue` (0.0000 → **0.4002**). **`directors_cut` does NOT move at any share** — both its branches pay in dead dials — which corrects an expectation the `EB-118` row carried. `D16` beneath it was `EB-118` Phase 2's two formerly-inert terms going live (`STATIC_ETHEREAL_SHARE` pricing `big_badda_boom` 8.0000 → 4.8000 base, and `choose_one`'s `MAX(modes)` arbitration reachable but moving no number; the share is RATIFIED at 0.6, R205). `D15` beneath that is `EB-43` — the spotlight limb of `core_complete`/`_core_progress` requires a machinery payoff. |
| `P` `POLICY_VERSION` | **10** | `tier05/draft.py` | **`EB-118` Phase-3 Window 3's exhaust-chooser repair** (R211). **Not a flip — no switch was staged for it.** `policy.exhaust_victim`'s DEFAULT payout hook changes from `identity_blind_payout` to **`formula_aware_payout`**, which pays a candidate the MARGINAL contribution it would make to the exhausting card's OWN printed `exhaust_selection_*` count, times that card's own printed `per`, times the board its own printed `target` names — R211's **multiplicity clause**: an `all_enemies` formula multiplies by `len(state.living_enemies)`. It is derived from what the card prints, never a hardcoded prefer-expensive: change the slope and the chooser changes with it, delete the card and the chooser is identity-blind again. `PILOT_WEIGHTS_VERSION` **5** labels the weight that arrives with it, **`EXHAUST_FORMULA_PAYOUT_WEIGHT = 1.0`** — and unlike v2/v3/v4 this is a genuinely NEW weight rather than an existing one entering the read set. **What re-baselines is narrower than the stamp suggests, and it is asserted rather than argued:** the hook returns 0.0 for any card printing no selection formula, exactly TWO rows on any sheet print one (`pearl_barrage`, `the_tide_remembers`), and the chooser is deterministic given the pool — so every other chosen-Exhaust carrier's pick is provably unchanged, all twelve of them, Sly riders included. That sweep is a test, and it exists BECAUSE it replaces a fourth scratch run that would have been provably bit-identical to baseline. The **Rare-rotation trade is ACCEPTED and paired with retrieval** (`shell_of_sanctuary`'s W3 body loans a rotated Rare back out of the Exhaust pile). `P9` beneath it was the Phase-2C mode-chooser flip (`MODE_CHOOSER_ENABLED` True, `effects._chosen_mode` asking `policy.choose_mode`); Phase-2A's `PILOT_POLICIES_ENABLED = True` is inside that value at `P8`. |
| `C` `CONSTANTS_VERSION` | **19** | `tier0/constants.py` | **`EB-118` Phase-3 Window 3's card-body pass** (R211, [USER] 2026-08-25 — the `W3` ratification slate). ONE window, **EIGHT sheet rows, all three characters**: five NEW rows and three **REWRITES THAT KEEP THEIR CARD IDS**. **Klee** gains the three ratified Spark sinks, the first rows on any sheet to print `spend_spark` — `powder_charge` (spend 2, `detonate bonus: 4`, upgrade `{bonus: +3}`), `hold_the_line` (spend 2, Block 5, `enemy_intends_attack` → Block 6, upgrade `{conditional_block: +3}` raising both halves) and `smoke_and_sparks` (spend 2, Vulnerable 3, upgrade `{vulnerable: +1}`). The 3–4 sink floor is met AT THREE. **All three are `role: glue`, so no payoff count moves anywhere**; what moves is sub-pool size, and `klee/spark`'s payoff DENSITY falls 24% → 21% — a disclosure, not a breach (that arm is not on R199's priority list), and the second consecutive window in which it thins. The Spark price is at TOP LEVEL on all three, which is structural: a `spend_spark` in a branch is invisible to the playability gate and the payoff would fire unpaid. **Furina** gains `change_the_bill` (`salon_rotate` + `salon_perform` + Block 3, upgrade `{block: +3}`) — the first sheet row in the repo to print EITHER Salon verb, both built and unused since Phase 2 — and `take_it_from_the_top` (Block 5 + `spotlight_moved_this_turn` → 10 damage, upgrade `{conditional_damage: +4}`), which takes `furina/spotlight` payoff supply 5 → 6 over a sub-pool 17 → 18: **fourth in the ruled priority order, so a disclosure item**. **Kokomi's pool stays at 76 rows AND at the same 76 ids**: `pearl_barrage` stops reading the exhaust PILE and reads the CARD YOU CHOSE (`exhaust_from 1 chosen` + `5 + 3 per exhaust_selection_cost`, delta `{formula_per: +1}` → `{formula_base: +3}`, ladder 5/8/11 over the whole live range because her sheet has no card above cost 2); `shell_of_sanctuary` keeps its id and becomes **"Salvage the Line"** (cost 2 → 1, `block 11` → draw → **recall from exhaust** → Charge 2 → Block 4, `exhaust: true`, `[generic]` → `[priest, assist]`, upgrade sheet UNTOUCHED because `{block: 4}` was already the ruled 4 → 8); `the_tide_remembers` keeps its id and becomes **"Tide of Names"** (`exhaust_from 1 chosen` + `5 + 2 per cost` to ALL, delta `{damage: +3}` → `{formula_base: +2}`, tags and role unmoved so `kokomi/priest` holds at 12). **The effect order on Salvage the Line is the ruled correction and it is load-bearing** — recall-then-draw puts the rescued card at draw-pile index 0 and the draw pops index 0, so it would land straight in hand, defeating the rule that a retrieved card goes to the TOP of the draw pile and never to hand. It is also the repo's FIRST Exhaust-retrieving row, so `lint_recall_exhaust`'s card-shape leg stops being vacuous. **Two standing debts move, measured:** the flat-Block clone cluster 8 → 7, and the exhaust-pile reader family 5 → 3 (which completes R208's `damage@one~` five-to-two). `kokomi` near-duplicates hold at 29 against an untouched limit of 30; distinct signatures `kokomi` 57% → 59%, `klee` 62% → 63%, `furina` 76% → 76%. **The standing read this window owed is TAKEN and PUBLISHED** (`review/active/sitting-reads-2026-08-25-c19-d17-p10.md`), **DIAGNOSTIC-SCOPED and NOT the Phase-4 milestone table** (R211 item 7): the pilot has no hold-versus-spend term for Sparks, and its scorer reads neither Furina row's state nor Tide of Names' payout, so those numbers are floors and a null result on them is not evidence. `C18` beneath it was **`EB-136`'s same-target binding** (R210, [USER] 2026-08-25 — full parity). Not a sheet window and not a card-body pass: no printed number, label, upgrade delta or dial value moves. What moves is how the resolver AIMS. A card's `target: enemy` ops used to re-resolve INDEPENDENTLY PER OP to the lowest-HP living enemy; they now bind to ONE creature picked at card-play construction and held for the whole play, which is C#'s `init`-only `cardPlay.Target`. `times` binds in the same pass (hits after the aim dies fizzle, no re-pick); `force_random_targeting` rolls once per card and only for a card that aims; and the dead-target rule is reproduced op by op AND IS NOT UNIFORM — aimed damage FIZZLES (`AttackCommand` breaks), aimed powers LAND ON THE CORPSE (`PowerCmd.Apply` guards only `CanReceivePowers`), and `place_bomb`, `move_bombs`, `detonate`, `apply_aura` and `swirl` land there too, each on the decompiled evidence recorded in the blast-radius audit. **Archive: every combat AND tier-0.5 number for every character, INCLUDING THE ANCHOR'S** — the ruled scope is 28 live cards plus 7 more for `times`, and it reaches `ref_ironclad`'s starter `bash`, `ref_silent` and both `real_*` pools. The anchor renormalises to 3.0 on every axis by construction, which is exactly why its moved combat behaviour is declared: it is the DIVISOR in `axes.normalize`, and `bash`'s Vulnerable now lands on the body its 8 killed instead of walking to a living bystander — a live debuff removed, not a rounding difference. Named consequences: `sparkly_explosion`'s `C17` DIAGNOSTIC caveat is **CLEARED**; `EB-118` (1)'s bomb-placement chooser is superseded for `target: enemy` (nothing in `policy.py` edited, and the `W4` sweep's source-derived scope narrows behind it); and ONE question is left open on purpose — `_op_swirl`'s aura re-aim, which Q1(b) and the row's destination-scoring severance answer differently, pinned as unruled by a strict xfail. **No standing baseline is owed (R207 as agreed at the ruling): `W3`'s single public read absorbs the movement and this landed before it; the disclosure is a commit-hash scratch in PR text.** `C17` beneath it was the `EB-118` Phase-3 **Window 2b card-body pass** (R208) — five ratified bodies across all three sheets, the first window since `C13` to archive all three characters at once: `sparkly_explosion` becomes `move_bombs` + `detonate bonus: 3` + `damage 14` in that order (upgrade `{damage: +5}` unchanged, so 14 → 19; `spark` tag dropped); `standing_room_only` becomes Block 3 plus an `encore_at_least_5` branch paying Block 3 else a draw, retyped attack → skill with `role` payoff → glue and upgrade `{block: +2}`; `dramatic_entrance` becomes Deal 7 plus a `fanfare_at_least_12` 7-to-ALL branch, no label moving; `undertow` takes exactly two changes (formula base 4 → 5, an appended `exhaust_pile_at_least_3` draw) and keeps everything else; `depths_judgment` becomes Deal 14 plus a Block 8 branch, upgrade `{formula_per: +1}` → `{damage: +4}`, and its bar reads **`exhaust_pile_at_least_8`** — item (f) of that window, ruled late into it by R209 ([USER] 2026-08-25, pre-merge), which moved the bar 6 → 8 on both faces against clean fire rates of 38.4% and 24.2%; under R58 the bar may rise again and may never come down. `C16` beneath that was Window 2's three ratified Kokomi bodies (`moon_signal`, `crane_wing`, `tighten_the_cords`) plus `encore_performance`'s ruled `{retain: true}`; `C15` beneath that was Window 1's label pass (sixteen `role` conversions, five `archetypes` changes, and `SecretStash.cs` dropping Big Badda Boom from `demolition_commons`); `C14` beneath that was `deep_breath`'s mode 2 (`spend_encore 3` + `draw 3`, R205); `C13` beneath that was the `EB-118` Phase-2 sheet-and-engine integration window, and `C13` is the world the standing baseline below was read in. |

**Standing baseline:** `review/active/sitting-reads-2026-08-25-c19-d17-p10.md`
— twelve arms, taken at `RT12/D17/P10/C19` on `main` = `a247f25`, all twelve in
ONE pass with `game_ref/` present, so both `real_*` floors sit in the main
tables rather than in an addendum (`real_ironclad` **5.2%** win / **65.5%**
act-1, `real_silent` **1.2%** / **54.1%**). It is `W3`'s single public read and
it **publishes DIAGNOSTIC-SCOPED rather than as the Phase-4 milestone table**
(R211 item 7): the pilot has no hold-versus-spend term for Sparks, and its
scorer reads neither new Furina row's state nor Tide of Names' payout, so those
rows contribute FLOORS and a null on them is not evidence. **Its Δ column spans
`C13` → `C19`** — five `CONSTANTS_VERSION` bumps, `D16` → `D17`, and `P7` →
`P10` — because none of `C15`, `C16`, `C17` or `C18` was owed a standing
baseline and none was given one; this read absorbs their movement as R207's
sequencing intended. **No row's Δ is attributable to `W3` alone.**
Per-character attribution inside `W3` is by commit-hash scratch comparison
(R207), taken at build time, and is not citable the way a stamped table is.
**The table has NO control set and says so**: `C18` moved the anchor's own
combat behaviour, so `ref_ironclad` and both `real_*` floors moved with the
roster and none of the three is a control across this span. The one interval
separation anywhere in it is `kokomi / priest` act-1, 39.9% → **45.0%**. It
supersedes `review/active/sitting-reads-2026-08-24-c13-d16.md`, which stands as
published (R101b).
Under **R207** a published standing table is owed at a meaningful product
milestone or when a
pending decision needs one; intermediate attribution is by commit-hash scratch
comparison, which is not citable the way a stamped baseline is
(`EXPERIMENTS.md`). Version stamps themselves are unchanged: every change to a
published-world variable still bumps its stamp. **The Phase-4 milestone read
follows when the three diagnostic caveats above clear; it is not owed at any
bump landed so far.**

Pinned, and NOT part of the run-cell stamp:

- `A6_INSTRUMENT_VERSION = 2` (`tier0/harness/axes.py`) — the scorecard's
  application-uptime term (`0.5*aoe + 0.3*debuff + 0.2*uptime`), anchored
  ADDITIVELY so `ref_ironclad` stays exactly 3.00. v1 and v2 A6 numbers are
  discontinuous by design.
- Heuristic pilot weights live in `content/pilots/archetypes.yaml` and
  `pilot/policy.py`; `STOKE_*` are deliberately NOT in `constants.py`.
- `RUN_NODE_TEMPLATE = "NNNRETN$ERB"` is DEAD as of `RT` v6, kept only as the
  archived-world name and for tests that pin a node sequence.
- **Acts** (`RUN_ACTS`): `act1` (easy_fights 3), `act2` "the Hive" (2), `act3`
  "Glory" (2).
- **Map (StS2 DAG):** `MAP_FLOORS = 16`, `MAP_TREASURE_FLOOR = 8`,
  `MAP_REST_FLOOR = 14`, `MAP_BOSS_FLOOR = 15`, `MAP_MAX_EDGES = 3`,
  `MAP_MAX_FLOOR_WIDTH = 6`, `MAP_PATHS = 6`. Room odds
  `N 0.53 / ? 0.22 / R 0.12 / E 0.08 / $ 0.05`.

## Lifecycle

- **Tier 0 v0.1 — LOCKED.** Frozen v2 errata: non-boss Frozen is **soft
  control** (−50% next action + Shatter on the first Attack hit), bosses take
  **Vulnerable 2** instead (§2.2; R44). The v0.1 scorecard baseline and median
  identity are regression-locked (`test_errata.V02_MEDIAN`).
- **Tier 0.5 M5 — SHIPPED.** The live run model is the real StS2 map; the
  M5–M8 archive world was the v1 run template, and its run-layer numbers are
  never compared across template versions unlabeled.
- **Kokomi meter-20 — RATIFIED (R139).** The current build is the comparison
  baseline; the dead v0.3 W1 comparator is not rebuilt.
- **Roster slot 4 — Zhongli countersigned (R108), not yet scheduled.** The deep
  dive is unblocked; the pre-slot-4 gate is the roster registry
  (`tier0/roster.py`).

## Roster

Ship order is stable and meaningful (`tier0/roster.py`); reports print it.

| id | display | nation | element / cadence | default plan | archetypes |
|---|---|---|---|---|---|
| `klee` | Klee | Mondstadt | Pyro, catalyst-grade (all attacks apply) | demolition | demolition, spark, reaction |
| `furina` | Furina | Fontaine | Hydro, Skill-grade | salon | salon, spotlight, fanfare |
| `kokomi` | Sangonomiya Kokomi | Inazuma | Hydro, catalyst cadence | priest | priest, commander, assist |

Klee is the compatibility baseline character. Companion pools ship per nation:
`docs/mondstadt-companions.yaml`, `docs/fontaine-companions.yaml`,
`docs/inazuma-companions.yaml`.

**Reference anchors** (measurement anchors, NOT roster members — no art, no
pool, no C# class): `ref_ironclad`, `real_ironclad`, `ref_silent`, `real_silent`
(`tier0/roster.py:165-171`). The scoring anchor is `("ref_ironclad", "starter")`
under the `generic` pilot, normalized so every axis reads exactly `3.0`. The
`real_*` variants depend on a local `game_ref/` tree that is gitignored and
absent on a fresh clone; both pools verify (ironclad 76, silent 87) and both
anchors load. Still owed there: three `*_char_facts.yaml` that no roster arm
reads, a durable-backup location ([USER]'s call), and a guard against the
destroyer — BACKLOG `EB-128`.

## Content inventory

Live sim inventory (`docs/current/atlas/tier0-pilot-roster.md` §2): **322 cards
in the loader index** (3 are acquisition-only Ancient side-sheet rows, leaving
the 319 the atlas quotes; 317 → 322 at `W3`, which added five personal rows and
rewrote three in place), **5 character sheets** (3 roster + 2 reference),
**6 encounters, 15 pilot weight sets**. The battery encounters are frozen
(`content/encounters/battery.yaml`, FROZEN 2026-07-19). Card sheets
`docs/klee-cards.yaml`, `docs/furina-cards.yaml` and `docs/kokomi-cards.yaml`
all carry the `tempo_band:` field and hold **239 personal rows** (79 / 84 / 76);
Kokomi's 76 are **5 basic / 31 common / 26 uncommon / 14 rare, 70 draftable**,
and `W3` held them there on purpose — all three of her Window-3 items are
rewrites of existing rows under their existing ids, so neither her count nor
her id list moved. Klee's 79 are 76 + the three `W3` Spark sinks; Furina's 84
are 82 + the two `W3` Salon/Spotlight rows.
Balance numbers (HP, decks, bands) live in `tier0/content/characters/*.yaml`,
the ratified artifact — not in the registry. Furina's pool carries **zero**
`raise_fanfare_cap` riders: register lint `R7` retired with them, and LAW now
describes `Fanfare Cap +X` as an available explicit verb rather than a rider
every Power carries.

## Mod card coverage (generated)

Codegen: `tools/gen_roster_cards.py` (`tools/gen_klee_cards.py` per-character).
The manifests are the live coverage ledgers, and these figures are read from
them rather than from prose.

- **Klee** — the compatibility baseline profile; fully generated.
- **Furina** — **83 of 84** generated, 1 blocked
  (`let_the_people_rejoice`, intentionally hand-written kit machinery)
  (`klee-mod/KleeCode/Cards/Furina/Generated/manifest.json`). `blocked` HELD AT
  1 across `W3`, which is the number to read there: that window introduced the
  first sheet use of BOTH Salon verbs and the generator emitted them with no
  new blocker.
- **Every generated card on every profile ships its upgrade.** All three
  manifests' `upgrades.no_upgrade_path` lists are **empty**, and the two
  curated codegen-debt registers
  (`tools/lint_upgrade_coverage.CODEGEN_DEBT`,
  `tier0/tests/test_roster_codegen.FURINA_UPGRADE_GAP_PENDING_FB1`) are both
  empty sets. `gen_klee_cards.EXPRESSIBLE_DELTAS` covers `conditional_block`
  and `conditional_damage` as well: the top-level half of such a delta moves
  through the op's own var and each branch half swaps on an `IsUpgraded` read
  with `{IfUpgraded:show:up|base}` rendered beside it.
- **Kokomi** — **75 of 76** generated, **1 blocked**
  (`klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json`, whose `coverage`
  block reads `total 76 / generated 75 / blocked 1`). The one block is
  `ceremonial_garment`, hand-written kit machinery, and it is the only entry in
  the manifest's `blocked` map. The manifest's `upgrades.no_upgrade_path` list
  is **empty**, so every generated Kokomi card ships with its upgrade. The
  `EB-69` sim/mod asymmetry is **closed** — both engines hold all fourteen fill
  cards and all fourteen upgrade deltas. The two new selection screens read
  RULED prompt copy (2026-08-25), carried as `cards` loc rows keyed on the VERB
  rather than on a card id — `KLEEMOD-SLY_GRANT` and
  `KLEEMOD-RECALL_FROM_DISCARD`, beside the carrier-less
  `KLEEMOD-RECALL_FROM_EXHAUST` — and merged by `KleeMod.InjectLocStrings`.
  They reach the live mod at the next deploy; the rendered look is an eyes-on
  item.

## Mod build environment (pinned)

Slay the Spire 2 **v0.107.1**, commit `59260271` (2026-06-18), Steam buildid
`23811903`, appid `2868840`, branch `public`. MegaDot v4.5.1, BaseLib 3.3.7.0,
.NET SDK 9.0.316, ilspycmd 8.2.0.7535. The PCK contract version is
`roster-pck-v3`; the shipped mod package is `klee` **v0.2**
(`klee-mod/Klee/manifest.json`, `min_game_version` 0.107.1). Pins frozen at tag
`pre-simplification-2026-08-06`.

## Systems

- **tier0 combat kernel** — op interpreter, powers, statuses, reactions,
  resources; comparability-first and emit-only toward the run layer. 7-axis
  scorecard, anchor `(ref_ironclad, starter) = 3.0`, frozen battery.
  **NO axis value gates anything (R204):** the live per-axis deck-band system is
  retired as acceptance law roster-wide — all three characters' `deck_bands` /
  `stale_bands` data, both loader accessors, the `BAND EXCEEDED` emission, and
  the hard deck-band and median-identity tests — with **no replacement bands
  ratified**. Seven-axis values and declared identity comparisons are
  **reportable diagnostics only**: they may identify something to investigate,
  and may not gate a merge, require re-banding, or justify moving a value. The
  per-character identity comparison was demoted, not deleted — it reports
  through `axes.identity_flags` on every deck of every run. Klee's
  frontload-over-scaling identity remains **binding design intent** (LAW).
  **Ratified 1,000-fight `winrate_bands` are UNAFFECTED.** Kokomi's rotation law
  lives at three seams off one predicate (`Card.is_junk`): a Status or a Curse
  is never one of her cards — never conscripted, dropped from the unfiltered
  chosen-Exhaust pool, and paying no Charge and no Burst particle on exhaust by
  any route. Artifact itself is C#-only and unmodelled in sim: `AuraPower` and
  `BombPower` are `Buff`-typed and coexist with Artifact, while `FrozenPower`
  and reaction-applied Vulnerable / Weak / Poison stay real Debuffs.
  (`docs/current/atlas/tier0-engine.md`, `tier0-harness-tests.md`)
- **tier0.5 run sim + drafter** — run-level model, acts, runner, draft, and the
  real StS2 16-floor map/route policy. (`docs/current/atlas/tier05-sim-core.md`,
  `tier05-economy.md`, `tier05-metrics.md`)
- **understudy** — the bot playtest bridge driving the real game (Guardrail-7,
  no-fun rule). (`docs/current/atlas/understudy.md`)
- **klee-mod** — the C# character mod (`KleeCode/`), the PCK build/deploy
  pipeline, and a headless C# test project (`KleeTests/`, `EB-105`). Co-op has a
  **partial** automated backstop: per-seat ownership and attribution are
  testable; multiplayer transport and anything needing a live `CombatState` is
  play-only (`klee-mod/KleeTests/README.md`).
  (`docs/current/atlas/klee-mod-cards.md`, `klee-mod-runtime.md`,
  `klee-mod-build-pck.md`)
- **vendor STS2_MCP bridge** — the vendored wire contract the understudy speaks.
  (`docs/current/atlas/vendor-sts2-mcp.md`)
- **art pipeline** — `ImageGen/` card/UI/model art staged into the roster mod
  and packed by `tools/build_pck.ps1`. (`docs/current/atlas/tools.md`)

## Active workstreams

Status only. Open decisions are in [`QUEUE.md`](QUEUE.md); engineering tasks in
[`BACKLOG.md`](BACKLOG.md).

- **Richness-pass deferred families — TWO NAMED WINDOWS, NEITHER OPEN.** The
  three-character richness pass ran to completion: Phase 2's three windows, then
  Phase-3 Windows 1, 2 and 2b at `C15`/`C16`/`C17`, then Window 3 as ONE public
  window at `C19`/`D17`/`P10` with `PILOT_WEIGHTS_VERSION` 5 beside it, and
  `W3`'s single DIAGNOSTIC-SCOPED standing read is published — it is the
  standing baseline named above. **What outlived the pass is two content
  families ruled OUT of `W3` with named destinations (R211), and the body-sheet
  gate (R202 call (5)) travels with each of them: no implementation in either
  window until [USER] rules it an exact sheet.** **(i) the Klee BOMB-BOARD
  READERS → `W10`**, a post-`W3` Klee window. **(ii) `F3` / the Furina
  ENCORE-SPENDER family → `W11`**, which opens only AFTER the pilot's Encore
  opportunity-cost repair — spenders cannot be priced against a resource the
  pilot values wrongly, and that repair is a second `POLICY_VERSION` change
  carrying its own re-baseline (R191, one variable per window). `W10` and `W11`
  are WINDOW names, not register ids: `W1`–`W9` are the watch register below,
  and `W4` is SEPARATELY the pilot-policy weight sweep (`OPERATIONS.md`) — a
  pre-existing collision that is deliberately not extended. **Nothing is
  scheduled on either window**, and the Phase-4 milestone read is not owed until
  the standing baseline's three diagnostic caveats clear.
- **Register diet** — this file's half is DONE; the `BACKLOG.md` half is
  UNBLOCKED by W2's landing, still not done, and SCHEDULED next after the W2b
  merge (BACKLOG `EB-131`).
- **Payoff-reach re-registration — RUN AND GRADED 2026-08-24.** R121's
  countersigned six-step order has run end to end. The grade, the controls, the
  tripwires and the two defects the run found (`EB-123`, `EB-124`, both since
  fixed) are in `EXPERIMENTS.md`; the design call it raised (`M37`) is ruled
  (R199), which is also the Phase-3 authorization and its four guardrails.
- **Kokomi playtest** — unrun
  (`docs/current/playtest/kokomi-playtest-protocol.md`).
- **Enemy remapping** — planned. **Art passes** — Furina and Kokomi surfaces
  (Kokomi's are newest). **Animation sprint 2.** **Axis-validity tracks** —
  Track A / Track E logs.

## Open [USER] pile (pointers)

Every row below is OPEN in [`QUEUE.md`](QUEUE.md) and owned by [USER]: Kokomi's
stability-band declaration (`S4-G6`), the staged lever-2 pull-or-not
(`S4-G13`) and her protocol playtest (`S4-G14`); the shop-rerun slate entry and
countersign (`M14`); the regret-margin prediction slots (`M13`); the `M17` sweep
countersign and its post-sweep `C2` landing; the name/lore and art eyes-on pile
(`S4-G11`, `S4-G12`/`CC-G1`/`CC-G2`, `S4-G17`, `M16`, `M26`, `M19`, `S8`+`S10`,
Art debt); and the Fontaine Rares close-out (`M10`).

## Watch register (dormant)

Blessed mechanisms with a named quantity and a named trigger — monitored, not
open decisions, and nothing is tuned on the strength of being watched. Each
returns to [USER] only when its trigger fires.

- `W1` X4 (block-side Guest Cast), `W2` X6 (salon power level), `W3` X12 (co-op
  reaction potency — instrument unblocked since `O-1` closed; a new reading
  runs under EXPERIMENTS law), `W4` X5 (fanfare floor).
- **`W5` `lynette_box_trick`** (X7, R161) — deliberately left at its current
  rarity; as a companion card it is close to "what if I high-roll a colorless
  option". **Trigger:** playtest shows it overperforming.
- **`W6` `gyorin_formation` — pre-emptive Block RATE.** Explicitly not a
  single-turn spike: the card is 6 Block now (+1 per 2 Charge) and 6 more at the
  start of the next turn — 12 across two turns, not 12 on one. The worry is 6
  pre-emptive Block *every turn* for as long as it keeps coming around, on a
  character whose Charge bank fills on every rotation and is never spent (R80).
  **Trigger:** her stability number moves materially in the post-fill baseline.
- **`W7` `what_the_tokoyo_took` — upper-tail discard count and realized
  damage.** The reprice (cost 2 → 1, 3-per → 4-per) was ruled as a real power
  increase. A chained turn reaching 6+ discards is 30 damage for 1 energy (33
  upgraded). **The obligation is on the INSTRUMENT:** the post-fill baseline
  must report **p90/p99 per-turn discard count and this card's realized damage
  distribution**, never a worked example. The tail is the whole question.
- **`W8` `send_the_runner` — burst-particle cadence.** Charge is a wash
  (`CHARGE_PER_EXHAUST = 1` replaces the dropped grant exactly), but the card
  now also pays `KOKOMI_BURST_PER_EXHAUST = 2` particles it never paid before —
  at Common, at cost 0, repeatable. **Trigger:** Burst frequency across a run
  reads above the ratified meter-20 cadence (R139) in the post-fill baseline.
- **`W9` `X9` — Kokomi's Charge bank, uncapped and never spent.** R188 ruled
  workshop axis **G**, the null option: **no Charge read budget** — a deferral
  of a nerf, not an endorsement, with the §3.3 double read ruled intended
  deckbuilder stacking. Reads per turn are instrumented and the instrument is
  deliberately inert: `resources.note_charge_read` tallies every resolved read
  onto `CombatState.charge_reads_this_turn` tagged by source and `combat` emits
  one `charge_reads_turn` sample per completed player turn; nothing in engine,
  pilot or drafter reads the tally back, so it is not a budget and cannot become
  one by accident. Declared blind spot: the sample rides `turn_close`, which a
  turn ending in the last kill or the player's death never reaches, so the
  truncation is toward the BUSY end. **Trigger:** a reads-per-turn reading or a
  live playtest shows repeatable reads dominant — "dominant" is not a number
  yet, and §5.1 of
  `review/active/charge-reads-per-turn-registration-2026-08-13.md` is the slot
  that makes it one, and that slot is [USER]'s (BACKLOG `EB-78`).

(Migrated from the retired watch-items docket, frozen at tag
`pre-simplification-2026-08-06`; `W5` added 2026-08-10, `W6`–`W8` at `EB-69`
2026-08-23, `W9` 2026-08-24.)
