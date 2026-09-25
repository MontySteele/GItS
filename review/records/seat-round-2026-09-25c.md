# Seat round, 2026-09-25 (evening): Furina draft 3

**Why this round ran:** a rule change on 0.2.3778+proto (#672). [USER] ruled the Stage review:
- the Bow is the performer's act, once more;
- no act applies Hydro;
- performers behind the front lose half their Fanfare above 5 at the end of the turn.

**The seats:** two Opus seats. Codex was out of usage ("You've hit your usage limit"), so no GPT seat ran. Two earlier attempts died on a seat-page leak, the raw event name `hit_furina`, which #674 fixed. Raw records are in the session scratchpad.

| Seat | Budget reached | How far it got |
|---|---|---|
| Opus, lane 1 | 120 acts | 5 fights won, stopped in the first elite (Skulking Colony at 27/75), floor 7 |
| Opus, lane 2 | 120 acts | 5 fights won, stopped in the Phantasmal Gardener elite, floor 8 |

## What played well

- **Timing the end-of-turn acts.** Performers act before the enemy moves, so both seats planned kills around them:
  - lane 1 aimed Ensemble Piece at the slug the performers would not finish;
  - lane 2 filled the third seat last, and Full House's doubled acts killed a Corpse Slug and stunned another.
- **Card order.** Lane 2: raise the back performer's Fanfare, then Ousia Surge, then the Spend, then summon last. Improvised Number goes before the other summons, since it only summons on an empty stage.
- **The first Hydro payoff.** Tidal Flourish's Hydro set up Crashing Waves "exactly as printed", a clean two-turn payoff under the new Hydro rule.
- **Banking for a Spend** (Rising Applause, then Curtain Rise two turns later). Both first turns presented a decision.

## What did not

- **The Bow after a hit did nothing.**
  - Seven times across both seats, Usher's Bow ("Furina gains 3 Block") came after the killing hit, on the enemy's turn, and had expired by Furina's turn.
  - The afternoon seat had said the same.
  - "The plain exit is the minimum" was the accepted trade, but a Bow that reads as broken is worse than a small one.
- **The front was too thin.**
  - Lane 2's opening Usher (3 Fanfare) died on round 1 or 2 in five of six fights.
  - Multi-hit enemies cleared the whole stage every round of the elite.
  - So Full House (lane 2's never-again), Ensemble Piece, Ousia Surge and the Spend bonuses sat at their minimum.
  - Lane 1 never filled three seats: Take the Stage was its only summon, and its random rolls never brought back Usher.
- **A Five-Century Act** was lane 1's never-again card.
- **Unclear on screen:**
  - a Spend never appears in the stage log;
  - Chevalmarin's act logged "6 in total" and later "4 in total" against four enemies;
  - "What you played" never names the performer a random summon rolled;
  - "Elemental Reaction" was never defined;
  - who is the back performer when one performer stands alone (lane 1 learned it from the Spend chooser).
- **Dead shipped cards:** Duet and Courtroom Drama depend on Companion cards the seat almost never saw. The guest batch's supporting pool replaces those shipped rows.

## What to change

The Furina draft-3 fixes PR:
1. **A performer knocked out on the enemy's turn Bows at the start of Furina's next turn.** The display shows the Bow as waiting.
2. **The front gets thicker.** The opening Usher goes from 3 to 5 Fanfare, and summons arrive with 2 instead of 1.
3. **The seat page:** a Spend log line, the Chevalmarin log checked, the rolled performer named, and the reaction glossary line attached.

The guest batch (`review/active/furina-guest-batch-2026-09-25.md`, ruled this evening) is built on top of these.
