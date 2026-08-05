# Mutation round — the code tonight's batch added

> Last Call, Round Two, track K. 2026-08-05. **ZERO design authority.**
> S6's mutation audit (`review/mutation-audit/blind-spot-report.md`) ran over
> the tree as it stood BEFORE tonight's five merges. This is the same method
> run over what those merges added: 86 mutants across 8 target modules.
>
> **Iron rule, carried from S15: zero should-be findings.** A pin is written
> only where the correct behaviour is unambiguous from something that already
> existed — a field's own docstring, an emit-site comment, a CLI help string,
> a ratified ruling. Everything else is a FINDING, recorded with the mutant
> and with what it would take to specify it, and with **no opinion on what the
> behaviour should be**. Nothing in this document decides anything.

---

## Method

S6 was a report, not reusable tooling: one Opus agent per module, one hand
mutation at a time, no harness left behind. The approach is reproduced here
and driven instead of hand-run — a mutant table (`(id, target, file, old,
new)`, `old` required to occur exactly once), applied by exact string
substitution, then reverted, with the target's test subset run in between.

- **Kill** = the target's subset goes red under the mutant.
- **Apparent survivor** → re-run under the **full suite** (`pytest -q -x`),
  S6's second stage, because a mutant a narrow subset misses may still be
  caught by a battery test somewhere else. Every apparent survivor below was
  confirmed against the full suite; none of them were killed by it.
- Operators used: comparison swaps (`>=`/`>`, `!=`/`==`, `and`/`or`), sentinel
  and default swaps (`-1`/`0`, `None`/`""`, `True`/`False`), denominator and
  bucket swaps, constant bumps, dropped guards, dropped accumulations,
  reordered teardown steps, off-by-one indexing.

Baseline in the round's worktree (`origin/main` @ `8daedb7`, `game_ref`
junctioned): **1810 passed, 6 skipped, 14 xfailed** in 160 s. The six skips
are the gitignored-art / unbuilt-pck guards, i.e. the "committed-only" shape.
With this round's 32 pins: **1842 passed, 6 skipped, 14 xfailed**, green in
both `-p no:randomly` and the default randomised ordering.

All 43 apparent survivors were re-run under the full suite. **None of them was
killed by it** — every gap the scoped subsets found is a gap the whole suite
has, which is worth stating because the scoped-subset shortcut is the part of
this method most likely to be doubted.

### Out of scope, stated once

`vendor/STS2_MCP/gits/GitsSeed.cs`, `gits/GitsResources.cs` and the
`McpMod.cs` / `McpMod.StateBuilder.cs` edits are **C# and were not mutated**:
the harness is Python, and there is no C# test project in this repo to
measure a kill against (`docs/` and the co-op notes have said so since the
co-op backstop finding). Their Python-side contract — the endpoint URL, the
payload shape, the `resources` key — *is* mutated, under target G/F.

### Test subsets

| target | subset run per mutant |
| --- | --- |
| `metrics` | `test_pin_track_d_telemetry`, `test_track_d_telemetry`, `test_pin_tier0_harness`, `test_combat`, `test_effects`, `test_axes`, `test_ic_effects`, `tier05/test_pin_tier05_metrics`, `tier05/test_runner` |
| `emit` | as above, plus `test_pin_engine_combat`, `test_pin_engine_powers`, `test_pin_engine_reactions` |
| `reaction_telemetry` | `tier05/test_pin_reaction_telemetry`, `test_reaction_telemetry`, `test_runner`, `test_elite_blitz` |
| `draft` | `tier05/test_pin_draft_v14`, `test_m5`, `test_pin_tier05_draft`, `test_m6`, `test_m7`, `tier0/test_patch_sentinel` |
| `trace_replay` / `soak` | `test_pin_understudy_p15`, `test_understudy_p15`, `test_understudy_soak`, `test_understudy_committed`, `test_understudy_rng`, `test_understudy_policy_v1` |
| `bridge` | `test_understudy_p15`, `test_understudy_soak`, `test_vendor_pin` |

---

## Kill rates

Two columns, because the pins written by this round are part of the answer.
**Before** is the tree as tonight's batch left it. **After** is the same 86
mutants against the same subsets with this round's pin files added.

| # | target | file | mutants | killed (before) | killed (after) | survived (after) |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A | D1/D2 telemetry fields & aggregates | `tier0/harness/metrics.py` | 22 | 8 (36%) | 20 (91%) | 2 |
| B | telemetry emit sites | `tier0/engine/combat.py`, `powers.py` | 8 | 3 (38%) | 6 (75%) | 2 |
| C | per-act reaction share | `tier05/reaction_telemetry.py` | 9 | 6 (67%) | 8 (89%) | 1 |
| D | v14 `core_complete` limbs | `tier05/draft.py` | 11 | 9 (82%) | 11 (100%) | 0 |
| E | recording comparison | `understudy/trace_replay.py` | 16 | 7 (44%) | 13 (81%) | 3 |
| F | soak: meters, selectors, seeds, bound | `understudy/soak.py` | 17 | 7 (41%) | 16 (94%) | 1 |
| G | bridge seed endpoint | `understudy/bridge.py` | 3 | 3 (100%) | 3 (100%) | 0 |
| — | vendored C# fork | `vendor/STS2_MCP/gits/*.cs` | — | not run (no C# test project) | — | — |
| | **total** | | **86** | **43 (50%)** | **77 (90%)** | **9** |

Read the "before" column the way S6's is meant to be read: it measures what
the batch's own tests would CATCH, not whether the code is right. Track D and
P1.5 both shipped substantial test files; what those files pin is what the
instruments PRODUCE on a real battery. What survived is almost entirely
DEFINITIONS — denominators, sentinels, which bucket an event lands in, which
screen counts as a choice — each of which leaves every produced number
well-formed while changing what it means.

`draft` (82% before) and `bridge` (100%) are the two targets that were already
well covered; both are small, recent, and were written with their own boundary
tests. `metrics` (36%) and the emit sites (38%) are the thin spots, and
`trace_replay`/`soak` are thin in the same way: the code that only runs when
something is unusual — an old log, a refused seed, a turn the fight ended
inside — had nothing standing on it.

---

## Pins written

34 mutants moved from SURVIVED to KILLED. Four new files, 32 tests, in the
S15 pin idiom (`test_pin_*.py`, one docstring per test naming the source of
truth it is quoting).

| file | tests | kills |
| --- | ---: | --- |
| `tier0/tests/test_pin_track_d_telemetry.py` | 11 | A3, A4, A6, A13, A14, A15, A16, A17, A18, A19, A20, A21, B1, B3, B7 |
| `tier05/tests/test_pin_reaction_telemetry.py` | 2 | C2, C6 |
| `tier05/tests/test_pin_draft_v14.py` | 2 | D3, D10 |
| `tier0/tests/test_pin_understudy_p15.py` | 17 | E3, E7, E8, E12, E14, E16, F3, F7, F8, F9, F10, F12, F14, F15, F17 |

Sources of truth quoted, so the citations can be audited rather than trusted:

- `metrics.damage_all_ops.__doc__` — "the enemy-side DoT, which the `damage`
  event stream never carried" → the D1 denominator, and therefore both the
  complement and the quotient derived from it (A3, A4).
- The D1 field comment enumerating amp / splash / dot → an Overload splash
  belongs in `reaction_damage_splash` (A6), and a merge carries each bucket
  into its own sibling (A18, A19).
- `metrics.reaction_share.__doc__` — "POOLED, not averaged over fights" and
  `share_by_fight_mean` "because the two answer different questions" (A13).
- The `turn_trajectory` comment — "-1 ... an unsampled value, never a zero" —
  and `turn_profile.__doc__` — "skips the -1 rows ... so a mean over two turns
  is not mistaken for a mean over two hundred" (A15, A16, A17, A20).
- The `turn_open` / `turn_close` emit comments — "the block that SURVIVED the
  enemy" vs "the block standing when the player hands the turn over" (B1, B3).
- The `dot_tick` emit comment — "`to_player` is explicit rather than inferred
  from `target`: an enemy may legitimately be named 'player' in a fixture"
  (B7).
- `reaction_telemetry._fight_contexts.__doc__` — "only N/E/B nodes run a
  fight", naming `elite_blitz._fight_contexts` as the precedent (C2).
- `core_complete.__doc__` as amended by DRAFTER_VERSION 14 — "DRAFT_CORE_SIZE
  on-plan enabler/payoff cards, AT LEAST ONE of which is a payoff" (D3), and
  `_generic_core_counts`' single `archetype in c.archetypes` filter (D10).
- `trace_replay.FIGHT_KEYS.__doc__` — "fields that IDENTIFY a fight ... as
  opposed to describing it" (E3); the SEED finding's own text — "nothing below
  is a comparison" (E7); `compare_runs.__doc__` — "an empty list is the
  acceptance condition" (E12); `seed_of.__doc__` — "`chosen` is None on a
  read-back run" (E16).
- soak.py's "UNSEEN, NOT EMPTY" block — "only the ABSENCE of the map leaves
  the column unseen" (F3); the `SELECTOR_SCREENS` comment — "`overlay` ... a
  screen nobody can answer has no choice to record" (F7); the `--max-fights`
  help and the bounded-stop comment — "stop the run cleanly after N closed
  fights", "the fight that is open has already closed" (F8, F9); the
  read-back-is-the-verification comment (F10); `note_seed_channel.__doc__` —
  "the trigger is the first CHOICE, not the setup" and "Idempotent -- N runs
  share one entry" (F15, F17); the teardown comment — "THE SEED RELEASE GOES
  FIRST, and it runs unconditionally" (F14); the `--seed` help — "run i takes
  seed i, cycling" (F12).

Two pins are worth calling out because they pin a USE rather than a value, and
the use is where the mutation lived:

- **F7.** `test_the_selector_screen_set_excludes_overlay` already pins the
  tuple. The mutation did not touch the tuple; it widened the condition at the
  call site to `MID_FIGHT`, which re-admits the overlay with the tuple intact.
- **D3.** `test_generic_core_requires_a_drafted_payoff` pins that both limbs
  bite. It does not pin where the assembly limb's edge falls, and a strict `>`
  moves `core_complete` one card later while `_core_progress` still reads 1.0
  — which is the exact predicate/progress drift `_generic_core_counts` was
  extracted to make impossible.

---

## Survivors

9 after the pins: **7 findings and 2 equivalent mutants.** None of these is a
bug report and none carries a recommendation. Each row is: the mutant that
lived, the behaviour nothing states, and what it would take to state it.

### Findings — behaviour genuinely unspecified (7)

| id | site | mutant that survived | what is unspecified | what it would take to specify it |
| --- | --- | --- | --- | --- |
| **K-1** | `metrics.extract`, `dot_tick` branch | `ev.get("to_player", True)` → `ev.get("to_player", False)` | What a `dot_tick` event **without** a `to_player` key counts as. Today the only emitter always sets it, so the default is unreached; the field comment explains why the flag is explicit but says nothing about its absence. | A line stating either that the key is mandatory on `dot_tick` (and a red test on an event lacking it), or which side an event without it is attributed to. Both are one sentence; neither exists. |
| **K-2** | `metrics.extract`, `dot_tick` branch, and `powers.on_turn_start` | `effective = min(hp_loss, ...)` → `min(dot, ...)` | What `effective` means on a **player-side** tick that Encore partly absorbed — the tick as printed, or the part that reached HP. The overkill clamp is documented; the interaction with Encore absorption is not. No consumer reads the player-side value today (D1 routes on `to_player` and takes enemy-side only). | A ruling on the definition, or a statement that `effective` is defined for enemy-side ticks only and undefined elsewhere. Note that if a later instrument reads player-side `effective`, this becomes load-bearing before anybody notices. |
| **K-3** | `combat._player_turn`, `turn_open` | `hp=max(0, state.player.hp)` → `hp=state.player.hp` | Whether the clamp is reachable. The comment cites the `round_hp` precedent (which clamps identically at line 804, as does `hp_left` at 860), so the SHAPE is house idiom; what is unstated is whether `player.hp < 0` can reach a turn opening at all. No construction was found in this round that reaches it. | Either a demonstration that a negative-HP turn opening is reachable (Fairy revive ordering is the candidate path), or a line recording that the clamp is defensive and unreachable — the same note `tier05/relics.py` puts on its skipped relics. |
| **K-4** | `reaction_telemetry.aggregate` | `b["fights_with_any"] += bool(fs.damage_from_reactions)` → `bool(fs.reactions)` | What `fights_with_any` is any **of**. The module header defines `amp`, `splash`, `dot` and `share` and stops there; the key name does not finish the sentence, and both readings are live in the same module (`reactions` is in the same bucket). The sibling key in `metrics.reaction_share` **is** unambiguous — `fights_with_any_reaction_damage` — and is pinned (A14); this one is the same quantity under a name that does not say so. | Either a definition line in the module header, or a rename to match the tier-0 sibling. The rename is a doc/report change and is [USER] surface: the key is printed in `format_block`. |
| **K-5** | `soak._meters` | drop the `_ENCORE_RESOURCE_ID not in resources` guard from the fallback | What a `resources` map carrying an Encore value that will **not parse as an int** should record: `-1` (unseen — the value could not be read) or `0` (the map was present, so the meter was visible). "Only the ABSENCE of the map leaves the column unseen" reads one way; "a number this file cannot see is recorded as unseen" reads the other. Both sentences are in the same docstring. | One sentence choosing between them. The two rules only collide on a malformed wire value, which is why the collision shipped unnoticed. |
| **K-6** | `trace_replay.selector_lines` | `(list(row) + [None] * 5)[:5]` → `[None] * 4` | The minimum selector-row width a reader must accept. Padding by 5 tolerates a row of length 0; padding by 4 tolerates length ≥ 1. Rows written by any recorder that exists are length 5, and `trace`'s stated rule ("reads as empty rather than raising") is about missing KEYS, not short ROWS. | A statement of the row contract — either "selector rows are always 5-wide and a short row is corrupt" or "readers pad to 5 from any width". The meter-row equivalent (`len(m) > 4`) IS now pinned, via a 4-wide pre-Encore row that a real older recorder wrote; no such artefact exists for selectors, because the field is P1.5-new. |
| **K-7** | `trace_replay.describe_run` | `all(e == -1 for e in encore)` → `any(...)` | What the one-word `encore=UNSEEN` label means on a run whose meter rows are **mixed** — some turns read, some unseen. `all` reports UNSEEN only if the meter was never once read; `any` reports it if it was ever missed. Nothing states which question the label answers, and a mid-run bridge swap or a fight opened before the resource map existed makes the mixed case real. | A line saying what the column is claiming, or a second column. This is a report-legibility question and it touches a printed artefact. |

### Equivalent under the current code (2)

Not findings. A mutation whose effect no reachable input can distinguish is
not a gap in the tests; recording them stops a later round re-deriving them.

| id | site | mutant | why it cannot be observed today |
| --- | --- | --- | --- |
| A22 | `metrics.extract` | `turn_open[t] = ...` → `turn_open.setdefault(t, ...)` (last write vs first) | `state.turn` only increments and `turn_open` is emitted once per player turn, so within one `extract` no turn number is written twice. Staged fights are merged by `merge_stages`, not by re-extraction. |
| E5 | `trace_replay.fights` | `r.get("record") == "fight"` → `"fight" in str(r.get("record"))` | No other record tag `soak` emits contains the substring "fight": the vocabulary is `run_begin`, `seed_read_back`, `seed_chosen`, `fight`, `defect`, `decision`, `bounded_stop`, `game_over`, `forced_default`, `run_end`. Latent, not live — a future tag such as `fight_open` would make the two differ silently. |

K-3 (the `turn_open` HP clamp) sits between the two tables: on the code as it
stands, the clamped and unclamped forms produce identical logs, which is why
it is filed as a finding about *reachability* rather than as an equivalent
mutant outright.

---

## What this round did not do

- It did not change any behaviour. Every file touched outside `docs/` is a new
  `test_pin_*.py`; no source line moved.
- It did not grade anything. No number in this document is evidence about
  balance, difficulty, legibility or fun — the same Guardrail-7 fence
  `trace_replay` prints on its own reports.
- It did not mutate the C# fork, and the 90% figure above is a Python-side
  figure. The vendored bridge's `gits/` endpoints have exactly the coverage
  their Python callers give them, which is the endpoint URL, the payload
  shape, and the marker/manifest discipline `test_vendor_pin` enforces.
- It wrote no pin whose correctness rests on this session's judgement. Where
  the judgement would have been needed, there is a row in the findings table
  instead.
