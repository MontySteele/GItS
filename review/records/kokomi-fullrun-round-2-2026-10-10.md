# Kokomi whole-run round 2, 2026-10-10

This round grades the two growth Powers (`review/active/kokomi-growth-powers-2026-10-10.md`, built in #1060): Flood Tide and the new Grand Design.
- Five whole-run Sonnet seats on the base-five seeds, A0.
- Build 0.2.4807+next.
- The packet, records and scripts are in the session scratchpad (`kokomi-fullrun-r2/`), which is gitignored.
- A Fable reviewer reviewed the round. The main session accepted the review with one correction, listed at the end.

## Result: 0 of 5, now level with the same-night base

| Seed | Round 2 | Round 1 | Base, whole-run (same night) |
|---|---|---|---|
| CYHZM9S0VPW6 | floor 39, Axebot (act 3) | floor 33 | floor 33 |
| DJCAV76ZKAUN | floor 8, Bygone Effigy elite | floor 17 | floor 24 |
| 30KMHAVG9SMQ | floor 33, The Insatiable | floor 43 | floor 33 |
| YEWA0B7AVE45 | floor 40, Soul Nexus elite (act 3) | floor 33 | floor 33 |
| R41TX5Q0ZQYN | floor 33, Kaiser Crab | floor 17 | floor 33 |

- Mean death floor 30.6, against 28.6 in round 1 and about 39 for the pooled base (`base-five-fullrun-2026-10-10.md`).
- Against the same night's whole-run base, she is level or ahead on four seeds. The floor-8 elite death is the fifth.
- With five runs, the gap to the pooled base is about 1.5 standard errors. So she is at the whole-run base, but not shown to be at the pooled base.
- Three of the five deaths were by exactly 1 HP or 1 Block.

## The four lines from the Powers paper

| Line | Result | Grade |
|---|---|---|
| Act-2 boss damage a turn above 40 (round 1: 26.9) | median 38.4 | Missed by 1.6. Level with the pooled base (39.4) |
| Act-1 normal fights do not speed up by more than 10% | 3.6 turns, against 3.5 | Met. Act 1 was not trivialised |
| Flood Tide taken when offered, played when held | taken at 3 of 3 card rewards and the 1 bundle; played in 69% of fights held | Met |
| Grand Design's top Strength under 30 | top Strength 5 | Met, but the card never really ran (below) |

**The late-game collapse is gone.** Plan damage per fight by act:
- Round 1: 22.0 / 16.8 / 5.7.
- Round 2: 25.8 / 52.6 / 53.3.

The two act-2 bosses above 40 had an engine: lane 1 the Casket with Grand Design, lane 4 Nereid's Ascension with Flood Tide and What the Tokoyo Took. The two below 40 had none. Lane 3 took a Prismatic Gem over the Watatsumi Casket. Lane 5 never saw Flood Tide and entered the boss at 32/80.

## What is still wrong

**1. Act 1 still bleeds.**
- HP lost per act-1 normal fight: 11.0, against 11.9 in round 1 and 5.9 for the pooled base.
- Her damage a turn is 22% below base, and her Block a turn is 37% below base.
- **Causes:**
  - A Plan lands a turn late, so a three-turn fight pays a third of its damage on turn 2 and the enemy swings once more.
  - Kurage's Oath is almost always written as a Plan, so its Block never happens.
  - Open the Casket at a count of 1 or 2 spends a Strike's Energy for 1 or 2 Strength.
- Her act-1 Commons are at base rate, so the pool is not the cause. The rest is the starter, which is pick 1.

**2. Deaths with no Block in hand: a drafting habit.**
- Seats took 14 of the 47 Block cards offered at card rewards. Coral Bulwark was taken 1 of 4 times, Bubble Ward 0 of 2, Kelp Wall 0 of 2.
- The same-night base seats died the same way, so the pooled reference already contains this habit.
- No kit change.

**3. Grand Design can't run as built.**
- The rule works: with it in play, floor 35's Casket read 3, 5, 7, 9 across Opens.
- But Open the Casket is one card, dealt into the opening hand, with no Exhaust. Once played, it sits in the discard pile until the deck cycles, which is once a fight in a 36-card deck.
- The paper's risk model and its sim assumed an Open every turn. The build doesn't allow that, which is why top Strength was 5.

**4. Change of Plans: 0 of 8 taken, even at cost 0.**
- What it does is strong: the Plan's number lands this turn, and the Casket still ticks.
- But its text shows no number, so seats take a card with one instead.

**5. What the Tokoyo Took reached 31 Strength.** This is in line.
- It needed a Casket of 15 on turn 4 of an act-2 boss, built from two Rares and an Uncommon Power.
- That gave 55 damage a turn, about the per-act base's 58.
- It is a one-use Exhaust card, the Casket's Limit Break. Keep.

## What changes (Claude ships)

1. **Change of Plans:** "The Bake-Kurage carries out your first Plan now. Draw 1 card." It still costs 0 and Exhausts; the upgrade removes the Exhaust.
2. **Grand Design:** "Open the Casket no longer empties the Casket. At the start of your turn, put it into your hand." This makes the card the one the paper simmed. It is graded on the same under-30 line, and the lever if it fails is the ratio (Strength equal to half the count), not a cap.
3. **Open the Casket** shows its number in combat ("Gains N Strength"), the way Driftglass does.
4. **Seat-page polish:**
   - `--define` also searches enemy briefings;
   - the Neow bundle confirm line lists every card taken;
   - a Plan row whose number the target's Vulnerable raised says "(after Vulnerable)".

**Checked in source, no change.** The packet's other defect claims are base game, a seat misread, or a rule:
- Press the Advantage's Hard To Kill cap;
- Oath's Plan rising under Vulnerable;
- Kunai's Dexterity on Evening Watch's dusk Block;
- `choose` taking a whole Neow bundle;
- the bridge refusing to plan a Strike;
- Sandpit's countdown.

## The main session's correction to the review

The review proposed a Sonnet round on the fixed build "in parallel" with [USER]'s run. Seats never run while [USER] plays, so the round can only come before or after his run. That is pick 2.

## For [USER] (settled 2026-10-11)

Both picks were settled by [USER]'s Kokomi run and his rulings after it ("you're good to proceed", 2026-10-11):
- **Pick 1 (act 1):** neither option was taken as written. [USER] ruled a Casket change instead: "I think that the casket should start at 0 and then have a ramping cost (goes up by 1 each time)" (#1067). He also allowed starter changes: "I'm also fine with modifying the starters if the rates are low". Kurage's Oath's Plan and Slack Water rose with the Plan pricing (#1066, #1069).
- **Pick 2 (his run):** (a). He played her before any further seat round.

The picks as offered:

1. **Act 1.** The round-1 pool tempo fixes moved act-1 HP loss only from 11.9 to 11.0 a fight, against base's 5.9. The rest comes from the Plan's one-turn delay and the starter, which only you can change.
   - **(a) Default:** leave the starter. Play the build and judge act 1 by feel. Only the Change of Plans retune ships.
   - (b) Slack Water deals 6 damage instead of 4, with its Weak and Plan line unchanged.
   - (c) Open the Casket draws 1 card even unupgraded (today only the upgrade draws), so an early Open is never a dead card.
2. **Your Kokomi run.**
   - **(a) Default:** play her on the next +next build, with the fixes above, before any further seat round. Seats grade the fixes after your run.
   - (b) First run one Sonnet round on the fixed build, about half a day of game time, then play.
