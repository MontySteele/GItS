# STATE

> **What currently ships** — roster, systems, versions — and the pointers into
> everything else. Snapshot only, near 150 lines by rule (`CLAUDE.md` §Norms),
> whose read order routes the detail to [`STAMPS.md`](STAMPS.md),
> [`QUEUE.md`](QUEUE.md), [`BACKLOG.md`](BACKLOG.md), [`LAW.md`](LAW.md),
> [`EXPERIMENTS.md`](EXPERIMENTS.md), [`OPERATIONS.md`](OPERATIONS.md),
> [`workstreams.md`](workstreams.md), [`watch-register.md`](watch-register.md)
> and [`atlas/`](atlas/).

## Live cell

**`RT13 / D18 / P11 / C21`**, read live via `tier05/cells.py`, with
`PILOT_WEIGHTS_VERSION` **6**. A number is not comparable across a stamp
boundary unless labeled, and a report without a stamp is not citable. What each
level covered and archived is in [`STAMPS.md`](STAMPS.md), not here.

| stamp | value | source | what this value covers |
|---|---|---|---|
| `RT` `RUNTEMPLATE_VERSION` | **13** | `tier0/constants.py` | `EB-83`: Wood Carvings joins the act-1 event pool (12 own → 13), the last of `EB-68`'s conversions — two colorless reskin cards, a ninth enchantment, and the first printed carrier of `block_at_turn_start`. |
| `D` `DRAFTER_VERSION` | **18** | `tier0/constants.py` | `EB-28`: the drafter prices Furina's Salon deploy through one [USER]-overridable dial, `STATIC_SALON_MEMBER_VALUE = 1.5`. |
| `P` `POLICY_VERSION` | **11** | `tier05/draft.py` | R207's scorer-literacy window: Spark hold-versus-spend, five state predicates, payout-aware selection scoring. |
| `C` `CONSTANTS_VERSION` | **21** | `tier0/constants.py` | `EB-219`: Prune's printed `gain_spark` ops leave the sheet, her Spark grant becoming Klee's own kit declaration (`KLEE_COMPANION_SPARK_*`, LAW:145). |

**Standing baseline:** `review/records/sitting-reads-2026-08-26-c20-d18-p11.md`,
twelve arms at `RT12/D18/P11/C20` (`main` = `190e598`) in ONE pass with
`game_ref/` present: `real_ironclad` **5.2%** / **65.5%** act-1, `real_silent`
**1.1%** / **54.0%**; **no interval separation on any arm and no control set**,
which it says itself. Under R211 item 7 it is both the standing re-baseline and
the Phase-4 milestone table, **and that read is TAKEN**. It is an `RT12` read
and the world is now `RT13` (`EB-83`, act-1 event odds), so under R68 it is
stale rather than wrong: **the re-baseline that bump owes has not been run.**

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

Live sim inventory (`atlas/tier0-pilot-roster.md` §2): **324 cards in the
loader index** (3 acquisition-only Ancient rows, leaving the 321 the atlas
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
`+proto` dev mark (R217 D). **Installed: `0.2.2564+proto`** (2026-09-04,
the #373 stack at `fb7b12d8` on main `f1c6c9ec`, ALL FOUR arms on since R250:
the round-9 to round-13 builds, R253's nine audited rows, R254's starter
reader, Countdown, Stoke the Fuse, Aria's bar at 3, and the four fixers'
27 face, tip, page and bridge rows including the bridge's action cap
`EB-456`), the prototype arms behind
`-p:PrototypeCards=true` and the Furina arm behind `-p:FurinaReframe=true`
too; every arm ships OFF in a release package. **Last RELEASE
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
- **Klee** — Rounds 8 and 9 are RULED (R250, R252, narrowed by R253;
  `review/ruled/klee-overhaul-round-8-2026-09-04.md`, `...round-9-2026-09-04.md`):
  the Splash pays the largest Bomb, and the pool's defence shelf is three
  conditional rows (Dodoco Cover, Careful Now, Barbara — Front Row Seat);
  Fire Safety and Safety Lesson were withdrawn on the charter audit
  (R253, `review/records/card-audit-2026-09-04.md`). Round 10 is READ
  (`review/ruled/klee-overhaul-round-10-2026-09-04.md`): six runs on
  `0.2.2401+proto`, six act-1 clears, none past act 2; Dodoco Cover played
  every fight, Careful Now split the seats along cook-or-cash, Front Row
  Seat unseen; no pick, `EB-390`-`EB-400`. **Round 11 is READ**
  (`review/active/klee-overhaul-round-11-2026-09-04.md`): two seats on
  `0.2.2476+proto` with Countdown in the pool (undrawn), floors 5 and 10,
  both budget-out; the loan against the clock priced on the nose, a Spark
  gain nothing prints (`EB-418`), random Set off and one-charge reaction
  rules unprinted (`EB-431`, `EB-432`); no pick. **Round 12 is READ**
  (`review/active/klee-overhaul-round-12-2026-09-04.md`): two seats on
  `0.2.2501+proto`, floors 10 and 8, ordering read as the puzzle, the Mine
  tip read as mitigation (`EB-436`), Block and Skittish learned by experiment
  (`EB-443`), Countdown undrawn in five runs; no pick. **Round 13 is READ**
  (`review/active/klee-overhaul-round-13-2026-09-04.md`): one seat on
  `0.2.2547+proto`, floor 14 at a declared budget overrun, eight of eight
  fights, "don't use your big spell" read as the kit's best decision, the
  Bomb queue and the enemy-turn Melt invisible (`EB-450`), events unnamed
  (`EB-448`); no pick. **Round 14 is READ**
  (`review/active/klee-overhaul-round-14-2026-09-04.md`): one seat on
  `0.2.2564+proto`, floor 8 at the bridge's cap, six of six fights, the
  Spark economy read as the kit's engine, an invisible Mine (`EB-457`), the
  enemy block printed twice (`EB-458`); no pick. **Round 15 is READ, targeted**
  (`review/active/klee-overhaul-round-15-2026-09-04.md`): two runs, Countdown and
  Stoke the Fuse granted then Grounded and Sparks 'n' Splash; Stoke played
  five times with a real ordering rule, Countdown quiet, Sparks 'n' Splash
  never played in four fights of its own kit, the intent hedge and the map's deck list wrong
  (`EB-461`, `EB-447` reopened); no pick. [USER]'s act-1 run is due on
  `0.2.2401+proto`. The round-8 clear is read against a control run (below).
- **Kokomi** — Rounds 4d and 5 are RULED (R250,
  `review/ruled/kokomi-overhaul-round-4d-2026-09-03.md`, `...round-5-2026-09-04.md`):
  six Plan-only cards gain a weaker now-line, and a single-target Plan is aimed
  when written if the engine can carry a second selection, else lands on the
  front enemy that is not a Minion. Round 9 is READ
  (`review/ruled/kokomi-overhaul-round-9-2026-09-04.md`): both rules read
  true, run 2 cleared acts 1 and 2 and died on act-3 floor 39 after a misread
  of The Moon's face; the pool's empty shelf is tempo (no energy, no Retain),
  one pick, `EB-376`-`EB-381`. **Round 10 is BUILT** — the TEMPO SHELF, round 9
  pick 1 at its default AS AUDITED (R253,
  `review/ruled/kokomi-overhaul-round-9-2026-09-04.md`): Tide Chart and
  Ripple, on a new `plans_held` count in both engines, the pool 30 rows;
  Held Tide and Tidal Rhythm were withdrawn on the charter audit and are
  not on the surface. **Round 10 is READ**
  (`review/ruled/kokomi-overhaul-round-10-2026-09-04.md`): two seats on
  `0.2.2446+proto`, floors 6 and 11, both budget-out, neither drew Tide
  Chart; the Plan's Shrink line read true again, the jellyfish stood empty
  on most turns, one pick (starter Plan density), `EB-402`-`EB-403`,
  `EB-408`-`EB-411`; RULED R254, starter density stands. **Round 11 is READ**
  (`review/active/kokomi-overhaul-round-11-2026-09-04.md`): two seats on
  `0.2.2476+proto`, floors 10 and 10, both budget-out; the six round-10
  fixes read true, the Plan read as the kit's decision and as autopilot in
  one run, `EB-426`-`EB-428`, `EB-433`; no pick. **Round 12 is READ**
  (`review/active/kokomi-overhaul-round-12-2026-09-04.md`): one seat on
  `0.2.2501+proto`, floor 11; a carry-out into Block prints nothing, an
  Attack face not Weak-folded, the Plan tip's aim sentence unread
  (`EB-440`-`EB-442`); no pick. **Round 13 is READ**
  (`review/active/kokomi-overhaul-round-13-2026-09-04.md`): one seat on
  `0.2.2547+proto`, the act-1 boss reached at a declared budget overrun,
  eight of eight fights, War Council read as four different correct calls,
  a targeted potion vanishing untargeted (`EB-452`), the carry-out panel
  omitting a Plan (`EB-453`), Change of Plans dead until it says why
  (`EB-455`), the bridge to count actions (`EB-456`); Tide Chart undrawn a
  seventh time; no pick. **Round 14 is READ**
  (`review/active/kokomi-overhaul-round-14-2026-09-04.md`): one seat on
  `0.2.2564+proto`, floor 12 at the cap with the elite dying, Arcane
  Scroll gave no card (`EB-459`), dual-intent attack numbers never land
  (`EB-461`), Kurage's Oath's tag contradicts its rider (`EB-462`); Tide
  Chart undrawn an eighth time; no pick. **Round 15 is READ, targeted**
  (`review/ruled/kokomi-overhaul-round-15-2026-09-04.md`, RULED R257):
  Tide Chart granted and dead as printed (zero draws on three of four
  plays), which fired R254's re-ask trigger; **R257 took the default**: Tide
  Chart redesigned to pay after the carry-outs (`EB-478`, GPT-audited before
  a tester), the starter stays two kit cards; `EB-467`-`EB-469`. [USER]'s act-1 run is due on
  `0.2.2501+proto`. The Kurage
  memory is base kit behind `C.KURAGE_MEMORY` (`EB-198`, `EB-234`).
- **Furina** — the reframe is countersigned (R220 A); slice 1 is built in the
  sim and, since PR #298, in the C# behind `FURINA_REFRAME`, both OFF. **Slice
  2's five `proto_fr_` rows are built** (2026-09-02; nine with round 4's
  riders): the named deploy, two
  Evokes and the drain pair, on a new `drain_fanfare` op and the
  `Deploy`/`Evoke`/`Drain` tips. R250 (2026-09-04) LIFTS the R220 B sequence: the arm is on in the
  installed dev build, soaked, and **round one is read**
  and RULED (R251, `review/ruled/furina-reframe-round-1-2026-09-04.md`): one
  Sonnet seat cleared act 1 at 8 of 78, the reframe's rules read true, the
  shipped Burst won the boss fight. **Round two is BUILT**: the shipped Burst
  retires under the arm alone — no draw, no feed, no kit card, behind
  `FURINA_REFRAME_BURST` in both engines, the shared retirement still
  `EB-199` / `EB-200`'s (`EB-365` closed) — with `EB-364`, `EB-366`, `EB-367`
  and `EB-368`. Round 2 is RULED (R253,
  `review/ruled/furina-reframe-round-2-2026-09-04.md`): the riders re-priced
  arm-only and Encore absorption kept and printed. **Round 4 is BUILT** — round 2 pick 1 at its default, the four copies
  passed the charter audit: four
  arm-only `proto_fr_` copies of the shipped Fanfare riders at the arm's own
  scale (12/12/15/20 down to 6/6/8/10), swapped in for the shipped ids at the
  same rarity by `loader._pool_substitutions` and
  `FurinaReframeRoster.SwapOfferedRiders`, so the shipped sheet stands and an
  arm-off run is offered the shipped card. **Round 4 is READ**
  (`review/ruled/furina-reframe-round-4-2026-09-04.md`): two seats on
  `0.2.2446+proto`, floors 4 and 8, both budget-out, no rider copy drawn,
  Fanfare decorative below the bars; four real decisions named, one pick
  (a reader in every deck), `EB-404`-`EB-407`, `EB-412`-`EB-414`; RULED R254:
  Aria of Recompense reads Fanfare under the arm (5 more Encore at 3 since
  round 6, from 6), the
  starter stays two kit cards, **BUILT** as `proto_fr_aria_of_recompense`.
  **Round 5 is READ**
  (`review/active/furina-reframe-round-5-2026-09-04.md`): two seats on
  `0.2.2476+proto`, floors 10 and 10, both budget-out; the turn one with no
  Encore in every fight, the reader carried at Fanfare 3 and its line never
  paid, nine rows (`EB-419`-`EB-425`, `EB-429`, `EB-430`); one pick, the
  Encore opening. **Rounds 6 and 7 are READ**
  (`review/active/furina-reframe-round-6-2026-09-04.md`, `-round-7-`): one
  seat each on `0.2.2501+proto` and `0.2.2547+proto`, floors 11 and 10, the
  reader's bar moved to 3 (round 6 default), a member's roll spent the paid
  performance on a reviving Minion (`EB-451`, skips Minions as R250's shape),
  the retired Burst's tip still taught at a reward (`EB-449`); the Encore
  opening read the same a third time. **Round 8 is READ**
  (`review/active/furina-reframe-round-8-2026-09-04.md`): one seat on
  `0.2.2564+proto`, floor 10 at the cap, six of six fights with the elite,
  Guest Cast skipping Chiori's hit (`EB-463`), a Replay performing no member
  (`EB-464`), five faces feeding a Burst no screen shows (`EB-449`), the
  Encore opening read the same a fourth time. **Round 9 is READ**
  (`review/active/furina-reframe-round-9-2026-09-04.md`): one seat on
  `0.2.2577+proto`, floor 11 at the cap, six of six with the elite at zero
  HP; enemy Block never printed (`EB-474`), three undefined terms
  (`EB-475`), a performance takes Vulnerable and does not Shatter
  (`EB-476`), an empty stage halves a Companion card silently (`EB-477`);
  turn one read as a real choice, dry by construction. [USER]'s act-1 run
  is due on that build. No stamp moves, nothing measured.
- **Control run** — R250 pick 4, RUN 2026-09-04
  (`review/records/control-ironclad-2026-09-04.md`): the same Opus seat family
  playing base Ironclad at Ascension 0 died on the act-1 boss, floor 17, where
  the arm pools (33 Klee / 30 Kokomi rows
  against 79 / 76 shipped) cleared
  three of seven kit runs. The clears are the kits'; a clear on a 30-row pool
  is consistency as much as strength. The second control (same afternoon,
  §5) died on the same floor to the same Death Blow; no third is queued.
- **Companion cards** — R234 ruled the slate whole, Mondstadt first, in
  parallel; `EB-249` / `EB-250` / `EB-251` are what it owes; Itto and Gorou's
  rate are noted there from the round-5 and act-1 reads.
- **Repo debt** — the deploy gate, the push hook, derived register ids and
  the agent rituals as scripts and skills are being built (2026-09-02).
- **Deferred content families** — `Win10` and `Win11`, both FROZEN by R213.

## Open [USER] pile

Every open row is in [`QUEUE.md`](QUEUE.md) and owned by [USER] — `M69` and
the art eyes-on pile (R250 closed `S4-G6`, `S4-G14` and `M45` as overtaken); the text-conventions
proposal is ruled (R249, `review/ruled/text-conventions-shipped-2026-09-02.md`;
builds `EB-345`, `EB-346`). The six blessed mechanisms are in [`watch-register.md`](watch-register.md), all
dormant; `W6`, `W8` and `W9` were struck by R256 with the shipped Kokomi's
Charge and Burst. R256 (2026-09-04) ruled the rulings deprecation audit at all
four defaults (`review/ruled/rulings-deprecation-audit-2026-09-04.md`): R56
struck, R58 scoped to Balance sheets, and each overhaul's Balance landing
strikes its own LAW lines (its §3).
