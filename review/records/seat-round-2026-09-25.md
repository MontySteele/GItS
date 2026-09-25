# Seat round, 2026-09-25 (overnight)

**Why this round ran:** a rule change and new numbers.
- The Klee playtest fixes and the balance review (#658) went out on build 0.2.3739+proto.
- The Furina Stage changes (#659) went out on build 0.2.3744+proto: the orb-style full-stage summon, the performer and Stage tooltips, and Undercurrent at cost 1.

**The seats:** four, two per character. All ran on the arms klee, companion, kokomi and furina-stage. The raw records are in `review/qa/blindplay/` and are gitignored.

| Seat | Character | Budget reached | How far it got |
|---|---|---|---|
| GPT-6 Sol (Codex), lane 1 | Klee | 150 acts | 7 fights |
| Opus, lane 2 | Klee | 120 acts | 6 fights, floor 9, all won including the Phrog Parasite elite |
| GPT-6 Sol (Codex), lane 1 | Furina | 150 acts | 4 fights |
| Opus, lane 2 (second attempt) | Furina | 119 acts | 4 fights, stopped in the Terror Eel elite at 55/140 |

## Klee

**What played well:**
- Both seats named the same decision in every fight: let the Bombs grow another turn, or set them off now and take less damage. The GPT seat: "A good Block draw made waiting easy; a hard attack pushed me to detonate sooner."
- Mines killing enemies just before their hit.
- Choosing which enemy gets Jumpy Dumpty's Bomb.
- Ka-pow! (fire everything) against the new Pocket Match (fire only the largest) on a stacked enemy. This is the choice #658 built Pocket Match for, and the Opus seat met it unprompted.
- The GPT seat had no "never again" card.

**What did not:**
- **Unspent Sparks in the Opus run.** Fights ended with 3, 4, 10 and 10 Sparks unspent. Its deck held one Spark sink (Sparkling Burst), and it passed Dig In twice, Sit Tight and Boom Badge in the draft. So this is mostly the draft, but "nothing on screen points you to a Spark sink".
- **Sparkling Burst** was the Opus seat's never-again card: "+1 Energy with no draw and no card worth the energy".
- **Rapid Fire** was the Opus seat's automatic answer in three fights.
- **Openings repeat.** The GPT seat: "place Jumpy Dumpty, block, wait for Mk.III or a Set off card, then detonate". Jumpy Dumpty is a starter card.

**What to change:**
- Nothing yet. Sparkling Burst and Rapid Fire are one seat each. Watch both in [USER]'s next Klee run, along with whether Sparks sit idle when the draft does take the sinks that the balance review just made cheaper.
- The readability nits go to BACKLOG with the co-op set PR: the Bomb and Set off glossary lines, and the seat page not showing Ka-pow!'s damage or a fight-ending Rapid Fire's hits.

## Furina

**What played well:**
- **The GPT seat understood the Stage without help:** "builds a stage of performers who act at the end of each turn. Their Fanfare is both protection and fuel for stronger attacks, so keeping a performer alive matters as much as playing the card that summons them." This is the first read of the new performer tooltips, after [USER]'s friend found the Stage confusing.
- Both seats traded Fanfare as a shield against Fanfare to Spend.
- The Opus seat also:
  - left enemies low for Crabaletta's or Chevalmarin's end-of-turn act to finish;
  - weighed the order of Raise and summon.
- Neither seat had a never-again card besides Take the Stage, which is a starter card and is not changed.

**What did not:**
- **A Rapt Audience did nothing with one performer.** The Opus seat saw this on fight 4, turn 1. It is by design (a lone lead is also the back, and the upgraded card would make it immortal), but the face never said so.
- **The Spend chooser confused the Opus seat:**
  - it opened with a single row when Spend was not available;
  - its rows were labelled "cost 0, skill";
  - under Weak, the row title and body showed different numbers;
  - sending a card or `end turn` while it was open caused both of the seat's refusals.
- **No screen says the Stage has 3 seats**, so the Opus seat never risked a third summon. As a result, **no seat reached a full stage, and the new orb-style rule is untested by seats.** No Bow happened in the Opus run either.
- The seat page's log did not record Raises or enemy hits on the lead.
- A lone enemy printed as "Gas Bomb (2)".
- Stage Presence, Soloist's Solicitation and a free Momentum Strike were automatic plays.

**What to change:** the Furina seat-fixes PR, all readability and truthfulness, with no design moved:
- A Rapt Audience says it needs 2 performers.
- The Stage badge says "Up to 3 performers".
- The chooser is skipped when Spend is not available, and its row labels are fixed.
- The log records Raises and hits.
- Numbering is fixed.

The full-stage rule needs [USER]'s play, or a seat told to fill the stage.

## Tooling

The first Opus Furina attempt never reached its game. Lane 2 was embarked at the same moment as lane 1's Codex seat, and the lane-2 game never came up (the port refused every call). A teardown and re-embark worked. Embark lanes one at a time until that race is understood.
