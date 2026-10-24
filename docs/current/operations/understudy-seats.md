## Understudy, the seats, and blind play

The procedure a seat run needs, and nothing else. When a round runs and how
many seats it takes: `CLAUDE.md` and `operations/stage-gate.md`. Code depth:
`understudy/README.md`, `docs/current/atlas/understudy.md`. The pre-2026-09-23
page (measured histories, live proofs, grader bakeoff):
`git show 2b73880a:docs/current/operations/understudy-seats.md`.

Raw transcripts, seat records and session logs stay on disk (`review/qa/` is
gitignored for new files, `understudy/logs/` always was). The committed result
is one page in `review/records/`; a display defect is one line in `BACKLOG.md`.

### The Balance suite record (one page)

Five base seeds, one seat per lane for the whole run
(`operations/stage-gate.md`). The record is this page and nothing more;
analysis goes in the paper that uses it.

````md
# <Kit> Balance suite <N>, <date>

Build: `<kit>-next` <sha> (<version>+next). Change set under test: <paper path>,
its prediction line quoted: "<the one line, written before the run>".
Seeds, seats and grading as suite <N-1>: A0, one <model> seat per lane for the whole run, normal
fights against the base five's counted runs on the same seeds
(`review/records/base-five-baseline-2026-10-05.md`).

| Seed (base character) | End floor (cause) | Suite N-1 | Base | Act 1 dmg / HP | Act 2 dmg / HP | Act 3 dmg / HP |
|---|---|---|---|---|---|---|
| <seed> (Ironclad) | | | | | | |
| <seed> (Silent) | | | | | | |
| <seed> (Defect) | | | | | | |
| <seed> (Necrobinder) | | | | | | |
| <seed> (Regent) | | | | | | |
| **All** (fights per act) | mean | mean | mean | ratio (n) | ratio (n) | ratio (n) |

Ratios are the kit's median damage a turn and HP lost per fight over the base
five's, normal fights, by act (`tools/telemetry_report.py`; draw windows by
run, not clock time). The bar: runs reach act 3 as the base five's do, and each
ratio within about 15%.

## The prediction, graded

"<the line>": **PREDICTED / MISS / SPLIT**, with the number that grades it.
A SPLIT names the clause that failed.

## Picks

1. **<the call this suite feeds>.** (a) <default>. **Default.** (b) <other>.

Raw transcripts: `review/qa/blindplay/<session>/` (local, gitignored).
````

### Running one blind seat

```sh
# an Opus subagent playing by hand: paste this brief, never rewrite it
python tools/seat.py --opus-brief --lane 1 --character KLEEMOD-KLEE --scratch <dir>
```

`--opus-brief` prints the embark to run first on stderr; `--help` has its
flags (`--max-actions`, `--scratch`, `--record`, `--coop`). `tools/seat.py`
(the `seat` skill) runs the same steps you can run by hand, and its teardown
runs even when the session fails:

```sh
python -m understudy.embark --character klee --lane 1       # bridge, launch, embark
$env:GITS_LANE = '1'                                         # PowerShell; bash: export GITS_LANE=1
python -m understudy.blindplay observe                       # eyeball one live screen
python -m understudy.blindplay session --max-actions 40 --max-wall-s 5400
python -m understudy.embark --teardown --lane 1              # put it all back
```

**A newcomer seat** (2026-10-19) tests whether a kit explains itself: add `--newcomer` to `--opus-brief`. The seat gets the brief's NEWCOMER section (the commands and seat rules, no rule explanations, an exit form), and its lane scripts set `GITS_NEWCOMER=1`, so the page shows only what a player sees (`understudy/blindplay_newcomer.py`: the player's hover tips via the bridge's `?audience=player`, no ledger, forecasts, glossary or page notes, and `--define` answering with the game's own tip or none). The lane needs a bridge built from this tree or later; `observe` warns once on stderr when it is older.

- `embark --ascension N` sets the run's ascension (a mismatch on read-back
  fails the embark), so a base-game control run can match a mod run.
- Every embark unlocks the lane's saves as `unlock all` does (epochs, A10).
  Lane 0 is never touched.
- **A second seat on a lane that already played** (rare: seats are whole-run
  since `review/records/furina-fullrun-round-2026-10-10.md`): `observe
  --brief` defines each word once per lane, so run
  `GITS_LANE=N python -m understudy.blindplay new-seat` first.
- **`REFUSAL STOP` is sticky** for every later seat on the lane; lift it with
  `python -m understudy.blindplay reset-refusals --lane N` (budget untouched).
- `embark --hold` attaches to a game somebody else launched and changes
  nothing. `--teardown` needs `--lane N` or `--stamp S` (lane-less used to
  mean lane 0). It walks the reversibility ledger on disk (the lane's live
  game first, else its newest embark) and refuses another lane's sidecar.

| variable | what it does |
|---|---|
| `GITS_LANE` | the ONLY way the `blindplay` commands find a lane (no flag). Unset it before a deploy. |
| `GITS_LOCAL_*`, `GITS_CODEX_*` | the dormant backends' settings; their module docstrings name them |
| `STS2_MCP_PORT` | a lane's bridge port; set by the lane machinery, never by hand |

### Lanes, and embarking several at once

Five seat lanes, `lane1` to `lane5`, ports 15527 to 15531, each with a
disposable user tree under `%LOCALAPPDATA%\gits-lanes\laneN`
(`instances.SEAT_LANE_COUNT`).

```sh
python -m understudy.embark --lanes 1,2,3,4,5 --character klee --ascension 0 \
    --max-actions 1500 --seeds S1,S2,S3,S4,S5      # lane N gets the Nth seed
python -m understudy.embark --teardown --lanes 1,2,3,4,5   # or --teardown --lane N
```

Each lane embarks in its own process (log: `understudy/logs/embark-<time>-laneN.log`)
and the command prints one row per lane. A failed lane does not stop the
others: tear it down with `--teardown --lane N` and embark it again.
`--characters` takes one name or one per lane. Each seat still sets
`GITS_LANE=N`.

- `--varka-knight pyro|hydro|cryo|electro|roll` (one, or one per lane) forces
  Varka's starting Knight (Amber, Barbara, Kaeya, Lisa); the seed's later
  rolls are unchanged. New runs only; co-op and `--hold` ignore it.
- `--abyss` runs with the Spiral Abyss modifier (solo, `--lanes`, `--coop`);
  the embark fails `abyss_not_honoured` if the run does not read it back.
  `--hold` refuses it.

Traps:

- **Lane 0 is the owner's game** (port 15526, the real `APPDATA`):
  `tools/seat.py` refuses it without `--allow-lane-0`. A lane above 0 is never
  a run of record; if its profile goes wrong, delete
  `%LOCALAPPDATA%\gits-lanes\laneN`.
- **One install, one `mods\klee` for every lane.** `deploy.ps1` and
  `deploy_proto.ps1` refuse while any `SlayTheSpire2` process is up; tear the
  lanes down, never deploy around them.
- **Ask before launching a lane while [USER] is playing** (lanes take the
  controller and the GPU).
- **The bridge (`mods\STS2_MCP`) is shared and no teardown removes it**; a
  bridge with a game running on it is reused, never rewritten. Only
  `deploy_bridge.ps1 -Remove`, by hand, removes it.
- **Kill and frame by pid, never by image name**: a kill by name takes the
  other lane's game. `harness frame` takes the pid off the lane's sidecar.
- Parallel embarks are serialised on the shared install by
  `instances.install_lock()` and launches staggered by
  `instances.LAUNCH_STAGGER_S`; do not launch lanes around the embark.
- Each lane launch reveals obtained epochs and turns `STS2_MCP` and `klee` on
  in the lane's own saves (lane 0's are never written).
- The menu wait scales with the profile's run-history store (180 s + 1 s per
  5 files, capped at 900 s); nothing in the harness touches that store.
- `seed_read_back_crossed` is a harness defect, not a game one.
- The machine stays awake while a session holds a game
  (`understudy/keepawake.py`; `powercfg /requests` shows it).

### Running a co-op round (two seats, one run)

```sh
python -m understudy.embark --coop --lanes 2,3 \
    --characters KLEEMOD-KLEE,KLEEMOD-FURINA --ascension 0    # host first
python tools/seat.py --opus-brief --lane 2 --character KLEEMOD-KLEE --coop
python tools/seat.py --opus-brief --lane 3 --character KLEEMOD-FURINA --coop
# seat A: GITS_LANE=2 ...blindplay observe / act "..."; seat B: GITS_LANE=3
python -m understudy.embark --teardown --coop --lanes 2,3     # client first
```

- The transport is the game's `--fastmp` (ENet on localhost), so two lanes on
  one Steam account play together. The host alone takes `--ascension` and
  `--seed`.
- One UDP port per pair, derived from the host lane (lane 1: 33771, lane N:
  33770 + N), so two pairs can run (`--lanes 1,2` and `--lanes 3,4`, each torn
  down by its own `--teardown --coop --lanes`). Not yet proven live with two
  pairs up.
- **Never resume a fastmp save**: every co-op embark starts a fresh run.
- `--keep-bridge` launches without refreshing `mods\STS2_MCP` (from a worktree
  carrying a bridge edit).
- The page adds *The other player* and *Choices so far*; a WAITING page offers
  `wait` and does not count toward the stall stop. A card aimed at the partner
  is played `on "<their character>"`.
- **A co-op run is not a run of record.**

### Blindness rules (the coordinator's side)

- **The seat reads no repo file** and runs only `observe` and `act`.
  `harness state`, `scenario`, `staged_turn` and `soak` print the pilot's
  recommendation; one look ends the round's value. The brief
  (`operations/seat-brief.md`) tells the seat this: paste it verbatim.
- **The seat's model family may not be the author's** (R217 C). Claude
  authors, GPT grades and reviews; `authored_by:` on every prototype row names
  the families that wrote it, and `seat grade` / `seat review` refuse a turn
  whose row lists the seat's own family. `local` can be named but never
  authors a row.
- A seat that supplies card text, a number, a mode or a rewritten row has
  that remedy **discarded**; Claude re-derives from the clause the seat named.
- Every seat record ends with a non-blindness declaration ("Repo files read:
  none." if true).
- Nothing a seat produces is balance evidence (Guardrail-7, R217 G). It is
  feedback on legibility and decisions.

### Blind play: the page

```sh
python -m understudy.blindplay observe [--raw-file <state.json>]
python -m understudy.blindplay act "<command>" [--raw-file <f>] [--dry-run]
python -m understudy.blindplay session [--max-actions N] [--max-wall-s S]
```

The command grammar is the brief's (`operations/seat-brief.md`). An unknown or
hazardous screen renders as `TOOL-BLOCKED: <state_type>` and is never driven.
Keyword definitions are `ArmKeywordTips.cs`'s words, and
`understudy/blindplay_notes.py` must say the same. The combat page's enemy
lines come from `understudy/blindplay_enemies.py` (a test fails on an act 1-3
elite or boss with no entry) and `understudy/blindplay_moves.py`.

`session` drives one run with budgets on actions, wall time and consecutive
refusals. Its record is `review/qa/blindplay/<session>/record.md` (gitignored),
with the identity block read off disk (`mods\klee\manifest.json`,
`release_info.json`) and `wire.json` beside it.

**Asked of `STS2_MCP`: a resolving-part marker on a multi-part intent
(`EB-461`).** `BuildEnemyState` sends one entry per intent part and nothing
that says which part resolves, so the page prints every part neutrally ("icon
shows 8, one part of this move"). `STS2_MCP` is vendored
(`vendor/STS2_MCP/`): this is a request upstream, not a local edit.

### Dormant seats

The Codex and local-model backends (`--backend codex|local` on `tools/seat.py`
and `blindplay session`) and staged turns are dormant since 2026-09-28; the
code stays because the live path imports it.

### Attended drivers (scenarios, forced events, act skips, grants)

```sh
python -m understudy.scenario check
python -m understudy.scenario run understudy/scenarios/<s>.yaml --why "..."
python -m understudy.force_event --list
python -m understudy.force_event <EVENT_ID> --why "..."
python -m understudy.skip_act --list
python -m understudy.skip_act --why "..."
python -c "from understudy import bridge; print(bridge.give_relic('THE_BOOT', why='...'))"
python -c "from understudy import bridge; print(bridge.fight('KAISER_CRAB_BOSS', why='...'))"   # off a map or reward screen
```

All need the bridge and an open run, all require `--why`, and every response
carries `bridge.GRANT_GUARDRAIL`: **nothing measured after one is comparable
to anything.** `skip_act` is not rng-neutral. The first `?` after a skip is
the act's Ancient, not the forced event. `CurrentActIndex` is zero-based.

### Fight telemetry and the Balance report

Every fight writes one JSON line (`PlayTelemetry.cs`; keys in
`understudy/README.md`, "Telemetry schema") to
`%APPDATA%/SlayTheSpire2/gits_telemetry/` or the lane's own tree. The Balance
gate (`stage-gate.md`) reads them:

```sh
python tools/telemetry_report.py --character Klee --character base5
python tools/telemetry_report.py --character Klee --since 2026-10-02 --baseline-since 2000-01-01
python tools/telemetry_report.py --character Klee --seed <run seed> --cards-merge-upgrades --json
```

Flags are in `--help`. Records older than 2026-10-02 lack Block and the wider
damage credit and are left out of those medians, so window a kit to its
current build.

**Card offers** are logged by the bridge, not the fight telemetry: every
`blindplay act` answering a card reward, shop, out-of-fight chooser or bundle
appends a row to `understudy/logs/offers/card-offers-laneN.jsonl`
(gitignored). Read it with `python tools/offer_report.py --character Varka
--element pyro`. The log is the running checkout's, so pass a second
worktree's folder with `--dir`.

### Also

`KleeTests` runs the shipped `klee.dll` against the real game assemblies,
headless (`klee-mod/KleeTests/README.md`). One round, one branch: never
continue a round on a branch already handed over for merge.
