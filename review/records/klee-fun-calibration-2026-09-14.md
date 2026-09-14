Status: RECORD (a registration at the Prototype stage; results appended per build)

# Klee fun calibration: can the seats stand in for [USER] on three questions?

Written 2026-09-14 from the process reflection of the same day. Prototype
stage, so measurement law does not bind (`stage-gate.md`): no slate, no
countersign, no register row. What binds is the order of events written
here, which a commit hash proves, and the scoring rule, which is fixed
before any answer exists.

## 1. The question this answers

Nine days of the overhaul produced 916 commits, 77 seat rounds across three
kits and four [USER] runs. The two rulings that moved Klee (R265, R270) came
out of [USER]'s two runs; Furina's reframe ran 16 seat rounds before [USER]
reset it, and no round saw the reset coming. The loop's only trusted fun
sensor is [USER], and it reads about once every two days. The seats already
write what bored them and what felt dead (`RUN_QUESTIONS`, the Opus brief's
§3), but the machinery says out loud that nothing they write is evidence
about fun (`understudy/README.md`, "No fun, ever"; `RECORD_DISCLAIMER`).
Nobody has tested whether that sentence is true of the current seats.

**The calibration asks one thing:** when a seat and [USER] play the same
build on the same seed and answer the same three questions, do they name
the same turns and the same card?

## 2. The three lines

Every seat, and [USER], answers at the end of an act-1 run, one line each:

1. `MOST WANTED TURN: fight N turn N -- why`
2. `NOTHING TURN: fight N turn N -- why` (the turn that felt like nothing;
   "none" is an answer)
3. `NEVER AGAIN: <card title> -- why` (the card you would never draft again;
   "none" is an answer)

They are asked in the same shape by the backend seats
(`understudy/blindplay_session.py` `RUN_QUESTIONS` items 6-8), by an Opus
seat (`docs/current/operations/seat-brief.md` §4) and of [USER] by the
sitting. Both seat instruments changed on this commit (the prompt's sha256
is stamped on every sealed record, so the change is visible); every
calibration seat plays on the changed instrument, and no round before this
commit is comparable on these three lines.

## 3. Procedure, per build

Three builds, the first being R271 §8 stage one (`EB-749`), then stage two
(the Mines batch), then whatever round 28's finding builds.

1. The build is deployed `+proto` and the seed for the calibration run is
   chosen and written here BEFORE any seat plays.
2. **Three seats play act 1 on that seed:** two blind Opus seats (lanes 1
   and 2) and the Codex seat (`tools/seat.py --backend codex`), the round's
   ordinary read. Their records land under `review/qa/klee-round-<n>-<date>/`
   and their three lines are copied into §5 below **and committed** before
   [USER] plays. The commit hash is the seal.
3. **[USER] plays act 1 on the same seed** (the game's seed entry), for as
   long as act 1 takes, and answers the three lines in a message. The
   sitting copies them into §5 verbatim, under the seal's hash.
4. **[USER] scores agreement**, three yes/no marks per seat: does the
   seat's line name the same turn (same fight, same turn, or the same play
   on a neighbouring turn where the draw differed) and the same card, or
   "none" on both. A "why" that names a different reason for the same turn
   is still a match; a different turn with the same reason is not.

## 4. The scoring rule, fixed now

- **A seat AGREES on a build** when at least two of its three lines match.
- **A build AGREES** when at least two of the three seats agree.
- **The seats become the daily fun sensor** if two of the three builds
  agree. Then `understudy/README.md`'s second rule and `RECORD_DISCLAIMER`
  are amended on this evidence to say what the seats can carry (the three
  lines, as opinion calibrated against [USER] on named builds), [USER]
  reads once a week, and the round loop closes at seat speed.
- **Otherwise the sentence stands as written**, the calibration closes with
  that result, and the process turns the other way: fewer builds, more
  paper design per build, every build sized to what one [USER] run can
  judge.

Either outcome licenses exactly the change named for it and nothing else. No
number on any prototype row is quotable off this record (R215 B).

## 5. Results

### Build one — `EB-749`, stage one of R271 §8

_Seed: (written before any seat plays)._
_Seats' three lines: (copied and committed before [USER] plays)._
_[USER]'s three lines: (verbatim)._
_Agreement: (three marks per seat)._

### Build two — stage two, the Mines batch

_Not yet built._

### Build three

_Not yet built._

## 6. Defaults applied (E), disclosed

- The three questions, their shape and the same-seed rule are the
  instrument; a seat answering off-shape is asked once more and then
  recorded as it answered.
- Agreement is [USER]'s reading, not a grader's: the question is whether
  the seat tracks [USER], so [USER] is the reference by construction.
- Two-of-three at each level is the threshold because a one-of-three
  sensor would be no better than reading a round at random, and
  three-of-three would fail on one bad seed.
- The Klee done gate this calibration serves is written in
  `docs/current/operations/stage-gate.md` under the Prototype loop.
