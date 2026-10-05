# Kokomi seat round after the Rare pass and the kit review, 2026-10-05

**What ran.**
- Build 0.2.4463:
  - the Rare pass (#907);
  - the whole-kit review (#930): Ceremonial Garment 1 cost at 2 [3], Deep
    Current 8 [11], Open the Casket+ draws 1, and wording;
  - seat pages 5 and 6.
- Ascension 0, through act 3. Sonnet seats, one per act, handed over between
  acts.
- **Seeds are two of the base-five baseline's**
  (`review/records/base-five-baseline-2026-10-05.md`), so each run pairs
  with a base character on the same map:
  - lane 1 uses the Silent's seed (Kokomi uses the Silent's frame);
  - lane 2 uses the Defect's seed.
- No separate control lane. The Ironclad control earlier today
  (`review/records/varka-r6-round-2026-10-05.md`) repeated its baseline run
  to the floor.

| Lane | Seed | Act 1 | Act 2 | Act 3 | Base character, same seed |
|---|---|---|---|---|---|
| 1 | CYHZM9S0VPW6 | The Kin, out at 25/80 | The Insatiable in 4 turns, out at 76/97 | **lost** to the Queen, floor 48, Queen at 238/400 | Silent: lost to the Queen, floor 48, Queen at 38/400 |
| 2 | DJCAV76ZKAUN | Ceremonial Beast, out at 12/80 | **lost** to The Insatiable, floor 33, boss at 118/321 | — | Defect: lost to Test Subject, floor 48 |

**Verdict: Kokomi reaches the places a base character reaches, but with
much less damage.**
- Lane 1 died at the same boss on the same floor as the Silent, with the
  Queen at 238 HP left against the Silent's 38.
- Lane 2 died an act earlier than the Defect, 1 Block short at 9 HP.
- This matches the fight telemetry: her damage a turn in ordinary act-2
  fights is about half a base character's
  (`review/active/klee-balance-measurement-2026-10-05.md` §3). The kit's
  open question since 2026-10-02 is the damage gap, and this round confirms
  it rather than closing it.

## What played well
- **Deep Current at 8 [11] was the change that landed.** Lane 1 took it
  three times and named it the happiest draw ("11 AoE for 1"). Its AoE
  killed the act-2 boss's adds.
- **Strength before writing Plans was the best line in the round.** A Plan
  keeps the Strength it was written with. Lane 1, act 2 boss, turn 2: the
  potions and Open the Casket gave Strength 14, then three Plans landed for
  135 of the boss's 321. Act 3, Frog Knight: Riptide Ruin for 74 on both
  bodies at 13 Strength.
- **Plan or play now, and the order Plans are written in,** were real
  decisions in every act (Feint with three Plans carried out was lethal;
  Opening Gambit doubling the next Plan).
- **Frozen through Kaeya** turned 17-damage hits into 8, and seats chose
  Defend over attacking to keep the freeze. One seat broke it with its own
  Deep Current once.
- **The flip** (turning a waiting two-line Plan to its now-line) worked
  when used. It was used once, on Kurage's Oath+.

## What did not
- **Damage at the bosses.** Both runs died in damage races: the Queen with
  Chains of Binding (one card a turn), and The Insatiable's Sandpit clock.
- **NEVER AGAIN:**
  - Sea Glass Harvest, twice (lane 1, acts 2 and 3): "6 Block with no
    statuses worth transforming", and its Plan "transformed nothing";
  - Tide Wall (lane 2, act 1): "lands a turn late for the damage it claims
    to block";
  - Coral Tithe (lane 1, act 1): "needs 3 in the Casket";
  - a second Masterstroke (lane 2, act 2): 3 Energy retained with no
    3-Energy turn.
- **Open the Casket was tried from hand while it sat in the discard pile,**
  three times across lane 1's acts. One of those missed a lethal by 3.

## Screen and text problems
1. **"Incoming this turn" ignored Dusk Plans** (lane 2, both acts). It
   overstated damage, and lane 2 died 1 Block short. Fixed after the round
   by #932: the bridge now sends a waiting Dusk Plan's text, and the line
   counts its Block. It shipped in 0.2.4468.
2. **The Plan list prints a waiting Plan's damage without the target's
   Vulnerable.** Surging Shoal showed 50 there against 75 on the card in
   hand, and 75 landed. The cause: a queued card is in no pile, so the game
   never refreshes its number (the #932 investigation). Backlog.
3. **Tide Wall's Plan reads the enemy's intent when it is carried out, not
   when written.** The face says "plus the damage the enemy intends", and
   the seat read that as the intent on screen.
4. **Copy numbers renumber after a play.** A seat typed "Frantic Escape (2)"
   after the first copy was played and got the cost-2 copy; that cost 20 HP.
   Backlog.

## What to change (built with this record)
1. **Tide Wall's Plan:** "plus the damage the enemy intends next turn."
   Wording only. The Plan is carried out next turn, and that is when it
   reads the intent.
2. **Sea Glass Harvest's now-line: 6 [7] Block becomes 8 [11],** Coral
   Bulwark's Common rate, so the card is a fair Block card when no status is
   in hand. Its Plan is unchanged. Prediction: no NEVER AGAIN next round.

**Not changed: the damage gap.** It is the kit's open design question (the
2026-10-04 Big Plan pass named it a paper after [USER]'s run). This round
adds the evidence: per-turn damage at half a base character's, and runs
lost in boss damage races while reaching the same floors.
