# Haiku 5.5 seat benchmark, five seeds, 2026-10-08

**Question.** Can a Haiku 5.5 seat (medium effort, the `haiku55-seat` agent) stand in for the
Sonnet 5.5 seat on base-character rounds? The 2026-10-07 benchmark was one seed per model: Haiku
died at the act-1 boss, Sonnet won.

**What ran.** The five base characters on their usual seeds (A0, the staging build 0.2.4590+next,
the page from main at #971), one Haiku seat per act with `new-seat` between acts. They are compared
with the ten Sonnet runs on the same seeds: the counted base runs of 10-05 and tonight's control.
Run instances: Haiku `20261008-0244xx` and `-024500`; Sonnet as in the Klee suite 5 record.

## Result

| Seed | Haiku ended | Sonnet, 10-05 | Sonnet, control |
|---|---|---|---|
| Ironclad 30KM | f8, act-1 elite (Phantasmal Gardeners) | f48 | f33 |
| Silent CYHZ | f17, act-1 boss (The Kin) | f48 | **won** |
| Defect DJCA | f24, act-2 normal fight (Louse Progenitor) | f48 | f48 |
| Necrobinder YEWA | f33, act-2 boss (Knowledge Demon) | f46 | f48 |
| Regent R41T | f33, act-2 boss (Kaiser Crab) | f48 | f46 |

Haiku reached act 3 on no seed. Sonnet reached act 3 on 9 of 10 runs.

## Fights (all fights each model played on these seeds)

| | Damage a turn | HP lost per fight | Turns | Block a turn |
|---|---|---|---|---|
| Act 1 normal, Haiku / Sonnet | 20.5 / 19.9 | 11.4% / 7.5% | 3.0 / 3.1 | 2.5 / 3.1 |
| Act 1 boss | 30.0 / 28.3 | 62.0% / 50.3% | 7.2 / 7.8 | 3.8 / 5.9 |
| Act 2 normal | 28.5 / 32.7 | 15.7% / 13.2% | 3.7 / 3.2 | 5.6 / 4.9 |
| Act 2 boss | 32.6 / 47.3 | 65.2% / 62.0% | 7.0 / 7.8 | 10.1 / 10.8 |

- **In act 1, Haiku deals Sonnet's damage and loses half again as much HP doing it.** It blocks
  less, and the seats' own deaths read the same way: "no line survived" at the elite, and "block
  shortfall" at The Kin.
- **In act 2 its decks fall behind:** 0.87 of Sonnet's damage in normal fights and 0.69 at the boss.
- **Its records are thinner.**
  - Three of the eight Haiku act seats lost their turn-by-turn notes to a context compaction and
    wrote those fights from a one-line log.
  - Two named cards wrongly.
  - One ran a bare `python3`, which hangs on this machine.

## What this means for rounds

A Haiku seat dies earlier than a Sonnet seat on the same seed, so a kit graded by Haiku seats would be
graded mostly on acts 1 and 2. It is not a stand-in for Sonnet on balance rounds.
- **Sonnet stays the seat.**
- Haiku is usable for short bridge smoke checks: one act, one screen type, or a page change.

This is five runs, one per seed, so it gives a direction, not a measurement. It agrees with the
one-seed benchmark of 2026-10-07.
