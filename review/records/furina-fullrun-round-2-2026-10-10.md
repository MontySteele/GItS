# Furina whole-run-seat round 2, 2026-10-10

This is the second round on build 0.2.4772+next. It used the same cards as round 1 (`furina-fullrun-round-2026-10-10.md`), with the legibility fixes from #1046. Same seeds and the Ironclad control, one Sonnet seat per lane for the whole run.
- Embark `20261010-165817`.
- The packet, seat records and the reviewer's scripts are in the session scratchpad (`furina-fullrun-r2/`, `furina-fullrun-r2-review/`), which is gitignored.
- A Fable reviewer reviewed the round. The main session accepted the review with one correction: the rarity split is now 20 / 38 / 20, after Navia moved to Uncommon.

## Result

| Seed | Round 2 | Round 1 |
|---|---|---|
| JF391WG2NN0X | floor 33, Kaiser Crab (entered at 67%) | floor 27, act-2 elite |
| WDETA8RRGH98 | floor 25, Decimillipede elite, died with 78 Fanfare | won |
| 0J427L1YQV15 | floor 48, Aeonglass | won |
| TYXJLVY31QN7 | **won** | floor 48, the Queen |
| Ironclad control | floor 33, Knowledge Demon | floor 48 |

**Against round 1's lines.**
- **Wins: 3 of 8 pooled.** The pass line was 4 of 8.
- **Act-2 bosses:** she won 5 of the 6 she reached. Four of the five wins lost 55% of max HP or less after the return.
- **The control** reached floor 48 once in the two rounds.
- **The fail clause was not triggered:** the one act-2 boss death entered at 67% HP, under the 80% line. So the shelved picks (Standing Room Only, Wriothesley) stay shelved.

**Reading 3 of 8.** It is undetermined at this sample size: the 95% interval runs from 14% to 69%.
- The control also won only 1 of 2 over the same rounds.
- Base-five seats won 0 of 5 (#927).
- Per fight she has not moved. Pooled normal fights: 1.05× base damage, 1.50× Block, and 0.71× base HP lost after the return. Act-2 bosses: 68.2 and 53.5 damage a turn, against base's 58.4.
- More seat rounds on this build would measure seat variance, not the kit.

## What the rounds surfaced: the stranded bank

**Two of the five whole-run deaths held a big bank with nothing to spend it on:** 38 Fanfare (round 1, lane 1) and 78 (round 2, lane 2). Lane 3's 55 was different: it had spent 57 earlier in that fight and lost a race.
- **Turn-level check:** of 67 turn starts with 20 or more Fanfare, 34 played no Spend card that turn. Some of that is deliberate banking: lane 4 won with Bravura+ for 88.
- **Kit density.** 20 of her 80 cards Spend, but only 6 of 20 Commons do, and only two Commons take a big bank (Spirited Aria and Crashing Waves). Income comes from every hit, 24 Drain cards and 19 Repay cards.
- **The draw-free sinks are not drafted.** Freminet was offered five times and passed five times; Navia was offered twice and passed twice.
- **Drafting:** the seats play the Spend cards they hold at an even rate. Lane 2 held 3 Spend cards in 27 and passed seven more at rewards.
- **Verdict: both the seats' drafting and the kit's density.** [USER]'s "no Fanfare from Repay" ruling was about income; this is about outlets.

## Defects and legibility, checked in source

- **Real page gap.** While Surrounded, the hand does not mark which cards turn her to face their target. The Surrounded line states the rule (`blindplay_notes.py:111`), and the card face carries the aim (`blindplay_board.py:1621`). Claude fixes this.
- **Rule, by design or seat error (no change):**
  - Grand Deluge is refused at 3 HP. A Drain to 0 HP is refused, as ruled 2026-10-09.
  - AoE ignoring `on` already says so in its reply (`blindplay_session.py:931-935`).
  - Rest-site upgrades re-pick through `skip`.
  - Neow's Fury allows 0 picks.
  - Hydro Lance's text is correct.
  - The run-over page's "Act 2" is correct: Knowledge Demon is an act-2 boss.
  - Fanfare rising more than HP lost comes from Drain plus hits plus Repay (`FurinaStageDirector.cs:310-424`). The keyword says "for each HP you lose or Repay".
- **Unverified, base game:** Wax Lizard Tail did not fire after Toy Box. This needs a live repro, with no change before it.

## What changes (Claude ships)

1. Telemetry records the number of Spend cards in hand at each turn start, next to `fanfare_turn_start`.
2. While Surrounded, the page marks the hand cards that take `on`.
3. A chooser that allows 0 picks says a bare `confirm` closes it with nothing taken.
4. A Wax Lizard Tail repro goes on the backlog.

## For [USER]

1. **Fanfare outlets.** **Default (a): no card change.** You take the question into your run: did the bank strand you, and would a Common sink have fixed it?
   - (b) Move one spend-all card (Standing Ovation or Bravura) to Common. This changes the split.
   - (c) Quick Flourish becomes "Spend up to 8: 2 damage for each". This was declined on the Spend paper; the new fact is the two stranded deaths.
   - (d) A draw-free Uncommon sink Power, a new design.
2. **Furina's stage.** **Default: Furina goes to your playtest now, with no third seat round on this build.** The alternative is one more round after pick 1 changes a card, graded on stranded-bank deaths: 0 of 4.

**Ruled 2026-10-10, both at default.** [USER]: "Makes sense on Furina." No card change for outlets; the stranded-bank question goes into his run. Furina goes to his playtest, with no third seat round on this build.
