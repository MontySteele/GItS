# Varka payoff round, 2026-10-10

This round grades the Pyro/Cryo payoff fix (#983, `review/active/varka-payoff-fix-2026-10-08.md`).

**What ran**
- Solo Varka at A0 on staging 0.2.4682+next.
- The offers round's five seeds, with card offers logged.
- Sonnet seats. Embark stamps `20261010-0133xx`.
- Seat records and the fact packet are in the session scratchpad (`varka-payoff-r1/`), which is gitignored.
- The review below is by a Fable reviewer, after one exchange with the main session:
  - Pyre Oath is held, not given a new per-turn prompt.
  - Wolfpack's "top of draw pile" was dropped after a copy-chain check.

## Result

| Seed | Starting Knight | This round | Offers round (10-08) | Base character |
|---|---|---|---|---|
| 30KMHAVG9SMQ | Kaeya, Cryo | floor 33, The Insatiable at 57/321 | floor 44 | floor 48 |
| CYHZM9S0VPW6 | Kaeya, Cryo | **won** (Queen, 7 HP left) | floor 48 | floor 48 |
| DJCAV76ZKAUN | Barbara, Hydro | **won** | floor 40 | floor 48 |
| YEWA0B7AVE45 | Amber, Pyro | floor 33, Knowledge Demon at 89/379 | floor 48 | floor 46 |
| R41TX5Q0ZQYN | Kaeya, Cryo | **won** (Aeonglass) | floor 48 | floor 48 |

- Varka won 3 of 5. The offers round won 0 of 5, and the base five won 0 of 5 on these seeds.
- Both deaths were at act-2 bosses, on turns with no element card in hand.
- Normal fights by act, as a ratio of base (`tools/telemetry_report.py`, 109 fights):
  - damage a turn: 1.05 / 0.91 / 0.69;
  - HP lost: 0.36 / 0.60 / 0.72;
  - Block a turn: 4.9 / 8.0 / 12.5, against base 2.2 / 2.9 / 7.5.

He wins by not dying, not by killing faster.

**Verdict:** Varka is at or a little above a base character for these seats, on the Block side, which is project review pick 1. Five runs cannot separate 3/5 from the spread between suites. Two seeds ended 11 and 15 floors earlier than last round. Strength numbers hold until a replication.

## Did the fix work? One of three lines

**The payoff cards** (offered / taken / played):

| Card | Offers round | This round |
|---|---|---|
| Stoke the Flames | 9 / 1 / 0 | 7 / 3 / 33 |
| Deep Freeze | 7 / 0 / 0 | 10 / 1 / 9 |
| Glacial Edict | 8 / 1 / 1 | 7 / 1 / 5 |
| Ember Cleave | 12 / 1 / 9 | 8 / 0 / 0 |
| Pyre Oath | 9 / 0 / 0 | 10 / 0 / 0 |
| Wildfire Oath | 6 / 0 / 1 | 4 / 0 / 0 |

**What worked:**
- **Stoke the Flames** worked. Lane 3 built the first Pyro deck seen solo: a 115-damage Ascension at the final boss, and it won.
- **The Cryo payoffs** worked wherever they were taken. Lane 5 won, and Deep Freeze into Icebreaker+ was its MOST WANTED turn.

**Why the Pyro misses are structural:**
- **Every Pyro Common was passed at the same rate**, so the misses are not card quality:
  - Amber: Baron Bunny 1/13
  - Sharpshooter 1/8
  - Kindled Edge 1/7
  - Ember Cleave 0/8
- **The starting Knight is fixed by seed.** `BoreasFang.cs:164` rolls it from `PlayerRng.Transformations`, so these seeds give Kaeya three times, Amber once and Barbara once. Pyro is off-element on 3 of 5 runs by construction.
- **The take rates moved little:**
  - Pyro rose from 10% to 13%.
  - The Varka-owned average is 23%.
  - Hydro fell from 20% to 7%, and seats already have more Block than they need.

## What changes (Claude ships)

1. **Stoke the Flames:** "Exhaust a card. Pyro becomes your current element. Gain 2 [3] Pyro Oath."
   - Today the code gains Oath before switching, so Dawn Wind's March never sees the gain.
   - Ember Cleave gets the same op order.
2. **Wolfpack:** "Whenever you play Four Winds' Ascension, shuffle a copy of it into your Draw Pile. The copy Exhausts."
   - Today the copy goes to the discard pile and almost never returns in a 3-turn fight.
   - With the change, an Ascension comes about every 2.5 to 3 turns. That is about 20 damage a turn averaged at Oath 15, never two in a row.
   - The copy chain was checked in `VarkaPowers.cs:932-950`.
3. **Unwavering Banner:** the card says "gain 1 Oath of it". The code pays the current element (`VarkaPowers.cs:603-606`). The text becomes "gain 1 Oath of your current element instead."
4. **Twin Gales:** add a line to the seat page saying what each Swirl paid. Numbers are held.
5. **Sucrose, Mollis Favonius,** on `klee-next`: "This turn, Melt, Vaporize and Overloaded deal 4 additional damage."
6. **Held:**
   - Ember Cleave's numbers, Deep Freeze, Glacial Edict, Wildfire Oath and Absolute Zero.
   - Pyre Oath, until a forced-Pyro round. If it is still passed there, the fallback is "Whenever you Exhaust a card, gain 2 Pyro Oath".
   - Windborne Resolve, flagged for pick 1. Two copies gave 36 to 68 Block a turn.

**Defects to fix:**
- The Oath log line says "Boreas's Fang" after Orobas swaps the relic. It should name the held relic (`VarkaOath.GainLine` :752, `blindplay_render.py:1577`).
- "WhatMod: KleeMod" shows on the Orobas event's relic text (`blindplay_read.py:193-205`).
- Four Winds' Ascension's once-per-combat rule needs a line in its hover or hand row.
- Sucrose with no aura on the board needs a "no aura to Swirl" line.
- The current element should sit by the hand on the seat page, not after the powers.

**Seat error:** Kaeya printing 9 is 6 × 1.5 Vulnerable. Barbara does not Freeze an Axebot because Frozen converts only on bosses. Tempest Charge's draw does fire.

## For [USER]

**Hydro's job.** Hydro is Varka's Block element, and seats took Hydro cards 7% of the time. He already Blocks 2 to 4 times as much as base. The choice is between:
- keeping Hydro as Block and accepting the shelf, or
- giving Hydro another job (a paper would follow).

**Default:** keep it, and re-read after the replication.

## Next round

- Log the current element on every `cards_played` row.
- Add a lane override for the starting Knight (`GITS_VARKA_KNIGHT`). It still draws the seed's roll and discards it, so later rolls do not change.
- First forced round: Amber on all five seeds, with the card changes above. It grades Ember Cleave, Pyre Oath, Wildfire and the Pyro Common rate.
- Grading lines:
  - Wolfpack's copy is played at least once in every run that holds it.
  - Pyre Oath is taken at least once from a reward.
- Then a replication on unforced seeds before any word on strength, followed by [USER]'s run.
