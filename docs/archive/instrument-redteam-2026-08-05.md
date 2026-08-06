> **MOVED 2026-08-06 — Clear the Stage, Track R-B (charter R119, rail 1).**
> Old path: `docs/instrument-redteam-2026-08-05.md` — new path: `docs/archive/instrument-redteam-2026-08-05.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Citers repointed in the move commit; see
> `review/stage-clear/rb-move-manifest.tsv`.

# Instrument red-team — Track O, "House Lights"

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Date: 2026-08-05. Branch `findings/track-o`, cut from main at `91e9258`.
Twelve Opus slices, each holding one instrument. **No game was launched and no
C# was built** — every finding below reproduces from a committed fixture by
driving the Python module directly. Anything reachable only from a live run is
recorded as UNTESTED-PATH and is *not* counted as a finding.

**Review artifact — zero design authority.** Nothing here is a balance opinion.
Where a fix would require a behaviour choice it is *surfaced in prose and left
unwritten*; no instrument file was modified by this track. The only code this
branch adds is test fixtures and pin tests.

## Verification contract

A finding EXISTS only if it reproduces from a committed line or fixture on
central replay. Every slice self-tested before returning. Three classes:

| Class | Meaning |
|---|---|
| **SILENT-LIE** | Confirmed, reproducible: the instrument emits a plausible-but-wrong number, or a plausible-but-wrong absence, with no error, warning, or diagnostic. |
| **DECLARED-LIMIT** | The instrument's own docstring or doc states this boundary. **Not a defect.** Cited by file and line. |
| **UNTESTED-PATH** | Plausible, but only decidable against a live game. One line each, no severity. |

Pins were written **only** where correct behaviour is unambiguous from
existing docs or tests (the S15 zero-should-be rule). **No finding is pinned** —
pinning a defect would ratify it. No failing test entered the suite.

---

## THE HEADLINE: absence reads as agreement

Six of the twelve slices, attacking six different modules, independently landed
on the same failure. **The measurement stack cannot distinguish "the two
recordings agree" from "there was nothing to compare."**

- `trace_replay.render_compare` over two stamps whose run logs do not exist
  prints `run 001: IDENTICAL seed=None` … `VERDICT: identical traces` — the
  literal P1.5 acceptance condition — over zero fights, zero seeds, zero files
  (slices 1, 4, 5).
- `compare_runs`' seed guard, whose stated job is "two runs on different seeds
  are two different runs", evaluates `None != None` as false and disarms itself
  on every path where the seed is unknown (slice 1).
- `trace()` reads a missing key and an empty list identically, so a pre-P1.5 log
  and a log where every selector screen escaped recording compare equal
  (slice 2).
- An empty resource map means "no custom resources are registered" *and* "the
  read degraded" *and* "this bridge predates P1.5" (slice 3).
- `replay.read_jsonl` and `report.read_run_log` both drop an unparseable line
  with `except JSONDecodeError: continue` and neither module has any concept of
  a line it failed to read — so a one-row `s7-divergences.tsv` is
  indistinguishable from perfect fidelity (slices 4, 5).
- A soak run that never embarked is reported as "3 of 3 requested runs
  completed" (slice 9).

The instruments are not merely quiet about missing data. **They report missing
data as the successful outcome.** Every "identical", "clean", "0 divergences"
result this week should be re-read with the question *"was there anything in
the file?"* attached.

---

## TOP 5 BY SEVERITY

### 1. The gauntlet stage-merge overstates every published Track H per-fight rate (slice 12)

`gauntlet` has two stages; the other five encounters have one.
`runner.run_battery:46` merges the two into ONE `FightStats`, and then
`aura_profile`/`summarize` divide by `len(all_stats)` — **records, not
combats**. The numerator covers 3500 combats; the denominator counts 3000
records. Driving the shipped corpus (klee/reaction_weighted, 500/encounter,
seed 20260805) reproduces every per-encounter figure in
`docs/reactions-corpus-2026-08-05.md` §3.1 **byte-exactly**, and then shows what
those figures should be:

| figure | published | true (per combat) |
|---|---:|---:|
| gauntlet `aura apps/fight` | **12.026** | **6.013** |
| `all` row `aura apps/fight` | **7.6987** | **6.5989** (16.7% overstated) |
| `all` row `aura ops/fight` | 1.797 | 1.5403 |
| payoff `evaluated_per_fight` | 1.6770 | 1.4374 |
| gauntlet `aura_starved_fights` | **0.0000** | **0.0030** |

12.026 is the largest value in that column and reads as "gauntlet is the
aura-richest encounter"; per combat it is mid-pack, **below** attrition (9.45)
and tank_boss (9.486) — the merge inverts the ranking the table is read for.
The starved-fights row is erased outright, because a starved stage merged with a
reacting stage reads as `reactions > 0`. `merge_stages`' docstring declares the
merge; **nothing declares that the resulting per-fight rates are not comparable
across encounters.** Pooled counts and every ratio-of-sums (`share`,
`applications_per_turn`) are unaffected — the defect is exactly in the
per-record denominators. *Surfaced fix: carry `combats: int = 1` on
`FightStats`, summed by `merge_stages`, and denominate per-fight rates by
`sum(s.combats)`.*

### 2. Track D's hydro uptime reads 95% where the truth is 15% (slice 7)

`tick_auras` walks only `state.living_enemies` (`reactions.py:71`), so an aura
on an enemy that **dies** never emits its expiry and the interval runs to the
last turn in the log. Fixture: hydro applied to enemy A on turn 2, A dies on
turn 2, the fight continues 18 more turns against a hydro-free enemy B →
**uptime 95.0% (19/20)**; the identical application on a surviving target reads
**15.0% (3/20)**. A 19-turn interval is structurally impossible —
`AURA_DURATION_TURNS = 2` bounds any interval at 3. The docstring
(`aura_telemetry.py:12-14`) declares "a small systematic overcount … identical
across cells"; **both halves are false** — the overcount scales with fight
length after the kill, which is precisely what differs between the arms
`exp_curtain_call.py` prints side by side. Reproducer:
`python review/redteam/fixtures/track_o/s07-repro.py`.

### 3. The P1.5 acceptance condition is satisfied by absence (slices 1, 4, 5)

See the headline above. `render_compare("S04C","S04C")` over an index whose run
JSONLs are absent prints `VERDICT: identical traces`. `read_run_log` returns
`[]` for a missing file, both sides contribute zero records, `zip` iterates zero
times, and the empty finding list — documented at `trace_replay.py:152-154` as
the acceptance condition — is printed as agreement. **The log directory is
gitignored, so absence is the normal state of a fresh clone.** Compounding it,
trace identity silently omits `outcome` and `turns` *without declaring them*, so
a won 2-turn run and a lost 5-turn run also compare `IDENTICAL`.

### 4. The reaction amp is sampled before the multipliers that scale it (slice 8)

`amp_delta` is emitted at `reactions.py:164-166` from `effects.py:363` — above
`modify_damage_taken` (367), Slow (372) and the overkill clamp (381). Base 20
pyro into a hydro aura on a **Vulnerable** body: total dealt 45, the same hit
without the aura deals 30, true uplift **15**. D1 reports `amp = 10`,
`damage_from_base_ops = 35` (true 30), `reaction_share = 0.2222` (true 0.3333).
This is Family A run backwards — a counter sampled on the wrong side of the
moment it observes. The corpus declares only the *over*-read half
(`docs/reactions-corpus-2026-08-05.md:54-63`), so **a reader correcting for the
declared bias moves further from the truth**. Blast radius exceeds Track D:
`reaction_damage` carries the same error into the **ratified A6 axis**
(`metrics.py:74-76`), and Superconduct applies Vulnerable, so reaction decks
manufacture their own under-read.

### 5. `--max-fights` burns every other seed, silently (slice 9)

`soak()`'s restart gate fires on `outcome == "defect"` only
(`soak.py:1575`), so a `bounded` stop never restarts the game and leaves the
previous run parked on `rewards` — which kills the *next* run with
`unexpected_start_state`. Driving the real loop with `runs=6, max_fights=4`:
observed `bounded(S1)`, `DEFECT(S2)`, restart, `bounded(S3)`, `DEFECT(S4)`,
stop-and-surface. The index records `seeds: [S1..S6]`, `requested_runs: 6` —
**seeds actually measured: `["S1", "S3"]`.** Under `--no-setup` no restart ever
issues and the cascade is unbroken: one seed of six. The surviving sample is a
*deterministic* subset (the odd positions), and the morning report prints
"3 of 3 requested runs completed" above a row reading
`| 2 | None | unexpected_start_state |` directly beneath the sentence "Each row
is reproducible from its seed".

### Also severity 5 (outside the top five only because their blast radius is narrower)

**A partially degraded resource read becomes a hard 0, charged to the sim (slice 3).**

`GitsResources.cs:42-43` and `:104-107` declare a **two-state** contract: empty
map ⇔ nothing registered; absent key ⇔ pre-P1.5 bridge. The writer's own
per-handler `catch` (`:144-148`) and four unguarded drops (`:128, :131, :137,
:138`) manufacture a **third** state the declaration never names — a non-empty
map missing one key. `soak.py:653-657` resolves that into a hard `0` in the
Encore column: exactly the value `soak.py:585-589` declares forbidden ("A zero
would be a measurement claiming the meter was empty in fights where it
demonstrably was not"). `replay.py:539` then counts it into the
`l2_encore_compared` denominator and `:587` charges it to the sim as a
divergence row. The corruption detector at `:677` fires only when the column is
zero at *every* opening — **defeated by exactly the intermittent shape a
per-handler catch produces.**

> Also severity 5, and only outside the top five because their blast radius is
> narrower: a round that opens behind an in-combat overlay is never opened, so
> the selector answer is filed under the previous round and every meter
> denominator drops to 0 while the CLI exits clean (slice 2); `SCHEMA_VERSION`
> is written by both feeds and **read by neither replayer**, so a transposed
> meter column replays clean and is charged to tier0 as a Fanfare/Salon
> infidelity (slice 4); one dropped log line makes `fight_specs` adopt the
> previous fight's decisions and **fabricate** a
> `suspected_reading_corruption=1` row that exists only because the reader lost
> a line (slice 5); and `effects.SPOTLIGHT_FORCE` does not cross
> `run_many(jobs>1)`, whose docstring promises "element-for-element identical to
> the serial one" (slice 6).

---

## Per-slice results

### Slice 1 — P1.5 bridge seed honouring

The seed **request** path is honest: `bridge.set_seed` sends what it was given,
the moment is correct and already pinned, and `RunDriver.run` does raise
`seed_not_honoured`. The **verification** path lies. Every guard is keyed on the
seed string alone, and that string is `None` on more paths than the code
anticipates.

| ID | Title | Class | Sev |
|---|---|---|---|
| O1-1 | `compare_runs` disarms its own seed guard when the seed is unknown (`None != None` is false) | SILENT-LIE | 5 |
| O1-2 | Run logs that do not exist compare as `IDENTICAL` / `VERDICT: identical traces` | SILENT-LIE | 5 |
| O1-3 | A truncated JSONL line is dropped without a word, erasing `seed_read_back` | SILENT-LIE | 4 |
| O1-5 | `GameSeedLeak` fails **open** on lower-case and <6-char seeds — including the repo's own test literals | SILENT-LIE | 4 |
| O1-4 | `chosen`/`honoured` recorded and never consulted | SILENT-LIE | 3 |
| O1-6 | `policy_rng("boss")` and `policy_rng("rest")` are byte-identical streams (`_label_offset` collides) | SILENT-LIE | 3 |
| O1-8 | `--seed ''` silently reverts a chosen-seed soak to the read-back arm while the index records `seeds: [""]` | SILENT-LIE | 3 |
| O1-7 | `policy_rng` returns a fresh `Random` per call — a "stream" is a constant (currently inert) | SILENT-LIE | 2 |
| — | "Whether the GAME honours a seed" is out of scope | DECLARED-LIMIT (`test_understudy_p15.py:20-25`) | — |
| — | hp/damage deliberately outside trace identity | DECLARED-LIMIT (`trace_replay.py:56-60`) | — |

### Slice 2 — selector recording

**A selector-bearing screen can escape recording, two independent ways.**
`SELECTOR_SCREENS` covers 3 of the 15 screens `DECISION_SCREENS` says can carry
a choice, and recorded answers are stamped with `fight.turns`, a counter that
only advances on a `COMBAT -> COMBAT` transition.

| ID | Title | Class | Sev |
|---|---|---|---|
| O2-1 | A round opening behind an in-combat overlay never opens: answer filed under the previous round, wrong arm attributed, all meter denominators → 0 | SILENT-LIE | 5 |
| O2-2 | `relic_select`/`crystal_sphere` in neither `SELECTOR_SCREENS` nor `MID_FIGHT`: answer dropped **and** the fight closed `survived` and re-opened as a second record | SILENT-LIE | 4 |
| O2-3 | 9 of 15 `DECISION_SCREENS` produce no selector row at all | SILENT-LIE (coverage) | 3 |
| O2-4 | A `card_select` answered with no fight open is dropped everywhere — no record, no counter, no defect | SILENT-LIE | 3 |
| O2-5 | A 4-wide row: `replay` silently skips it, `trace_replay` renders it as an answer | SILENT-LIE | 3 |
| O2-6 | Absent vs zero indistinguishable in `trace()`, `compare_runs`, `describe_run` | SILENT-LIE | 3 |
| O2-7 | A 6-wide row accepted by `replay`, silently truncated to 5 by `trace_replay` | SILENT-LIE | 2 |
| O2-8 | `tally["selector_rows"]` counts duplicates; `_selector_choice` is last-wins — two published numbers counting different things | SILENT-LIE | 2 |
| — | `selectors` is bot-feed only | DECLARED-LIMIT | — |
| — | `overlay` excluded on purpose (the shape a soft-lock takes) | DECLARED-LIMIT (`soak.py:686-688`) | — |

O2-1, measured on the same two-turn fight with the same two answers:
`ledger_rows` 1 → **0**, `l2_turns_with_selector` 2 → **1**, every
`l2_*_compared` counter 1 → **absent**, turn 1's arm `self` → **`companion`**,
turn 2's arm `companion` → **`None`** (falls back to tier0's heuristic — the
policy-standing-in-for-a-recording the flag exists to remove). Warnings: none.
Exit: clean. `selector_rows` still reports 2.

### Slice 3 — the resource reader

The declared silent-empty-map degradation is real, correctly sited, and
honoured. The attack succeeded on the space the declaration does not cover: see
TOP-5 #5. Twelve silent lies, headed by partial degradation (sev 5), the
defeated corruption detector (sev 5), and a degraded `0` that **overwrites** the
sim's own Encore where the `-1` sentinel would have preserved it — then is
compared against itself, guaranteeing agreement on a reading that never
happened (sev 4). Separately, `KLEEMOD_FANFARE_FLOOR` and
`KLEEMOD_FANFARE_CAP_BONUS` are on the wire by construction and read by nothing,
so **the B3 Fanfare ledger replays every fight at floor 0 / base cap** (sev 4:
20 decays to 18 in the engine, 16 in the replay).

### Slice 4 — cross-feeding the two replayers

There are not two formats — there are **two overlapping views of one format**,
and neither replayer checks which view it was handed.

| ID | Title | Class | Sev |
|---|---|---|---|
| O4-S1 | Missing run logs read as agreement: `VERDICT: identical traces` on zero data | SILENT-LIE | 5 |
| O4-S3 | `schema` version written by both feeds, read by neither; a transposed meter column is charged to the sim | SILENT-LIE | 5 |
| O4-S2 | Trace identity silently omits `outcome`/`turns`: won vs lost = "identical traces" | SILENT-LIE | 4 |
| O4-S4 | `cross_feed_rows` silently drops every unmatched mod fight, with no matched counter | SILENT-LIE | 4 |
| O4-S5 | `trace_replay` accepts a mod-feed log as a soak run log, reports `selectors=0` and `(read-back)` | SILENT-LIE | 3 |
| O4-S6 | `replay.py` on decision-less input writes an EMPTY divergence TSV, rc=0 | SILENT-LIE | 3 |
| — | A run-log PATH handed as a stamp raises `SystemExit` | DECLARED-LIMIT (`report.py:50-51`) | — |
| — | The seed gate works — when both sides carry `seed_read_back` | DECLARED-LIMIT | — |

O4-S3 is the sharpest: `SCHEMA_VERSION = "1"` is documented as "bump on a
BREAKING change only", is stamped on every record by both `soak.py` and
`PlayTelemetry.cs`, and **the string `schema` does not appear in either
replayer**. A schema-99 log with two `meters_by_turn` columns transposed replays
clean, rc 0, `rows_flagged_reading: 0`, and produces
`l2.fanfare_after_turn sim=4 engine=1` — the transposition attributed to tier0
as exactly the family `docs/s7-divergences.tsv` is read for.

### Slice 5 — malformed and truncated logs

Fourteen mutations from a schema-exact baseline, through `replay.py`,
`report.py` and `trace_replay.py`, capturing stdout, stderr, `logging` and
`warnings`. **Zero diagnostics were emitted by any instrument on any mutation.**

Tested and **negative** on the brief's own hypothesis: no replayer aggregates a
fight `outcome`, so a truncated fight is never *counted as a loss* — it is
dropped. `report.py`'s run-level outcome comes from the index, so the index's
claim outlives the telemetry behind it.

| ID | Mutation | Class | Baseline → mutated | Sev |
|---|---|---|---|---|
| S05-01 | One unparseable line mid-file | SILENT-LIE | `l1_compared` 3 → **4** (*rises*), `rows_flagged_reading` 0 → **3**, fight `#f1` acquires floor 2 | 5 |
| S05-02 | Two fights' rows interleaved | SILENT-LIE | `fights_replayed` 2 → 1, flagged 0 → 3; `report.py` **unchanged**; `trace_replay` **IDENTICAL** | 5 |
| S05-03 | A `fight` record duplicated | SILENT-LIE | `2 fights` → **3**, plays 6 → 8, top source damage 36 → **54 (+50%)** | 5 |
| S05-04 | Index claims 3 runs, only run001 on disk | SILENT-LIE | `run 002: IDENTICAL`, `run 003: IDENTICAL`, **`VERDICT: identical traces`** | 5 |
| S05-05/06 | `floor` missing / null not missing | SILENT-LIE | floor 1 → **floor 0**; that bucket's median turns 2 → **0** | 4 |
| S05-07 | Duplicated round inside one fight | SILENT-LIE | `_meters_at` takes the **first** match; `_selector_choice` in the same module takes the **last** | 4 |
| S05-09/10 | Truncated mid-JSON / fight never closed | SILENT-LIE | 4 posted plays vanish with no orphan count | 4 |
| S05-08 | Plays reordered within a round | SILENT-LIE | `rows_flagged_reading` 0 → **1**: the L1 bracket goes negative and is charged to the game | 3 |
| S05-11/12/13 | Blank lines, out-of-order rounds, unknown row types | **correct (inert)** | byte-identical | — |
| S05-14 | `cards_played` row arity 3 | **LOUD (correct)** | `ValueError` at `replay.py:775` | — |

S05-01 is the worst result in the slice, and it is not a dropped number but an
**invented** one: `fight_specs` flushes pending decisions only on a
`record == "fight"` line, so when that line is dropped, fight 1's decisions are
adopted by fight 2's record, `target_id` is reused across fights, the merged
turn brackets fight-1 HP against fight-2 HP, goes negative, and the
negative-bracket guard — documented as "an enemy that split, hatched or was
replaced" — fires on a fabrication, emitting
`suspected_reading_corruption=1` with `cards=4/4` in the context column.

### Slice 6 — `--use-selectors` and the `SPOTLIGHT_FORCE` restore

**The predicted leak is not there.** `replay.py:483-502` saves the force, sets
it for the replayed turn's play loop only, and restores it in a real `finally`;
`test_understudy_replay_selectors.py:104` already pins the raising path, and the
nested case (an outer force is handed back intact, not cleared) was confirmed by
drive. `KeyboardInterrupt`/`SystemExit` pass through the same `finally`. An
honest negative. The silence is elsewhere.

| ID | Title | Class | Sev |
|---|---|---|---|
| S06-1 | `SPOTLIGHT_FORCE` and every mutated module knob does not cross `run_many(jobs>1)`; workers silently use defaults | SILENT-LIE | 5 |
| S06-3 | The recorded answer has no position within the turn, and no persistence between turns | SILENT-LIE | 4 |
| S06-2 | Selector-reconstructed and heuristic-reconstructed fights pooled into one unmarked TSV | SILENT-LIE | 3 |
| S06-4 | Turns whose plays all raised still emit sim-charged divergence rows, unflagged | SILENT-LIE | 3 |
| — | Individual experiment scripts know the `jobs>1` hazard by hand (`exp_furina_decay.py:102` "DO NOT add jobs>1") | DECLARED-LIMIT *per script*, silent in the shared instrument | — |

S06-1: `effects.SPOTLIGHT_FORCE` is a module global; `model.py:839` dispatches
through `ProcessPoolExecutor`, which on Windows spawns and re-imports. Eight
runs, seed 11, furina/salon/assigned — `jobs=2` with the force set returns the
**unforced baseline, element for element**, against a `run_many` docstring
promising "a wall-clock lever ONLY, never a fidelity tradeoff".

### Slice 7 — Track D telemetry writers under partial fights and deaths mid-write

**Track D** = R85 (Curtain Call) named `tier05/aura_telemetry.py` — hydro
application uptime — as its rider, with the ±10% bound living in the sprint log,
not the code. Two things are **fine**: no cross-fight contamination (fresh
`CombatState.log` per fight), and no missing flush on the death path
(`encore_end` fires on loss too). The damage is in denominators, liveness
filters, and one interval closer with no event to close on.

| ID | Title | Class | Sev |
|---|---|---|---|
| S07-01 | A hydro interval on an enemy that **dies** is credited to end of fight — 15% reads as 95% | SILENT-LIE (direction declared, magnitude falsified) | 5 |
| S07-02 | `applications_per_fight` counts the death fight and empty traces as whole fights (no liveness filter at all — uniquely among the six reducers) | SILENT-LIE | 3 |
| S07-03 | `mean_held_fraction`/`peak_fraction` average per-combat ratios in a function whose docstring promises pooling — **0.1000 vs a pooled truth of 0.6897** | SILENT-LIE | 3 |
| S07-04 | The overlap watch scores a run that died on floor 1 as "drafted but never played": `mean_plays` 27.00 → **13.50**, `never_played_runs` 0 → **10** | SILENT-LIE | 3 |
| S07-05 | Liveness filters discard fights carrying real content (60% overflow → 0.0%) | SILENT-LIE (module-level; engine path unproven) | 2 |
| S07-06 | `all-ticked 0.0%` renders identically for "every upkeep truncated" and "the stage never ticked" | SILENT-LIE (render) | 2 |

### Slice 8 — Track D writers vs granted plays: does Family A have cousins?

**Family A, restated:** `RunDriver._observe` wrote `fight.cards_played` inside
an arm guarded by `if st_b in COMBAT and st_a in COMBAT` — the state read back
*after* the play — so any play whose resolution moved the screen off a plain
combat state was silently never written down.

**The assigned stressor comes back clean.** `combat.resolve_free_play` emits the
same `play`/`damage`/`reaction`/`aura_op`/`aura_applied`/`conditional` events a
hand play does; `metrics.extract` reads every Track D and Track H counter off
the log, not off a sampled state; a granted play that lands the killing blow
keeps its row. Proven by driving both paths with the same card and diffing all
ten new counters — the only difference is `energy_spent`, which the free-play
contract declares. **Family A has no granted-play cousin in tier 0**, and that
is pinned.

The cousins are elsewhere, and all three are the same *boundary* shape — a
counter sampled on the wrong side of the moment it claims to observe. Two are
read **before** resolution: Family A run backwards.

| ID | New field | Cousin? | Class | Sev |
|---|---|---|---|---|
| S08-1 | D1 `reaction_damage_amp`, `damage_from_reactions`, `damage_from_base_ops`, `reaction_share` | YES — sampled before the multiplier chain | SILENT-LIE | 4 |
| S08-4 | C# `n_cards_played` (`PlayTelemetry.cs`) | YES — killing card's row dropped, record closed first | UNTESTED-PATH | 4 |
| S08-2 | H1 `aura_applications_by_source`/`_by_element` | YES — the killing-blow case, inverted | SILENT-LIE | 3 |
| S08-3 | D2 `turn_trajectory[3]`, `block_end_samples`, `mean_block_at_end` | YES — claims to drop the fight-ending turn, doesn't | SILENT-LIE | 3 |
| S08-5 | C# `reactions_by_turn` baseline `ReactionsAtStart` | YES — baseline at first *player turn*, not fight open | UNTESTED-PATH | 2 |
| S08-6 | **All** D1/D2/H1/H2 counters under a granted play | **NO** — verified clean, pinned | — | 0 |
| — | `aura_ops` counts ops resolving into nothing | DECLARED-LIMIT (`metrics.py:100-105`) | — | — |
| — | `amp` over-read on overkill/blocked hits | DECLARED-LIMIT (`reactions-corpus:54-63`) | — | — |
| — | A granted play skips Spotlight/burst counting | DECLARED-LIMIT (`combat.py:358-363`) | — | — |

S08-2, measured on 300 fights per arm with real decks and real pilots: auras
applied by a killing blow to a body that dies one statement later —
klee/reaction **10.8%**, furina/spotlight **14.5%**, kokomi/commander 7.8%,
klee/demolition 1.3%. They can never react, and `tick_auras` walks
`living_enemies`, so they are never booked as `auras_wasted` either: 1–14% of
the published "aura apps/fight" numerator.

S08-3: `metrics.py:80-92` says `block_at_end` is `-1` when the fight ended
inside the turn, and `combat.py:596` says such a turn "never reaches" the
`turn_close` emit. **Both are false** — the card loop `break`s and falls through
the whole turn-end tail. On 200 punisher fights (200 won, 1025 rows) only **9**
rows carry `-1`, all of them turn-*start* endings. `turn_profile[1]` reports
`fights=200, block_end_samples=200`: the documented "skips the `-1` rows" filter
removed nothing.

S08-4 **contradicts `docs/s7-probe-c.md:71-80`** on the C# side and is flagged
for that reason (read-only; blocked by the no-game constraint). The gate *is*
"record still open", and `PlayTelemetry.Damage` calls
`MaybeClose → FlushAll → Open.Clear()` on the killing blow, so `CardPlayed`
returns at `:249` and the killing card's play row is dropped — the same
one-play-per-won-fight footprint as the bot feed's. That would re-explain the
audit's "mod feed is always the higher number" as the bot feed losing all
Spotlights rather than the mod feed being complete.

### Slice 9 — the soak driver's `unexpected_start_state`

The already-observed B3 defect (`docs/probe-b-fanfare-residual.md:85`) **was
reproduced** from `s09-b3-parked-state.json` by driving the real `RunDriver`
against a stub bridge. The reproduction is worse than the row: `self.seed` is
assigned only *after* `_embark` while the raise is in `_to_main_menu` *before*
it, so `run_begin`/`defect`/`run_end` all carry `seed: null` despite
`chosen_seed="TRACKB3B"`, and the defect record reads `act:1, floor:4` off the
parked screen — **run 1's position, attributed to run 2**.

| ID | Title | Class | Sev |
|---|---|---|---|
| O9-6 | `--max-fights` guarantees the next run dies; the seed is burned and never retried | SILENT-LIE (selection bias) | 5 |
| O9-1 | A run that never embarked is reported as "completed" | SILENT-LIE | 4 |
| O9-2 | The chosen seed is erased from every record of the defect run | SILENT-LIE | 4 |
| O9-4 | Zero-fight runs sit in the fights-per-run denominator | SILENT-LIE | 4 |
| O9-5 | Depth median contaminated by `final_floor: None → 0` (median 2 against a true 4) | SILENT-LIE | 4 |
| O9-8 | A 3-run bounded soak loses a third of its sample and never trips stop-and-surface | SILENT-LIE | 4 |
| O9-3 | The defect record inherits the previous run's act/floor | SILENT-LIE | 3 |
| O9-7 | Harness-side defects share the headline count with genuine crashes | SILENT-LIE | 2 |

Slice questions, answered: **denominator — yes**, the rejected run lands in
`len(runs)`, the completion header, fights-per-run and depth spread (it
contributes no fight records, so the per-floor and damage tables stay clean).
**Reported — partially**: the kind reaches the defect table, but escalation needs
two strikes, the dead run counts as completed, and the burned seed is named
nowhere. **Retry — none exists**; the seed is consumed before the run starts, so
the bias is "silently drop the even positions", not "retry until it passes".
**Sequencing** — per-run state resets correctly; the residue is the game
*process*, cleared only by the restart gate that `bounded` does not trip.

### Slice 10 — the S13 replay harness itself

**Can a line verify spuriously? Yes, but narrowly — and the 71/71 headline
survives.** All 71 committed lines re-verify at 91e9258 (`71 lines: 71 verified,
0 errored`), so nothing is stale and nothing has rotted. The harness is loud
where it matters most: an unknown card, relic, encounter, metric, op or
claim-kind all return `ok: False`, and a scripted card that never reaches hand
is a miss that vetoes the verdict.

The defect is in the *shape of the predicate*. `claim` carries exactly one
metric — the keys across all 71 lines are `{kind, metric, op, turn, value}`,
with no conjunction — so a two-part exploit can only encode one part. Driving
every line with its script deleted, **1 of 71 verifies on a claim its own null
case satisfies**: `cost_free_play_4_zero_energy_25_plays` claims
`energy_spent_in_turn == 0` on turn 1, which a pilot that plays nothing meets
trivially; its own hypothesis reads "25 cards played, 80 damage dealt, card_cap
degeneracy fired, and energy_spent_in_turn is EXACTLY 0" — the harness verifies
only the last clause. The other empty-script pass,
`relic_stack_5_zero_card_popper_wipe`, is **correct**: that line's script is
`[]` by design and "ZERO CARDS PLAYED" is the exploit.

| ID | Title | Class | Sev |
|---|---|---|---|
| O10-1 | A claim satisfied by the null case verifies; `claim` has no conjunction | SILENT-LIE | 4 |
| O10-4 | The ledger's documented repro command cannot run outside one container (`sys.path.insert(0, "/home/user/GItS")`) | LOUD (repro defect) | 3 |
| O10-2 | `executed: True` for a script that never ran — unreached turns are not misses (40 turns demanded, 16 fought, `misses: 0`) | SILENT-LIE | 3 |
| O10-3 | `_resolve_relics` discards the run-layer half of every relic with no surface (latent; no current line depends on one) | SILENT-LIE | 2 |
| O10-5 | The docstring promises a degeneracy-break exemption the code does not implement (harmless — leftovers never become misses) | doc/code drift | 1 |
| O10-6 | `cards_played_in_turn` counts pilot intent, not engine play events | tested, **CLEAN** (9 == 9) | — |
| O10-7 | Stale `replay-results.json` masking a broken line | tested, **CLEAN** (zero verdict flips) | — |

### Slice 11 — v14 `core_complete` limbs under adversarial deck compositions

Limbs enumerated: reaction (`appliers>=2 && amps>=1`), spotlight
(`access>=2 && machinery>=1`), fanfare (`generation>=5 && floor>=5.0 &&
drafted_readers>=1`), generic/v14 (`on_plan>=DRAFT_CORE_SIZE && payoffs>=1`),
their four `_core_progress` mirrors, and the two consumers `model.py:704
plan_live` and `model.py:728 time_to_online`.

**The predicate itself is mechanically sound.** Driven against synthetic
adversarial multisets and 500+ real `model.run_one` runs, it is
order-independent on every limb, pure (no mutation of the shared `peek_card`
prototypes), and **never vacuously True** — every bar is >=1, and an empty deck
gives 0.0 progress on all archetype strings including unknown ones and the empty
string. `_core_progress == 1.0` iff `core_complete` on **all four** limbs, not
merely the salon one `test_m5` pins. The spotlight `not _is_spotlight_access`
guard is load-bearing and correct. **No SILENT-LIE inside `core_complete`.** The
vacuous-True hypothesis in the brief is refuted, not merely untested.

| ID | Limb | Adversarial deck | Class | Sev |
|---|---|---|---|---|
| S11-2 | generic v14 | `core_complete(deck,"generic")` on the generic anchors | SILENT-LIE (metric-level) | 3 |
| S11-1 | generic v14 | 4 copies of one on-plan **payoff**, zero enablers | DECLARED-LIMIT (asymmetry), reachable | 3 |
| S11-7/8 | reaction, spotlight | 2 copies of ONE applier / ONE companion | ambiguity: bar met from one *distinct* card | 2 |
| S11-14 | consumers | `run_metrics.py:50` truthiness vs `ab.py:126` `is not None` | latent, not live | 2 |
| S11-12 | fanfare | Furina starter alone: generation **5.0** against a bar of 5 | DECLARED-LIMIT | 2 |
| S11-3/4/5/15 | all four | order battery, empty deck, threshold+-1, purity over 24 runs | **not defects** — verified clean | — |
| S11-6 | generic v14 | base + upgraded copy counts as 2 cards | DECLARED-LIMIT | 1 |
| S11-11 | generic v14 | core bent to `cost=99, exhaust=True` still complete | undeclared scope, unreachable from content | 1 |

S11-2: `core_complete(deck, "generic")` is **unreachable** on the klee and
furina generic anchors — 0/40 runs each (klee max deck `(1,1)`, furina max
`(3,2)`), against kokomi/generic at 9/40. So `plan_live` is True on 100% of
their screens and `time_to_online` is None for 100% of their runs, and
`online_rate`/`median_time_to_online` are structurally `0.0`/`None` rather than
measured — **indistinguishable from a real achievability failure**. Not caused
by v14 (the pre-v14 bar gives the same 0/40); it is the `generic` tag being
nearly absent from those characters' draftable pools, surfacing through the
instrument. A [USER] ruling.

S11-1 is classed DECLARED-LIMIT (the docstring's letter permits it exactly,
`draft.py:281-284`) but recorded because it is **reachable**: v14 closed
"enablers with no payoff" and left the mirror open, and the drafter lands there
on **15% of kokomi/priest online decks (3/20)** and 12.5% of commander. The
justification in `d294b51` ("Four enablers and no payoff was never an assembled
deck") is symmetric and unaddressed. Closing it is a DRAFTER_VERSION 15 bump and
a design ruling, not a bug fix.

### Slice 12 — Track H aura/payoff counters: `aura_ops` vs `applications`, absent-vs-zero, pooling

As the code actually implements them:

- **`aura_ops`** — `dict[op_name] -> count of aura_op events`; one per
  *resolution* of `apply_aura`/`swirl`/`refresh_all_auras`, regardless of target
  count or whether anything landed. One card play is 2 ops under the Salon
  replacement multiplier.
- **`aura_applications`** — one per `aura_applied` event, emitted **once per
  enemy** that received a *sticking* aura onto a previously clean body.
  Same-element refreshes and anemo/geo emit nothing.

Op-resolutions versus per-body landings. Measured `applications/aura_ops` on one
deck: 3.25 (punisher), 4.67 (gauntlet), **8.84** (swarm).

| ID | Axis | Title | Class | Sev |
|---|---|---|---|---|
| S12-A | pooling | Gauntlet stage-merge collides two combats into one record in every per-fight rate | SILENT-LIE | 4 |
| S12-B | absent/zero | `absent` payoff slices written to the TSV as `evaluated=0, fired=0, rate=0.0` | SILENT-LIE | 3 |
| S12-C | definitions | `swirl_op` is a declared application source that **can never be recorded** | SILENT-LIE | 2 |
| S12-E | pooling | `merge_stages` writes into `stages[0]`; re-merging silently doubles every counter | UNTESTED-PATH (latent) | 2 |
| S12-D | definitions | ops and applications printed adjacent as "/fight" though different units | DECLARED-LIMIT; **no shipped consumer divides them** (all use sites grepped) | 1 |
| S12-F/G | pooling | act-cut `zip` truncation (0/60 misaligned); `damage_by_turn` offset collision (0/200) | **checked, holds** | — |

**The pooled counts are correct** — `aura_profile`/`payoff_profile` sum
key-wise, do not mutate inputs, and are order-independent. The lies are in the
denominators and the labels. S12-A is TOP-5 #1 above.

S12-B: only the string column `{prefix}_absent` preserves absent-vs-zero;
**16 of 40** cohort rows and **77 of 91** battery rows are in that state. Over
the 10 cohort `all` arms the pooled rate is **0.5173**, the unweighted mean over
all 10 rows **0.3501**, and over the 6 carrying arms **0.5834** — three
different numbers a reader could take off the same TSV. In the dicts "zero" is
only ever expressed as key *absence*; an explicit 0 is never written. *Fix:
write the empty string, not `0` — the pattern `payoff_cards_drafted` already
uses.*

S12-C: `swirl_op` is declared as a provenance in `metrics.py:105-110`,
`tier0/README.md:71-73` and the corpus doc, is passed at exactly one site
(`effects.py:957`, element anemo), and `reactions.apply_aura:60-62` returns
before emitting for anything outside `AURA_ELEMENTS`. **0 occurrences in both
committed corpora**; a 100-fight swarm battery resolved 44 `swirl` ops and
recorded 0 `swirl_op` against 132 `swirl_spread`. Its absence is structural, not
a measurement of Swirl.

---

## Honest negatives

Recorded because a red-team that reports only hits is itself an instrument that
lies. Each was driven, not merely read.

- **`SPOTLIGHT_FORCE` does not leak on the exception path** (slice 6). The save
  is restored in a real `finally`; the nested case hands an outer force back
  intact; `KeyboardInterrupt`/`SystemExit` pass through the same block. The
  brief's predicted defect is not there.
- **Family A has no granted-play cousin in tier 0** (slice 8). Both paths were
  driven with the same card and all ten new counters diffed; the only difference
  is `energy_spent`, which the free-play contract declares. Pinned.
- **`core_complete` is never vacuously True, and is order-independent** (slice
  11). The empty-pool hypothesis is refuted across 8 archetype strings.
- **A truncated fight is never counted as a loss** (slice 5). No replayer
  aggregates a fight `outcome`; the fight is dropped, not miscounted. The
  brief's stated hypothesis is wrong — though `report.py`'s run-level outcome
  comes from the index, so the index's claim outlives the telemetry behind it.
- **The S13 ledger's 71/71 reproduces at 91e9258** with zero verdict flips
  (slice 10). Nothing is stale.
- **Track H's pooled counts are correct** (slice 12); only the denominators lie.
- **A `cards_played` row of the wrong arity fails loudly** (slice 5, S05-14), as
  does an unknown card, relic, encounter, metric, op or claim-kind in the S13
  harness (slice 10). Where these instruments are strict, they are strict.

---

## Two process findings, surfaced not fixed

Neither is a code defect; both silently degrade measurement, and both bit this
track during the run.

**P-1 — `game_ref/` was destroyed a third time, mid-session.** The memory note
`game-ref-recovery` predicted it ("Expect a third time"). It emptied while this
batch ran: the suite silently went from `1873 passed / 6 skipped` to
`1917 passed / 41 skipped` — **35 tests stopped running with no failure and no
banner**, which is precisely the failure class this track exists to catch. All
four non-regenerable files survive with real content (verified by *reading* them,
not by filename — the stub-backup trap) in seven sibling worktrees, e.g.
`.claude/worktrees/s7-fidelity/game_ref/` (26 files, `silent_pool.yaml`
present). This track restored **only its own worktree** from that donor and
deliberately did not touch the shared checkout. *Owed to [USER]: restore
`GItS/game_ref/`, and note the likely mechanism — a `Remove-Item -Recurse -Force`
on a directory **junction** into `game_ref` deletes through the link into the
target. Sibling worktrees that junction `game_ref` are a standing loaded gun;
`cmd /c rmdir <link>` removes the link only.*

**P-2 — the harness-pinned worktree is contended.** `.claude/worktrees/land2`
was cycled to `findings/track-p` and then `findings/track-q` by other leads
while this track's slices were mid-run, and two commits landed on it from
another track. This track's branch survived only because its artifacts were
untracked; a `git clean` from any co-tenant would have destroyed them. Work was
moved to a dedicated worktree. *Owed: one worktree per track lead, or an
explicit lock.*

---

## Counts

| Slice | Instrument | SILENT-LIE | DECLARED-LIMIT | UNTESTED-PATH |
|---|---|---:|---:|---:|
| 1 | P1.5 bridge seed | 8 | 4 | 8 |
| 2 | selector recording | 9 | 3 | 5 |
| 3 | resource reader | 12 | 1 | 7 |
| 4 | replayer cross-feed | 6 | 2 | 4 |
| 5 | malformed/truncated logs | 10 | 0 | 6 |
| 6 | `--use-selectors` / SPOTLIGHT_FORCE | 4 | 1 | 4 |
| 7 | Track D under partial fights | 6 | 0 | 4 |
| 8 | Family A cousins | 3 | 3 | 4 |
| 9 | soak `unexpected_start_state` | 8 | 0 | 4 |
| 10 | the S13 harness itself | 3 | 1 | 4 |
| 11 | v14 `core_complete` | 1 | 10 | 5 |
| 12 | Track H aura/payoff pooling | 3 | 1 | 5 |
| **total** | | **73** | **26** | **60** |

Pins: **87** across 12 files (`tier0/tests/test_track_o_s01..s06, s08..s10,
s12.py`; `tier05/tests/test_track_o_s07.py`, `test_track_o_s11.py`).
Suite at this commit: **1960 passed, 6 skipped, 14 xfailed** — baseline
`91e9258` was 1873/6/14, so every one of the 87 pins passes and nothing
regressed. No finding is pinned; no instrument file was modified.
