# STATE

> **What currently ships** — roster, systems, versions — and the pointers into
> everything else. Snapshot only, near 150 lines by rule (`CLAUDE.md` §Norms),
> whose read order routes the detail to [`STAMPS.md`](STAMPS.md),
> [`QUEUE.md`](QUEUE.md), [`BACKLOG.md`](BACKLOG.md), [`LAW.md`](LAW.md),
> [`EXPERIMENTS.md`](EXPERIMENTS.md), [`OPERATIONS.md`](OPERATIONS.md),
> [`workstreams.md`](workstreams.md), [`watch-register.md`](watch-register.md)
> and [`atlas/`](atlas/).

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
which it says itself. Under R211 item 7 it is both the standing re-baseline and
the Phase-4 milestone table, **and that read is TAKEN**.

Pinned, and NOT part of the run-cell stamp: `A6_INSTRUMENT_VERSION = 2`
(`tier0/harness/axes.py`, anchored additively so `ref_ironclad` stays 3.00; v1
and v2 A6 numbers are discontinuous by design), and heuristic pilot weights in
`content/pilots/archetypes.yaml` and `pilot/policy.py`, `STOKE_*` deliberately
not in `constants.py`. The act and map shape reads live off `tier0/constants.py`
(`RUN_ACTS`, `MAP_*`, `ROOM_ODDS`); `RUN_NODE_TEMPLATE` is DEAD since `RT` v6,
kept only as the archived world's name.

## Lifecycle

- **Tier 0 v0.1 — LOCKED.** The R44 Frozen errata, the v0.1 scorecard baseline
  and the median identity are regression-locked (`test_errata.V02_MEDIAN`).
- **Tier 0.5 M5 — SHIPPED.** The live run model is the real StS2 map; the M5–M8
  archive world was the v1 run template, never compared across template versions
  unlabeled. **Kokomi meter-20 — RATIFIED (R139). Roster slot 4 — Zhongli
  countersigned (R108), unscheduled;** the pre-slot-4 gate is the roster
  registry (`tier0/roster.py`).

## Roster

Ship order is stable and meaningful (`tier0/roster.py`); reports print it.

| id | display | HP | nation | element / cadence | default plan | archetypes |
|---|---|---|---|---|---|---|
| `klee` | Klee | 62 | Mondstadt | Pyro, catalyst-grade (all attacks apply) | demolition | demolition, spark, reaction |
| `furina` | Furina | 78 | Fontaine | Hydro, Skill-grade | salon | salon, spotlight, fanfare |
| `kokomi` | Sangonomiya Kokomi | 80 | Inazuma | Hydro, catalyst cadence | priest | priest, commander, assist |

Klee is the compatibility baseline; companion pools ship per nation
(`docs/<nation>-companions.yaml`). HP sits against the base cast (Ironclad 80,
Defect 75, Regent 75, Silent 70, Necrobinder 66), Klee low by design. **R219 F
moved Furina and Kokomi, so every measured table quoting one of their rows is
stale under R68** until a re-baseline
(`review/records/roster-hp-scalers-2026-08-29.md` lists which).

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
`0.2.2083+proto.dirty`** (2026-09-02, main `3f6157c0`), a dev package carrying
the three prototype arms behind `-p:PrototypeCards=true`; the **last RELEASE
package deployed is `0.2.1357`** (2026-08-29). Pin history and the per-build narrative:
[`workstreams.md`](workstreams.md).

## Systems

Depth for each is in [`atlas/`](atlas/); these are one line apiece.

- **tier0 combat kernel** — ops, powers, statuses, reactions, resources; 7-axis
  scorecard anchored at `(ref_ironclad, starter) = 3.0`, frozen battery.
  **No axis value gates anything (R204)** — they are reportable diagnostics.
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
  inside; R220 B sequences it Kokomi → Klee → Furina, Burst retirement last.
- **Klee** — the overhaul is at Prototype round 5, the R242 starter, played
  by the Opus and local seats on lanes 1 and 2; the packet applies growth 5
  and puts Ka-pow!'s Retain, Dig In and the round-six play to [USER] (PR
  #292). The prototype balance pass (twelve D defaults on both arms, read
  `review/records/balance-read-prototype-2026-09-02.md`) is being built;
  `EB-311` to `EB-314` are its and round five's rows.
- **Kokomi** — the OVERHAUL is at Prototype round 2 on draft 6, *the Plan*
  (brief R241): the Bake-Kurage is a pet, a card played on it writes its Plan
  line; the pet-targeting and focus fixes (`EB-296`, `EB-300`, PR #288) are
  in the installed build and [USER]'s fresh rules-gate run is on it, four
  questions in `review/active/kokomi-overhaul-round-2-2026-09-02.md`. The
  sim twin runs beside the C# (`tier0/engine/kokomi_plan.py`), every drafter
  price still ZERO (`EB-311`); the Kurage memory is base kit behind
  `C.KURAGE_MEMORY` (`EB-198`, `EB-234`).
- **Seats** — two lanes beside [USER]'s game (`--lane 1` / `--lane 2`,
  `GITS_LANE`), proven twice on 2026-09-02; the local Qwen seat is
  live-proven (needs `GITS_LOCAL_PLAY_TOKENS=12000`); a teardown leaves the
  shared bridge in place (`EB-310`, met live). Player-facing text now has
  measured ceilings and a lint (`docs/current/text-conventions.md`, PR #291);
  the shipped-sheet proposal is [USER]'s
  (`review/active/text-conventions-shipped-2026-09-02.md`).
- **Furina** — the reframe is countersigned (R220 A), slice 1 is built in the
  sim behind five flags that all ship OFF, and the C# arm is deferred.
- **Companion cards** — R234 ruled the slate whole, Mondstadt first, in
  parallel; `EB-249` / `EB-250` / `EB-251` are what it owes.
- **Deferred content families** — `Win10` and `Win11`, both FROZEN by R213.
- **Also live** — funnel throughput (R221), enemy remapping, the Furina and
  Kokomi art passes, animation sprint 2, the axis-validity Track A / E logs.

## Open [USER] pile

Every open row is in [`QUEUE.md`](QUEUE.md) and owned by [USER] — Kokomi's two,
`M69`, the art eyes-on pile and `M45`'s five. **No prototype-slice row is
open**, and how the pile emptied is in [`workstreams.md`](workstreams.md). The
nine blessed mechanisms are in [`watch-register.md`](watch-register.md): `W9`
has FIRED and is back with [USER] as `M69`, the other eight are dormant.
