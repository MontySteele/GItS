## Understudy, the seats, and blind play

The procedure a seat run needs, and nothing else. This page was cut from
1,271 lines on 2026-09-23; the full text (the measured histories, the
two-instance live proofs and their defects, the local grader bakeoff, the
funnel's stopping-rule and requalification detail) is at

```
git show 2b73880a:docs/current/operations/understudy-seats.md
```

Depth on the code: `understudy/README.md`, `docs/current/atlas/understudy.md`.

### When a round runs, and what it leaves behind

A seat round runs **only when a rule changes or a new batch of cards lands**,
with **two seats** by default (`operations/stage-gate.md`). Raw transcripts,
seat records and session logs stay on disk: `review/qa/` is gitignored for new
files (the files already tracked there stay tracked), and `understudy/logs/`
always was. The committed result is one page in `review/records/`: what played
well, what did not, what to change. A display defect becomes one line in
`BACKLOG.md`.

### The Balance suite record (one page)

A Balance suite is five base seeds x three acts, one seat per act
(`operations/stage-gate.md`). Its record is this page and nothing more;
analysis goes in the paper that uses it, and screen defects go to
`BACKLOG.md` as one line each.

````md
# <Kit> Balance suite <N>, <date>

Build: `<kit>-next` <sha> (<version>+next). Change set under test: <paper path>,
its prediction line quoted: "<the one line, written before the run>".
Seeds, seats and grading as suite <N-1>: A0, one <model> seat per act, normal
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

# a backend seat (codex, or the local model), embark to teardown
python tools/seat.py --lane 1 --character KLEEMOD-KLEE --backend codex
python tools/seat.py --lane 2 --character KLEEMOD-KOKOMI --backend local \
    --max-actions 70 --max-wall-s 5400 --dry-run      # print the 3 commands
```

`--opus-brief` prints the embark to run first on stderr, with an explicit
`--max-actions` (120 by default, `--max-actions N` to change it), and with
`--scratch` names the seat's own notes file, `<scratch>/seat-lane<N>/notes.md`,
on the brief's lane line, and writes the lane scripts there: `o` (observe
--brief) and `a` (act --brief --observe, which acts and then prints the new
page, so a seat needs no `o` after every move). The map page prints the run seed (from the lane's
embark sidecar) and the ascension (from the wire).

`tools/seat.py` (the `seat` skill) runs the same three steps you can run by
hand, and its teardown runs even when the session fails:

```sh
python -m understudy.embark --character klee --lane 1       # bridge, launch, embark
$env:GITS_LANE = '1'                                         # PowerShell; bash: export GITS_LANE=1
python -m understudy.blindplay observe                       # eyeball one live screen
python -m understudy.blindplay session --max-actions 40 --max-wall-s 5400
python -m understudy.embark --teardown --lane 1              # put it all back
```

`embark --ascension N` starts the run at ascension N instead of the character's
saved last-used level, so a base-game control run can match a mod run (set on
the select screen after the pick; the sidecar records `ascension_requested`
beside the read-back `ascension`, and a mismatch fails the embark).

Every embark unlocks the lane's saves the way the game's `unlock all` does:
every epoch revealed (the character epochs add cards and relics to the pools)
and ascensions up to 10 (`instances.unlock_lane_progress`). Lane 0 is never
touched.

**A fresh seat on a lane that already played** (a per-act handoff: the act 1
seat stops and a new seat takes act 2 on the same run). `observe --brief`
defines each word once per LANE, so the new seat would never see the words the
last one met. Before starting each seat after the first on a lane, the
coordinator runs:

```sh
GITS_LANE=1 python -m understudy.blindplay new-seat   # forgets the lane's seen words; budget untouched
```

A seat can also ask for one word at any time: `observe --define "<Word>"`
prints the screen's definition, or the glossary's own row marked
"(not on this screen)".

Environment:

| variable | what it does |
|---|---|
| `GITS_LANE` | the ONLY way the design-blind `blindplay` commands find a lane (they take no flag). Unset it before a deploy. |
| `GITS_LOCAL_MODEL_URL` | the local model endpoint, e.g. `http://localhost:8010/v1`; required, no default |
| `GITS_LOCAL_MODEL_CTX` | the context size; a prompt that does not fit is refused, never truncated |
| `GITS_LOCAL_PLAY_TOKENS` | the local whole-run answer ceiling; use **12000** (the 4096 default truncates and the round dies with the game up) |
| `GITS_LOCAL_MODEL_FORM_TOKENS`, `GITS_LOCAL_MODEL_REVIEW_TOKENS` | the local grader's two answer ceilings (default 8192) |
| `GITS_CODEX_PRIMARY_STOP`, `GITS_CODEX_WEEKLY_STOP` | override the Codex usage stops (85% of the five-hour window, 50% of the week) for one run |
| `STS2_MCP_PORT` | the bridge port a lane's game listens on; set by the lane machinery, not by hand |

**embark** owns deploy, launch, readiness, embark and speed; it reads the run
seed back off the wire and stops with the game up. `--hold` attaches to a game
somebody else launched and changes nothing. `--teardown` rebuilds the session
from the reversibility ledger on disk and walks its undo steps (newest
embark first, or `--stamp` by name); it picks that lane's newest sidecar and
refuses another lane's.

### Five lanes, and embarking several at once

There are **five seat lanes**, `lane1` to `lane5` on ports 15527 to 15531,
each with its own disposable user tree under `%LOCALAPPDATA%\gits-lanes\laneN`.
Lane 0 (port 15526) is the owner's own game and profile and is never embarked
by a round. The count is one constant, `instances.SEAT_LANE_COUNT`; the
registry, the ports and every "known lanes" message derive from it.

Embark several lanes in one command, all at once:

```sh
python -m understudy.embark --lanes 1,2,3,4,5 --character klee --ascension 0 \
    --max-actions 1500 --seeds S1,S2,S3,S4,S5      # lane N gets the Nth seed
python -m understudy.embark --teardown --lanes 1,2,3,4,5   # or --teardown --lane N
```

Each lane runs the ordinary single-lane embark in its own process, with its
output in `understudy/logs/embark-<time>-laneN.log`. The command waits for all
of them and prints one row per lane: port, UP or FAILED, the character and the
seed read back off the wire, and the log. A failed lane does not stop the
others; tear that lane down with `--teardown --lane N` and embark it again.
`--characters` takes one name for all lanes or one per lane; `--seeds` one
per lane or none (the game rolls them). Each seat still sets `GITS_LANE=N`.

What makes it safe (the 2026-09-25 round's second lane never came up when two
lanes were embarked at the same moment):

- **The shared install is taken one lane at a time.** `steam_appid.txt`,
  `mods\STS2_MCP` and the launch all run inside `instances.install_lock()`, a
  machine-wide OS file lock (`%LOCALAPPDATA%\gits-lanes\install.lock`, freed
  by the OS if its holder dies). Unlocked, two embarks both saw no game up,
  both ran `deploy_bridge.ps1`, and one's `Remove-Item mods\STS2_MCP` landed
  while the other's game was booting: that game came up with no bridge and its
  port refused every call. Inside the lock, the second lane sees the first
  lane's game up and reuses the bridge. The menu wait is outside the lock, so
  the boots overlap.
- **Launches are staggered** by at least 8 s (`instances.LAUNCH_STAGGER_S`,
  recorded in `last-launch.json` beside the lock), so Steam initialises one
  game at a time. A lone embark never waits.
- **Each embark claims its own stamp** (`embark.reserve_stamp`, an exclusive
  create of its sidecar). The stamp is a clock reading to the second and names
  the sidecar and the reversibility ledger; two lanes in the same second used
  to share both, and the first lane's launch row (its pid) was lost.

- **A lane's mod list has the bridge on.** A fresh lane copies lane 0's
  `settings.save`, and lane 0's had `STS2_MCP` switched off on 2026-10-05, so
  the new lane 5 booted without the bridge ("Skipping loading mod STS2_MCP" in
  its `godot.log`). Every lane embark now turns `STS2_MCP` and `klee` on in the
  lane's own copy (`instances.enable_lane_mods`); lane 0's is never written.

What stays shared and is not locked: `mods\klee` (one deployed build for every
lane; deploy only with every lane down) and the bridge's FastMode capture
file `mods\STS2_MCP\GitsSpeed.original.conf` (every lane's prefs are seeded
from lane 0's, so the captured original is the same value).

### Running a co-op round (two seats, one run)

Two blind seats share ONE co-op run, each driving one player through the same
`blindplay observe` / `act` page:

```sh
python -m understudy.embark --coop --lanes 2,3 \
    --characters KLEEMOD-KLEE,KLEEMOD-FURINA --ascension 0    # host first
python tools/seat.py --opus-brief --lane 2 --character KLEEMOD-KLEE --coop
python tools/seat.py --opus-brief --lane 3 --character KLEEMOD-FURINA --coop
# seat A: GITS_LANE=2 python -m understudy.blindplay observe / act "..."
# seat B: GITS_LANE=3 python -m understudy.blindplay observe / act "..."
python -m understudy.embark --teardown --coop --lanes 2,3     # client first
```

- **The transport is the game's own `--fastmp`**: ENet on localhost instead of
  Steam lobbies, so two lanes on one Steam account can play together. The
  host launches with `--fastmp host_standard` (straight to the multiplayer
  character select) and the client with `--fastmp join --clientId 1000`; the
  embark waits for the host's lobby before launching the client, whose join
  gives up after 10 s. Both pick, the host alone takes `--ascension` (the
  lobby otherwise uses the host's saved level) and `--seed` if given, both
  confirm, and the embark waits until both bridges serve the run.
- **One UDP port per pair, so several pairs per machine.** The game hosts and
  dials a literal 33771; the bridge (`vendor/STS2_MCP/gits/GitsFastMpPort.cs`
  and `GitsFastMpPortPatch.cs`) moves it per process when the game is launched
  with `--gitsFastmpPort N`. The embark derives the port from the HOST lane
  (lane 1 hosts on 33771 with no extra argument, lane N on 33770 + N), passes
  it to both games, refuses while that port is taken, and refuses a pair whose
  lobby does not read back that port (`lobby.fastmp_port`; an installed bridge
  older than the patch serves none, so only a lane-1 pair runs on it). Two
  pairs at once: `--lanes 1,2` and `--lanes 3,4`, each torn down by its own
  `--teardown --coop --lanes`. Not yet proven live with two pairs up
  (2026-10-08).
- **Never resume a fastmp save.** `--fastmp load` looks the save up under the
  Steam id while the save names its players 1 and 1000; every co-op embark
  starts a fresh run.
- **Epochs do not block it.** `--fastmp` navigates past the main menu, so a
  lane whose menu is blocked by unrevealed epochs still embarks (lanes 2 and 3
  held two each on 2026-09-27).
- **What is written:** one sidecar per lane (`embark-<stamp>-laneN.json`, with
  a `coop` block; the lane readers and a single-lane `--teardown --lane N`
  read it as usual) and `coop-<stamp>-<host lane>.json` with both lanes, the
  port, the seed (read off the host's `current_run_mp.save`) and both
  ascension read-backs.
  `--keep-bridge` launches without refreshing `mods\STS2_MCP` (use it from a
  worktree carrying a bridge edit).
- **The page.** Once the run is up, `/api/v1/singleplayer` answers 409 and
  `bridge` follows it to `/api/v1/multiplayer`. The page adds *The other
  player* (HP, Block, whether their turn is ended, their pets) and *Choices so
  far* (map, shared event and chest votes). After `end turn`, or a vote the
  partner has not matched, the page opens with **WAITING** and offers `wait`
  (`act "wait"`, 60 s by default, `wait 120`, at most 300), which returns as
  soon as the other player moves anything on the wire. A waiting page does not
  count toward `session`'s stall stop. A card aimed at another player (the
  base game's ally target) is played `on "<their character>"`.
- **A co-op run is not a run of record**, for the lane reason and because
  nothing single-player is comparable to it.

### Blindness rules

- **Read no repo file.** A seat sees only what the bridge prints: `observe`
  and `act "<command>"`, nothing else. `harness state`, `scenario`,
  `staged_turn` and `soak` print the pilot's recommendation beside the screen,
  and one look ends the round's value. The Opus brief
  (`operations/seat-brief.md`) states these rules to the seat; paste it
  verbatim.
- **The seat's model family may not be the author's** (R217 C). Claude
  authors, GPT grades and reviews; `authored_by:` on every prototype row
  records the families that wrote it, and `seat grade` / `seat review` refuse
  a turn whose row lists the seat's own family. The `local` family can be
  named but never authors a row.
- A seat that supplies card text, a number, a mode or a rewritten row has
  that remedy **discarded**; Claude re-derives from the clause the seat named.
- Every seat record ends with a non-blindness declaration: every command
  outside the two allowed ones, and "Repo files read: none." if true.
- Nothing a seat produces is balance evidence or validation (Guardrail-7, R217
  G). It is feedback on legibility and decisions.

### Lanes (several games on one install)

- **Lane 0 is the owner's own game** on port **15526** and the machine's own
  `APPDATA`; `tools/seat.py` refuses it without `--allow-lane-0`. Lane N gets
  port 15526+N and `APPDATA=%LOCALAPPDATA%\gits-lanes\laneN`, for N = 1
  to 5.
- **A lane above 0 is never a run of record.** Its profile is disposable
  (seeded once from lane 0's `settings.save`, never read back); if it goes
  wrong, delete `%LOCALAPPDATA%\gits-lanes\laneN`.
- **Unrevealed epochs are revealed at launch, on lanes only.** A base-game run
  that unlocks a timeline epoch parks the menu at Settings and Quit
  (`manual_epoch_reveal_required`). Every lane launch (`embark`, `soak`,
  `seat`) first sets any `obtained` epoch in the lane's own `progress.save` to
  `revealed` and prints the ids (`instances.reveal_pending_epochs`). Lane 0
  and anything under the real `%APPDATA%` are never written.
- **One install means one deployed `mods\klee` for every lane.**
  `deploy.ps1` and `deploy_proto.ps1` refuse while ANY `SlayTheSpire2`
  process is up; tear the
  lane down rather than deploying around it. Ask before launching a lane while
  [USER] is playing (lanes take the controller and the GPU).
- **The bridge (`mods\STS2_MCP`) is shared and no teardown removes it.**
  `tools/deploy_round.py` installs it after `deploy.ps1` (and
  `deploy_proto.ps1` as its last step), so the owner's Steam game
  carries it on 15526 and an agent's lane takes 15527. A bridge already
  installed with a game running on it is reused, never rewritten. Only
  `deploy_bridge.ps1 -Remove` removes it, by hand.
- **Kill and frame by pid, never by image name.** A kill by name takes the
  other lane's game; `harness frame` takes the pid off the lane's embark
  sidecar and refuses when the lane names no live process.
- The machine stays awake while a session holds a game (`understudy/keepawake.py`);
  `powercfg /requests` in an elevated shell shows the harness's `python.exe`.
- The menu wait scales with the profile's run-history store (180 s + 1 s per
  5 files, capped at 900 s); nothing in the harness touches that store.
- A lane's seed read-back is checked against the lane's own save tree
  (`seed_read_back_crossed` is a harness defect, not a game one).

### Blind play: the page and the grammar

```sh
python -m understudy.blindplay observe [--raw-file <state.json>]
python -m understudy.blindplay act "<command>" [--raw-file <f>] [--dry-run] [--observe]
python -m understudy.blindplay session [--backend codex|local] [--max-actions N] [--max-wall-s S]
```

`observe` renders whichever screen is up as printed faces only; an unknown or
hazardous screen renders as `TOOL-BLOCKED: <state_type>` and is never driven.
`act` resolves one command by printed names: `play "<title>" [on "<enemy>"]`,
`end turn`, `choose "<name>"`, `skip`, `go "<node>"`, `buy "<item>"`, `rest`,
`upgrade`, `remove`, `use potion "<title>"`, `confirm`, `proceed`. Two things
printing one name are numbered (`Slug (1)`, `Slug (2)`); `(upgraded)` /
`(not upgraded)` separates copies. Once a card-selection preview is open the
pick is taken (`skip` cancels it); a transform's result is not printed because
the game has not chosen it. The live arm keywords get one definition each per
screen, in `ArmKeywordTips.cs`'s words (`understudy/blindplay_notes.py` must
say the same). `act --observe` prints the new page after a sent act (and
the unchanged page after a refusal), from the same process, so a move is one
call; never on `--dry-run` or `--raw-file`.

Three combat-page lines (2026-10-05), none of them a recommended play:
**What these enemies do (base game)** prints one line per kind of enemy,
from `understudy/blindplay_enemies.py` (curated from
`docs/current/dossiers/enemies/`; a test fails on an act 1-3 elite or boss
body with no entry), on the first page of each fight, once per fight (the
fight's own memory, which `new-seat` also clears; `--brief` never trims it;
plain `observe` prints it on every round-1 page; `observe --define
"<enemy>"` prints it again); **Incoming this turn** sums the attack
telegraphs against your Block, naming as unknown a part whose figure may not
count Weak or Vulnerable (on Furina's stage too, where guests cannot be
targeted; not in co-op, where a telegraph names no target); **Since last
page** names what the mod's `ResolutionLedger` filed that the after-state
does not show (a card drawn by an effect, a debuff Artifact negated, a
one-off enemy trigger, a stolen card given back, an attack that Shattered
Frozen, and on the next screen Furina's drained HP returned), only what is
new since the lane's last page. A debuff telegraph also names what the move
does (`understudy/blindplay_moves.py`, read off the base game by the move id
the bridge sends).

`session` drives one run: one command per screen, fight and run records at the
ends, budgets on actions, wall time and consecutive refusals. The seat's
record is `review/qa/blindplay/<session>/record.md` (local, gitignored) with
the identity block read off disk (`mods\klee\manifest.json`,
`release_info.json`), and beside it `wire.json`, the per-turn wire snapshot
the tester never sees. `--backend local` runs the same session over the local
model (same prompt, same page, same records), keeps one thread per act and
hands over at each act boundary; it is an option, not a seat any round rests
on.

**Asked of `STS2_MCP`: a resolving-part marker on a multi-part intent
(`EB-461`).** `BuildEnemyState` sends one entry per intent part (`type`,
`label`, `title`, `description`) and nothing that says which part resolves.
So the page prints every part neutrally ("icon shows 8, one
part of this move") and makes no claim about which lands; seats were hurt by
both guesses (r14 read a bare number as a promise, r15 read a hedge as a
warning). One key per intent on `BuildEnemyState` would close it. `STS2_MCP`
is vendored (`vendor/STS2_MCP/`, `PROVENANCE.md`): this is a request upstream,
not a local edit.

### Dormant seats: Codex, the local model, staged turns

No seat since 2026-09-28 has used these three, and their code stays because the
live path still imports it (`blindplay_session` reaches `seat`, which reaches
`staged_turn` and `codex_usage`; the `face-defects` lint reaches `scenario`).
The Codex seat (`python -m understudy.seat check|grade|review`, one-time
`npm install -g @openai/codex` and `codex login`) grades a staged turn or reads a
proposal as the doctrine or pair seat, refusing at 85% of the five-hour window
or 50% of the week. The local model (`understudy.local_model`, `local_seat`,
`local_tester`, served by `serve.ps1` on port 8010) gives subjective readings
only. Staged turns (`python -m understudy.staged_turn check|stage|grade|execute|ledger`)
set one board and write a blind `packet.md` for a grader. Each module's
docstring is the manual; the full text of this section is in git at
`bf073df4:docs/current/operations/understudy-seats.md`, lines 315-377.

### Attended drivers (scenarios, forced events, act skips, grants)

```sh
python -m understudy.scenario check
python -m understudy.scenario run understudy/scenarios/<s>.yaml --why "..."
python -m understudy.force_event --list
python -m understudy.force_event <EVENT_ID> --why "..."
python -m understudy.skip_act --list
python -m understudy.skip_act --why "..."
python -c "from understudy import bridge; print(bridge.give_relic('THE_BOOT', why='...'))"
```

All need the bridge deployed and a run open, all require `--why`, and every
response carries `bridge.GRANT_GUARDRAIL`: **nothing measured after one is
comparable to anything.** `skip_act` is the one that is not rng-neutral. The
first `?` after a skip is the act's Ancient, not the forced event; answer it
and walk to the next `?`. A dressed Teyvat event id is translated to its base
id and the driver prints that it did. `give_relic`, `give_potion` and
`give_gold` use the game's own commands. `CurrentActIndex` is zero-based.

### Fight telemetry and the Balance report

Every fight on every lane, and every fight you play, writes one JSON line
(`PlayTelemetry.cs`; keys in `understudy/README.md`, "Telemetry schema") to
`%APPDATA%/SlayTheSpire2/gits_telemetry/` or the lane's
`%LOCALAPPDATA%/gits-lanes/laneN/SlayTheSpire2/gits_telemetry/`. The Balance
gate (`stage-gate.md`) is read off them:

```sh
python tools/telemetry_report.py --character Klee --character base5
python tools/telemetry_report.py --character Klee --since 2026-10-02 --baseline-since 2000-01-01
python tools/telemetry_report.py --character Klee --seed <run seed> --cards-merge-upgrades --json
```

It prints medians by group x act x kind (damage a turn, HP lost % of max,
turns, Block a turn, losses), each group's normal-fight ratio to the base five
by act (the bar is within about 15%), and per-card plays and damage by act.
Solo fights only unless `--no-solo`; `--feed bot|human`; `--since/--until` are
local ISO times on `ts`; `--seed` matches the record's `run_id`. Records older
than 2026-10-02 lack Block and the wider damage credit and are left out of
those medians, not counted as zero, so window a kit to its current build.

**Card offers.** Fight telemetry logs plays, not offers. The bridge does:
every `blindplay act` that answers a card reward (`choose`, `skip`), a shop
(card shelves and prices, `buy` or anything else sent there), an out-of-fight
card chooser or a bundle appends one row to
`understudy/logs/offers/card-offers-laneN.jsonl` (gitignored) with the lane,
embark stamp, seed, character, act, floor, the room the reward came from, the
cards shown (upgrade flag, rarity, wire id) and what was taken
(`understudy/offer_log.py`). A reward screen left with its card reward never
opened is a row with no cards. Deck screens (remove, upgrade, transform) and
in-fight choosers are not offers and are not logged. Read it with
`python tools/offer_report.py --character Varka --element pyro` (or
`telemetry_report.py --offers ...`): per card, offered, taken, take rate and
the reward / shop / event split, and with a filter (`--element`, `--rarity`,
`--type`, `--tag`, `--card`) the character's sheet rows that match and were
never offered. The log is the running checkout's, so a seat run from a second
worktree writes there; pass each folder with `--dir`.

### Also

`KleeTests` runs the shipped `klee.dll` against the real game assemblies,
headless; `klee-mod/KleeTests/README.md`. Machine paths come from
`klee-mod/local.props` / `Directory.Build.props`. One round, one branch: never
continue a round on a branch already handed over for merge.
