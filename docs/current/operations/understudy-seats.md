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

### Running one blind seat

```sh
# an Opus subagent playing by hand: paste this brief, never rewrite it
python tools/seat.py --opus-brief --lane 1 --character KLEEMOD-KLEE

# a backend seat (codex, or the local model), embark to teardown
python tools/seat.py --lane 1 --character KLEEMOD-KLEE --backend codex
python tools/seat.py --lane 2 --character KLEEMOD-KOKOMI --backend local \
    --max-actions 70 --max-wall-s 5400 --dry-run      # print the 3 commands
```

`tools/seat.py` (the `seat` skill) runs the same three steps you can run by
hand, and its teardown runs even when the session fails:

```sh
python -m understudy.embark --character klee --lane 1       # bridge, launch, embark
$env:GITS_LANE = '1'                                         # PowerShell; bash: export GITS_LANE=1
python -m understudy.blindplay observe                       # eyeball one live screen
python -m understudy.blindplay session --max-actions 40 --max-wall-s 5400
python -m understudy.embark --teardown --lane 1              # put it all back
```

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
  port 15526+N and `APPDATA=%LOCALAPPDATA%\gits-lanes\laneN`.
- **A lane above 0 is never a run of record.** Its profile is disposable
  (seeded once from lane 0's `settings.save`, never read back); if it goes
  wrong, delete `%LOCALAPPDATA%\gits-lanes\laneN`.
- **One install means one deployed `mods\klee` for every lane.**
  `deploy_proto.ps1` refuses while ANY `SlayTheSpire2` process is up; tear the
  lane down rather than deploying around it. Ask before launching a lane while
  [USER] is playing (lanes take the controller and the GPU).
- **The bridge (`mods\STS2_MCP`) is shared and no teardown removes it.**
  `deploy_proto.ps1` installs it as its last step, so the owner's Steam game
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
python -m understudy.blindplay act "<command>" [--raw-file <f>] [--dry-run]
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
say the same).

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
So the page prints every part neutrally ("the number on its icon is 8, one
part of this move") and makes no claim about which lands; seats were hurt by
both guesses (r14 read a bare number as a promise, r15 read a hedge as a
warning). One key per intent on `BuildEnemyState` would close it. `STS2_MCP`
is vendored (`vendor/STS2_MCP/`, `PROVENANCE.md`): this is a request upstream,
not a local edit.

### The Codex seat

One-time, [USER]'s to do: `npm install -g @openai/codex`, then `codex login`.

```sh
python -m understudy.seat check                          # path, version, login
python -m understudy.seat grade <turn-id> [--model M] [--grader-id ID] [--dry-run]
python -m understudy.seat review <prompt-file> --role doctrine [--out F]
python -m understudy.seat review <prompt-file> --role pair     [--out F]
python -m understudy.codex_usage                          # the five-hour and weekly windows
```

`grade` runs one fresh sandboxed Codex turn from an empty scratch directory
outside the repo, proves blindness from the transcript, and hands the reply to
`staged_turn grade`. Both roles refuse at 85% of the five-hour window or 50%
of the week. GPT is the scarce budget: about three Codex calls per graded
turn. Sessions land in `understudy/logs/seat/` (gitignored).

**Doctrine seat protocol.** `review --role doctrine` reads a proposal against
the character's brief before anything is built and answers FOLLOWS or
REQUIRES_MODIFICATION per arm, naming the CLAUSE and the COMPARISON it rests
on (the row or base-game card it read the arm against, both cards' numbers,
the turn it matters on) or a counterexample board; a verdict without its
comparison is INCOMPLETE. `--role pair` reads a round after it runs and ends
each arm with NOT PLAYABLE / PLAYABLE / ESCALATE. In both roles a remedy the
seat volunteers is DISCARDED. A charter prompt quotes reference rows pasted
from the sheet, never from memory.

### The local model (Qwen on `llama-server`, port 8010)

```sh
python -m understudy.local_model --probe                  # models + one prompt
python -m understudy.local_seat grade <turn-id> [--dry-run]
python -m understudy.local_tester read <turn-id> [--dry-run]
python -m understudy.local_tester round <t01> <t02> ... --plan-only
python tools/local_model_sanity.py --dry-run
```

Launch the server with `serve.ps1` (`-Parallel`, default 2); the standing
control for runaway thinking is the server's `--reasoning-budget 4096`. One
request per slot;
`--read-workers N` needs a server with N slots and refuses otherwise. A local
reading is subjective feedback: not validation, not balance evidence, and not
the doctrine seat. Sessions land in `understudy/logs/local-seat/`
(gitignored).

### Staged turns (the single-turn funnel)

```sh
python -m understudy.staged_turn check   understudy/turns/<t>.yaml           # no game
python -m understudy.staged_turn stage   understudy/turns/<t>.yaml --why "..."
python -m understudy.staged_turn grade   <turn-id> <form.json>
python -m understudy.staged_turn execute <turn-id> <form.json> --why "..."
python -m understudy.staged_turn ledger
```

`stage` sets the board and writes a blind `packet.md`; hand it and
`understudy/qa_grader_prompt.md` to a fresh agent that did not design the
cards. `grade` applies the falsifiers and refuses a turn by name; `execute`
replays a graded line live (defect diagnostics only). A preflight refuses a
card listed in `understudy/face_defects.py` (each entry names its BACKLOG
item; `lint_face_defects` fails an entry whose item is gone).

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

### Also

`KleeTests` runs the shipped `klee.dll` against the real game assemblies,
headless; `klee-mod/KleeTests/README.md`. Machine paths come from
`klee-mod/local.props` / `Directory.Build.props`. One round, one branch: never
continue a round on a branch already handed over for merge.
