## Understudy, the seats, and blind play

### Understudy — targeted scenarios (attended only)

```
python -m understudy.scenario check                            # parse only, no game
python -m understudy.scenario run understudy/scenarios/spark-gate-refusal.yaml \
    --why "EB-142: does the Spark gate show as unplayable"
```

Needs the bridge DEPLOYED (`klee-mod\build\deploy_bridge.ps1`, no `-BuildOnly`),
`steam_appid.txt` in the game root, Steam running. Setup and teardown are the
soak's, via `soak.run_scripted`; the scenario itself starts at the first fight.

`--why` is required and is logged on every row, and every row also carries
`bridge.GRANT_GUARDRAIL`: a scenario grants a card and writes a board through
`/api/v1/gits/debug_state`, so **nothing measured on one is comparable to any
soak, any run, or any other scenario**. Guardrail-7 and the no-fun rule are
unchanged — it asserts numbers (HP, Block, power stacks, resource amounts,
prompts, `can_play`, `unplayable_reason`, printed text) and a failed assert is a
defect, never a design finding. It is deliberately unreachable from `soak.py`;
`tier0/tests/test_understudy_scenario.py` pins that. Depth:
`understudy/README.md` and `docs/current/atlas/understudy.md`.

### Understudy — staged turns and the blind QA funnel (`EB-149`, R213 step 2)

```
python -m understudy.staged_turn check     understudy/turns/<t>.yaml   # no game
python -m understudy.staged_turn closeness understudy/turns/<t>.yaml [--observed]
python -m understudy.staged_turn stage     understudy/turns/<t>.yaml --why "..." [--seed S]
python -m understudy.staged_turn grade     <turn-id> <form.json>
python -m understudy.staged_turn execute   <turn-id> <form.json> --why "..."     [--answer "<prompt>=<printed choice>"]
python -m understudy.staged_turn ledger
```

The protocol, in order. A turn declaring `exact_hand: true` (`EB-165`) opens
its staging with the bridge's `clear_hand` op, so the packet shows the declared
hand and nothing the game dealt on top of it; the cards go to the bottom of the
draw pile through the pile move underneath discard and exhaust, and `stage`
refuses to write a packet whose live hand is not the declared multiset.
**stage** sets the board through the scenario harness
and writes `review/qa/<turn-id>/packet.md` — printed card faces, HP, Block,
energy, live meters, enemy intents, and nothing else. **Hand that packet and
`understudy/qa_grader_prompt.md` to a FRESH agent** with no repo access, never
the agent that designed the cards. **grade** applies the falsifiers to its
answers: no second line, a fourth answer of *no*, an empty line, a designer
grading itself, a form answered against another packet, or a dominating line —
each refuses the turn BY NAME into `verdict.json`. **execute** replays a graded
line live and writes `execute-<grader>.json`; those numbers are defect
diagnostics under Guardrail-7 and nothing else. **The encounter is generated
from the run seed**, so `stage` records the seed the game used into
`packet.json` (not into the blind `packet.md`) and `execute` embarks with it —
proven byte-identical on a re-stage. `execute` then compares the live enemies
and hand against the packet and refuses `board_mismatch` before any play.
**ledger** rebuilds `review/qa/ledger.tsv`.

**A preflight runs before any launch** (`EB-169`). `understudy/face_defects.py`
registers card ids with an OPEN printed/runtime defect, each naming its
`BACKLOG.md` row; `check` and `stage` refuse `open_face_defect` naming the card
and the id, and `seat grade` re-checks the packet's printed hand. It ships
EMPTY — `EB-164` is closed — and `tools/lint_face_defects.py` on the ci lane
fails an entry whose row has left HEAD, so it can only be emptied.

**A line through a modal prompt replays from the form's own words**
(`EB-170`). A play in `chosen_line` may carry `exhaust: "<printed title>"` (the
Exhaust choice, a `hand_select`) and `choose: "<printed option text>"` (a
*Choose one* mode, a `card_select`); `execute` answers the prompt from them and
otherwise STOPS with `modal_unanswered`, naming the prompt and the offers —
never a heuristic pick. `--answer "<prompt>=<printed choice>"` is the
OPERATOR's answer for a form written before those keys existed whose q1 prose
names the choice unambiguously; it is logged as `source: "operator"`, consumed
at most once, and never overrides an answer the form carries.

**Who grades, since R217 A, as amended 2026-09-01.** [USER] plays **at rule
changes; the seats play the rest.** He fills no calibration forms at any point:
the independent seat's form reads a prototype NOT PLAYABLE or PLAYABLE with
no [USER] involvement, and two seats materially disagreeing ESCALATES. His play
is whole fights on a `+proto` build at the four rule-change milestones
(`CLAUDE.md` §Norms), which the funnel does not grade and does not wait on. So
the ledger's `user` grader row stays empty **by rule**, and the
down-weighting it feeds — a grader whose question two keeps disagreeing with
[USER]'s losing its solo SURVIVES — is **DORMANT**: the pin stays in code and
nothing exercises it. `stage --hold` (attaches to a running game and leaves the
board on screen) is still there and still works, as a way to put a staged board
in front of a person; it is not owed by the protocol.

### Understudy — the independent seat (Codex CLI)

A second vendor's model in the grader's chair, so R213's first guard holds
structurally rather than procedurally: `codex exec` cannot have seen this
repo's design conversation. One-time, and [USER]'s to do — the sign-in is
interactive and there is no API key:

```
npm install -g @openai/codex
codex login                                   # ChatGPT plan sign-in
```

Then:

```
python -m understudy.seat check                          # path, version, login
python -m understudy.seat grade <turn-id> [--model M] [--grader-id ID]
python -m understudy.seat grade <turn-id> --dry-run      # prompt + argv only
python -m understudy.seat review <prompt-file> --role doctrine [--out F]
python -m understudy.seat review <prompt-file> --role pair     [--out F]
```

**grade** builds the prompt from `understudy/qa_grader_prompt.md`, runs one
fresh sandboxed config-less Codex turn from an empty scratch directory
OUTSIDE the repo, and hands the reply to `staged_turn grade`. Blindness is
proven from the TRANSCRIPT — the `--json` stream, codex's session rollout and
stderr, allowlisted at every layer, unknown types refusing — because the
read-only sandbox stops writing, not reading, and the stdout stream does not
show tool-call attempts. A refused seat never reaches `grade`. The wrapper
fills exactly three fields (`grader.id/kind/model`) and the raw reply is kept
beside the filled form. **review** is the other role: not blind, read-only at
the repo root, for a second opinion on a diff.

**The seat reads its own meter before every call (EB-227).**
`python -m understudy.codex_usage` prints one line — the five-hour window and
the weekly window, each with its percentage and reset, and the rollout the
numbers came from. Both `seat grade` and `seat review` probe it before every
`codex exec` and **REFUSE**, in that role's own refusal shape, at or past
`CODEX_PRIMARY_STOP_PERCENT` (85% of the five-hour window) or
`CODEX_WEEKLY_STOP_PERCENT` (50% of the week) — overridable for one run with
`GITS_CODEX_PRIMARY_STOP` / `GITS_CODEX_WEEKLY_STOP`. The percentages are
recorded into the call's own record (`seat.json`, and `<out>.usage.json` for
a review) so a night's sessions say what a call actually costs. **The read is
as-of the last `codex` call**, not as of now: it comes from the rate-limit
line Codex itself wrote into its newest session rollout, nothing here asks
OpenAI anything, and a window whose `resets_at` has passed is counted as 0%
used. A machine with no rollout at all logs and proceeds — a missing file
never blocks a round. This is a floor under the standing budget, not a
replacement for it: the **three Codex calls per graded turn** (R217, and
`M64`'s split above, "Who holds the DECIDING chair") is still the rule, and
is unchanged.

Sessions land in `understudy/logs/seat/`, which is **gitignored** — the
prompt inlines the packet and the rollout carries a third party's system
prompt and raw output. The committed artifact is the form and the verdict
under `review/qa/<turn-id>/`.

**A closed round's per-turn directories leave HEAD (`EB-189`).** On
2026-09-02, 57 of them — 476 files, 51,726 lines of `packet`, `observed`,
`closeness`, `form-*` and `verdict-*` JSON from rounds already graded and
ruled — were removed. What each turn decided stays: `review/qa/ledger.tsv`,
the round's `*-round-summary.json` and its pair-review file, all at the top of
`review/qa/`. The raw bytes are retrieved from git, which is where closed
items live (CLAUDE.md §History retrieval):

```
git fetch --depth=1 origin e85d1309
git show e85d1309:review/qa/<turn-id>/observed.json
```

Forty per-turn directories were **kept** because a test or a lint reads them —
`understudy/qualify.py`'s battery and its regression set, the recorded-combat
fixture `kokomi-slice1-r3-t01/observed.json`, the authorship fixtures and the
`kokomi-slice2-t0*` set — as were `review/qa/blindplay/`, the two-instance
proof and the `kokomi-eb183-*` turns, whose packet is still open.

`closeness` is the one number (R213 F): the gap between the top two lines on
the pilot's own score surface, quotable under R215 B's exception because it
reads the TURN. SURVIVES means **not yet falsified** — nothing here rates a
turn. Depth: `understudy/README.md`.

### Doctrine seat protocol

**`seat review` has TWO jobs and `--role` picks which**, because they have
different output shapes and one text for both is a text that silences one of
them. The **remedy ban below is identical in both** — that half is the rule,
not the shape.

- **`--role doctrine`** (the default, so every existing caller is unchanged) —
  reading a slice proposal against the character charter BEFORE anything is
  built. Answers **FOLLOWS** or **REQUIRES_MODIFICATION** per arm and **names
  the clause**. That is the whole output.
- **`--role pair`** — the PAIR READ, run AFTER a round: shipped half against
  prototype half, with the forms, the falsifier's verdicts and the live
  replays inline. Answers the round's numbered questions per arm and ends each
  with **NOT PLAYABLE / PLAYABLE / ESCALATE**, and the protocol says in the seat's own
  prompt that PLAYABLE is not ship approval, not a balance reading and not
  validation (R217 G).

**Klee round 3 is why the roles are split.** `EB-190` shipped ONE protocol and
prepended it to every review; its two strongest lines — *"It overrides anything
below that conflicts with it"* and *"That is the whole output"* — did exactly
what they say, and round 3's pair read came back as two lines, *"PAIR A:
FOLLOWS"* / *"PAIR B: FOLLOWS"*, with no reading and no verdict. Round 3 was the
first pair read since that door landed. An unknown `--role` RAISES rather than
falling back, because a silent fallback is how a pair read gets the gate's
shape without anyone noticing.

**In both roles** the seat may not supply card text, a number, a mode or a
rewritten row: a remedy it volunteers is **discarded**, and Claude re-derives
from the named clause. Where a number has to be chosen, Claude derives it by
the shipped-face rule (lift the value off a shipped card, never invent a
breakpoint) and the seat only confirms that the derived row FOLLOWS. A pair
read MAY say an arm's BOARD did not ask its question and read it NOT PLAYABLE
for that;
it may not design the replacement board.

The reason is R217 C: independence is by MODEL FAMILY, author against grader. A
seat that writes a row and then grades it has graded its own work, and the
outcome is not evidence. **Klee slice 1 is the case** — the seat authored
Rummage's text and chose Slow Burn's number, then the same family graded and
pair-read both, and those two arms' outcomes were provisional. **They are not
any more:** Klee ROUND 3 (2026-08-29) re-derived both rows Claude-side from the
clause the seat named, set both `authored_by:` back to `[claude]`, re-ran the
two arms on two graders and re-read the pair, and both arms ADVANCE on a clean
independent read (`review/ruled/klee-slice-1-2026-08-29.md` §13). There is no
third family and none is being added; the roles are fixed at two — **Claude
authors, GPT grades and reviews** — so the separation has to be enforced
structurally.

**How it is enforced (`EB-190`).** Every prototype row on
`docs/prototype-surface.yaml` records `authored_by:` as a list of model
FAMILIES (`claude`, `gpt`). Anything a seat contributed beyond a clause name —
text, a number, a mode — adds its family to that list. `seat grade` and
`seat review` REFUSE a turn or a pair whose row lists the seat's own family.
`check_independent` is the door this rides on: it already refuses the Claude
family from the blind seat, and this generalises it from who is running to what
the row records about who wrote it.

### Local model as grader (experiment)

A model served on this machine in the grader's chair, so the funnel can keep
reading while a hosted quota is out. The stack is `llama-server` (llama.cpp
b10433, native Windows CUDA) on port **8010**, serving unsloth's
**Qwen3.8-27B-UD-Q4_K_XL** (17.9 GB GGUF), launched
`-c 262144 -ngl 99 --jinja --reasoning-format deepseek -fa on -ctk q8_0
-ctv q8_0 --host 0.0.0.0 --port 8010 --parallel 1` — ~39–57 tok/s decode,
~4K tok/s prefill. `--parallel 1` means **one request at a time**; every caller
here is serial and fanning out would queue behind itself and look like a hang.
The grader talks to `llama-server` **directly** over its OpenAI-compatible
routes; the LiteLLM proxy that fronts the same server (Anthropic `/v1/messages`
→ `llama-server`, for Claude-Code-as-client use) is not in this path and is not
needed for it.

```
export GITS_LOCAL_MODEL_URL=http://localhost:8010/v1   # required; no default
export GITS_LOCAL_MODEL_CTX=262144                     # refuse, never truncate
# GITS_LOCAL_MODEL_NAME    optional — default: whatever /v1/models reports
# GITS_LOCAL_MODEL_TIMEOUT optional — seconds, default 1800

python -m understudy.local_model --probe                 # models + one prompt
python -m understudy.local_seat  grade <turn-id> [--dry-run] [--grader-id ID]
python tools/local_model_sanity.py --dry-run             # plan + token estimate
python tools/local_model_sanity.py [<turn-id>...] [--doctrine]
```

**local\_seat** runs the SAME prompt (`seat.build_prompt`, so the two seats
cannot drift apart) against the same `packet.md` and writes the same artifacts
— `form-local-<slug>.json`, then `staged_turn grade` writes
`verdict-local-<slug>.json`. The grader id is `local-<slug of the served
model>`; `grader.model` is written `local:<served name>`, and both
`model_requested` and the server's own reported model land in the session's
`seat.json`. It keeps every refusal that decides whether a packet may be read
at all — `seat_authored_row`, `open_face_defect`, the turn and packet hashes —
and adds `prompt_exceeds_ctx` and `answer_truncated`, because a prompt that
does not fit is **refused and never truncated**: a grader answering a board it
was only partly shown produces a form that looks like a grade. With
`--reasoning-format deepseek` the reply carries `reasoning_content` beside
`content`; it is recorded as `reasoning` and **never parsed** — the form is the
`content`. Grading runs at **temperature 0** (the bakeoff's agentic sampling —
temp 1.0 / top\_p 0.95 / top\_k 20 — is not what a grade wants), and the
temperature is written into every artifact.

**The sanity harness** re-reads turns that are already **CLOSED** — by default
every `klee-slice1-r3-t*` and `kokomi-slice2-t*` directory carrying both an
`opus-5-fresh` and a `codex-gpt-5.6-sol` verdict — and prints the three
readings side by side: verdict agreement, whether the line matches, the local
form's stated line against the recorded ones, and whether the reader made the
round-1 **"which Attack is free"** misread (a claim of *free* checked against
the cost the packet PRINTS), with wall-clock and token counts per call. It
writes **only** under `review/qa/local-sanity-<date>/` and never inside a
closed turn's own directory — a published record stands as published (R101b),
and a third form beside two graded ones would read as a third grade.
`--doctrine` runs the seat's doctrine-gate prompt through the same protocol
frame and diffs the verdict words against the recorded GPT review. `--dry-run`
answers the first question — do the packets fit the window — with no endpoint
at all; a staged turn's prompt is ~1.9K tokens, so 32K would be ample and a
doctrine brief is the only thing that needs the big context. With
`$GITS_LOCAL_MODEL_URL` unset a real run says so and exits 2 having written
nothing.

**The limits, and they are the point (R217 G).** What a local model produces
is **subjective feedback**. It is **not human validation**, **not balance
evidence**, and the `local` family is **not an approved doctrine seat** — the
doctrine chair is still GPT's and the authoring roles are still fixed at two.
Nothing it produces enters a record, a register or the ledger. Its blindness
claim is also weaker and says so in `seat.json`: one HTTP request with no
tools, no filesystem and no repo root is a **structural** argument, not the
codex seat's transcript-proved one. `understudy/authorship.py` therefore keeps
two sets — `AUTHORABLE_FAMILIES` (`claude`, `gpt`, what `authored_by:` may
name, unchanged) and `FAMILIES` (`claude`, `gpt`, `local`, what
`model_family()` may recognise) — so a local reading can be **attributed**
without ever being authoritative. Sessions land in
`understudy/logs/local-seat/`, gitignored for the same reason the codex seat's
are.

**Serving flags that were measured, and the one that is the control.** The
GGUF carries the model's MTP layer, so `--spec-type draft-mtp --cache-reuse
256` is the intended launch: with it the server's own `timings` read 136 tok/s
on short prompts and 94 tok/s at 47K context, against 70 and 58 without, at
draft acceptance 69% and 53% and about +1.4 GB VRAM, all at temperature 0. The
control for runaway thinking is **server-side**: `--reasoning-budget 4096`
with `--reasoning-budget-message "Thinking budget exhausted. Stop thinking now
and write the final answer in the required format."` With that budget a staged
form completes in about 30 seconds and the 47K doctrine prompt answers in
about 76; without it the model never reached `content` at all, at either an 8K
or a 16K answer ceiling. **4096 is the standing budget**, not a provisional
one: the quality re-run under these flags answered all twelve closed turns
with **zero refusals** and returned a doctrine verdict in 73 s with the same
vocabulary and clause hits as the recorded GPT review
(`review/qa/local-sanity-2026-08-29-mtp4k/`, branch
`local-sanity-2026-08-29`). The client never caps reasoning and never
truncates — `answer_truncated` is the backstop, and it refuses.

### Local tester seat

[USER], 2026-08-29: *"Ask GPT for confirmation on the playtest findings … and
if they agree, then we can hand off playtesting to Qwen."* The Codex seat
answered **ADVANCE, for the staged single-turn tester seat only**, and attached
four conditions. This is that seat, and those four conditions in code.

**What runs where.** The local model fills the FORM — it picks a line and
answers the four questions. `staged_turn grade` is still the grade: the
falsifiers are mechanical and no model is in that loop. So the tester writes
`form-local-<slug>.json` and a record `tester-local-<slug>.json` beside it,
and the verdict is `verdict-local-<slug>.json` as before. The prompt is
`seat.build_prompt`'s, unchanged, so the two seats cannot drift apart, and the
`packet_sha256` pin and every refusal `local_seat` already kept are inherited
whole. **Grader work, whole-fight blind play and the doctrine gate stay with
the Codex seat**, and a PLAYABLE here is not validation, not balance evidence
and not ship approval.

**Who holds the DECIDING chair (R224, `M64`) — a SPLIT, by what the round can
do.** A round that can read **an arm PLAYABLE** gets the **Codex seat deciding
every board** — roughly seven Codex calls a round against the standing three,
and that cost is accepted because a PLAYABLE resting on a same-family read is
not author-disjoint (R217 C). A round that is an **INSTRUMENT round** — a
repair, a bench, anything on which **no PLAYABLE rests** — stays on the
**fresh-Opus**
deciding form, which R222 B seats. The round's own registration says which it
is, before it runs.

```
export GITS_LOCAL_MODEL_URL=http://localhost:8010/v1
python -m understudy.local_tester read <turn-id> [--position N]
python -m understudy.local_tester read <turn-id> --dry-run
python -m understudy.local_tester round <t01> <t02> … --plan-only
python -m understudy.local_tester round <t01> <t02> … [--seat-spot-check N]
python -m understudy.local_tester round <t01> … --seat-mode shadow|deciding
python -m understudy.local_tester qualify [--battery F] [--out F] [--land-dir D]
```

`read` reads one turn and hands the form to `staged_turn grade`; `--position`
is the turn's one-based place in the round, which is what the spot-check rate
counts. `round` RUNS a whole round — stage, read, grade, replay, board by
board — and ends by printing the turns that still owe the Codex seat, with the
`understudy.seat grade` command for each. `--plan-only` prints the
pre-registered order and the preflight result and sends nothing; commit that
schedule before the round, for the same reason a prediction slate is committed
before a run.

**The round pipelines its phases and launches one game (R221).**

```
python -m understudy.local_tester round <t01> <t02> … --plan-only
python -m understudy.local_tester round <t01> <t02> … [--first N] [--why ...]
python -m understudy.local_tester round <t01> … --lanes 2     # two games at once
python -m understudy.local_tester round <t01> … --read-workers 2  # N reads at once
python -m understudy.local_tester round <t01> … --serial      # the old order
python -m understudy.local_tester round <t01> … --attach      # someone else's game
python -m understudy.staged_turn packet-section <round-slug> [--write <packet.md>]
```

- **Two lanes, one game.** Game-bound steps (`stage`, `execute`) are
  serialized under one lock; the model-bound read runs beside the game's next
  stage, with a look-ahead of exactly one board. `--serial` restores the old
  strictly-phased order so a live comparison is possible.
- **The machine stays awake for as long as a session holds the game (EB-226).**
  `soak.Session.setup` takes a Windows power request
  (`ES_CONTINUOUS | ES_SYSTEM_REQUIRED`, `understudy/keepawake.py`) and
  `teardown` gives it back; it is refcounted, so two lanes share one hold. The
  flags are per-thread and a lane worker can outlive neither, so the request
  lives on its own thread that does nothing but stay alive. This does NOT
  depend on the power plan: an idle standby timeout ate 4 h 16 m out of a
  running funnel on 2026-08-29 and 56 minutes on 2026-08-30 before the
  timeout was set to never, and a setting nothing in this tree can see is not
  a fix. To confirm a live run is holding it, run `powercfg /requests` in an
  elevated shell — the harness's `python.exe` is listed under `SYSTEM:`, and
  `None.` there while a round is up means the request was not taken.
- **`--read-workers N`: the model half, and it is where the round is.**
  `KLEESPARK-R2` is the first pipelined round with a wall clock, and it says
  plainly what the funnel is bound by: six boards, 372 s total — **stage 89 s
  (14.8 s/board), read+grade 295 s (49.2 s/board), replay 124 s** — with the
  reads running back to back for 313 of the 372 s. Stage plus read is 384 s of
  work in 372 s of wall clock, so the pipeline hid ~73 s of the 89 s of
  game-bound work, about 16% of the round. **A read is three times a stage, so
  a second GAME instance cannot shorten a model-bound round and this flag can.**
  The 49.2 s is ONE local generation per board and essentially nothing else:
  the seat's own artifacts (`understudy/logs/local-seat/<turn>-<stamp>/`) are
  all written at the moment the reply lands, ~4,650 completion tokens at the
  server's ~95 tok/s; `staged_turn grade` is a mechanical pass over files and
  does not show up. **The deciding fresh-Opus form and the Codex spot-check are
  produced OUTSIDE the funnel** — nothing here calls a hosted model, the round
  finds the control form on disk by elimination — so neither is in this budget
  and neither is made concurrent by this flag. **Measured live on
  `funnel-bench-1` (2026-08-30, R2's six boards under bench ids,
  `--lanes 2 --read-workers 2`, `review/qa/funnel-bench-1-record.md`): six
  reads in 219 s against R2's 295 s, ~37 s per board effective, 1.35× — below
  the server's raw 1.76× because each read's ~10–15k-token prompt competes for
  the same GPU; a paired read took ~74 s where a solo one took 49 s.**
  `--read-workers N` is a semaphore of N over the read phase (N = 1 is the old
  single lock, exactly). **It needs a server with N slots:** `serve.ps1` runs
  `--parallel 2` since 2026-08-30 (`-Parallel`, default 2; measured on two
  concurrent 1000-token generations: 11.9 s against 21.0 s serial, 1.76x, per-stream
  87 tok/s against 103 solo, VRAM unchanged because the KV cache splits per slot),
  and the round REFUSES `N > 1` when the server reports fewer
  slots than asked, read from llama-server's own `/slots` (a list) or `/props`
  (`total_slots`). A server that answers neither is not a refusal — the
  operator is told the number is unknown. The cost of a second slot is KV
  cache: at `-c 131072` with a `q8_0` cache, `--parallel 2` splits the context
  per slot, so it is a shorter window per read or a bigger allocation, and
  nothing here changes the running server.
  **Concurrency may not reach the stopping rule.** The reads can COMPLETE out
  of order; every board of a set is joined before the rule is applied, the
  records are rebuilt in the pre-registered order, and `slot_state` reads
  grades off disk by turn id, which has no order term. Which boards run is a
  pure function of the grades. The round summary records
  `registered_order` beside `read_completion_order` so a reader can check that
  rather than take it.
- **`--first N`** is R221 B's sequential stopping, default **4**. The order is
  the smallest set covering every registered slot twice (ties to the closer
  closeness reading), and `--first` is raised automatically where the cover
  needs more. After the first set, a slot with two or more agreeing grades is
  DECIDED; the rest of the boards run only if they carry an UNDECIDED slot,
  and the others land in the ledger as **UNRUN with their seeds pinned**.
  `--first 0` runs every board. **A board declares its slots with a `slots:`
  list in its turn file**; a board that declares none carries one slot — its
  own id — so a round of undeclared boards never stops early, which is the
  safe default rather than a silent one.
- **One launch, and the part that is not buyable.** The round opens ONE
  `soak.Session`: the appid, the bridge deploy, the speed capture and the
  reversibility ledger are paid once rather than once per `stage` and once per
  `execute`. **The process is still restarted between boards**, because
  `soak.RunDriver._to_main_menu` starts from a menu, a staged board leaves the
  game mid-combat, and the wire has no in-run exit (`abandon_run` is a
  main-menu option). Each relaunch is recorded with its reason; a crashed game
  relaunches once and a second failure stops the round. Seed pinning is
  unaffected — the seed is fired at `_embark` on the attach path too, and read
  back off the wire (R95). `--attach` hands the whole lifetime to whoever is
  holding the game (`embark --hold`).
- **Both preflights run over every planned board before the launch**, so
  `EB-169` and `EB-187` refuse a round at a parse rather than after it has
  started spending game time.
- **And so does the slot REACHABILITY check (`EB-202`).** A round whose boards
  sit beside a `slots.yaml` has every counting slot's ceiling computed over
  the planned set before the one launch, and the plan is **REFUSED** when a
  ceiling is below the slot's threshold, naming the number. `KLEESPARK-R1`'s
  `P1` asked for 4 of 8 on a set with a ceiling of 3, and no reading of that
  round could have met it. The file is the smallest thing that says so: one
  `id`, one integer `threshold`, and a `predicate` that is a LIST OF CLAUSES,
  all of which must hold — `{left: <fact or int>, op: <comparison>, right:
  <fact or int>}`. The facts are named readings of one board's declared half
  (`spark_bank`, `energy`, `hp`, `block`, `hand_size`, `enemy_count`,
  `min_spark_price`, `affordable_spark_uses`, `affordable_spark_price_sum`,
  `spark_use_count`, `charge_bank`); a fact a board cannot answer is
  UNDEFINED and its clause is FALSE, so a board that cannot be asked does not
  qualify. There is no `or` and no nesting on purpose. **A round with no
  `slots.yaml` is legal** — every round committed before this existed carries
  none — and `staged_turn check` runs the same check per directory.
- **The LIVE-COUNT preflight, after each staging (`EB-208`).** The ceiling
  above is computed off the DECLARED board by construction, and the encounter
  is generated — a turn file can wish for three bodies and the seed can give
  one. So once `stage` has written `observed.json`, the round compares the
  live enemy count with the declared one; where they differ it writes
  `review/qa/<turn-id>/unreached.json` — declared, live, seed, slots — and the
  board is **UNREACHED** on every registered slot whose predicate reads
  `enemy_count`, and on no other. Those slots take **no grade** from that
  board in the stopping rule, in the round summary and in `packet-section`.
  The round does not stop: the board is still read, graded and replayed for
  the slots it could pose.
- **`staged_turn packet-section <slug>`** writes the round's results block
  from `review/qa/<slug>-t*/` and `review/qa/ledger.tsv`: per-turn rows, the
  per-slot tally, what the round spent (Codex reads counted separately), the
  UNRUN boards, and the ledger's own banners quoted. `--write <packet.md>`
  appends it. **The prose read is a marked empty slot and is never generated.**

**The seat sits in the SHADOW chair by default (`--seat-mode`).** R221 A
measured this seat against the fresh-Opus control at **4 of 8** verdict
agreement, and the control STANDS under every option on `M62`, so the local
read is not what a round is decided on while the control still rides every
packet. In `shadow` the seat reads every packet and its form and record are
written under the usual names — plus `role: "shadow"`, `seat_mode` and
`deciding: false`, on **both** files, so a form that travels alone is still
legible — and `staged_turn grade` still grades it, because a shadow read with
no verdict beside it could not be compared with the control at all. What it
does not get is the replay: **the fresh-Opus form is the deciding tester and
it is what `execute` replays**, found by elimination (`form-*.json` that is
neither `form-local-*` nor `form-raw-*`, newest wins). A board whose control
form has not been taken yet has its replay recorded as **OWED** and is never
quietly replayed from the shadow read. `--seat-mode deciding` restores the
pre-R221-A behaviour exactly. **And in the shadow chair the STOPPING RULE
reads the deciding grades and nothing else (`EB-209`)**: the shadow verdicts
are the only ones on disk while a shadow round runs — which is exactly what an
OWED replay means — and R222 B says a shadow reading decides nothing, so a
round that stopped on two agreeing shadow grades would have stopped on a
reading with no standing. A **refused deciding form is no grade** there: a
refusal is the funnel saying the form cannot be read against the board, not a
reading of it, which is also why it is not replayed. With no deciding grade
taken yet every slot reads UNDECIDED and the whole pre-registered order runs —
the safe direction, and what `KLEESPARK-R2` did by accident rather than by
rule. The round writes
`review/qa/<round>-round-summary.json` carrying the **per-turn agreement
count, shadow against deciding, on the VERDICT only** — which is the number
`M62`'s criterion is read off — and the ledger grew a trailing **`role`**
column (`shadow` / `deciding`; a row written before the chair existed parses
and reads `deciding`).

**A form is refused for a missing target (`EB-203`, `target_missing`).** A
play that names a card whose printed effects aim at ONE enemy and carries no
target cannot be replayed at all, and `KLEESPARK-R1` sealed two of eight
lines in that state. The rule is a falsifier like every other, refused before
the grade, and the refusal names the play **and prints the hand's cards that
take a target**. **`target: null` stays legal and is the required answer for
a card that aims at nobody.** The blind packet carries no targeting field —
the wire's hand entry has none — so the fact is derived from the card sheets
(`understudy/resource_order.SHEETS`) through each effect's own `target:` key,
where `enemy` is the one aimed spec and `all_enemies` / `random_enemy` /
`self` are not; a *Choose one* is judged on the mode the form recorded.
**Repair is out of scope (`M63`): this refuses and never repairs.**

**Requalification (`M62` (5), pass mark R223): `local_tester qualify`.** A fixed battery of
**18 sealed packets, six per category**, drawn equally from `kokomi-slice2`,
`klee-slice1-r3` and `klee-sparks-r1` (`understudy/battery/battery.yaml`) —
no new board is staged and no game is launched. The categories are the three
failures this funnel has actually seen: **targets** (an aimed card carries
one, a targetless card does not — both directions), **printed costs**
(`misreads.free_card_misreads`, the shipped check), and **intent
sensitivity** (the `intent_insensitive` falsifier itself). It writes a
scorecard JSON and one summary line of per-category counts. **The pass mark
is R223's and it is per category: targets 6 of 6, costs 4 of 6, intent 4 of
6, and all three must hold — there is no total.** The mark is [USER]'s, not
the tool's, so it lives in the battery file's `threshold:` block beside the
boards it grades; the tool only applies it. `qualify` prints PASS/FAIL per
category and overall, the scorecard JSON carries `pass` at both levels, and
the verdict is the **exit code — 0 on PASS, 1 on FAIL** (2 only when the
battery cannot be run at all: malformed, thin, or a mark it cannot reach).
The reads land in `--land-dir`, never in the sealed turn directories (R101b),
unchanged. The one
item shape the sealed record cannot give is the intent category's *two
packets identical except the telegraph* — no such pair has been staged, every
matched pair differs in the arm under test — so that category is scored one
board at a time, and the item shape widens when such a pair exists.

**`--lanes N`: two game instances, one install (`EB-206`).**

`--lanes 1` is the default and is the funnel exactly as it was — the
machine's own `APPDATA`, port 15526, no flag, no environment change. `--lanes
2` launches a SECOND `SlayTheSpire2.exe` from the SAME Steam install and
deals the boards to the two lanes in the pre-registered order.

- **Two processes, one install, and what makes that work.** Steam initialises
  twice on one account with no restart-if-necessary. Each process gets a
  wholly separate `user://` tree — saves, settings, shader cache,
  `mod_configs`, logs — by being launched with its own **`APPDATA`**. Lane 1's
  is `%LOCALAPPDATA%\gits-lanes\lane1`.
- **The port is the part a shared install cannot give you.** `STS2_MCP.conf`
  lives beside the mod dll INSIDE the game directory, so two processes read
  one conf and want one port. The vendored bridge now reads
  **`STS2_MCP_PORT`** from the environment FIRST, then the conf, then 15526,
  and logs which source won (`vendor/STS2_MCP/gits/GitsPort.cs`). Lane 0 is
  15526; lane 1 is 15527. With the variable absent the conf behaviour is
  upstream's, unchanged.
- **Cost:** roughly **1.3 GiB of VRAM and 1 GB of RAM per extra instance**.
  Two is what has been measured; nothing here says three works.
- **What two lanes buy, stated honestly.** The GAME half — staging and
  replaying — runs two boards at once. The MODEL half does not: there is one
  local server, so readings stay serialized across lanes unless
  `--read-workers` widens them. **Measured on `funnel-bench-1` (2026-08-30,
  the first full two-lane round, `review/qa/funnel-bench-1-record.md`): six
  stages took 93 s on two lanes against R2's 89 s on one — each stage stretched
  from ~15 s to ~30 s with two games up, so on this machine the second game
  competes with the first for the same CPU/GPU and the stage figure is a wash.**
  What the round proved is the routing: 6 of 6 seeds honoured, no crossing
  (`EB-210`'s fix, first time under a whole round), 4 launches per lane.
- **The order is unchanged, and so is the stopping rule.** R221 B's
  pre-registered order is the order boards are DEALT in; lanes decide which
  process stages next, never which board is next. `slot_state` /
  `split_rest` read grades by turn id and slot and have no lane term — a
  grade is a fact about the board, and the lane is bookkeeping the record
  carries so a reader can find the log. The ledger's trailing **`instance`**
  column sits AFTER `role` — `role` was appended first — and `ledger_rows`
  pads both, so a row written before either column existed still parses.
- **Only lane 0 installs the bridge, and NO lane ever removes it.**
  `deploy_bridge.ps1` rewrites the shared `mods\STS2_MCP`, so lane 1 is given
  `install_bridge=False`. (Since 2026-09-02 a session refuses to rewrite it
  anyway when a game is already up on an installed one — see the whole-run
  lane below — so the flag is the round saying it once for both its lanes
  rather than the only lock.) **The removal half is gone outright (`EB-310`):**
  the bridge is shared with the owner's own Steam launches, so every branch
  records it *shared, left in place* and no teardown takes it out.
  `deploy_bridge.ps1 -Remove` is the only remover, by hand.
- **STANDING RULE: lane 1's profile is DISPOSABLE.** It is seeded once from
  lane 0's `settings.save` (without it the lane boots with no mod profile) and
  nothing in it is ever read back. No run of record is played on it. If it
  goes wrong, delete `%LOCALAPPDATA%\gits-lanes\lane1`.
- **`--attach` is single-lane by construction**: it holds ONE game it did not
  launch, and refuses `--lanes 2` rather than guessing at a second.
- **A kill takes a pid, never an image name.** `soak._kill`'s old
  `taskkill /IM SlayTheSpire2.exe` belt would have torn down the other lane's
  game mid-board. A leftover game from a crashed soak is now the deploy
  script's own refusal to report (it lists the pids) and the operator's call.

**THE WHOLE-RUN HARNESS HAS THE SAME LANE (2026-09-02).** `--lane N` on
`embark`, `soak` and `scenario run`, and `GITS_LANE=1` for the three
`blindplay` commands, which take no flag — that module is design-blind and
may not import `instances` or `soak` at all, so the lane reaches it through
`bridge`, the client it already calls (`bridge.env_instance`; an explicit
`bridge.use` on the thread still wins over the variable). `--lane` prints the
export line. **Lane 0 is the default and is every command exactly as it was**
— no instance, no thread binding, no `-lane0` infix on any file name. So:
`python -m understudy.embark --character klee --lane 1`, then
`$env:GITS_LANE = '1'` and `python -m understudy.blindplay session`, then
`python -m understudy.embark --teardown --lane 1`, which picks that lane's
newest sidecar and refuses another lane's. **Three hazards, and where each is
enforced.** (1) A lane-1 run is **never a run of record**: its profile is
disposable, and the sentence saying so is written into the embark sidecar
(`lane_guardrail`, `run_of_record: false`) rather than left in a comment.
(2) One install means **one deployed `mods\klee` for every lane**, so
`deploy_proto.ps1` refuses while ANY `SlayTheSpire2` process is up — by image
name, deliberately, because by pid it would miss the other lane's game, whose
lock on `klee.dll` is the same lock; tear the lane down rather than deploying
around it. The other two shared halves are refcounted by pre-existence:
`steam_appid.txt` found in place is left in place (unchanged), and a bridge
that is **already installed with a game running on it** is REUSED — recorded
as pre-existing, so no lane rewrites a dll another lane's game holds, and no
teardown removes one it did not install. (3) The `godot.log` cursor
(`EB-292`'s `log_lacks`) reads **the lane's own log**, because `scenario`
resolves it through `bridge.current_instance()` and `scenario run --lane`
binds the thread BEFORE the `Runner` is built.

**PLAYING ALONGSIDE AN AGENT — the one-line procedure.** *The bridge mod is
installed before the owner launches, with the game closed.* `deploy_proto.ps1`
does that as its last step now, so every dev deploy leaves the install
parallel-ready: the owner's Steam-launched game then carries the bridge on
lane 0's port **15526** and the agent's lane takes **15527**. (A warning
rather than a failure if it does not take — the klee package is already
deployed by then, and the bridge is a harness. Undo it by hand with
`deploy_bridge.ps1 -Remove`.) **The refusal that used to block this was ours,
not Steam's:** `deploy_bridge.ps1` threw whenever any game process existed, on
the assumption that a running game holds the bridge dll — but an install with
no `mods\STS2_MCP` in it holds nothing, and a lane-1 attempt on 2026-09-02 was
refused for a danger that did not exist. It now asks whether the files it is
about to rewrite are **locked** (`Test-FileHeld`, `FileShare.None`), reports
the pids either way, and says out loud that mods load at BOOT so a deploy
reaches the next launch and not a game already up.

**PROVEN LIVE 2026-09-02, WITH THE BRIDGE PRE-INSTALLED.** Beside a game the
owner launched from Steam — which answered on 15526 — a lane-1 session came
up in **16 s** on `APPDATA=%LOCALAPPDATA%\gits-lanes\lane1` and
`STS2_MCP_PORT=15527`, its own bridge answering `state_type: menu`; two
`SlayTheSpire2.exe` processes ran side by side out of the one install; and
teardown removed the lane's process and its `steam_appid.txt` and nothing
else, with the owner's game still running and still answering. That is the
platform half and the Steam half together, on a game this harness did not
launch.

**AND THE FLAGS THEMSELVES ARE PROVEN, END TO END, 2026-09-02** —
`review/qa/lane1-live-reads-2026-09-02/`. `embark --character
KLEEMOD-KOKOMI --lane 1`, then `GITS_LANE=1` with `blindplay observe` / `act`
through Neow, the map (`map.md`), fight one (`fight1-round1.md`), a planned
turn and its morning (`fight1-planned.md`, `fight1-round2-morning.md`), then
`embark --teardown --lane 1` — all on **15527**, with no other game up. **The
one defect it found was `EB-310`, and it is the lesson:** the bridge under
`mods\STS2_MCP` is shared with the owner's own Steam launches, so an embark
may refresh it but no teardown may ever remove it — that teardown did, and the
owner's next launch would have had no bridge.

**PROVEN LIVE 2026-08-29** (`review/qa/two-instance/live-proof.json`, and
`understudy/twolane_proof.py` / `twolane_frames.py` are the two scripts that
did it). Both lanes up in **30.6 s** (lane 0 at 16.7 s, lane 1 at 30.6 s);
both bridges answering `menu` at once on 15526 and 15527; one board staged per
lane concurrently and both packets read back with the right hashes; one frame
per lane captured **by pid** through `PrintWindow`, with two identical windows
on the screen. Wall clock for the two boards: **52.4 s concurrent, 59.6 s
serial on one lane** — and the concurrent figure is honest rather than
flattering, because 37 s of it is one lane taking `EB-191`'s retry. Without a
retry a stage is ~14 s on either lane, so the real shape is two ~14 s stages
overlapping instead of running end to end.

**Three defects the live proof found, all three fixed here:**

1. `soak.run_scripted` rebound this MODULE'S `policy_v1` name for the duration
   of a run. With two lanes, lane 0's driver called LANE 1'S policy, whose
   `Runner` had already closed its log — `I/O operation on closed file`. The
   policy is a field on the driver now.
2. A `Session` with no instance USED to mean "lane 0" and rebound the calling
   thread. `stage_board` opens exactly such a Session on the lane worker's
   thread, so lane 1's board was staged into lane 0's game; both boards came
   back refused by `exact_hand`, each holding the other's cards. `None` means
   INHERIT the thread's lane.
3. Two drivers starting in the same second took the same
   `soak-<stamp>-run001.jsonl` and wrote one interleaved file. The lane is in
   the name now; a session with no lane adds no infix.

**What the live proof did NOT cover.** The proof staged boards and read
packets, and never called a model, a grade or a replay. `EB-191` (a chosen
seed reading back `None`) fires often enough with two games on one machine to
need the retry above, and it is not fixed here. Three lanes are untested and
unregistered.

**THE FOURTH DEFECT, AND IT IS THE ONE A GRADED ROUND FOUND (`EB-210`).**
`KLEESPARK-R2` was the first graded two-lane attempt and it died on its second
board: one lane asked for `NMQLUYZDLV`, the run read back the other lane's
`R7W86HG7WHUD`, and `t04` was refused by `seed_not_honoured`. **The ports were
never crossed.** `bridge`'s current-instance is thread-local, every lane worker
binds, and the whole seed dance routes correctly through the real pipeline.

**The seed read-back is a FILE read, and the file crossed.**
`bridge.current_seed` asks the compendium, and the mod builds that block by
OPENING `current_run.save` (`McpMod.Compendium.cs`, `BuildCurrentRunContext`).
`ResolveCurrentRunPath` fell through to `EnumerateSteamDataRoots`, which asks
`Environment.GetFolderPath(SpecialFolder.ApplicationData)` — and that API
reads the SHELL's roaming folder and **ignores the `APPDATA` environment
variable**, which is the one and only thing separating two lanes' user trees.
Godot honours the variable, so lane 1 wrote its saves to its own tree and
embarked on its own seed (its own `godot.log` says so); this API does not, so
both lanes read lane 0's save. The round then filed a defect against a game
that had honoured its seed exactly.

**Fixed in three places, each lock seen to fail first.** The `user://`
progress path is globalized through Godot before the rooted check, so the
enumeration is not reached at all; `APPDATA` goes first among its candidates
as the belt; and `bridge.LaneCrossed` refuses a `current_run` whose
`save_path` is outside this lane's tree instead of believing it, filed as
**`seed_read_back_crossed`** — its own defect kind, because "the game ignored
a seed" and "this harness read the wrong game's save" need different answers.
Lane 0, and every single-lane round ever run, has no `appdata` of its own and
is not checked.

**THE LANE-SEED FACT, stated once:** a lane's seed is honoured by its own
game; what a lane could not previously trust was the READ-BACK. Any harness
value the compendium derives from a save FILE is suspect under two lanes for
the same reason, and the fix above is per-process by construction rather than
by another list of paths.


**The four conditions.**

- **`answer_truncated` is a hard refusal, with no partial filing.** A reply
  that stops at the ceiling produces a refusal record and NO form; the turn
  then routes to the seat, because it has no reading at all.
- **The family is not authorable.** `local` stays in
  `authorship.FAMILIES` and out of `AUTHORABLE_FAMILIES` (`M53`), and
  `tools/lint_prototype_authorship.py` grew a third check that walks the
  tester records: one declaring an authoring family, one whose declared family
  contradicts its own model string, and one whose family is recorded as an
  author of a row it read are each a finding.
- **Periodic seat review.** `--seat-spot-check N` makes turn 1 and every Nth
  after it ALSO a Codex read. The default is **4** — a quarter of a round, and
  never zero on the shortest round this funnel runs. `0` disables the periodic
  half only.
- **The order flag.** `understudy/resource_order.py` reads the card sheets'
  effect ops and flags a line in which a card that SPENDS or converts a meter
  (`spend_*`, `salon_*`, `crash_fanfare`) precedes a card that READS it
  (`bonus_formula`, `requires`, a `conditional`'s `if:`). The record carries
  `resource_order_flag` naming both cards, and the turn routes to the seat
  **regardless of the rate**. A *Choose one* is judged on the mode the form
  recorded; one with no mode recorded flags on the union.

**The answer budget is configuration.** `GITS_LOCAL_MODEL_FORM_TOKENS` and
`GITS_LOCAL_MODEL_REVIEW_TOKENS` set the two ceilings (both default 8192, junk
falls back). They are not the runaway-thinking control — that is the server's
`--reasoning-budget`, above.

**The second misread class.** `understudy/misreads.py` now holds both: the
round-1 cost claim ("X is free", against the cost the packet prints) and the
arithmetic one the seat caught — *"the 3 HP that block would have prevented"*,
where five Block against an eight-damage intent prevents five and three is
what gets through. It fires only on the exact residual identity with all three
numbers on the page, because a false MISREAD is worse than a missed one.

**A local backend for WHOLE-RUN blind play — built, tested, and an OPTION
rather than a seat.** `understudy/local_play.py` is a second tester object of
`blindplay.CodexThread`'s exact shape, backed by the same OpenAI-compatible
endpoint everything else on this page talks to:

```
export GITS_LOCAL_MODEL_URL=http://localhost:8010/v1
export GITS_LOCAL_MODEL_CTX=131072          # refuse, never truncate
python -m understudy.blindplay session --backend local \
    --max-actions 40 --max-wall-s 5400
# GITS_LOCAL_PLAY_TOKENS   optional — the answer ceiling, default 4096
# GITS_LOCAL_SEAT_FAMILY   optional — override the derived vendor family
```

`--backend codex` is the default and the Codex path is unchanged, flag or no
flag. **`blindplay.Session` is not forked**: the same system prompt, the same
`prompt_sha256`, the same per-screen page, the same one-command-per-screen
grammar, the same transcript rows, the same fight and run questions verbatim,
the same `wire.json`, the same budgets and the same refusal handling. What the
backend adds is the transport — the run's context is kept HERE, in the
thread's own message list, because a chat route is stateless where `codex exec
resume` is not, and the reply shape codex is handed as `--output-schema` goes
out both as `response_format: json_schema` and as an OUTPUT FORMAT block
appended after the page (the belt `local_seat` already established; a server
with no grammar support costs one retry and records `schema_enforced: false`).

**Reasoning is stripped before the command parser and kept.** Both shapes: the
`reasoning_content` field `--reasoning-format deepseek` returns, and the
`<think>…</think>` block a server launched without it inlines. The scratchpad
lands in the run's transcript row (`kind: "local_reply"`) and in the turn's own
`reasoning.txt`, and never in the committed record.

**Nothing is truncated in either direction, and both ends refuse.**
`answer_truncated` (a reply that stopped at the ceiling) is the tester seat's
first condition applied to the run lane; `prompt_exceeds_ctx` is its twin —
a run's conversation grows by a page and a reply per screen, so **the window
is the thing to size before a live run**, and when it fills the run STOPS with
its fight records intact rather than playing on from a page it was half shown.

**The record says which chair played it.** `model_requested: local`,
`model_observed:` the name the endpoint reported, `server_version:` where the
server volunteers one, and `seat_family:` the VENDOR family (`qwen` on this
box) — because R217 C is read by model family and the authorship family
`local` names a chair rather than a vendor. `blindness:` says in words that
this backend's claim is **STRUCTURAL** — HTTP posts with no tools, no
filesystem and no repo root — where the Codex seat's is transcript-proved, and
that `seat_used_tools` has no counterpart on this route. R217 C is asked twice
at construction: once on `local:<name>` for attribution, and once on the bare
served name, which refuses the AUTHOR's own weights however they are served.

**WHY IT IS AN OPTION AND NOT A SEAT.** The Codex seat's ADVANCE (2026-08-29)
covered the **staged single-turn tester seat only**, and attached the four
conditions above. Whole-run blind play is a different and much longer-horizon
job — forty screens of accumulated context against one board — and no seat has
been asked whether the local model holds it. So **no round rests on this**, and
whether it ever does is a pick for [USER]. Everything the local grader is not
is true here: not human validation, not balance evidence, not an approved
doctrine seat, and grader work, the doctrine gate and the Codex seat's own
whole-fight blind play are where this page already puts them.

`tier0/tests/test_understudy_local_play.py` runs the whole loop with **no game
and no model server** — `blindplay.ScriptedWire` over the recorded fixtures for
the game, and a loopback HTTP stub speaking `/v1/models`, `/props` and
`/v1/chat/completions` for the model — so the wire itself is tested rather than
patched away.

### Blind play (`EB-167` / `EB-168`)

The same blindness widened from one staged turn to a whole run, and a seat
that plays it rather than grading it.

```
python -m understudy.blindplay observe [--raw-file <state.json>]
python -m understudy.blindplay act "<command>" [--raw-file <f>] [--dry-run]
python -m understudy.blindplay session [--model M] [--max-actions N]
```

**observe** renders whichever screen is up — combat, map, rewards, shop, rest,
event, the selection overlays — as printed faces and nothing else, through
`qa_packet`'s scrubber; an unknown or hazardous screen renders as
`TOOL-BLOCKED: <state_type>` and is never driven. `--raw-file` renders a saved
state (a `review/qa/<turn>/observed.json` envelope works), which is how the
tests and a desk check run with no game. **act** resolves one player-language
command — `play "<title>" [on "<enemy>"]`, `end turn`, `choose "<name>"`,
`skip`, `go "<node>"`, `buy "<item>"`, `rest`, `upgrade`, `remove`,
`use potion "<title>"`, `confirm`, `proceed` — against the current state by
printed names only, and posts it; with `--raw-file` or `--dry-run` it resolves
and posts nothing. Two things on one screen that print the SAME name are
NUMBERED, in printed order, the way a map fork's nodes carry `(path N)`:
`Water's Edge (1)` / `Water's Edge (2)`, `Slug (1)` / `Slug (2)`. The render
prints the number and the grammar accepts it; a name that is unique on its
screen is never numbered and stays valid bare; a bare name that is not unique
is refused with the numbered forms listed back (`EB-177`). **A number that has
gone STALE is accepted where one copy remains** (`EB-271`): the page re-counts
its list on every screen, so `Duck and Cover (1)` names a different card once
the other copy leaves, and the suffix is stripped and retried when the bare
name resolves to exactly one thing — a number that is still ambiguous is still
refused, with the names that would have worked. The `(upgraded)` /
`(not upgraded)` qualifier (`EB-173`) is unchanged and still separates a base
copy from an upgraded one, which the fold keeps as two different names.

**Three more things the page and the grammar now do.** The game's rich-text
markup is folded out of every printed name and body through
`qa_packet.strip_markup` (`EB-246`) — the SAME fold `scenario.card_key` uses,
so a *Choose one* option has one printed name rather than one on the staged
packet and another here; an UNPAIRED bracketed token is left alone on purpose,
so a bracketed card id is never laundered past the leak guard. A potion is
posted into the slot the WIRE gave it rather than its position in the belt,
and an aimed potion is aimed before it is posted while a self-aimed one carries
no target (`EB-269`, `ExecuteUsePotion`'s own table) — and the game's refusal
reaches the page as WORDS, because the bridge writes its reason under `error`
and this read only `message`. And the six LIVE arm keywords — Bomb, Set off,
Spark, Mine, Plan, Mend — get **one definition each, once per screen**, under
*Words on this screen* (`EB-272`), wherever the word reaches the page; the
sentences are `Cards/Prototype/ArmKeywordTips.cs`'s own, held in step from the
test side. **session** is the driver: one `codex exec` thread for the
whole run, one command per screen, the fight and run records at the ends, and
budgets on actions, wall time and consecutive refusals. All of it is built on
`naming` / `staged_turn.execute`'s title resolution and **never on
`harness state`**, which prints `policy_v0`'s recommendation beside the screen.

**Live acceptance, from the art-bearing main checkout** — the row closes on
this, not on the branch that built it. `session` attaches to a run already in
progress and stops on a menu rather than driving one, so embark first:

```
python -m understudy.seat check                  # signed in?
python -m understudy.embark --character kokomi   # bridge, launch, embark
python -m understudy.blindplay observe           # eyeball one live screen
python -m understudy.blindplay session --max-actions 40 --max-wall-s 5400
python -m understudy.embark --teardown           # put it all back
```

**embark** is the operator's side of that line and deliberately not importable
from `blindplay`: it owns `soak.Session`'s deploy / launch / readiness /
embark / speed path, reads the run seed BACK off the wire (R95), and then
stops with the game up and nothing torn down. `--hold` attaches to a game
somebody else launched and changes nothing. `--teardown` rebuilds the session
from the reversibility ledger ON DISK — a different process from the embark —
and walks soak's own undo steps, newest launching embark first or `--stamp`
by name. The sidecar it leaves in `understudy/logs/` is gitignored operator
scratch; the seed it read is what the sealed record carries.


Acceptance is a model completing one fight and then one Act-1 run, every action
in the transcript, and no internal id, policy hint or design tag in any
observation. Sessions land in `understudy/logs/blindplay/`, **gitignored** —
the prompts inline the screens and the rollout carries a third party's system
prompt. The committed artifact is
`review/qa/blindplay/<session>/record.md`: the identity block (model, codex
version, the deployed mod build and the game build — each read OFF DISK and
labelled with the file it came from, `mods\klee\manifest.json` and
`release_info.json`, never the bridge's health payload, which carries the
vendored bridge's own version and never ours — run seed read back off the
wire, prompt sha256, action count, termination reason) and the model's
records verbatim under the R217 G label. The author's own model family is refused as tester (R217 C). Beside it, `wire.json` carries the **per-turn wire snapshot** (`EB-216` / `M56`): one machine-written row per play and per `end turn` — turn, energy, every meter (BaseLib's registered resources AND the power-shaped ones, which is where Sparks ride), the hand with its printed energy and Spark prices, the Kurage queue strip and the pending PLANS with their targets where the build serves them (`EB-273`, the same absent / empty / populated contract), and the enemy count with intents — lifted off the API and **never shown to the tester**, because the tester's page is the grading surface and this is the grader's (R101b); each row also carries the **meter ledger** the play minted (R225: `before / price paid / gains by source / after`, read after the POST off `GET /api/v1/gits/meter_ledger`, with `blindplay.read_snapshots` and `blindplay.meter_plays` as the grader's read — instrument only, and nothing already published is re-graded on it).

**After PLAYABLE.** A prototype arm the pair read calls PLAYABLE goes to **whole-fight
blind play on a dev build**, automatically. It is the next gate, not a pick, and
nobody is asked for a form to start it. It has not run for any arm yet, and the
reason is structural: prototype rows are quarantined out of every pool, so a
blind run cannot draw one. Until `EB-188` lands the door — a `+proto` pool
inclusion, or the dev door granting a named arm into the starting deck — the
gate is **blocked, not skipped**, and an arm that reads PLAYABLE waits there
rather than moving on without it.

**One round, one branch.** A funnel round runs on its own branch cut from the
pushed tip. Never continue a round on a branch already handed over for merge:
Klee slice 1's round-2 grades landed ahead of the `STATE.md` line that described
round 1, because round 2 was written on the merged branch and went in with it.

`KleeTests` runs the shipped `klee.dll` against the real game
assemblies **headless** — no Godot, no launch. It is opt-in, not a deploy gate;
its boundary and its co-op coverage are in `klee-mod/KleeTests/README.md`.

Machine paths come from `klee-mod/local.props` / `Directory.Build.props`.
Depth: `docs/current/atlas/klee-mod-build-pck.md`, `klee-mod-runtime.md`.
