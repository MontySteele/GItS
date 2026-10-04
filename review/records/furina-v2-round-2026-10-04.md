# Furina v2 seat round, 2026-10-04

**What ran.**
- Build 0.2.4370 (the re-founded Stage, #892), ascension 0.
- Two lanes, with a Sonnet seat for each act and only a state handoff
  between acts.
- [USER] was away and asked for "two seats without me to sanity check
  basic viability".
- Raw records are in the session scratchpad and are gitignored.

| Lane | Seed | Act 1 | Act 2 | Act 3 |
|---|---|---|---|---|
| 1 | KJ8XRKSRPADD | Ceremonial Beast, ended 57/90 | Kaiser Crab, ended 12/90 | lost on floor 48 to the final boss (Test Subject, 123 HP left), one Block short |
| 2 | 3CFKT03MHT67 | Waterfall Giant, ended 29/78 | Knowledge Demon, ended 42/88 | lost on floor 43 to the Mecha Knight elite |

**Verdict: basically viable.** Both runs cleared two acts and died in act 3.
That is in line with recent Klee and Varka rounds. Nothing crashed, and no
rule misbehaved.

## What played well
- **Spending Fanfare was the kit's steady decision.** Both seats faced it
  every turn: Spend 3 on Curtain Rise, Tidal Flourish, Spirited Aria or
  Interval Bell, or bank it. On lane 1 the three Spend cards each traded
  differently: damage and Hydro, draw, or Energy.
- **Guests produced the best turns once drafted:**
  - Lane 2: "Ousia + Navia Bow + Tutti!+ made Navia hit three times", taking
    the Mecha Knight from 258 to 147.
  - Lane 1: "Regal Bearing+, Defend+, Tutti! turned stored block into
    Wriothesley's 32", taking the act-3 boss from 94 to 3.
  Both are guests bending a rule, as the paper intended.
- **A Bow pays.** Lane 1 found that a full-stage summon Bows Usher for
  Fanfare and "liked [it] once I saw it".
- **Reaction previews drove planned turns.** Hydro then Cryo for Frozen
  showed up in nearly every fight.

## What did not
- **Directing and seat order went unfelt for two acts.** Both seats passed
  Encore!, Stage Whisper, Lynette, Charlotte and Chevreuse in act 1. Lane 1
  said "nothing told me why seat order mattered; I never reordered
  anything." Cue cards were only picked up in act 2, and lane 2 called
  Stage Whisper "just cue Navia".
- **Fanfare piled up with one outlet.** Early decks held 5 or 6 Fanfare
  with Curtain Rise as the only Spend. Rising Applause and Season Tickets
  were called filler.
- **Eviction went unseen.** Three times a summon onto a full stage Bowed
  Usher off unnoticed. On lane 2 this happened on a boss's 27-damage turn.
  The rule is printed, but the card gives no warning on play.
- **The stage carried some turns alone.** Lane 1, act 2: "most fights had
  one or two dead turns where the end-of-turn stage acts did the work."
- **Weak cards:**
  - Tide of Applause ("too few reactions to earn a power slot");
  - Arkhe Alignment (2 Energy, never played);
  - Charlotte ("the draw bonus never mattered").

## Fixed already
#893, deployed in 0.2.4372:
- Interval Bell's chooser printed "Spend {IfUpgraded", and Raise a Toast
  had the same leak.
- Tidal Flourish and Quick Flourish previewed a reaction their plain mode
  cannot cause.
- Grand Deluge's text hid that its damage hits ALL.

## What to change (for [USER]'s own play, not yet built)
1. **A summon onto a full stage names who will Bow**, on the card in hand.
   This is a legibility fix and needs no design change.
2. **Seat order needs a reason a player can see in act 1.** Only Charlotte
   in front of a star, and Lynette, make order matter, and both are
   Uncommon guests. [USER]'s play decides whether this is a problem.
3. **A second early Spend outlet**, so Fanfare is not banked idle. Watch
   in [USER]'s play before adding one.
4. Tide of Applause, Arkhe Alignment and Charlotte are candidates for a
   number pass after [USER]'s play.

Not ours: Crab Rage's 99 Block never showed on the board, the Mecha
Knight's Artifact blocked Frozen, and the Slimed and Toxic statuses were
pure clog. Those are base-game behaviours.
