# Furina: the three Spend rounds together, 2026-10-10

This is the review of Spend rounds 1–3 against the Block round. It covers the Spend paper (PR #1014), the build (#1016), and the fixes #1022 and #1029.
- **Round 3:** staging 0.2.4723+next, embark `20261010-075837`.
- **Sources:** the packets and the reviewer's recomputations are in the session scratchpad (`furina-spend-r3/`, `review-work/`), which is gitignored.
- **Who reviewed:** a Fable reviewer. The main session accepted the review as written.

## What the four rounds show

**Results:** 0 wins in each Spend round (0 of 12 in all), against 2 of 4 in the Block round.

**Per fight she has not moved.** Median damage a turn on her four seeds:

| Round | Normals | Elites | All bosses | Act-2 bosses | Act-2 boss wins/losses |
|---|---|---|---|---|---|
| Base | 26.0 | 31.8 | 36.0 | 58.4 | |
| Block round | 25.2 | 31.0 | 35.7 | 51.0 | 2 / 1 |
| Spend r1 | 26.1 | 29.0 | 35.2 | 48.3 | 1 / 1 |
| Spend r2 | 24.7 | 31.8 | 42.0 | 45.9 | 1 / 2 |
| Spend r3 | 25.7 | 30.4 | 28.6 | 28.6 | 1 / 3 |

- Round 3's act-2 bosses are three fights, entered at 38/90, 50/83 and 61/83 HP.
- She blocked twice what base does and still lost 66% of her max HP, because the fights ran 10 turns against base's 7.

**The Spend change neither buffed nor nerfed her per fight.** Overflow is solved wherever a spender is drawn: the median Fanfare left at a fight's close was 3.5, and 26 of 68 fights closed at 0.

**Act-2 bosses were her wall before the Spend build.** Seed 0J42 has died to Kaiser Crab in five of six rounds.

**Her damage is an HP budget, not an engine.**
- Fanfare comes only from HP moving.
- Free Drain room is a quarter of max HP. A Repay can only return what was drained, and a hit costs real HP.
- In a 3-turn fight that is about 7 Fanfare a turn. In a 12-turn fight it is about 2 a turn.
- In the three deaths she earned 7 to 11 Fanfare a turn, and the bank was nearly empty at death.
- At low HP the engine shuts off: every Drain below the line is lost HP.
- Four of the five act-2 boss wins across the rounds carried a turn-scaling source: a damage guest (Wriothesley, Lyney) or stacked Powers. None of the six deaths did. Seats passed Wriothesley all five times he was offered.

## The seat-format confound

The Block, quarter-line and pool-75 rounds ran **one full-run seat per lane**. All three Spend rounds ran **per-act seats**. The Ironclad control is a useful check here, because nothing changed on its side:

| Seats | Control death floors | Control act-2 damage a turn |
|---|---|---|
| Full-run | 48 / 48 / 48 | 39.5 (Block round) |
| Per-act | 17 / 48 / 24 | 31.0 (r2), 19.8 (r3) |

Furina's drop has the same shape. Varka's round 1 (full-run seats) won 3 of 5; his per-act rounds won 1 and 2.

4 of 12 against 0 of 12 has a two-sided Fisher p of about 0.09. The control's drop accounts for most of it. Either the change, or the seat format, or noise could explain the gap; this data cannot separate them.

## What changes (Claude ships)

1. **High Stakes: every 5 [4] becomes every 4 [3].** This is round 2's pre-registered fallback: it read +2 to +4 a hit at bosses.
2. **High Stakes shows in the card preview.** Its damage gate drops the bonus when the preview runs: Hydro Lance printed 15 and dealt 18.
3. **The Drain chooser names where its Block comes from** (The Masquerade, or Freminet's line). A seat could not tell the two apart and called The Masquerade "neutral". It isn't: the Fanfare is the gain.
4. **No change** to Thunderous Applause, Hold the Stage, Gentle Current, Freminet, Navia's act, or the four up-to caps.

**Defects:** "Power Potion charged 1 for The Masquerade" is unverified. The mod code is clean and it needs a live read. Flutter is base game.

## For [USER]

1. **Where her long-fight damage comes from.**
   - **(a) Default:** a Repay prints its Fanfare even when there is no drained HP to return. The Block, Vigor and damage floor stays. This adds about 3 to 4 Fanfare a turn, roughly a third of the gap, and weakens the "take hits for Fanfare" habit.
   - (b) Standing Room Only, a Strength Power, moves to Uncommon. This moves the ruled 20 / 37 / 21 split.
   - (c) Leave the rules and make the guests the engine: Navia to Uncommon, and Wriothesley's act from 4 [7] to 5 [8].
   - Whichever is chosen, a rule-3 edit is a keyword rule, so it ships after your run.
   - **Ruled 2026-10-10: Navia to Uncommon first; (a) is rejected.** [USER]: "I don't want Repay to
     give fanfare without a spend right now, so I lean more towards putting Navia to Uncommon
     first." (b) and (c)'s Wriothesley change are not taken now.
2. **Seat format.** The control's results suggest per-act seats play worse than full-run seats. Per-act seats are the ruled cost and context-rot fix.
   - **Default:** after your run, one round on the same five seeds with full-run seats on the Spend build, to separate format from change.
   - The alternative is to keep per-act seats and treat the confound as fixed noise.
   - **Ruled 2026-10-10: yes.** [USER]: "Definitely agree with testing whole-seat runs since we seem
     to have gotten token counts under control." One full-run-seat round on the Spend build. Per-act
     seats stay the default until that round is read. Timing is not yet set.
3. **#1028's picks stand.**
   - Regina stops at the line. Default yes.
   - Navia to Uncommon. Default no. New fact: she has not been seen offered in seven rounds. Offer rows still need locating (`Diagnostics/RewardRowProbe.cs`).
   - **Ruled 2026-10-10 on #1028:** Regina stops at the line ("I'm good with stopping Regina's Drain
     at the line."); Navia moves to Uncommon (pick 1 above).

## Next

1. [USER]'s own run on the current build. Two questions for his record: does her Fanfare bank run dry against the act-2 boss, and should guests or Repay income carry long fights?
2. Then the full-run-seat round above.
