# Varka Balance suite (varka-fang-next), 2026-10-19

Build: `varka-fang-next` dfca5e7b2 (0.2.6051+next), main merged in (#1491).
Change set under test: `review/active/varka-fang-next-2026-10-19.md`:
Boreas's Fang's Pyro payout 5 (sec. 2), the power upgrade pass (sec. 3) and
the rarity sweep (sec. 4). Seeds, seats and grading as suite 1
(`review/records/varka-next-suite-1-2026-10-15.md`): A0, one Sonnet 5.5 seat
per lane for the whole run, the five suite seeds.

| Seed (base character) | End floor (cause) | Suite 1 (10-15) | Base |
|---|---|---|---|
| 30KMHAVG9SMQ (Ironclad) | **won** (Test Subject) | 40 | 48 |
| CYHZM9S0VPW6 (Silent) | 48 (Queen + Torch Head) | won | 48 |
| DJCAV76ZKAUN (Defect) | 48 (Test Subject, form 3, at 150/300) | 48 | 48 |
| YEWA0B7AVE45 (Necrobinder) | **won** (Test Subject #C64) | 48 | 46 |
| R41TX5Q0ZQYN (Regent) | **won** | won | 48 |
| **All** | 48.0, 3 wins | 46.4, 2 wins | 47.6, 0 wins |

Every run reached the act-3 boss. 118 fights (`tools/telemetry_report.py
--character Varka --since 2026-10-19T19:45 --tempo`).

## The predictions

- **P1 (Pyro payout averages 5.0): met.** 64 Pyro payouts dealt 312 damage,
  4.9 a payout; overkill and Block pull it under the nominal 5. Electro 5.3,
  Hydro 2.8 Block, Cryo 0.9 Vulnerable a payout.
- **P2 (floors within suite 1's range, no seed an act lower): met.** Three
  seeds equal or better (30KM 40 to won, YEWA 48 to won), one win became a
  floor-48 loss (CYHZ, same act).
- **P3 (Fang share rises by under 2 points from 4.1%): met.** 3.5% of
  Varka's damage, down 0.6 points.
- **P4 (Cryo's Vulnerable bonus, reported):** 177 Cryo payouts, 1,329 bonus
  damage from the Vulnerable they put on, 7.5 a payout. Counting it, the
  Fang's share is 11.0%. The bonus counts every hit on an enemy while a
  Fang Vulnerable stood on it, including Vulnerable another card would have
  applied anyway, so 11.0% is a ceiling.
- **P5 (no upgraded power moves the floors alone): met** (P2).
- **P6 (the changed powers, offered / taken):** Lupical 4 / 2, Weathervane
  5 / 2, Unwavering Banner 6 / 0, Absolute Zero 5 / 0, Eye of Stormterror
  5 / 0, Wildfire Oath 4 / 0. West Wind's Blessing and Comrades of the
  Expedition are co-op cards and were not offered.
- **P7 (the moved cards, offered / taken):** Converging Winds 7 / 5,
  Weathervane 5 / 2, Dawn Wind's March 4 / 0 (now Uncommon); Rally to the
  Banner 4 / 0, Grand Master's Order 3 / 0 (now Rare).

## What played well

- Order inside a turn was the decision in all five seats: which element card
  goes last sets the aura a Swirl takes, which goes first sets the Oath a
  payoff reads (lanes 1, 2, 4, 5).
- Swirl-to-all chains (Converging Winds, Sucrose, Wall of Gales) cleared the
  many-body fights: the Kin, four Exoskeletons, three Inklets (lane 3).
- Stacked Weak and Vulnerable into Icebreaker+ (Weak 22 / Vulnerable 27 on
  Test Subject, lane 1) and Fury+ as a tutor were the biggest choices.

## What did not

- Four of the six changed powers that were offered were never taken, Banner
  0 of 6 included. The upgrades did not make them draft picks.
- Weak cards named by two or more seats: Rising Gale and Jean's Wind
  Companion with no aura to Swirl; Boreas Unbound; Shifting Gale; For Crepus.
- Lane 5: once Yoimiya was out, Dandelion Gale+ played twice won most fights
  alone.
- Both losses were the act-3 boss: Test Subject's form 3 (Intangible every
  other turn) and the Queen's 99-turn Frail/Weak/Vulnerable into Torch Head.

## Screen notes for the UI review

Frames: 54 shots of the five lanes, one every 4 minutes, kept in the
session scratchpad (`varka-suite-2/frames`, not committed).

- "Swirl pays X" follows the current element, not the aura's; two seats
  learned it only from preview lines.
- Banner of the West Wind's Oath move is invisible until a number jumps.
- Tidal Bulwark's "Deals 0 damage" reads as a bug before Block is up.
- Four Winds' Ascension's damage figure shifts with the current element in a
  way a seat read as wrong.
- Stoke the Flames ("next Pyro Attack") gives no hint that Amber's card is a
  Skill.
- The feed sometimes drops Cycle of Seasons' damage lines.

## What to change

- Promote: every threshold prediction met and the floors rose.
- The four powers offered and always passed (Banner, Absolute Zero, Eye,
  Wildfire); their next look is their
  base text, not their upgrades.
- The screen notes above go to `BACKLOG.md` with the next Varka text pass.
