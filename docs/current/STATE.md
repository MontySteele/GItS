# STATE

> **What currently ships** — roster, systems, versions — and where each
> workstream stands today, in one paragraph each. Snapshot only, near 150
> lines by rule (`CLAUDE.md` §Norms). The per-round narrative is
> [`workstreams.md`](workstreams.md); stamp history is [`STAMPS.md`](STAMPS.md);
> open picks are [`QUEUE.md`](QUEUE.md); engineering rows are
> [`BACKLOG.md`](BACKLOG.md); rules are [`LAW.md`](LAW.md); measurement law
> is [`EXPERIMENTS.md`](EXPERIMENTS.md); subsystem depth is [`atlas/`](atlas/).
> Rewritten to this size 2026-09-08 under R267.

## Live cell

**`RT13 / D18 / P11 / C21`**, read live via `tier05/cells.py`, with
`PILOT_WEIGHTS_VERSION` **6**. A number is not comparable across a stamp
boundary unless labeled, and a report without a stamp is not citable.

| stamp | value | source | what this value covers |
|---|---|---|---|
| `RT` `RUNTEMPLATE_VERSION` | **13** | `tier0/constants.py` | `EB-83`: Wood Carvings joins the act-1 event pool. |
| `D` `DRAFTER_VERSION` | **18** | `tier0/constants.py` | `EB-28`: Salon deploy priced through `STATIC_SALON_MEMBER_VALUE = 1.5`. |
| `P` `POLICY_VERSION` | **11** | `tier05/draft.py` | R207's scorer-literacy window. |
| `C` `CONSTANTS_VERSION` | **21** | `tier0/constants.py` | `EB-219`: Prune's Spark grant becomes Klee's kit declaration. |

**Standing baseline:** `review/records/sitting-reads-2026-08-26-c20-d18-p11.md`,
twelve arms at `RT12/D18/P11/C20`: `real_ironclad` **5.2%** / **65.5%** act-1,
`real_silent` **1.1%** / **54.0%**; no interval separation and no control set.
It is an `RT12` read and the world is `RT13`, so under R68 it is stale rather
than wrong; the re-baseline that bump owes has not been run. R219 F moved
Furina's and Kokomi's HP, so every measured table quoting their rows is stale
too (`review/records/roster-hp-scalers-2026-08-29.md`).

Pinned and not part of the cell: `A6_INSTRUMENT_VERSION = 2`; heuristic pilot
weights in `content/pilots/archetypes.yaml` and `pilot/policy.py`. The act
and map shape reads live off `tier0/constants.py`.

## Lifecycle

**Tier 0 v0.1 LOCKED** (R44 errata, `test_errata.V02_MEDIAN`). **Tier 0.5 M5
SHIPPED** on the real StS2 map. Kokomi meter-20 ratified (R139); roster slot
4 Zhongli countersigned (R108), unscheduled. All three kits are at the
**Prototype** stage under the design course-correction (R213 / R217 / R218):
seats drive the rounds, [USER] plays when a rule changes, and nothing
measured on a prototype row is quotable (R215 B).

## Roster

| id | display | HP | nation | element / cadence | default plan | archetypes |
|---|---|---|---|---|---|---|
| `klee` | Klee | 62 | Mondstadt | Pyro, catalyst-grade | demolition | demolition, spark, reaction |
| `furina` | Furina | 78 | Fontaine | Hydro, Skill-grade | salon | salon, spotlight, fanfare |
| `kokomi` | Sangonomiya Kokomi | 80 | Inazuma | Hydro, catalyst cadence | priest | priest, commander, assist |

Reference anchors, not roster members: `ref_ironclad`, `real_ironclad`,
`ref_silent`, `real_silent` (`tier0/roster.py`); the scoring anchor is
`("ref_ironclad", "starter")` under the `generic` pilot at `3.0` on every
axis. The `real_*` variants need the gitignored `game_ref/` tree. Three
hand-authored `*_char_facts.yaml` are still [USER]'s to supply (`EB-128`).

## Content inventory

**324 cards in the loader index**, 5 character sheets, 6 encounters, 15 pilot
weight sets; battery encounters FROZEN. The three shipped sheets hold **239
personal rows** (79 / 84 / 76) in `tier0/content/characters/*.yaml`. The
prototype surface (`docs/prototype-surface.yaml`) carries the three
overhaul pools beside them: Klee 45 rows, Kokomi 39, Furina's arm copies.
Codegen (`tools/gen_roster_cards.py`) ships every generated card with its
upgrade; Furina 83 of 84 and Kokomi 75 of 76 generated, the two blocks
hand-written kit machinery.

## Mod build environment (pinned)

Slay the Spire 2 **v0.111.0** (`41cef1ea`, buildid `24724944`, branch
`public-beta`), MegaDot v4.5.1, BaseLib **3.4.5.0**, .NET SDK 9.0.316, PCK
contract `roster-pck-v3`, package `klee` **v0.2**. Deploy stamps
**`MAJOR.AUTO`** with the `+proto` dev mark. **Installed: `0.2.3069+proto`**
(2026-09-08, main after #461, all four arms on: the prototype rows behind
`-p:PrototypeCards=true`, the Furina arm behind `-p:FurinaReframe=true`;
every arm ships OFF in a release package). **Last RELEASE package:
`0.2.1357`** (2026-08-29). Pin history: [`workstreams.md`](workstreams.md).

## Systems

- **tier0 combat kernel** — ops, powers, statuses, reactions, resources;
  7-axis scorecard anchored at `(ref_ironclad, starter) = 3.0`. No axis
  value gates anything (R204). Prototype twins: `tier0/engine/kokomi_plan.py`,
  `tier0/engine/klee_overhaul.py`.
- **tier0.5 run sim + drafter** — the real 16-floor map; Plan lines priced
  under `PLAN_DELAY_DISCOUNT`.
- **understudy** — the bot bridge driving the real game (Guardrail-7, no fun
  claims), two lanes beside [USER]'s game, the local Qwen seat, the
  doctrine-review seat (`understudy.seat review --role doctrine`).
- **klee-mod** — the C# character mod, the PCK build/deploy pipeline, a
  headless C# test project (1,501 tests); co-op's backstop is partial.
- **vendor STS2_MCP bridge**; **art pipeline** (`ImageGen/` → `build_pck.ps1`);
  player-facing text has measured ceilings and a lint.

## Workstreams, today (2026-09-08)

- **Klee.** 24 seat rounds read and one [USER] act-1 run
  (`review/ruled/klee-user-run-1-2026-09-07.md`, R265). The starter is
  R242's basics plus Jumpy Dumpty (Innate, R261) and Ka-pow!, the
  0-cost Retained detonator,
  held twice (R262). Every Hexerei card gives a Spark (R265 pick 1,
  `EB-642`) and the mark pays on any card carrying it (`EB-663`, round 24).
  **No pick open.** [USER]'s second run is PLAYED (2026-09-08,
  `0.2.3069+proto`, `review/records/klee-user-run-2-2026-09-08.md`): act 1
  cleared, died mid act 2 to the Entomancer; the concept and the
  attack-or-Block tension confirmed, a Spark-centric defence fun but
  inconsistent, three tips trimmed. **Round 25 is READ**
  (`review/active/klee-overhaul-round-25-2026-09-08.md`): on
  `0.2.3105+proto` a natural lane with Countdown and an assembled
  Spark-defence lane, floors 11 and the act-1 elite; Spark never bound on
  either (peaked at 8 while taking damage), the defence failed on
  detonator draw and Energy, never on Sparks or Bombs, and lane 1 declined
  every Spark-priced card; **one pick open, [USER]'s:** what Spark is for
  (QUEUE `klee-spark-purpose 5.1`, default: a lubricant that buys the
  scarce things). Round 26 waits on it.
  **Open question, not closed by round 24:** whether spending Sparks is
  interesting: round 23 found the bank never scarce on a natural lane and
  deadlocked on a Spark deck, and no round 24 seat named a Set off the
  Companion Spark alone bought.
- **Kokomi.** 32 seat rounds and one [USER] act-1 run ("better than before,
  but the central loop feels too auto-pilot", R265). The brief is at draft 7
  (`review/active/kokomi-brief-2026-09-01.md`), carrying Dusk and the queue
  as a resource (R265), the cap retired (R266) and R267. Pool passes two to
  five rebuilt the pool to 39 rows; passes six and seven (Plan lines on the
  basics) were **withdrawn** the day they landed under [USER]'s rule that
  starter basics are never changed (#461). **R267 (2026-09-08)** restored
  Slack Water's morning Plan and Scout Ahead's position clause and sent
  passes four and five to the audit door. **R268 (2026-09-08)** answered
  the Plan-less hand nowhere for now
  (`review/ruled/kokomi-plan-less-hand-2026-09-08.md`). **No pick open.**
  Next round: the depth of the current pool's Plan interactions, with Scout
  Ahead and Slack Water on the lane, before any access card is drafted.
- **Furina.** The reframe (R220 A) ran 16 seat rounds on the arm and one
  [USER] act-1 run whose notes were all interface (`EB-627`–`EB-629` built,
  one eyes-on owed on the next deploy). On 2026-09-07 [USER] reset the kit
  to its identity: three concepts (A the Tide, B the Arkhe, C the Flood),
  **A taken as the working theory** the same night; the deeper sketch under
  A carries **five picks, [USER]'s**, one of them a C pick on the healing
  exception (PR #443; #433 is superseded by it and closes on its pick 2).
  No build until the picks.
- **Control run** — R250 pick 4: the same Opus seat family playing base
  Ironclad died on the act-1 boss twice (`review/records/control-ironclad-2026-09-04.md`);
  a kit clear on a 30-row pool is consistency as much as strength.
- **Elements and reactions** — R263 / R264: Dendro deferred with its
  boundaries drawn; the layer's brief (`review/active/reaction-brief-2026-09-06.md`)
  owes a GPT audit; `EB-410` is the open display half.
- **Companion cards** — R234 ruled the slate, Mondstadt first; `EB-249` /
  `EB-250` / `EB-251` are what it owes; `companion-cards-2026-08-30.md` §P5a
  is open.
- **Repo hygiene (R267 pick 4)** — STATE at this size, closed BACKLOG rows
  archived to tag `backlog-archive-2026-09-08`, no-pick round packets in
  `review/records/`, hooks resolved from the project dir. Older open
  packets: `eb74-lever2-options` (a staged lever, C), `p2-hard-state-thresholds`
  (picks 1–4).
- **Deferred content families** — `Win10` and `Win11`, FROZEN by R213.

## Open [USER] pile

[`QUEUE.md`](QUEUE.md) holds the eyes-on rows (Furina's rebuilt board, the
Curtain Call faces, three running-game looks, the end-of-turn docket). The
picks on branches are Furina's identity (PR #443); the older open packets in `review/active/` are the companion
P5a pick, `eb74`'s staged lever and the P2 thresholds. The six blessed
mechanisms are in [`watch-register.md`](watch-register.md), all dormant.
