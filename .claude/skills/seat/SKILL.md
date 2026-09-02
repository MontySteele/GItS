---
name: seat
description: Run one blind seat end to end - embark a lane, play the run through blindplay session with the right environment, tear the lane down - or print the blindness brief to hand an Opus seat. Use for any blind-play round.
---

# seat — embark, play, tear down; or brief an Opus seat

## A backend seat (codex or the local model)
```sh
python tools/seat.py --lane 1 --character KLEEMOD-KLEE --backend codex
python tools/seat.py --lane 2 --character KLEEMOD-KOKOMI --backend local \
    --max-actions 70 --max-wall-s 5400 --dry-run   # print the 3 commands
```

Prints the record path, action count and termination reason. Teardown runs even
when the session fails, so the lane's game never outlives the round.

Two variables it sets that are expensive to forget: **`GITS_LANE`**, the only
way the design-blind `blindplay` commands find the lane, and
**`GITS_LOCAL_PLAY_TOKENS=12000`** for the local backend — at the 4096 default
the reply truncates and the round dies with the game already up.

## An Opus seat (a subagent playing by hand)

```sh
python tools/seat.py --opus-brief --lane 2 --character KLEEMOD-KLEE
```

Prints `docs/current/operations/seat-brief.md` with the lane filled in. **Paste
it; never rewrite it.** A rewritten brief is a different instrument, and two
rounds graded against two briefs are not comparable.

## Standing rules

- **A lane above zero is never a run of record**: its profile is disposable and
  nothing in it is read back. **Lane 0 is the owner's own game** and is refused
  without `--allow-lane-0`.
- **The seat's model family may not be the author's** (R217 C), and the record
  carries the non-blindness declaration.
