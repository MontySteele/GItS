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
`public-beta`), MegaDot v4.5.1, BaseLib **3.4.7.0**, .NET SDK 9.0.316, PCK
contract `roster-pck-v3`, package `klee` **v0.2**. Deploy stamps
**`MAJOR.AUTO`** with the `+proto` dev mark. **Installed: `0.2.3674+proto`**
(2026-09-17, main after #631, arms `klee,companion,kokomi,furina-stage,teyvat`:
the prototype rows behind `-p:PrototypeCards=true`, the Stage behind
`-p:FurinaStage=true`, the Teyvat frame behind `-p:TeyvatFrame=true` and ON
for the deploy proofs, OFF again on the next calibration deploy; the reframe
arm left the tree under `EB-726`, so `furina-stage` is her only arm; every arm
ships OFF in a release package).
**Last RELEASE package:
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

- **Klee.** 26 seat rounds read and two [USER] act-1 runs
  (`review/ruled/klee-user-run-1-2026-09-07.md`, R265;
  `review/records/klee-user-run-2-2026-09-08.md`: act 1 cleared, died mid
  act 2, the attack-or-Block tension confirmed, a Spark-centric defence fun
  but inconsistent). The starter is R242's basics plus Jumpy Dumpty (Innate,
  R261) and Ka-pow!, the 0-cost Retained detonator, held twice (R262). Every
  Hexerei card gives a Spark (R265 pick 1, `EB-642`) and the mark pays on
  any card carrying it (`EB-663`). **R270** ruled Spark a currency whose
  income stays, Regent's Stars the comparison; **pool pass two** (`EB-732`,
  `review/records/klee-pool-pass-two-2026-09-08.md`) gave it six sinks
  paying Block, cards and Energy, built on `0.2.3159+proto`. **Round 26 is
  READ** (`review/active/klee-overhaul-round-26-2026-09-08.md`): the sinks
  made turns when the bank could pay, and the bank cannot pay on turn one,
  where rule 4 gives 1 and the cheapest sink costs 2; its opening-bank pick
  is **HELD** behind the consolidated read. **R271 (2026-09-14)** ruled the
  pool consolidation at its four defaults
  (`review/ruled/klee-pool-consolidation-2026-09-09.md`): Fwoosh! and
  Fireworks Show cut, Powder Charge redesigned as Booby Trap, Grounded on
  "no Set off card last turn", Return to Sender capped at its own Block,
  six rows shelved as lower value, and the slices in the order Mines,
  finding and overflow, React's route, Spark-supported Cook, mischief. Its
  §8 staging is the next build: stage one (cuts, redesign, repairs) read by
  round 27, stage two (the Mines batch) by round 28. **Stage one is BUILT
  and round 27 is READ** (`EB-749` closed; BaseLib moved to 3.4.7 under it,
  `EB-751`; `review/records/klee-overhaul-round-27-2026-09-14.md`): four
  seats on one seed, the core decision in every one, Grounded's condition a
  fork, the Splash pairing an engine that then runs itself, Tinder Toss
  never declined in three plays (one more read before its price moves).
  Round 28 is the Mines batch plus the opening-bank comparison. **The fun
  calibration**
  (`review/records/klee-fun-calibration-2026-09-14.md`) rides the next three
  builds: seats and [USER] answer three fixed lines on one seed, and the
  score decides whether seats can read for [USER]; Klee's done gate is in
  `operations/stage-gate.md`.
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
- **Furina.** The retired reframe (R220 A) ran 16 seat rounds and one
  [USER] act-1 run whose notes were all interface. On 2026-09-07 [USER]
  reset the kit to its identity, and on 2026-09-08 the design sitting
  re-founded it as **the Stage**: three performers as pets with visible
  bars, Fanfare IS the bar, damage order Block / lead / Furina per attack,
  Spend from the lead, a bow on Spend only, no Burst bar
  (`review/active/furina-stage-brief-2026-09-08.md`, draft 2 after GPT's
  read). **R269 (2026-09-08)** ruled its three picks: build it, the healing
  law gets the pet clause (`LAW.md`), the concepts packet and #433 close.
  Encore, the Spotlight, the Fanfare counter and the reframe arm retire
  under it, and **`EB-726` took the reframe out of the tree whole**
  (2026-09-16): one Furina arm, `furina-stage`. Batch one is BUILT in both engines (`EB-723`-`EB-725`, #443,
  #469) and **round one is READ**
  (`review/active/furina-stage-round-1-2026-09-08.md`): three seats on one
  seed; turn one was a wager two seats named, all three wanted a second
  performer, and none ever saw the stage, because the blind-play page has
  no renderer for Furina's pets (`EB-735`) and the mixed offer still
  printed the shipped meters (`EB-736`). Rule 3 clarified (`EB-738`), the
  Refill renamed (`EB-739`), all built (#472). **Round two is READ** (packet on PR #473,
  [USER]'s, with one pick): with the stage printed, turn one was a real
  decision about the bar in all three seats, the reserve read as a second
  damage source, and the three read as three at the exit and one at the
  table; the Spend fired without a choice (four of six seats), the shipped
  Fanfare buff still ran under the arm, and the glossary still carried the
  old words. `EB-743`-`EB-748` are BUILT: Spend is a choice on play (E
  default), the event lines name their effect, the glossary is the
  Stage's, the shipped meters are never granted, readers print the live
  number, a refusal names its power. Round three next.
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
- **The Teyvat run frame (R272, 2026-09-14)** — the non-mechanical layer
  reopened beside the kits: events, text, portraits, act theming and locally
  packaged music; enemy intents, boss behaviour, relic and potion mechanics
  stay frozen, as do the measurement windows `Win10` and `Win11` (R213).
  **R273 (2026-09-14)** ruled the nation mapping
  (`review/ruled/teyvat-nation-mapping-2026-09-14.md`): each act has two
  faces, act 1 Mondstadt or Liyue, act 2 Natlan or Inazuma, act 3 Fontaine or
  Sumeru; the Abyss is reserved as the act-4 face (scoping read
  `review/records/teyvat-act4-scoping-2026-09-15.md`); Nod-Krai and Snezhnaya
  are scored as later faces (act tables §7: Nod-Krai on Glory, Snezhnaya on
  the Hive by default). **Built (2026-09-15):** a face is a sibling
  `ActModel` sharing the zone's encounter objects; all six dressings are
  registered behind the `TeyvatFrame` arm, OFF on every calibration deploy;
  122 dressed events (act 1: 38, act 2: 50, act 3: 34; Mondstadt 20, Liyue
  18, Natlan 25, Inazuma 25, Fontaine 17, Sumeru 17, generated by
  `tools/gen_teyvat_events.py` from the faces under
  `dossiers/content/event-faces/`, nothing parked), 38 death lines, one
  every enemy dressed and moving: 149 face-slots on 122 plates (`EB-811`)
  with five shared motion sets picked per row (`EB-816`; a still enemy proven
  to animate, `review/records/teyvat-proofs-11-lane1-2026-09-17.md`) and six
  bosses on bespoke layered rigs, two or three cut parts each (`EB-817`,
  unproven in the running game), the eight Ancients
  dressed per face with Teyvat names, epithets and lines, boons untouched
  (R275, `dossiers/content/ancient-faces.tsv`, art pending), real act plates on all six dressings (30, `media/ACT.tsv`)
  (`operations/act-assets.md`), music packaged from `media/MUSIC.tsv` and
  playing in 27 slots: combat, elite, boss and map per face plus menu, shop, rest (#612)
  (`operations/media.md`). Proven in the running game: act 1 both faces,
  combat backgrounds, rest site, six dressed act-1 events
  (`review/records/teyvat-proofs-4-2026-09-15.md`, `-5-`); and acts 2 and 3
  on all four faces — map header, combat background and real fights, rest
  site and dressed events — reached through the act-skip op
  (`review/records/teyvat-proofs-7-2026-09-16.md`); and on the `0.2.3480`
  deploy the Punch-Off at both speeds, the four unfinished event pages, the
  dressed Slippery Bridge's card name and a dressed-id force
  (`review/records/teyvat-proofs-8a-2026-09-16.md`). Nothing parked;
  the Slippery Bridge price literal and the potions event per arm are open
  rows. Kickoff
  `review/ruled/teyvat-run-frame-2026-09-14.md`.

## Open [USER] pile

[`QUEUE.md`](QUEUE.md) holds the eyes-on rows (Furina's rebuilt board, the
Curtain Call faces, three running-game looks, the end-of-turn docket). The
picks on branches are Furina's identity (PR #443); the older open packets in `review/active/` are the companion
P5a pick, `eb74`'s staged lever and the P2 thresholds. The six blessed
mechanisms are in [`watch-register.md`](watch-register.md), all dormant.
