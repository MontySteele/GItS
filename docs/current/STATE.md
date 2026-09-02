# STATE

> **What currently ships** — roster, systems, versions — and the pointers into
> everything else. Snapshot only, near 150 lines by rule (`CLAUDE.md` §Norms).
> Where the detail went: [`STAMPS.md`](STAMPS.md) stamp history ·
> [`QUEUE.md`](QUEUE.md) picks · [`BACKLOG.md`](BACKLOG.md) engineering ·
> [`LAW.md`](LAW.md) rules · [`EXPERIMENTS.md`](EXPERIMENTS.md) measurement law
> · [`OPERATIONS.md`](OPERATIONS.md) commands ·
> [`workstreams.md`](workstreams.md) workstream status, build detail and the
> [USER] pile · [`watch-register.md`](watch-register.md) · [`atlas/`](atlas/).

## Live cell

**`RT12 / D18 / P11 / C21`**, read live via `tier05/cells.py`, with
`PILOT_WEIGHTS_VERSION` **6**. A number is not comparable across a stamp
boundary unless labeled, and a report without a stamp is not citable. What each
level covered and archived is in [`STAMPS.md`](STAMPS.md), not here.

| stamp | value | source | what this value covers |
|---|---|---|---|
| `RT` `RUNTEMPLATE_VERSION` | **12** | `tier0/constants.py` | `EB-104`'s run-layer half: banner-aware shop, relic-derived potion capacity, floored rest heal, one-door Book of Five Rings, event rewards rolling `RARITY_ODDS`. |
| `D` `DRAFTER_VERSION` | **18** | `tier0/constants.py` | `EB-28`: the drafter prices Furina's Salon deploy through one [USER]-overridable dial, `STATIC_SALON_MEMBER_VALUE = 1.5`. |
| `P` `POLICY_VERSION` | **11** | `tier05/draft.py` | R207's scorer-literacy window: Spark hold-versus-spend, five state predicates, payout-aware selection scoring. |
| `C` `CONSTANTS_VERSION` | **21** | `tier0/constants.py` | `EB-219`: Prune's printed `gain_spark` ops leave the sheet, her Spark grant becoming Klee's own kit declaration (`KLEE_COMPANION_SPARK_*`, LAW:145). |

**Standing baseline:** `review/records/sitting-reads-2026-08-26-c20-d18-p11.md`,
twelve arms at `RT12/D18/P11/C20` (`main` = `190e598`) in ONE pass with
`game_ref/` present: `real_ironclad` **5.2%** / **65.5%** act-1, `real_silent`
**1.1%** / **54.0%**; **no interval separation on any arm and no control set**,
which it says itself. Its §0 grades the predecessor's three scorer caveats
CLEARED, so under R211 item 7 it is both the standing re-baseline and the
Phase-4 milestone table, **and that read is TAKEN**. It supersedes the
`c19-d17-p10` read, which stands as published (R101b).

Pinned, and NOT part of the run-cell stamp: `A6_INSTRUMENT_VERSION = 2`
(`tier0/harness/axes.py`, anchored additively so `ref_ironclad` stays 3.00; v1
and v2 A6 numbers are discontinuous by design), and heuristic pilot weights in
`content/pilots/archetypes.yaml` and `pilot/policy.py`, `STOKE_*` deliberately
not in `constants.py`. The act and map shape reads live off `tier0/constants.py`
(`RUN_ACTS`, `MAP_*`, `ROOM_ODDS`); `RUN_NODE_TEMPLATE` is DEAD since `RT` v6,
kept only as the archived world's name.

## Lifecycle

- **Tier 0 v0.1 — LOCKED.** Frozen v2 errata: non-boss Frozen is soft control
  (−50% next action + Shatter on the first Attack hit), bosses take Vulnerable 2
  (R44); the v0.1 scorecard baseline and median identity are regression-locked
  (`test_errata.V02_MEDIAN`).
- **Tier 0.5 M5 — SHIPPED.** The live run model is the real StS2 map; the M5–M8
  archive world was the v1 run template, never compared across template versions
  unlabeled. **Kokomi meter-20 — RATIFIED (R139);** the dead v0.3 W1 comparator
  is not rebuilt. **Roster slot 4 — Zhongli countersigned (R108), unscheduled;**
  the pre-slot-4 gate is the roster registry (`tier0/roster.py`).

## Roster

Ship order is stable and meaningful (`tier0/roster.py`); reports print it.

| id | display | HP | nation | element / cadence | default plan | archetypes |
|---|---|---|---|---|---|---|
| `klee` | Klee | 62 | Mondstadt | Pyro, catalyst-grade (all attacks apply) | demolition | demolition, spark, reaction |
| `furina` | Furina | 78 | Fontaine | Hydro, Skill-grade | salon | salon, spotlight, fanfare |
| `kokomi` | Sangonomiya Kokomi | 80 | Inazuma | Hydro, catalyst cadence | priest | priest, commander, assist |

Klee is the compatibility baseline; companion pools ship per nation
(`docs/<nation>-companions.yaml`). HP sits against the base cast (Ironclad 80,
Defect 75, Regent 75, Silent 70, Necrobinder 66): Furina 60 → **78** and Kokomi
70 → **80** by **R219 F**, both canonical HP-scalers, Klee low by design, so
every measured table quoting a Furina or Kokomi row is stale under R68 until a
re-baseline (`review/records/roster-hp-scalers-2026-08-29.md` lists which).

**Reference anchors** (measurement anchors, NOT roster members): `ref_ironclad`,
`real_ironclad`, `ref_silent`, `real_silent` (`tier0/roster.py:165-171`), the
scoring anchor being `("ref_ironclad", "starter")` under the `generic` pilot,
normalized so every axis reads `3.0`. The `real_*` variants need a local
`game_ref/` tree, gitignored and absent on a fresh clone; both pools verify
(ironclad 76, silent 87). Still owed: three hand-authored `*_char_facts.yaml`
that no roster arm reads, [USER]'s to supply (`EB-128`).

## Content inventory

Live sim inventory (`atlas/tier0-pilot-roster.md` §2): **322 cards in the
loader index** (3 acquisition-only Ancient rows, leaving the 319 the atlas
quotes), **5 character sheets**, **6 encounters, 15 pilot weight sets**;
battery encounters FROZEN (`content/encounters/battery.yaml`). The three card
sheets carry `tempo_band:` and hold **239 personal rows** (79 / 84 / 76).
Balance numbers live in `tier0/content/characters/*.yaml`, the ratified
artifact. Furina's pool carries **zero** `raise_fanfare_cap` riders, register
lint `R7` retiring with them.

## Mod card coverage (generated)

Codegen `tools/gen_roster_cards.py` (`gen_klee_cards.py` per character); the
per-character `Generated/manifest.json` files are the live coverage ledgers and
these figures are read from them. **Klee** fully generated. **Furina** 83 of
84, 1 blocked (`let_the_people_rejoice`). **Kokomi** 75 of 76, 1 blocked
(`ceremonial_garment`). Both blocks are hand-written kit machinery. **Every
generated card ships its upgrade:** all three `upgrades.no_upgrade_path` lists
and both curated codegen-debt registers are empty.

## Mod build environment (pinned)

Slay the Spire 2 **v0.111.0**, commit `41cef1ea`, buildid `24724944`, appid
`2868840`, branch **`public-beta`**, `main_assembly_hash` `222455745`. MegaDot
v4.5.1, BaseLib **3.4.5.0** (Workshop `3737335127`), .NET SDK 9.0.316, ilspycmd
8.2.0.7535, PCK contract `roster-pck-v3`, package `klee` **v0.2** with
`min_game_version` 0.111.0. Deploy stamps **`MAJOR.AUTO`** (R214) with the
`+proto` dev mark beside it (R217 D). The **installed build is
`0.2.1786+proto.dirty`** (2026-08-30), a dev package carrying both prototype
arms behind `-p:PrototypeCards=true`; the **last RELEASE package deployed is
`0.2.1357`** (2026-08-29). Pin history and the per-build narrative:
[`workstreams.md`](workstreams.md).

## Systems

Depth for each is in [`atlas/`](atlas/); these are one line apiece.

- **tier0 combat kernel** — ops, powers, statuses, reactions, resources; 7-axis
  scorecard anchored at `(ref_ironclad, starter) = 3.0`, frozen battery.
  **No axis value gates anything (R204):** axis values and declared-identity
  comparisons are reportable diagnostics only, and ratified 1,000-fight
  `winrate_bands` are unaffected.
- **tier0.5 run sim + drafter** — run model, acts, runner, draft, and the real
  StS2 16-floor map/route policy.
- **understudy** — the bot playtest bridge driving the real game (Guardrail-7,
  no-fun rule), plus the targeted-scenario harness and the `GitsDebugState`
  board-setup door, attended only.
- **klee-mod** — the C# character mod (`KleeCode/`), the PCK build/deploy
  pipeline, and a headless C# test project. Co-op's automated backstop is
  partial: transport and anything needing a live `CombatState` is play-only.
- **vendor STS2_MCP bridge** — the wire contract the understudy speaks.
  **art pipeline** — `ImageGen/` art staged into the roster mod and packed by
  `tools/build_pck.ps1`.

## Active workstreams

Status only, one line each; the narrative, the round records and every citation
are in [`workstreams.md`](workstreams.md).

- **Design course-correction (R213 / R217 / R218)** — the frame the rest runs
  inside: quarantined prototype surface, the independent seat, Kokomi → Klee
  → Furina in sequence with the shared Burst retirement last (R220 B).
- **Klee** — the overhaul is at Prototype: round 4 is ruled (R242: Klee
  starts each combat with 1 Spark, no long fuse, and the starter takes the
  canonical shape, Strike x4 / Defend x4 / Jumpy Dumpty / Ka-pow! at 0);
  round 5 is that build, seats first, then [USER] since rule 4 changed.
  `review/ruled/klee-overhaul-round-4-2026-09-02.md`; `EB-289` to `EB-291`.
- **Kokomi** — the OVERHAUL is at Prototype round 2 on draft 6, *the Plan*
  (brief R241): the Bake-Kurage is a pet, a card played on it writes its Plan
  line, both seats played the build, [USER]'s first run's finds are fixed
  (PR #271) and the fresh rules-gate run is on 0.2.2024+proto; packet
  `review/active/kokomi-overhaul-round-2-2026-09-02.md` (PR #275). The sim
  twin runs beside the C# (`tier0/engine/kokomi_plan.py`), every drafter
  price still ZERO. Beside it the Kurage memory is base kit behind
  `C.KURAGE_MEMORY`, display rebuild `EB-198`, cadence read `EB-234`.
- **Seats** — two games at once (`--lane 1` / `GITS_LANE`, PR #274), proven
  end to end on lane 1 2026-09-02 (`review/qa/lane1-live-reads-2026-09-02/`,
  which also took the map and arm-keyword live reads and found `EB-310`: no
  teardown may remove the SHARED bridge); a local-model seat (`blindplay
  session --backend local`, PR #269, live proof owed); and the render fixes
  `EB-290`/`EB-294`/`EB-299` (PR #272).
- **Furina** — the reframe is countersigned (R220 A), slice 1 is built in the
  sim behind five flags that all ship OFF, Spotlight is ruled one-mode priced
  (R228), and the C# arm is deferred.
- **Companion cards** — R234 ruled the slate whole, Mondstadt first, in
  parallel; `EB-249` / `EB-250` / `EB-251` are what it owes.
- **Deferred content families** — `Win10` (Klee bomb-board readers) and `Win11`
  (Furina Encore spenders): named, neither open, both FROZEN by R213.
- **Also live** — funnel throughput (R221, lanes and read-workers at 1.35× on
  reads), enemy remapping, the Furina and Kokomi art passes, animation sprint 2,
  the axis-validity Track A / Track E logs.

## Open [USER] pile

Every open row is in [`QUEUE.md`](QUEUE.md) and owned by [USER]: Kokomi's
stability band (`S4-G6`, mechanism answered at R231) and her protocol playtest
(`S4-G14`); `M69` on the Charge read budget; the art eyes-on pile
(`S4-G12`/`CC-G1`/`CC-G2`, `S4-G17`, `M26`, Globe Head, `grand_gala` r6); and
`M45`'s five post-playtest calls. **No prototype-slice row is open.** How the
pile emptied is in [`workstreams.md`](workstreams.md). The nine blessed
mechanisms are in [`watch-register.md`](watch-register.md): `W9` has FIRED and
is back with [USER] as `M69`, the other eight are dormant.
