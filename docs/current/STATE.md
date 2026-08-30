# STATE

> **What currently ships** — roster, systems, versions, and active workstreams.
> Snapshot only: how a stamp reached its current value lives in
> [`docs/current/STAMPS.md`](STAMPS.md) and in the commit that bumped it, not
> here. Open decisions live in
> [`docs/current/QUEUE.md`](QUEUE.md); engineering tasks in
> [`docs/current/BACKLOG.md`](BACKLOG.md); normative rules in
> [`docs/current/LAW.md`](LAW.md); measurement law and active registrations in
> [`docs/current/EXPERIMENTS.md`](EXPERIMENTS.md); how-to commands in
> [`docs/current/OPERATIONS.md`](OPERATIONS.md).

## Live cell

**`RT12 / D18 / P11 / C20`**, read live via `tier05/cells.py`, with
`PILOT_WEIGHTS_VERSION` **6**. Numbers are never comparable across a stamp
boundary unless labeled, and a report without a stamp is not citable
(`EXPERIMENTS.md`). What each level below the live value covered, and what it
archived, is in [`STAMPS.md`](STAMPS.md) — not here.

| stamp | value | source | what this value covers |
|---|---|---|---|
| `RT` `RUNTEMPLATE_VERSION` | **12** | `tier0/constants.py` | The run-layer half of the window-2 correctness batch (`EB-104`): banner-aware shop, relic-derived potion capacity, floored rest heal, one-door Book of Five Rings counting, and event card rewards rolling `RARITY_ODDS`. History → [`STAMPS.md`](STAMPS.md). |
| `D` `DRAFTER_VERSION` | **18** | `tier0/constants.py` | `EB-28`: the drafter prices Furina's Salon deploy through ONE new [USER]-overridable dial, `STATIC_SALON_MEMBER_VALUE = 1.5` — nine salon rows re-price on both faces, nothing else moves. History → [`STAMPS.md`](STAMPS.md). |
| `P` `POLICY_VERSION` | **11** | `tier05/draft.py` | The scorer-literacy window (R207): the pilot gains a Spark hold-versus-spend term, five state predicates and payout-aware selection scoring, repairing the standing read's three diagnostic caveats in code — they clear at the re-baseline, not here. History → [`STAMPS.md`](STAMPS.md). |
| `C` `CONSTANTS_VERSION` | **20** | `tier0/constants.py` | `EB-139`'s Swirl aura-aware bind (R211) — an aimed Swirl binds whole to the lowest-HP aura-bearer; one companion's damage moves, the anchor does not — plus the ruled Sweet Dreams body (R189/R205, joined 2026-08-26): new any-aura predicate `target_has_aura`, Block 8 → 5. History → [`STAMPS.md`](STAMPS.md). |

**Standing baseline:** `review/active/sitting-reads-2026-08-26-c20-d18-p11.md`
— twelve arms at `RT12/D18/P11/C20` (`main` = `190e598`), all twelve in ONE
pass with `game_ref/` present, so both floors sit in the main tables
(`real_ironclad` **5.2%** win / **65.5%** act-1, `real_silent` **1.1%** /
**54.0%**). **There is NO interval separation on any arm** — zero, on either
rate column — and it **has NO control set and says so**: all twelve arms moved,
anchors included. Its §0 checks the predecessor's three scorer caveats against
code and grades all three **CLEARED**, so under R211 item 7 it publishes **BOTH
as the standing re-baseline AND as the Phase-4 milestone table — the milestone
read is TAKEN** (label Claude's under R212, reasoning in §0.4). It supersedes
`review/active/sitting-reads-2026-08-25-c19-d17-p10.md`, which stands as
published with its DIAGNOSTIC-SCOPED header intact (R101b).

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

| id | display | HP | nation | element / cadence | default plan | archetypes |
|---|---|---|---|---|---|---|
| `klee` | Klee | 62 | Mondstadt | Pyro, catalyst-grade (all attacks apply) | demolition | demolition, spark, reaction |
| `furina` | Furina | 78 | Fontaine | Hydro, Skill-grade | salon | salon, spotlight, fanfare |
| `kokomi` | Sangonomiya Kokomi | 80 | Inazuma | Hydro, catalyst cadence | priest | priest, commander, assist |

Klee is the compatibility baseline character. Companion pools ship per nation:
`docs/mondstadt-companions.yaml`, `docs/fontaine-companions.yaml`,
`docs/inazuma-companions.yaml`.

Starting HP sits against the base cast — Ironclad 80, Defect 75, Regent 75,
Silent 70, Necrobinder 66 (`game_ref/*_char_facts.yaml`). Furina 60 → **78**
and Kokomi 70 → **80** by **R219 F** (2026-08-29): both are canonically
HP-scalers, so pools under the cast's average read wrong; Klee stays low by
design. Every measured table that quotes a Furina or Kokomi row predates the
change and is stale under R68 until a re-baseline —
`review/active/roster-hp-scalers-2026-08-29.md` lists which.

**Reference anchors** (measurement anchors, NOT roster members — no art, no
pool, no C# class): `ref_ironclad`, `real_ironclad`, `ref_silent`, `real_silent`
(`tier0/roster.py:165-171`). The scoring anchor is `("ref_ironclad", "starter")`
under the `generic` pilot, normalized so every axis reads exactly `3.0`. The
`real_*` variants depend on a local `game_ref/` tree that is gitignored and
absent on a fresh clone; both pools verify (ironclad 76, silent 87) and both
anchors load. Still owed there: three `*_char_facts.yaml` that no roster arm
reads — hand-authored, not tool-regenerable, and [USER]'s to supply (BACKLOG
`EB-128`). The other three legs of that row are done: the durable-backup
location is RULED (OneDrive, 2026-08-24) and its mirror is built
(`tools/backup_game_ref.py`), `tools/purge_worktree.py` refuses a worktree
purge that would take gitignored data with it, and a missing reference layer
now fails loudly at load (`loader.require_reference_layer`) instead of by
traceback mid-cell.

## Content inventory

Live sim inventory (`docs/current/atlas/tier0-pilot-roster.md` §2): **322 cards
in the loader index** (3 are acquisition-only Ancient side-sheet rows, leaving
the 319 the atlas quotes; 317 → 322 at `Win3`, which added five personal rows and
rewrote three in place), **5 character sheets** (3 roster + 2 reference),
**6 encounters, 15 pilot weight sets**. The battery encounters are frozen
(`content/encounters/battery.yaml`, FROZEN 2026-07-19). Card sheets
`docs/klee-cards.yaml`, `docs/furina-cards.yaml` and `docs/kokomi-cards.yaml`
all carry the `tempo_band:` field and hold **239 personal rows** (79 / 84 / 76);
Kokomi's 76 are **5 basic / 31 common / 26 uncommon / 14 rare, 70 draftable**,
and `Win3` held both her count and her id list there — all three of her `Win3`
items are rewrites under existing ids. Klee's 79 are 76 + the three `Win3` Spark
sinks; Furina's 84 are 82 + the two `Win3` Salon/Spotlight rows.
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
  1 across `Win3`, which introduced the first sheet use of BOTH Salon verbs and
  emitted them with no new blocker.
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
  (`klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json`, `coverage` reads
  `total 76 / generated 75 / blocked 1`). The one block is `ceremonial_garment`,
  hand-written kit machinery, and the only entry in the manifest's `blocked`
  map. `upgrades.no_upgrade_path` is **empty**. The `EB-69` sim/mod asymmetry is
  **closed** — both engines hold all fourteen fill cards and all fourteen
  upgrade deltas. The two new selection screens read RULED prompt copy
  (2026-08-25), carried as `cards` loc rows keyed on the VERB rather than a card
  id — `KLEEMOD-SLY_GRANT` and `KLEEMOD-RECALL_FROM_DISCARD`, beside the
  carrier-less `KLEEMOD-RECALL_FROM_EXHAUST` — merged by
  `KleeMod.InjectLocStrings`. They reach the live mod at the next deploy; the
  rendered look is an eyes-on item.

## Mod build environment (pinned)

Slay the Spire 2 **v0.111.0**, commit `41cef1ea` (2026-08-13), Steam buildid
`24724944`, appid `2868840`, branch **`public-beta`**, `main_assembly_hash`
`222455745`. MegaDot v4.5.1 (`v4.5.1.m.14.mono.custom_build`, the editor
`tools/build_pck.ps1` drives — a local download, not a Steam artifact, so the
game update did not move it), BaseLib **3.4.5.0** (Workshop item
`3737335127`), .NET SDK 9.0.316, ilspycmd 8.2.0.7535. The PCK contract version
is `roster-pck-v3`; the shipped mod package is `klee` **v0.2**
(`klee-mod/Klee/manifest.json`, `min_game_version` **0.111.0** — the hooks the
port binds do not exist on 0.107.1, so the old floor was a claim the game's own
gate would have acted on). The version string deploy stamps is **`MAJOR.AUTO`**
(R214), with the `+proto` dev mark beside it (R217 D).

**Pin history.** The previous pin was v0.107.1, commit `59260271`
(2026-06-18), buildid `23811903`, branch `public`, BaseLib 3.3.7.0, frozen at
tag `pre-simplification-2026-08-06`; it moved here under **R218**
(2026-08-28), which took `M46` option (2) — port and re-pin — after Steam
switched this install to `public-beta` mid-sitting. Every measurement and
deploy label from R218 on rides the pin above; live numbers were never
comparable across a game build anyway (R95), and the sim references no game
assembly and is unaffected.

The installed build is **`0.2.1416+proto`** (2026-08-29), a dev package
carrying BOTH prototype arms — Kokomi's Kurage-memory base kit and Klee's
Spark alternative-cost rows — behind the `-p:PrototypeCards=true` compile
switch. **It does not boot:** a regression in that package stops the mod
loading, so the sealed Kokomi blind run it was built for HAS NOT STARTED. The
fix is in flight on branch `kokomi-blind-run`, which mints the defect row; that
row is not carried here because it does not exist on this branch yet. **The
last runnable install is the release package `0.2.1357`** (2026-08-29, from
`klee-slice-1-round-3` `605b76f`) — no `+proto`, no `+dirty`, deployed as the
teardown of the Klee slice 1 ROUND 3 funnel run and of `EB-188`'s live
acceptance, both of which ran on `0.2.1353+proto`. It carries the same C# as
`0.2.1269`; nothing on a shipped sheet moved between them, and the only C# those
rounds added is compiled out of a release build by construction (the quarantined
prototype rows). `validate.ps1` OK; pack 9,586,076 bytes.
It carries `EB-171`'s port and the two face fixes `0.2.1209` was missing: the
exhaust-selection rate (R215 C) and `EB-164`'s eighteen re-worded scaling
faces. **Re-verified live on 0.111.0** (`EB-171`): the mod loads, all nine
`understudy/scenarios/` scenarios PASS, `embark` reaches a live Kokomi run,
and the prototype quarantine still refuses a `KLEEMOD-PROTO_…` grant from
outside. The `klee` mod is ENABLED in the game's own mod settings.

## Systems

- **tier0 combat kernel** — op interpreter, powers, statuses, reactions,
  resources; comparability-first and emit-only toward the run layer. 7-axis
  scorecard, anchor `(ref_ironclad, starter) = 3.0`, frozen battery.
  **NO axis value gates anything (R204):** the live per-axis deck-band system is
  retired as acceptance law roster-wide, with **no replacement bands ratified**.
  Seven-axis values and declared identity comparisons are **reportable
  diagnostics only** — they may not gate a merge, require re-banding, or justify
  moving a value. The identity comparison was demoted, not deleted; it reports
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
  no-fun rule). A targeted-scenario harness (`understudy/scenario.py` + the
  `GitsDebugState` board-setup door with five `set_*` verbs plus
  `clear_hand` (`EB-165`), attended only)
  is built and proven live: all five scenarios green on 2026-08-26.
  (`docs/current/atlas/understudy.md`)
- **klee-mod** — the C# character mod (`KleeCode/`), the PCK build/deploy
  pipeline, and a headless C# test project (`KleeTests/`). Co-op has a
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
  three-character richness pass ran to completion (Phase 2's three windows, then
  Phase-3 `Win1`/`Win2`/`Win2b` at `C15`/`C16`/`C17`, then `Win3` as ONE public
  window at `C19`/`D17`/`P10`), and `Win3`'s single DIAGNOSTIC-SCOPED standing
  read is superseded by the baseline named above. **What outlived the pass is
  two content families ruled OUT of `Win3` with named destinations (R211), and
  the body-sheet gate (R202 call (5)) travels with each: no implementation in
  either window until [USER] rules it an exact sheet.** **(i) the Klee
  BOMB-BOARD READERS → `Win10`**, a post-`Win3` Klee window. **(ii) `F3` / the
  Furina ENCORE-SPENDER family → `Win11`**, which opens only AFTER the pilot's
  Encore opportunity-cost repair — spenders cannot be priced against a resource
  the pilot values wrongly — and that repair is a second `POLICY_VERSION` change
  carrying its own re-baseline, because attribution is exactly what it buys
  (R207: one variable per window where attribution matters; several may share a
  window otherwise). **NAMING, as of 2026-08-26: the CONTENT windows are
  `Win1`/`Win2`/`Win2b`/`Win3`/`Win10`/`Win11`**, spelled `W1`–`W3`/`W10`/`W11`
  in older packets — `W1`–`W9` are the watch register below, and `W4` is
  separately the pilot-weight sweep (EXPERIMENTS `W4`, run per `OPERATIONS.md`).
  **Both windows are FROZEN by R213 (2026-08-26) until the design
  course-correction below reports.** The **Phase-4 milestone read is
  TAKEN**: the three diagnostic caveats' repairs landed as the one `P11` window
  (`EB-143`/`EB-144`/`EB-145`, `EB-129` riding), all three graded CLEARED
  against code, and the `RT12/D18/P11/C20` re-baseline above carries both labels.
- **Payoff-reach re-registration — RUN AND GRADED 2026-08-24.** R121's
  countersigned six-step order has run end to end. The grade, the controls, the
  tripwires and the two defects the run found (`EB-123`, `EB-124`, both since
  fixed) are in `EXPERIMENTS.md`; the design call it raised (`M37`) is ruled
  (R199), which is also the Phase-3 authorization and its four guardrails.
- **Kokomi playtest** — EXPLORATORY run played 2026-08-26 on `0.2-1159`
  (raw notes `review/active/kokomi-playtest-notes-2026-08-26.md`);
  the confirmatory protocol run is unrun
  (`docs/current/playtest/kokomi-playtest-protocol.md`).
- **Design course-correction — R213 (2026-08-26), authority amended R217
  (2026-08-28), pin moved R218 (2026-08-28).** Status only: the words are
  the three commits; the running narrative is the slice packet.
  - **Standing law.** Freeze on W10/W11, staged levers, tuning and new
    windows. Quarantined prototype surface (`EB-147`), proven from OUTSIDE
    on every release build since `0.2.1209`. GPT's **D1–D9 are LAW** as the
    design charter, provisional through the Klee slice, **no numeric design
    bands**, decision closeness (R213 F) the only numeric falsifier. Kokomi →
    Klee → Furina, sequentially; E1–E4 reopened. **R220 B gives that sequence
    a tail:** the shared Burst meter is retired roster-wide, and the order is
    **Kokomi → Klee → Furina for the three folds, the shared retirement
    LAST** — each fold lands behind its own flag and its own slice's grading,
    and the one branch that touches the engine, the three sheets, the pilot,
    the C# and LAW at once lands after all three so no character is ever left
    holding a dead gauge (`EB-199`/`EB-200`). Furina's reframe carries her
    fold, so it is one of R220's three and it is the last of them.
    **The independent seat**
    ([USER]'s ChatGPT/Codex subscription through `understudy/seat.py`;
    independence by model FAMILY) RETURNS a prototype or ADVANCES it with
    no [USER] form; two seats disagreeing ESCALATES; SURVIVES is never ship
    approval. [USER] owns briefs, direction picks, money, final signoff.
  - **Instruments live.** Staged turns, blind packets, the four-question
    form and closeness (`EB-149`); exact hand (`EB-165`); replay of every
    graded line, modals answered from the form or refused (`EB-170`);
    open-face-defect preflight (`EB-169`, register empty); a face states
    its scaling once (`EB-164`, `tools/lint_face_scaling.py`); blind play of
    any screen with a one-thread seat driver (`EB-167`/`EB-168`, six sealed
    sessions under `review/qa/blindplay/`, records name both builds,
    repeated printed names numbered `(1)`/`(2)` — `EB-177`; the frame
    after a kill ridden out — `EB-178`; powers, meters and a repeated
    card name say what the feed does not carry — `EB-179`);
    pinned managed assemblies in the vault (`EB-172`).
  - **Kokomi slice 1** (`review/active/kokomi-slice-1-2026-08-27.md`,
    §§Round 1–4): four rounds on the quarantined surface, **no shipped
    number moved**. Round 4 (`0.2.1293+proto`) re-boarded the two arms
    round 3 returned and ran them on TWO graders: 8 forms, 8 SURVIVES,
    7 of 8 replays clean. The reviewer reports **both board repairs
    worked**; Sanctifying Circle **ADVANCES**, Blazing Ooyoroi RETURNS on
    an implementation defect rather than its board (`EB-184`: a modal
    typed Attack demands a target on its targetless Block mode, so that
    line cannot replay). Slice tally: six ADVANCE, one open RETURN.
    Advance means whole-fight play next, not ship.
  - **Blind-play testimony** (R217 G — iteration feedback, never
    validation): the FIRST run carrying a prototype arm is session
    `20260829-181718` (Klee, `0.2.1353+proto`, Second Helping granted);
    its run-end record names the tension as detonate-now versus leave the
    Bomb attached, and calls play repetitive once "free Bomb, attack to
    detonate, then block with leftover energy" settles in. Earlier,
    runs B5 and B6 name, unprompted, the tension as immediate
    Block versus Charge investment, Bake-Kurage as the win condition, and
    the repetitive state as "Water's Edge versus Coral Guard"; B6 reports
    Burst accumulating with no visible spend and Gorou's Charge/Burst grant
    unprinted — the Charge-keyword gap R215 D deferred into E1, now with a
    blind witness. The bridge gap the runs uncovered: `EB-181`.
  - **Kokomi slice 2** (`review/active/kokomi-slice-2-2026-08-29.md`, §8):
    R213 E1's four Charge arms, RUN 2026-08-29 on `0.2.1293+proto`. Eight
    turns in four matched pairs, seeds pinned after 29 rolls; closeness
    SURVIVES on all eight, declared and observed. Sixteen forms on two
    graders (15 SURVIVES / 1 REFUSED), sixteen replays, one flagged
    `misread`. Pair read: **two ADVANCE** (Fathom the Tide, Twin Tides)
    and **two RETURN** (Sounding Line, Watatsumi Levy — their boards, per
    the review). Four numbered picks wait in §9. Defects minted:
    `EB-182` (no per-option playability on the choose-a-card screen,
    proven off the decompile), `EB-183` (R216 D's per-companion half,
    owed and unbuilt).
  - **Klee slice 1** (`review/active/klee-slice-1-2026-08-29.md`, §11–§13):
    R213 E2's three Spark-spending arms. **Round 1** RUN 2026-08-29 on
    `0.2.1314+proto`: six turns in three matched pairs, seeds pinned
    after 11 rolls; closeness SURVIVES on all six both ways, though the
    OBSERVED reading was blind to the Spark bank (`EB-185`), so the
    DECLARED reading is the one committed. Twelve forms on two graders
    (7 SURVIVES / 5 REFUSED). **Ten of twelve replays were refused live**
    with `EnergyCostTooHigh` — filed then as a shipped display defect and
    **ruled NOT A DEFECT by [USER] 2026-08-29**: every Attack showing
    cost 0 at a bank of 3 is the intended mechanic (whichever is played
    first takes the discount; the rest snap back), so those ten lines
    were readers failing to chain the keyword's second sentence. The row
    is gone as a false positive, and `M48` is ANSWERED with it (R219 A/B):
    the rule is retired by the Sparks re-author rather than amended.
    Pair read: two ADVANCE (Second Helping, Rummage), one RETURN (Slow
    Burn — its board and presentation). Minted there: `EB-187` (a staged
    board's Burst assumption double-counted the Skill tag and corrupted a
    grade). **Round 2** RUN 2026-08-29 on `0.2.1323+proto`, same seeds,
    same boards, same cards, new turn ids: `EB-185` and `EB-187` CLOSED
    and the PACKET taught to print Spark's rule and each card's printed
    cost. Twelve fresh forms (7 SURVIVES / 5 REFUSED) and **all twelve
    replays played to completion**. Pair read: **two ADVANCE** (Second
    Helping, Slow Burn) and **one RETURN** (Rummage — priced honestly,
    the draw destination costs 16 damage and 5 Block and no grader took
    it). A fourth arm, Bag of Tricks, stays held for
    [USER] at §6.1, and §6.2's question about the automatic rule now has
    two rounds of live witness. Also minted: `EB-191` (a replay's run
    seed reads back `None` on 7 of 12 launches; a retry always works).
    **Round 3** RUN 2026-08-29 on `0.2.1353+proto` (§13), the
    independence repair: Rummage's text and Slow Burn's printed Burst
    figure RE-DERIVED Claude-side from the seat's own clause, both rows
    back to `authored_by: [claude]`, and the lint's four-entry debt list
    emptied by its own staleness rule. Pair 3's board unchanged on its
    seed; pair 2 RE-SET to the reviewer's specification (energy 4, a hand
    of three, a declared draw pile) on a fresh seed after nine rolls.
    Eight forms (7 SURVIVES / 1 REFUSED), **eight clean replays**, and
    the replay witnesses the draws: Rummage reached Kaboom!, Pop! and
    Jumpy Dumpty, all playable, and no grader spent energy on one. Pair
    read: **both arms ADVANCE**, so the PROVISIONAL flag is lifted on
    both. Found and fixed there: `seat review` prepended the doctrine
    gate's protocol to the pair read as well, which silenced it —
    `--role {doctrine,pair}` now splits the output shape.
  - **Process status (2026-08-29 review pass).** The independence breach
    is **REPAIRED and the two Klee arms are no longer provisional.** The
    doctrine seat had authored Rummage's text and chosen Slow Burn's
    number and the same family then graded them; **no third family**
    (`[USER]`, 2026-08-29), so role separation is enforced by recorded
    authorship (`EB-190`) and both rows were re-derived Claude-side from
    the seat's clause in Klee round 3, `authored_by: [claude]`, with the
    clean outcomes replacing the provisional ones. Whole-fight blind play
    is the **automatic** gate after ADVANCE; the door is BUILT and now
    ACCEPTED LIVE — `EB-188` **CLOSED** on sealed session
    `20260829-181718` (`0.2.1353+proto`, seed `71D8JS1VSKRN`, 120
    actions, six fights, the record naming `arms_granted`), where Second
    Helping was granted, drawn and played. `M48` is ANSWERED (R219 A/B); `M51` and
    `M53` are ANSWERED by R220 (F and E). **`M47`, `M49`, `M50`, `M52`,
    `M54`, `M55`, `M56`, `M57`, `M59`, `M60` and `M64` are CLOSED by R224
    (2026-08-30)** —
    the sitting slate landed WHOLE, `M47`, `M55` and `M64` with them, so
    **no prototype-slice row is open for [USER]**. The slate's own
    engineering is `EB-213`–`EB-219`, and the packet stays in
    `review/active/` as the record, every item carrying its RULED marker. Slice 2's round-2 boards
    (branch `kokomi-slice-2-round-2`, unstaged) no longer wait on `M50`:
    its four rows are ruled, so they re-board against the ruled kit.
  - **Klee Sparks — RE-AUTHORED, both engines, behind a flag**
    (`review/active/klee-sparks-2026-08-29.md`; evidence
    `docs/current/research/regent-stars-economy.md`). R219 B/C: the
    threshold rule retires and Sparks become an ALTERNATIVE CARD COST,
    with **no cap** — the governor is generator scarcity, matched to
    Regent's pattern, not a ceiling. Built: seven prototype rows plus an
    eighth, `proto_true_spark_knight`, the strict Rare Power that prices
    every Attack at 3 Sparks; sim behind `SPARK_ALT_COST_ENABLED`, C#
    behind `-p:PrototypeCards=true` (so a release build contains no type
    from the arm), and the price moved out of the rules box onto a **cost
    badge** that reads the same number the gate charges. The packet's §9
    doctrine-seat read is CLEAN. Nothing shipped moved. **`M51` is
    COUNTERSIGNED (R220 F):** the DRAFT prediction slate P1–P6 is signed
    under R212(2) and the eleven as-built calls at §10.11 stand as built,
    none vetoed. `LAW.md:481` moved `spark` from the bounded meters to the
    unbounded with it — the re-author has no cap, so the bounded-at-3 entry
    was a dead reference. Klee's Burst fold rides this arm (R220 B), and
    `M60`'s `K1` set its rarity: **R224 D rules it Rare, once per combat,
    gated by Exhaust on the body**, with the feed table taken as written
    (`K2`). **The §14 direction is option (5), migrate before you
    duplicate, and its BRANCH is Spark-only, FLAG-GATED** (R224 B): the
    three hybrids go to 0 Energy with the price paid wholly in Sparks as a
    dev-only substitution under `SPARK_ALT_COST_ENABLED` (`EB-218`), the
    shipped pool byte-identical with the flag off. The round-2 picks are
    answered with it: `EB-208`'s fix is
    (a) then (c), `P4` stays UNREACHED as published, and the next gate is
    (e).
  - **Kokomi Kurage memory — BASE KIT** (`review/active/kokomi-kurage-memory-2026-08-29.md`
    §11–§13). R219 D: the Bake-Kurage is **always on**, part of the base
    kit rather than a summoned card, and one Muster card joins the base
    deck to teach the pattern. The memory queue prices each remembered
    card at 3× its cost, fuelled at 1 Charge per Exhaust, blocked when the
    front is unaffordable, uncapped. **Kurage's Oath is RULED and BUILT**
    at *3 Block per memory played, 5 upgraded* — [USER]'s placeholder, no
    measurement attached and none quotable. Sim, C# and the blind-run
    prediction slate are all merged; the run itself waits on the boot
    regression above. **The four rows the redesign left unruled are RULED
    (R224, ex-`M50`):** the *Bake-Kurage* row and its upgrade delta retire
    together under the re-authoring (carried on `EB-199`, not deleted while
    the flag is off), the Tamakushi Casket refresh re-keys to an immediate
    extra pulse under `KO1`(a), and `KURAGE_MEMORY_KEYWORD_NEEDS_SUMMON` is
    deleted with its branch (`EB-217`). Kurage's Oath stays as [USER] ruled
    it — 3 Block per memory played, 5 upgraded, a placeholder with no
    measurement attached — and the surface's missing upgrade channel is now
    `EB-213`. The blind run's own four picks are ruled with them: Rule 1
    prints as the Muster KEYWORD and the gate re-runs on `KURAGEMEM002`
    (`EB-214`), the published grades stand while future records carry a
    per-turn wire snapshot (`EB-216`), and the prototype face takes the
    per-row `description:` channel with the loc merge deleted (`EB-215`).
    Where the Charge-source line goes is still `M55`.
    **The memory's DISPLAY is being rebuilt**: the strip the blind run
    tested was diagnosed true on both misread frames and found
    insufficient rather than defective, so [USER]'s direction turns it
    into one card at the screen's left edge — the next memory, ringed
    blue if the bank pays it and red if not, the Charge count under it,
    and a click opening the whole queue with the same colours running up
    it. No meter bar at all. §14 has the three build options and the
    running-affordability projection the queue view needs. `M61` is
    ANSWERED — option 3, and the element draws for the local seat only —
    and `EB-198` is BUILT on `kurage-memory-card`, awaiting the live check.
  - **Furina REFRAME — PACKET CLOSED, COUNTERSIGN OPEN**
    (`review/active/furina-reframe-2026-08-29.md`). R220 A, from [USER]'s
    brief and his four answers: the Salon is an **orb board** in the Defect
    shape whose members never auto-play, **Fanfare is its Focus and its
    Burst** — a full meter is a maximally scaled Salon and that fill state
    IS the reward — Encore is both her deferred Block and the currency that
    aims the stage, a Companion play triggers one member without evoking it,
    and her own cards Evoke. No Burst card prints at a threshold; "drain it
    all for a giant effect" becomes an optional **Rare payoff card**,
    drafted, not base kit. Spotlight is named as deliberately unresolved.
    The packet **supersedes E4 §3, §4, §7.1 and §12 on paper**
    (`review/active/furina-e4-2026-08-29.md` stays in place as the record).
    No code, no constant, no sheet row and no LAW line has moved.
    **`M52` is re-pointed** onto this packet's §3 ruling text and its §3.1
    prospective LAW text, and the sixteen design picks are **`M59`**.
    **BOTH ARE COUNTERSIGNED BY R224 (2026-08-30) and both rows are
    CLOSED:** §3 signed, §3.1 signed AS PROSPECTIVE (adopting amendments 3
    and 4), LAW:145 taken as the relayed rewrite (b) with the packet's own
    tightening — "directly" defined, "cheaply repeatable" kept — also
    prospective, so **no `LAW.md` line moved**; and `F1`, `F13`, `F14` at
    option (2) with the other thirteen at their defaults, Slot 6 kept.
    **Nothing implements before Klee closes** (R213). Her Burst fold is one of R220 B's
    three, and it is the last of them.
  - **Build and grading rhythm (facts, not rulings).** CI takes a
    **docs-only fast path** (`tools/ci_changed_paths.py`) and runs pytest
    under xdist with a pip cache — the pytest job is ~3.5 min, from ~5.
    The scarce budget is the Codex seat's: GPT-played runs are paced per
    five-hour window, so a sitting plans around them rather than assuming
    them. The **local model** (Qwen 3.8 27B over llama.cpp) now holds a
    **TESTER seat on staged single-turn reads**, handed off by R220 E:
    [USER]'s condition — GPT confirming the playtest findings first — was
    met by the Codex seat's **ADVANCE** at
    `review/qa/local-sanity-2026-08-29-seat-review-codex-gpt-5.6-sol.md`,
    and `M53` is ANSWERED as pick (1) by entailment. The `local` family is
    RECOGNISED and never AUTHORABLE (`understudy/authorship.py`:
    `FAMILIES` yes, `AUTHORABLE_FAMILIES` no), and **no grading chair is
    granted** — grader work, whole-fight blind play and the doctrine gate
    stay with the Codex seat. The seat runs under its own four conditions
    (`answer_truncated` a hard refusal with no partial filing, the family
    non-authorable, periodic seat review, and review of any line that
    spends a resource before a resource-reading play);
    `understudy/local_tester.py` is the mechanism and OPERATIONS' **Local
    tester seat** section is the amended rule. The periodic-review rate is
    settled at N = 4 (`M58`, answered by R220 G).
  - **Funnel throughput — R221 BUILT AND PROVEN LIVE; R222 D and R223 in
    force.** A blind-QA round
    measured ~70 min for 8 turns, with roughly a third of it the game idling
    while models read. `local_tester round` now RUNS a round rather than
    reading it: stage / read / grade / replay pipelined behind one game lock
    with a look-ahead of one board, ONE `soak.Session` for the whole round
    (the process is still restarted between boards — the wire has no in-run
    exit, so `abandon_run` from a fresh launch is the only way back to a
    menu), `--first N` sequential stopping with UNRUN rows carrying pinned
    seeds, and `staged_turn packet-section <slug>` writing the results block
    from the records with the prose read left as a marked empty slot.
    **`KLEESPARK-R2` (2026-08-30) was the first pipelined round: 372 s for
    six boards — stage 89 s, read+grade 295 s, replay 124 s — and it showed
    the round is MODEL-bound (a read is ~3× a stage).** Built since and
    proven on `funnel-bench-1` (2026-08-30, R2's six boards under bench
    ids, shadow chair, no Codex; `review/qa/funnel-bench-1-record.md`):
    `--lanes N` (`EB-206`: two `SlayTheSpire2.exe` from one install, own
    `APPDATA` and bridge port; `EB-210`'s seed crossing fixed, 6 of 6
    seeds honoured) and `--read-workers N` (a semaphore over the read
    phase, refused above the server's slot count; `serve.ps1 -Parallel 2`
    since 2026-08-30) — **six reads in 219 s against 295 s, 1.35×; staging
    a wash on two lanes (93 s against 89 s, the second game competes for
    the same GPU); 251 s launch-to-teardown against ~313 s**. Also live:
    `--seat-mode shadow|deciding`, the `target_missing` falsifier
    (`EB-203`), and `qualify`, the requalification battery, with R223's
    pass mark (targets 6/6, costs ≥ 4/6, intent ≥ 4/6; first run 10/18,
    FAIL). The fresh-Opus control's retirement threshold was `M62`,
    **answered by R222 B**: verdict agreement **4 of 8** on `KLEESPARK-R1`
    and 3 of 6 on `R2`, so the control STANDS — and the seats have swapped
    roles. The fresh-Opus form DECIDES; the local seat reads in SHADOW,
    recorded and never graded, until it clears **≥ 6/8 over one round**
    AND the battery. `M63` is answered by R222 C: the funnel refuses a bad
    form and never repairs one. Open on the instrument: `EB-205`,
    `EB-208` (its (a) live-count preflight is BUILT and merged, #197;
    (c), the character/build/context-keyed seed ledger, remains — R224
    ruled the sequence), `EB-211` (costs passes on silence) and `EB-212`
    (intent self-report). **`M64` is ANSWERED by R224** as a SPLIT: Codex
    decides every board on a round that can ADVANCE an arm; fresh-Opus
    rounds are INSTRUMENT rounds.
  - **Next.** Klee slice 1 has no open engineering: all three arms read
    ADVANCE on clean independent reads and Second Helping has its
    whole-fight run. **Rummage's and Slow Burn's whole fights are RULED
    (R224, item 19)**: Rummage FOLDS into the §14 mixed-pool deck rather
    than being staged as a separate fight for the same hybrid-price
    question, and Slow Burn's fight is HELD until `M60`/`EB-199` settle
    what its Burst rider becomes. What is owed next is the boot fix that
    unblocks the sealed Kokomi
    run, slice 1's `EB-184`, and R224's seven new rows
    `EB-213`–`EB-219` — of which `EB-219` (Prune's re-author) and
    `EB-218` (the Spark-only migration) precede the mixed-pool fight.
    No [USER] row is open on the slice work.
    A4/A6 unminted until their prerequisites are real; A1-extended and A5
    DEFERRED. Slice 1 stays under R213/R216.
- **Enemy remapping** — planned. **Art passes** — Furina and Kokomi surfaces
  (Kokomi's are newest). **Animation sprint 2.** **Axis-validity tracks** —
  Track A / Track E logs.

## Open [USER] pile (pointers)

Every row below is OPEN in [`QUEUE.md`](QUEUE.md) and owned by [USER]: Kokomi's
stability-band declaration (`S4-G6`) and her protocol playtest (`S4-G14`); the shop-rerun slate entry and
countersign (`M14`); the name/lore and art eyes-on pile
(`S4-G11`, `S4-G12`/`CC-G1`/`CC-G2`, `S4-G17`, `M16`, `M26`, `M19`, `S8`+`S10`,
Art debt); the Fontaine Rares close-out (`M10`); and — after **R224
(2026-08-30) closed `M49`, `M50`, `M52`, `M54`, `M56`, `M57`, `M59` and `M60`**
— **`M47`, `M55` and `M64` with them, so NO prototype-slice row is open.**
R224 landed `review/active/sitting-2026-08-30.md` WHOLE: the Klee round-2
picks and the §14 direction with its Spark-only migration branch (`EB-218`);
`M47` at option (3), build per-mode playability (`EB-182`) then re-ask; `M55`
at (5) re-scoped to the pile view, folded into `EB-214`; `M64` at a SPLIT —
Codex decides any round that can ADVANCE an arm, fresh-Opus rounds are
INSTRUMENT rounds, the rule written into OPERATIONS' *Local tester seat*
section; Rummage folded into the §14 mixed-pool deck and Slow Burn's fight
HELD on `EB-199`; the Spark drain sequenced after the mixed-pool read; and the
burst packet's architecture paragraph plus **all eight** §3.2 LAW blocks
countersigned AS PROSPECTIVE — **no `LAW.md` line moved**. **Ceremonial Garment
is LOOT** — draftable Rare, `kit_card` and `requires: burst_energy_full`
dropped, the v1.9 kit-grant machinery deleted outright, prospective and carried
on `EB-199`. LAW:145 as signed opened one new item, ruled the same day:
**Prune** is re-authored, her Spark grant becoming a declared Klee-engine
response (`EB-219`). `M48` was answered by R219; `M58`
by R220 G (N = 4); `M51` was answered by R220 F and `M53` by R220 E; `M62` and
`M63` by R222 B and R222 C.

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
  deliberately inert (`resources.note_charge_read` →
  `CombatState.charge_reads_this_turn`, one `charge_reads_turn` sample per
  completed player turn; nothing reads the tally back, so it is not a budget and
  cannot become one by accident). Declared blind spot: the sample rides
  `turn_close`, which a turn ending in the last kill or the player's death never
  reaches, so the truncation is toward the BUSY end. **Trigger:** a reads-per-turn
  reading or a live playtest shows repeatable reads dominant — "dominant" is not
  a number yet, and §5.1 of
  `review/active/charge-reads-per-turn-registration-2026-08-13.md` is the slot
  that makes it one, and that slot is [USER]'s (BACKLOG `EB-78`).

(Migrated from the retired watch-items docket, frozen at tag
`pre-simplification-2026-08-06`; `W5` added 2026-08-10, `W6`–`W8` at `EB-69`
2026-08-23, `W9` 2026-08-24.)
