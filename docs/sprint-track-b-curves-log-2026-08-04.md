# Sprint log — Track B: the two feeds and the first curves (2026-08-04)

Session: the hand-back note of 2026-08-04 evening
(`docs/handback-note-2026-08-04.md`), executed in order. Worktree G4.
Item 1 (the clean N=3) is recorded as **R98** and in
`docs/sprint-understudy-p1-log-2026-08-04.md`; this log is **Item 2**.

Charter: `docs/axis-validity-session-charter.md` §4. Deliverables: **B1** the
demand curve, **B2** the output curves over it, both from **two feeds**, both
labelled with their feed, and every empty cell left empty.

Status: **B1 and B2 SHIP for Act 1 on the bot feed. Acts 2 and 3 are EMPTY and
stay empty until the human feed plays there.** The generated document is
`docs/track-b-curves.md`; it regenerates with
`python tools/track_b_curves.py --out docs/track-b-curves.md`.

---

## What landed

| item | where |
|---|---|
| The human feed (C#, on by default, no UI) | `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs` |
| Its registration, on the single hook chain | `klee-mod/KleeCode/KleeMod.cs` |
| Bot-feed telemetry additions (pool, meters, end-of-turn block, feed labels) | `understudy/soak.py` |
| B1 + B2 generator | `tools/track_b_curves.py` |
| The curves | `docs/track-b-curves.md` |
| Tests | `tier0/tests/test_track_b_curves.py` (15) |
| Schema, now a live shared surface | `understudy/README.md` |
| The hand-back note, verbatim | `docs/handback-note-2026-08-04.md` |

**Nothing in `tier0/`, `tier05/`, the drafter or any sheet moved.** No balance
value, no card, no floor, no axis disposition, no drafter price. The only
number this pass added to the C# side is a schema version string, and the
constant-parity lint confirms it: 71 mirrored, 16 declared unmirrored,
unchanged.

## The two feeds, and why the second one had to exist

Understudy debt #3 — the bots die in Act 1 — caps the **bot** feed and nothing
else. A demand curve for Acts 2 and 3 needs somebody to reach Acts 2 and 3, and
the only instrument that does that is [USER] at the table. So Track B is built
on two feeds writing **one schema**:

| | bot feed | human feed |
|---|---|---|
| written by | `understudy/soak.py` (policy_v1) | `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs` |
| tagged | `feed: "bot"`, `source: "soak"` | `feed: "human"`, `source: "mod"` |
| seats | 1 | as played — one record PER SEAT |
| density | dense and cheap | sparse, on the table's schedule |
| reach | Act 1 | wherever the run goes |
| attribution | enemy HP drop observed after an action | the damage hook itself, with dealer and card |

**Zero friction was a requirement, not a preference.** The hook is on by
default in normal play, has no UI, no toggle and no export step, and writes to
`user://gits_telemetry/` — `%APPDATA%/SlayTheSpire2/gits_telemetry/`. It is
*outside* the mod directory on purpose: `deploy.ps1` deletes and re-copies
`mods/klee`, so the KleeArt idiom (write beside the dll) would destroy the log
at exactly the moment it holds the newest data. A test pins the path.

**Three rules the hook obeys**, in the order that breaking them costs:

1. It never touches game state and never consumes game RNG. Co-op is
   deterministic lockstep; a desync caused by a *measurement* would be the
   worst defect this repo has shipped.
2. Every entry point is wrapped. An exception out of a combat hook lands in an
   async continuation and takes the run with it (finding 21's failure mode).
   And `Subscribe` is wrapped too, because it runs inside the roster's single
   hook delegate — a throw there would disable the aura, resource and garment
   hooks concatenated beside it.
3. The JSON is hand-written, not reflected. The key names **are** the shared
   schema; a serializer deriving them from field names would turn a C# rename
   into a silent cross-session break.

## Cross-session note — the telemetry schema is now a LIVE shared surface

Filed here per D4/D5 and the house pattern (`docs/animation-sprint-2-log.md`).
P1's note said this section was "a heads-up rather than a cross-session note,
because Track B has not started reading it". **Track B has now started reading
it**, so the heads-up is discharged into the real thing.

**Who reads and writes the surface, as of this commit:**

| surface | role |
|---|---|
| `understudy/soak.py` → `FightTelemetry.as_record` | writer (bot) |
| `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs` → `FightRecord.ToJson` | writer (human) |
| `tools/track_b_curves.py` | reader (B1/B2) |
| `understudy/report.py` | reader (the morning report) |

**The rule, restated where it now bites:** *adding* a key is free; *renaming or
repurposing* one is a cross-session change that takes its note first. Two
writers in two languages cannot see each other, so
`tier0/tests/test_track_b_curves.py::test_the_two_feeds_write_the_same_fight_record`
compares the key sets directly and names each permitted asymmetry
(`potions_used` is bot-only — no first-party potion hook exists for the mod
side; `character` and `ts` are mod-only). A drift in either direction is a red
test, not a discovery six weeks later.

**What changed under that rule in this pass — all ADDITIONS:** `schema`,
`feed`, `source`, `seats`, `seat_index`, `character`, `enemy_pool_by_turn`,
`meters_by_turn`, `block_at_turn_end`. Nothing was renamed. Logs written before
today carry none of them, and the reader treats a missing `feed` as `bot`
rather than as unlabelled — which is what those logs are.

**Three measurements the additions buy, and why each was not already there:**

- `enemy_pool_by_turn` — *the honest output curve*. `damage_by_source` credits
  the play the reader happened to observe next, and demonstrably under-counts:
  in the first validation soak a fight with 44 HP of enemies attributed 33. The
  pool's own drop between two turn openings cannot under-count, because it does
  not care who did it.
- `block_at_turn_end` — block sampled at the turn OPENING is whatever survived
  the enemy's turn. That is a different quantity wearing the same word, and the
  wrong one to lay over a demand curve.
- `meters_by_turn` — the instrument the Salon pre-registration names. Read by
  power ID, not by title: a display name is loc data and moves with a wording
  pass.

## Guardrail 7, enforced rather than promised

Every table in `docs/track-b-curves.md` is headed with its feed, the two feeds
are never averaged, and `--` means *no fight of that shape has been recorded by
that feed*. Tests hold all three: one asserts the banner and the R14 reference
survive, one asserts no row mixes feeds, one asserts an act with no data
renders empty **and is named as empty** rather than quietly interpolated from
its neighbour. A bot-feed number is a **bot-limited floor** — what a heuristic
with declared reductions managed on read-back seeds, not what the fight demands
of a person.

## The pre-registrations, GRADED BEFORE ANYTHING WAS READ INTO THE RUN

Both carried in from R89/R95 via §7.8 of the Track A log. The grading rule was
fixed before the numbers existed: **grade only where the data supports it, and
name the instrument where it does not.**

<!-- GRADES -->

## Reversibility ledger — game-directory changes this session

| # | change | undo | state |
|---|---|---|---|
| 1 | `steam_appid.txt` created at the game root (three soaks) | `Remove-Item steam_appid.txt` | **REVERTED** by each soak's teardown |
| 2 | `mods\STS2_MCP\` deployed from the vendor pin (three soaks) | `.\build\deploy_bridge.ps1 -Remove` | **REVERTED** |
| 3 | `SlayTheSpire2.exe` launched directly (three soaks) | terminated at teardown | **REVERTED** |
| 4 | `FastMode=Instant`, `TimeScale=3.0` via the speed endpoint | `POST {"enabled": false}` | **REVERTED** on soaks 2 and 3; **NOT REVERTED** on soak 1 (the bridge was gone — the game had died). Leak-checked and clean: soak 2 captured `fast_mode: "Fast"` at setup, so `Instant` never reached `settings.save` |
| 5 | `mods\klee` replaced: **0.2-247 → 0.2-288** | `git checkout 0691724 && cd klee-mod && .\build\deploy.ps1` | **STANDING BY DESIGN** — the human feed cannot record [USER]'s sessions from a build that does not contain it. In the gate package. |
| 6 | `user://gits_telemetry/` created (`%APPDATA%/SlayTheSpire2/`) | delete the directory | **STANDING BY DESIGN** — this is the human feed's log directory |

Entry 5 is the one that is not self-reverting, and it is deliberate: the point
of a zero-friction hook is that it is already there the next time [USER] plays.
It is a **content-identical build plus a read-only hook**, validated by
`validate.ps1` (OK, all rules) on a clean tree — but it is a build change to
the game [USER] plays, so it goes in front of them rather than in a footnote.

Worktree-local, gitignored, and NOT repo changes: `klee-mod/local.props` and
`game_ref/` copied from the main checkout; `ImageGen/images/` copied and
`.venv` / `art/raw` junctioned so `deploy.ps1`'s own gates (S6*, S7, S10) could
actually run rather than skip.
