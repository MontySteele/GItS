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
`+proto` dev mark (R217 D). **Installed: `0.2.2136+proto.dirty`** (2026-09-02,
main `4da69fe5`), the three prototype arms behind `-p:PrototypeCards=true`; the
Furina arm needs `-p:FurinaReframe=true` too and ships OFF. **Last RELEASE
package: `0.2.1357`** (2026-08-29). Pin history: [`workstreams.md`](workstreams.md).

## Systems

Depth for each is in [`atlas/`](atlas/); these are one line apiece.

- **tier0 combat kernel** — ops, powers, statuses, reactions, resources; 7-axis
  scorecard anchored at `(ref_ironclad, starter) = 3.0`, frozen battery.
  **No axis value gates anything (R204).** Prototype twins beside it:
  `tier0/engine/kokomi_plan.py` and `tier0/engine/klee_overhaul.py`.
- **tier0.5 run sim + drafter** — run model, acts, runner, draft, the real
  StS2 16-floor map; the drafter prices Plan lines under the instrument dial
  `PLAN_DELAY_DISCOUNT` (EB-311, shipped scores byte-identical).
- **understudy** — the bot playtest bridge driving the real game (Guardrail-7,
  no-fun rule), two lanes beside [USER]'s game (`--lane 1` / `--lane 2`), the
  local Qwen seat (`GITS_LOCAL_PLAY_TOKENS=12000`), and the scenario harness.
- **klee-mod** — the C# character mod (`KleeCode/`), the PCK build/deploy
  pipeline, a headless C# test project; co-op's automated backstop is partial.
- **vendor STS2_MCP bridge** — the wire contract the understudy speaks.
  **art pipeline** — `ImageGen/` art staged into the roster mod and packed by
  `tools/build_pck.ps1`. **Player-facing text** has measured ceilings and a
  lint (`docs/current/text-conventions.md`).

## Active workstreams

Status only, one line each; the narrative, the round records and every citation
are in [`workstreams.md`](workstreams.md).

- **Design course-correction (R213 / R217 / R218)** — the frame the rest runs
  inside; R220 B sequences it Kokomi → Klee → Furina, Burst retirement last.
- **Klee** — Prototype round 6 is installed: the R242 starter with R243's
  numbers (growth 4, Ka-pow! Retain, the Sparks 'n' Splash echo, the base
  Strike applying nothing) and the Plan/Bomb upgrade pass (EB-315). The
  Fable card audit (PR #302)
  is the next build; the seats then play three acts before [USER] does.
- **Kokomi** — Prototype round 3 on draft 6, *the Plan* (brief R241), the
  rules gate passed on [USER]'s act-1 run (R243). Installed with the same
  build; the casket and morning legibility rows (`EB-316`, `EB-317`) and the
  Fable card audit (PR #303) are next; the acts-2/3 depth is the Plan cards'
  own design, no momentum rule. The Kurage memory is base kit behind
  `C.KURAGE_MEMORY` (`EB-198`, `EB-234`).
- **Furina** — the reframe is countersigned (R220 A); slice 1 is built in the
  sim and, since PR #298, in the C# behind `FURINA_REFRAME`, both OFF; no
  card rows exist for it yet.
- **Companion cards** — R234 ruled the slate whole, Mondstadt first, in
  parallel; `EB-249` / `EB-250` / `EB-251` are what it owes; Itto and Gorou's
  rate are noted there from the round-5 and act-1 reads.
- **Repo debt** — the deploy gate, the push hook, derived register ids and
  the agent rituals as scripts and skills are being built (2026-09-02).
- **Deferred content families** — `Win10` and `Win11`, both FROZEN by R213.

## Open [USER] pile

Every open row is in [`QUEUE.md`](QUEUE.md) and owned by [USER] — Kokomi's two,
`M69`, the art eyes-on pile and `M45`'s five; the text-conventions shipped
proposal (`review/active/text-conventions-shipped-2026-09-02.md`) carries four
more. The nine blessed mechanisms are in [`watch-register.md`](watch-register.md):
`W9` has FIRED and is back with [USER] as `M69`, the other eight are dormant.
