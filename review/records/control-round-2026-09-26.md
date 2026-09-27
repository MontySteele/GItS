# Base-game control round, 2026-09-26

**Question ([USER], 2026-09-26):** "it used to be that our playtest agents were
not capable of beating the game, or usually even act 1, but I saw some runs
have reached the final boss ... assess if this is because the agents (you) are
just way better at playing the game vs the older agents, vs our new characters
being too strong."

**Answer:** it is mostly the seats. On a page that shows them what the game
shows a human, base-game characters reach the act 3 boss about as often as
Klee and Furina do. The one sign of extra strength is Klee's two wins; two
runs are too few to act on at Prototype.

## How it was run

Every run used the same instrument as the Klee and Furina seat rounds:
- a blind Opus seat, with the brief from `tools/seat.py --opus-brief`;
- a full run from floor 1, playing to win;
- 900 actions and 10,800 s;
- one lane per seat.

Raw records are gitignored in `review/qa/seats-2026-09-26/`: `control-*.md`
for round 1 and `control2-*.md` for round 2.

## Round 1 (build 0.2.3874, the page as it was)

| Character | Asc | How it ended |
|---|---|---|
| Ironclad | 0 | died to the act 2 boss (Knowledge Demon), floor 33 |
| Silent | 5 | died to the act 2 boss (Kaiser Crab), floor 33 |
| Defect | 0 | died in an act 2 hallway fight, floor 29 |
| Necrobinder | 0 | died to the act 2 boss (Kaiser Crab), floor 33 |
| Regent | 0 | died to the act 3 boss (Aeonglass), floor 48 |

Three of these seats were playing partly blind, because the page dropped
something the wire carried:
- Defect's orbs were never shown.
- The Necrobinder's Osty HP was never shown.
- The Regent's star total and star costs were never shown.

Silent embarked at A5, because each character starts at the last ascension it
played and lanes share their saved progress.

## Round 2 (0.2.3881 to 0.2.3883, all A0, page fixed)

| Character | How it ended | Bosses beaten |
|---|---|---|
| Ironclad | died in an act 2 hallway fight (Spiny Toad), floor 25 | 1 |
| Silent | died to Aeonglass, floor 48 | 2 |
| Defect | died to Aeonglass, floor 48 (won 24 of 25 fights) | 2 |
| Necrobinder | died to Test Subject, floor 48 | 2 |
| Regent | died to Aeonglass at 110 of 512 HP, floor 48 | 2 |

## Klee and Furina, the same day (full runs from floor 1)

| Kit | Runs | Asc | Reached act 3 | Died at the act 3 boss | Won |
|---|---|---|---|---|---|
| Klee | 5 | 0-1 | 4 | 1 | 2 |
| Furina | 6 | 2-3 | 4 | 3 | 0 |
| Base game, round 2 | 5 | 0 | 4 | 4 | 0 |

The void wave-3 Klee lane 2 run and the dressed act 2 and act 3 starts are
excluded. Counts are from the `klee-*`, `furina-*` and `wave3-*` records in the
same folder.

## What it means

- **The seats are much better than the old ones.** On a fair page, four of five
  base-game runs beat two bosses and died at the final one.
- **Round 1 overstated the kits.** Reaching act 3 went 8 of 11 for the kits
  against 1 of 5 for the base game in round 1, and the gap closed once the page
  was fixed. The page had been written around our own characters (the Stage
  forecast, the Bomb header) and had quietly left out the base game's
  resources.
- **Klee's two wins are the only sign of excess strength.** Two of five at
  A0-A1, against none of nine base-game runs. Two runs cannot carry a
  conclusion at Prototype; measurement is the Balance stage's job
  (`docs/current/EXPERIMENTS.md`).
- **Furina is not over the line.** At A2-A3 she reaches the final boss as often
  as the base game does at A0.
- **Aeonglass is the common wall.** Its Wither cards, one per six cards played,
  growing each time, killed three of the four base runs that reached it, and
  one Klee run lost to it.

## Caveats

- The samples are small: one or two runs per character.
- The ascension levels do not match. Furina was at A2-A3 against the base game
  at A0, which flatters the base game. Most base characters have only A0
  unlocked in the lane profiles, so `--ascension 1` was refused.
- The page fixes landed only after Klee and Furina had played. Their runs had
  their own page, which was never missing a resource.
- The Regent's round 1 page changed partway through its run, when #706 was
  pulled.
- Several seats sent two game commands in one message, against the brief. Each
  record declares it, and the commands resolved in order.

## What the round changed

- **#705:** `embark --ascension N` sets the level at character select and
  refuses a run whose level reads back differently.
- **#706, #707 and #708:** seat page fixes for:
  - orbs, Osty, the star total and star costs;
  - the whole map;
  - Klee and Furina glossary terms leaking onto base-game screens;
  - upgrade text, powers applied, and transforms named;
  - Foul Potion at the Merchant;
  - the rest-site retry;
  - about twenty smaller text bugs.
- **The epoch trap.** A base-game run that unlocks a timeline epoch leaves its
  lane's main menu with only Settings and Quit. The fix is to reseed that
  lane's `progress.save` from a clean lane.

No picks.
