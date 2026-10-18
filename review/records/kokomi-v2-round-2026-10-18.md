# Kokomi v2 round, 2026-10-18: do the archetypes appear on their own?

These are the first seats after the v2 build (#1420, `review/active/kokomi-cards-2026-10-18.md`, picks 1 (b),
2 (a) and 3 (a)):
- **Draft the Orders** replaces Shell of Sanctuary;
- **Tidal Rebuke** spends your Block;
- **Tidal Riposte** stores its bonus for your next Attack;
- **Endless Shoal and Kurage Canopy** skip Sting and Ward Plans.

Six blind Sonnet seats played whole runs at A0 on 0.2.5867, with the user asleep and the game cleared for
the night. Lanes 1 to 3 drafted freely. Lane 4 was briefed toward Grand Strategy and lane 5 toward Read the
Tide. Lane 5 ran twice, because its first run died in act 1 before it saw a Rare. Every seat also answered
"What did your deck build toward, its best turn, and what did you give up?" Seat records are in scratch
`seats/seat-lane*`; transcripts are not kept.

## Results

| Lane (draft) | Seed | End floor (cause) |
|---|---|---|
| 1 (free) | 30KMHAVG9SMQ | 48 (Test Subject, form 2, act 3 boss) |
| 2 (free) | CYHZM9S0VPW6 | 33 (Knowledge Demon at ~127/379) |
| 3 (free) | DJCAV76ZKAUN | **48 W** |
| 4 (Grand Strategy) | YEWA0B7AVE45 | 33 (Knowledge Demon at 30/379) |
| 5a (Read the Tide) | R41TX5Q0ZQYN | 17 (Ceremonial Beast at 19 HP) |
| 5b (Read the Tide) | QKX3T5L8AM2P | 48 (Test Subject at 103/300) |

Against the base five over all bot runs since 2026-09-01 (`tools/telemetry_report.py --character Kokomi
--character base5 --since 2026-10-18T03:45 --baseline-since 2026-09-01 --feed bot`), normal fights only:

| Act | Damage a turn vs base | HP lost vs base | Before v2 (rounds since 2026-10-14) |
|---|---|---|---|
| 1 | 0.99 | 0.82 | 1.10 / 1.05 |
| 2 | 0.91 | 0.77 | 0.91 / 0.91 |
| 3 | 1.15 | 1.25 | 1.02 / 1.30 |

Her numbers barely moved. That's expected: v2 changed what her decks aim at, not how strong they are.

**Bosses ended five of the six runs.** Two seats lost to Knowledge Demon's choices, which take away draw,
Energy and Block (Mind Rot, Waste Away, Disintegration). A Plan deck that needs a setup turn suffers most from
those. One more seat died in the act 1 boss fight, after a Flank Plan read the boss's next intent and dealt
0.

## What each deck built toward (the seats' own answers)

- **Lane 1 (free):** Plans plus Electro-Charged poison from a Companion's Ring. Masterstroke, Oath+ and Wrath
  as bursts, with Stings pumped by Watchful Shoal.
- **Lane 2 (free):** "plan-then-hit". Shoal Call's Stings planned as 3 to ALL, cashed by Tideturn+, Press the
  Advantage and Wrath. Best turn: 3 planned Stings into Tideturn+ for 40.
- **Lane 3 (free, won):** "many cheap or free Plans (Stings from Shoal Call), doubled by Gambit or Nereid's
  Ascension, scaled by Strength". Best turn: Gambit, Oath+ and Stings for 183 on a boss form.
- **Lane 4 (Grand Strategy):** 4 to 8 Plans, most of them Stings, behind two Following Currents and Battle
  Formation, finished by Feint. Best turn: seven Stings planned, then Feint+ for 64.
- **Lane 5b (Read the Tide):** drifted into "a Plan-and-AoE deck". Its best moment was still the brief's: Tide
  Wall's Plan landing 38 Block on a 30 hit.
- **Lane 5a (Read the Tide):** Kelp Wall, Brine Sting and Flank worked as intended. Best turn: 22 damage back
  for 0 taken.

## What played well

- **Arranging Plans is the fun.** Every seat named a planned turn as its most-wanted turn: Opening Gambit
  before Oath, Second Wave doubling Oath, and Nereid's Ascension doubling the first Plan. Keeping the
  current Nereid's Ascension (pick 1 (b)) looks right: lane 3 called it a turn-maker.
- **Read the Tide's Commons and Uncommons work when drafted.** Lane 5a's Brine Sting, Kelp Wall and Flank,
  and lane 5b's Tide Wall.
- Enemy rules gave real puzzles: Spiny Toad's Thorns (Plans dodge it), Test Subject's Intangible (plan on
  its Intangible turns), and Crab Rage.

## What did not

1. **Free drafting still converges on one deck: cheap Stings as Plans, plus a multiplier.** All three free
   seats, and the Grand Strategy seat, fed their planning counts with 0-cost Stings. v2 stopped
   Stings from replacing themselves through Endless Shoal. But the count payoffs (Feint, Turning Tide,
   Tideturn, Breakwater, Shoal of Spears, Battle Formation) still count a Sting Plan like any other. That's
   the same hole, in different cards.
2. **Read the Tide's new Rares never showed up.** Tidal Rebuke was played 0 times this round: lane 3 removed
   it at a shop and called it "never again", in a deck that wasn't built for it. Tidal Riposte was played once,
   and lane 5b says its bonus never visibly paid off. That's being checked as a possible bug. Neither seat
   aiming for Read the Tide stayed there: Rares are rare, and the archetype has no Uncommon that pays off
   Block.
3. **Plans that read enemy intent read it when they land.** Two seats were caught out by this (Flank dealt 0
   on a changed intent, Tide Wall added nothing on an Empower). The rule is right, but nothing says it.
4. **Status cards and Frail** were "pure tax" in two seats. That's the base game working as intended,
   recorded only.

## What to change

1. **Hygiene, being built now:** the Plan tip will say Plans read the enemy when they land. Riposte, Pincer
   (a seat never saw its Plan take effect) and a doubled War Council line are being checked. A loop probe for
   Kokomi is being built.
2. **A pick for [USER]:** make the count payoffs skip Sting and Ward Plans, as Endless Shoal now does. That
   would split Grand Strategy (arranged real Plans) from the Shoal (Stings played now) along the line the
   paper drew. Recommended.
3. **A pick for [USER]:** give Read the Tide an Uncommon payoff, so a deck aiming for it finds one before
   the Rares. Its job would be the one Coral Crash does at Common. Not drafted yet.
4. Tidal Rebuke's fate waits for a deck that actually ran it: one seat played it 0 times.
