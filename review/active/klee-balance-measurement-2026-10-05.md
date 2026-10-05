# Klee at Balance: what to measure

Paper, 2026-10-05, main session. [USER] ruled Klee to Balance on 2026-10-03
(`QUEUE.md`), then: "time to properly measure Klee! This includes thinking
through the old legacy instrumentation and figuring out what actually makes
sense in the first place - is the old plan still too cumbersome to be worth
doing?"

Short answer: yes, it is too cumbersome, and worse, it measures the wrong
game. The instrument that can see Klee already exists and is already
recording. Five picks at the end.

## 1. What the old plan asks

`docs/current/operations/stage-gate.md` (the Balance paragraph) and
`docs/current/EXPERIMENTS.md`, which "binds in full" at Balance:

- Klee's rows are re-authored onto "the character's real sheet" under a
  `CONSTANTS_VERSION` bump.
- Every measurement a playtest will grade is pre-registered: Claude drafts a
  slate, commits it before any run, you countersign within five days, and the
  grade goes in blind.
- Every number is world-stamped (RT/D/P/C) and run through a sim `Cell`.
- **Exit: the twelve-arm sim re-baseline publishes.**

## 2. Why it no longer fits

1. **The sim cannot see where Klee loses.** 200 sim runs of the current kit
   (`tier05.runner --character klee`, stamp RT13/D18/P11/C22): 0 wins, act 1
   cleared in 40%. In the real game, seats cleared act 1 in all six of her
   last six runs (final-pass, Opus-check and pre-Balance rounds,
   `review/records/klee-*-2026-10-0[24].md`). She dies to Thorns, Frail and
   Weak attrition, and the Kaiser Crab. Thorns and on-hit status injection
   are not modelled (`BACKLOG.md`, SKIP-10.9), and the sim's act-3 boss
   "cannot test this boss" (`BACKLOG.md`, Aeonglass).
2. **The last re-baseline changed nothing.** The 2026-08-26 twelve-arm table
   (3,000 runs an arm) says of itself "it recommends nothing, tunes nothing"
   (`review/records/sitting-reads-2026-08-26-c20-d18-p11.md`). No card or
   number moved because of it.
3. **Klee's real balance work never used it.** Her 2026-09-25 pass shipped 13
   number changes from yardsticks, your play and two seats, with no sim read
   (`review/records/klee-balance-2026-09-25.md`).
4. **The machinery is gone.** The twelve-arm script was deleted (commit
   `38cb6e0b`). The "real sheet" (`docs/klee-cards.yaml`) was deleted by
   legacy cleanup stage 5. The calibration bands are retired. Two of the
   table's three kits (Furina, Kokomi) are prototypes, and "no number
   measured on a prototype row is quotable" (`EXPERIMENTS.md`).
5. **Cost before the first number.** About six code tasks (restore the
   script, the `EB-195`/`EB-255`/`EB-810` bump, port the Aeonglass, archetype
   tags, re-author a sheet), plus a slate and a countersign.

## 3. What can see Klee: the real game

Every fight on every seat lane, and in every game you play, writes one line
of telemetry (`klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs`). Each line
holds the encounter, HP lost, turns, damage by card, statuses and reactions.
There are 1,366 Klee fights and 804 base-character fights on file today.

A first read, single-player fights only, counting Klee's fights since the
final pass (2026-10-02) and the base five's from every lane. Each figure is
the median across fights.

| Normal fights | Damage a turn | HP lost, % of max | Fights |
|---|---|---|---|
| Base five, act 1 | 11.8 | 7.5 | 403 |
| Klee, act 1 | 15.8 | 11.1 | 74 |
| Base five, act 2 | 26.5 | 10.4 | 113 |
| Klee, act 2 | 17.4 | 16.0 | 37 |
| Base five, act 3 | 38.2 | 9.5 | 94 |
| Klee, act 3 | 24.0 | 14.3 | 7 |

**Klee out-damages a base character in act 1, then falls to about two
thirds of its damage and takes about one and a half times its HP loss in
act 2.** That is the seats' story (clears act 1, dies in act 2 short of
Block), now with a number. The other kits show the same act-2 gap (Varka
19.6, Furina 16.1, Kokomi 13.2), but their figures span several builds.

**Caveats.**
- The figures are bot seats, not humans.
- Klee's act-3 sample is small (7 fights).
- Block is logged for Klee only today.
- Base characters' Poison and orb damage may be under-counted. If so, the
  real gap is wider, not narrower.

## 4. Proposal: Balance measured on the real game

- **The bar.** Klee plays at a base character's level. The base five's
  Sonnet baseline (`review/records/base-five-baseline-2026-10-05.md`) is
  0/5 at A0, with every run ending in act 3. Klee meets the bar when:
  - her runs reach act 3 as the base five's do;
  - her act-by-act damage a turn and HP lost sit within about 15% of the
    base five's;
  - your run says she is fun.
- **Instruments.**
  - A telemetry report: one tool that prints the table above for any
    character and build range, plus per-card play and damage rates. The
    rates replace the sim's "taken from over 70% of offers, played in under
    5% of fights" checks.
  - Block logged for every character.
  - Klee seat runs on the baseline's five seeds, so each run pairs with a
    base character on the same map.
- **Predictions, kept light.** Each balance change states its expected
  effect in one line in its own paper, before the round (for example, "act-2
  damage a turn from about 17 to about 21"). The next round's telemetry
  grades it. This keeps the part of pre-registration that matters (no moving
  goalposts) without slates or countersigns.
- **The sim.** It is not used for the Balance gate. Kit design sims in
  Prototype (`tools/varka_expansion_sim.py` and the like) stay. The
  re-baseline items (`EB-195`, `EB-255`, `EB-810`, the Aeonglass port) are
  parked.
- **Rows** stay on `docs/prototype-surface.yaml`. `STATE.md` records the
  stage, so there is no re-authoring and no `CONSTANTS_VERSION` bump.

## 5. Cost

- One coding task: the telemetry report, and Block logged for every
  character.
- One Klee round on the five baseline seeds through act 3. #927 cost 12.4M
  fresh-input equivalent for five runs.
- After that, balance passes run as they do now: a change, then two seats
  graded on telemetry.

## Picks

1. **Klee's Balance gate is the base-character bar, measured on the real
   game** (seat runs on the baseline seeds, fight telemetry, your run), not
   the sim re-baseline. This amends `stage-gate.md`'s Balance paragraph.
   Default: yes.
2. **Pre-registration becomes a one-line prediction in each change's paper,
   graded by the next round.** Slates, countersigns and blind grading retire
   for kit balance. This amends `EXPERIMENTS.md`. Default: yes.
3. **The sim's Balance machinery is parked**: no re-baseline, and `EB-195`,
   `EB-255`, `EB-810` and the Aeonglass port wait. Default: (a) park, and
   delete the unreachable shipped-kit code (`BACKLOG.md`, legacy cleanup
   stage 6) when convenient. The other option is (b): keep the old plan and
   do the six code tasks first.
4. **Klee's rows stay where they are**, with no re-authoring and no
   `CONSTANTS_VERSION` bump. Default: yes.
5. **First steps**: build the telemetry report, then run Klee on the five
   baseline seeds through act 3 when the lanes are free. Default: yes.
