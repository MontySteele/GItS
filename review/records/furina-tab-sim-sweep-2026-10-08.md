# Furina, the Salon's Tab: tier 0.5 sweep (2026-10-08)

Measurement only. No card text or number was changed. These are sim numbers
from prototype rows, so they are not quotable as sheet values. Read them
against each other and against the reference characters, not as absolute
win rates. Even Ironclad wins only about 7% here.

## Commands (run from the worktree `GItS-furina-sweep`, branch `furina-sweep-2026-10-08`)

`PY` = `.venv/Scripts/python.exe`, `PYTHONPATH=.`. All cells use the realistic loadout (relics and potions) and seed 11, and all cells share the same seeds.

- **[S1]** `PY -m tier05.exp_furina_tab_sweep --runs 1000 --seed 11 --jobs 8 --only furina`
- **[S2]** the same script with `--only real_ironclad --only real_silent`, run from the main checkout because it needs `game_ref/`. Its sim code matches origin/main except for one test file. Ironclad and Silent are the only base characters the run sim has.
- **[S3]** `PY -m tier05.exp_furina_tab_sweep --runs 3000 --seed 11 --jobs 8 --only furina --policy blind`
- **[S4]** `PY -m tier05.exp_furina_tab_sweep --runs 1000 --seed 11 --jobs 8 --quick` (the K3 cells)
- **[L]** `PY -m tier0.harness.furina_loop_probe --jobs 0`, and the same command with `--pre-fix`

Draft policies: **blind** takes a random card from each screen. **adaptive** is the greedy drafter. **assigned** follows her `salon` plan. Route **hunter** seeks elites; **cautious** avoids them.

## 1. Win rate

| Cell (hunter route) | Win | Act 1 cleared | Act 2 cleared |
|---|---|---|---|
| Furina, blind [S1] | 2.7% | 71.3% | 18.4% |
| Furina, blind, 3000 runs [S3] | 2.4% | 72.5% | 19.0% |
| Furina, adaptive [S1] | 5.6% | 81.3% | 30.5% |
| Furina, assigned [S1] | 1.5% | 82.5% | 17.4% |
| Ironclad, blind / adaptive [S2] | 5.4% / 6.9% | 54.7% / 59.7% | 19.7% / 24.9% |
| Silent, blind / adaptive [S2] | 0.2% / 1.9% | 44.5% / 51.4% | 5.7% / 10.8% |

On the cautious route Furina scores 2.9% blind, 5.3% adaptive and 1.5% assigned, with act-1 clears of 93 to 96% [S1]. Ironclad scores 6.7% and 8.2%, and Silent 0.9% and 2.5% [S2]. Furina sits between Silent and Ironclad, closer to Ironclad. Her act-1 clear rate is the best of the three.

## 2. Packages

**The greedy drafter cannot see her kit.** Under adaptive drafting, 22 of her 34 cards are never picked [S4]. That covers all seven guests, every Power, Salon's Tab, Pneuma Refrain, Singer, Interval Bell, Standing Ovation, Fountain, Revelry, Rejoice and Bis!. The drafter only picks her plain attacks and Usher, at a 7 to 30% pick rate, plus companion cards.

The cause is in `tier05/draft.py`: every `stage_*` op is priced at zero (`FURINA_STAGE_OPS`, `_STAGE_ZERO`). So a card whose value is a guest, Drain, Repay or Spend scores nothing. The adaptive and assigned cells therefore measure her attacks, not her packages. Only the blind draft exercises the packages.

**A fair per-card read under the blind draft [S3].** It compares runs that were offered the card in the first four screens and took it against runs that passed it. The blind pick is random, so the difference is roughly causal. Units are acts completed out of 3. The standard error is about ±0.07 when about 200 runs took the card and ±0.05 when about 400 did.

- **Carry wins:**
  - Guest Star: Lyney +0.33 (win 5.0% against 2.0%).
  - Guest Star: Clorinde +0.29 (only 61 runs, so noisy).
  - Gentilhomme Usher +0.15.
  - Wriothesley +0.14.
  - Crabaletta, Solicitation and Quick Flourish +0.11 each.
  - The pattern: the Drain cluster and the guests that turn Drain into damage.
- **Hurt or do nothing:**
  - Fountain of Lucine −0.23.
  - Let the People Rejoice −0.15, Critics' Darling −0.14, Standing Ovation −0.13, Salon's Encore −0.12, Lynette −0.12, Singer of Many Waters −0.11, Sigewinne −0.10 and Surging Waters −0.09.
  - The spend-all finales and the Repay package do not carry runs.
- **Never played, which is a pilot gap:** Guest Star: Charlotte and Guest Star: Sigewinne are played 0.00 times per fight even when held [S3]. Their act is a Repay, and `policy.stage_act_parts` values that act at 0. Their numbers above say nothing about the cards.
- **Rarely played:** the Rares Revelry, Rejoice, Critics' Darling and Singer are played 0.09 to 0.12 times per fight when held.
- **Fanfare piles up unspent:** per fight she gains 29.2 (16.1 from hits, 8.2 from Drain, 5.0 from Repay), spends 12.6 and ends with 16.6 [S1, adaptive].

## 3. Loops

**No infinite loop was found.** The probe [L] searched all 36 sheet rows: the 34 pool cards plus Curtain Rise and Rising Applause, in base and upgraded forms. It tried every combination of up to three cards, under every one of her Powers, on an empty stage and on a three-guest stage.

- **Productive loops:** 0.
- **Inert loops:** 2, Interval Bell x2 (base, and upgraded). It can be replayed forever but gains nothing, and no Power or guest makes it productive.
- **The probe still catches what it fixed:** with the old Interval Bell put back (`--pre-fix`, Energy now instead of next turn), it finds 20 productive loops. All use Bell, for example Charlotte+ with Bell and Salon's Tab, or Lyney+ with Bell and Pneuma Refrain. `test_furina_loop_probe` pins both directions and is green in the full gates.
- **Limit:** the probe is one long turn. It does not cover end-of-turn guest acts, next-turn Energy from Salon's Tab or Fountain's schedule.
- **Whole-fight check for runaways [S3, S4]:**
  - The most cards played in one turn, in any fight, is 12. In 999 fights out of 1000 it is 9 or fewer.
  - The biggest single turn of damage is 259. In 999 out of 1000 it is 185 or less.
  - That is no runaway.

## 4. K3: Drain is a reflex in the sim

The shipped sim decider takes every legal Drain mode (100%), by construction. The line blocks 16% of Drain offers: 51,954 of 326,183 [S4]. That is the only thing that ever says no.

To test whether saying no could pay, [S4] reruns the same seeds with the same card-play pilot and changes only the in-card Drain choice:

| Drain choice | Taken | Win | Act 1 cleared | Act-1 elite won | HP lost per act-1 elite won |
|---|---|---|---|---|---|
| Always | 100% | 5.6% | 81.3% | 91.5% | 28.9 |
| Only when Block covers the posted hit | 35% | 2.4% | 67.1% | 83.2% | 33.9 |
| Never | 0% | 1.5% | 60.5% | 79.6% | 36.0 |

Every refusal costs her. Here is why:

- She drains 8.2 HP per fight. The Singer and cards repay 5.0 of it during the fight, and the curtain call returns the other 3.2.
- Each drained HP also prints Fanfare and buys the bigger effect.
- She loses less HP overall by draining.

So K3 shows up as "Drain is free": the right play is always yes, and only the line stops it. It still needs a seat or [USER]'s run to judge, because the card-play pilot cannot plan across turns.

## 5. Pool fit: easy in act 1, the usual act-2 wall

The table shows adaptive draft on the hunter route, Furina [S1] against Ironclad and Silent [S2].

| Fight | Won (F / I / S) | Turns (F / I / S) | HP lost when won (F / I / S) |
|---|---|---|---|
| Act-1 hallway | 98.9 / 99.5 / 98.9% | 3.7 / 3.6 / 4.2 | 5.4 / 9.0 / 3.8 |
| Act-1 elite | 91.5 / 71.0 / 66.9% | 6.0 / 6.5 / 7.9 | 28.9 / 37.6 / 31.1 |
| Act-1 boss | 98.5 / 98.5 / 93.6% | 7.1 / 6.9 / 9.1 | 26.2 / 34.8 / 28.6 |
| Act-2 boss | 61.0 / 52.4 / 32.6% | 9.9 / 9.7 / 11.3 | 55.0 / 62.6 / 53.6 |
| Act-3 boss | 43.1 / 44.5 / 41.3% | 7.2 / 7.4 / 8.5 | 38.5 / 55.5 / 45.4 |

- **Not a slog:** her fights are as short as Ironclad's and shorter than Silent's.
- **Act 1 is easy:** she wins the act-1 elite 20 points more often than either base character and loses less HP doing it. This matches the starter overshoot sec.17 found and the "extremely easy" note from the earlier Stage run.
- **Where she dies:** after act 1 she runs into the act-2 hallway and the act-2 boss, like everyone else. The commonest deaths are act-2 hallway (289), act-2 boss (195) and act-3 hallway (115) [S1].

## For the caller (engineering, no design)

1. The drafter prices her verbs at zero, so the greedy cells never draft her packages. A real per-package read needs those verbs priced, which is a drafter-world change.
2. The combat pilot never plays Charlotte or Sigewinne. `policy.stage_act_parts` gives Repay acts no value.
