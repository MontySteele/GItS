# Kokomi review, seat round 3 (2026-10-13, build 0.2.5234, five Sonnet seats, A0)

Written by Fable from the five lane records and notes in the round's scratch folder. Card texts are the Kokomi rows of `docs/prototype-surface.yaml`; engine facts are from `klee-mod/KleeCode/Powers/Prototype/KokomiPlan.cs`, `KokomiRefounding.cs` and `CompanionOverhaulPowers.cs`; the base-game yardstick is `game_ref/silent.json`. The round was read for one question from the 2026-10-13 review: did any drafted card make a fight shorter as it went on, and were Stings made and played.

**Claude's read (2026-10-13).** Agreed, and the A-list is built in its own PR, Kurage Canopy included: a Ward per carried-out Plan is the jellyfish half's Ward source in a Plan deck, it carries Watchful Shoal's dead half, and a Ward written as a Plan makes one Ward the next turn, which is a steady drip, not a loop. Raw seat records stay in the session scratchpad (gitignored by rule). The one pick is below.

**Result: 0 of 5**, but the shape moved. Lane 1 died act 2 floor 24 (Slumbering Beetle + two Bowlbugs); lane 3 lost to Kaiser Crab (floor 33); lane 4 lost to The Insatiable at 33 of 321 (floor 33); lane 2 died act 3 floor 46 (The Lost + The Forgotten, arriving at 1 HP); lane 5 died to Aeonglass at 159 of 512 (floor 48). Round 1 was 0 of 5 with two runs dead before the act-2 boss; round 2 was 1 win with every run at its act-2 boss. The base five at the same seat and ascension were 0 of 5, all dead in act 3. Kokomi is now a notch under base, not an act under it.

## 1. What the round answers

**Stings were made and played in every run.** Round 1 had zero Stings in five runs. This round, counting the seats' per-fight lines (approximate where the seats said so):

| Lane | Stings made / played | Wards made / played | Sting sources drafted | Act-1 boss won at |
|---|---|---|---|---|
| 1 | ~45 / ~40 | 0 / 0 | Endless Shoal, Kurage Bloom, Watchful Shoal | 46 / 80 |
| 2 | ~87 / ~83 | ~15 / ~11 | Kurage Bloom, Jellyfish Drift; Wards from Watatsumi Drill | 28 / 77 |
| 3 | ~53 / ~53 | ~8 / ~7 | Kurage's Wake+, Kurage Bloom+, Drift, Shoal Call; Wards from Bubble Ward | 63 / 80 |
| 4 | ~34 / ~32 | ~15 / ~15 | Kurage's Wake x2, Drift, Brine Sting; Wards from Drill | ~58 / 80 |
| 5 | ~275 / ~260 | 0 / 0 | Shoal Call x4, Bloom x2, Watchful Shoal x2, Barrage, Wake x2, Drift x2, The Shape of Water x2 | 52 / 87 |

Round 1's act-1 boss exits were 24, 33, 14, 14 and 23 of 80. This round's mean is 49. The act-1 chip problem the last review named is gone, and it went with the jellyfish half.

**Did a drafted card make a fight shorter as it went on?** Yes, in four of five runs, and each time it was a drafted engine, not a big number:

- Lane 5, act-1 boss turn 2: a Kurage's Wake Plan written on turn 1 plus Shoal Call x2 and Watchful Shoal+ put ten Stings at 9 and Barrage into Ceremonial Beast for 105, tripping its Plow stun and cancelling an 18 hit. Later: three Bowlbugs killed in one turn against 40 incoming (A2 F5, "2 Shoal Calls = 10 Stings + Shape of Water"), Owl Magistrate dead turn 3, Ovicopter dead turn 3.
- Lane 4, Cubex F4: Second Wave Plan then Kurage's Wake Plan on turn 2 made six Stings; with Resolve of Watatsumi's +2 Strength they hit 6 each and killed it from 35 on turn 3 ("the best turn of the run"). Shinobu's Ring plus her Hydro then ran Electro-Charged poison through the Kin Priest (F8, "Poison 10 killed it").
- Lane 2: Masterstroke planned (42 to 46) ended Devoted Sculptor on turn 4 before Ritual reached 27 Strength (F19) and the Turret before it fired (F18); Coral Crash turned Riptide Guard + Defend + Casket into 18 to 27 (F5, F6, F10, F22); two Resolves made Pearl Current's Plan 21 to each crab (F17).
- Lane 3: Nereid's Ascension doubled Oath to 36 (F13, F15) and Ambush to 24 (F16); Yoimiya and Itto did the rest.
- Lane 1 is the exception: its Sting engine (Bloom one a turn, Endless Shoal one per Plan) never held three Stings at once ("All Streams and The Shape of Water were underplayed because Stings are Ethereal and few"), and its death fight ran 13 turns with the Beetle at +2 Strength a turn (F13).

So the jellyfish half exists in play and compounds. The two runs that went deepest (lanes 2 and 5) were the two with the most Stings; the one with the fewest reached the fewest floors (lane 4, 34 Stings, floor 33) or died in an Unknown-room elite fight (lane 1).

## 2. Why runs still die

**Seat error, named per lane.** Lane 3 never visited a shop in 33 floors and died with 562 gold (record header), and took a card "without viewing the offer" (F1 note). Lane 5 typed `end turn` twice and skipped a whole turn at 56 HP (F4, 56 to 35), wasted The Shape of Water on one Sting through the bridge's card renumbering (F6), bought four "???" relics blind (fake merchant) and let Claws turn four Strikes into five Mauls (act 3). Lane 4 miscounted Energy and took 21 for nothing (F9), then took 13 misreading a second Sanctifying Ring (F14). Lane 1 mis-added Energy on its death turn and did not burst the sleeping Beetle on turn 4 when it had the Plans to (F13, the seat's own reading). Lane 2 made the fewest errors; its 25-card deck with seven Block cards met Mecha Knight (Burns) and Axebot x3 (Weak + Frail every cycle) back to back and arrived at The Lost at 1 HP (F23 to F25).

**Kit, from the five death fights.** They are five different fights with no shared hole: a scaling sleeper in an Unknown room (lane 1), Kaiser Crab's Weak 2 / Frail 2 with max Block 13 under Frail (lane 3, F20), The Insatiable's Sandpit race lost on a draw with no Frantic Escape until turn 4 (lane 4, F15, 33 HP left on the boss), act-3 attrition then a Strength/Dexterity steal (lane 2), and Aeonglass's Wither feeding on eight Stings a turn (lane 5). Three things in those fights belong to the kit:

1. **Frail and Weak late.** Her Block is five to eleven per card at 1 Energy, each rounded down separately under Frail (lane 5 Axebot: "Defend 3, Shell+ 6, Kelp 3"; lane 3 Kaiser Crab: "max Block 13"). Her planned Block is cut the same way; `KokomiPlan.cs` carries a Plan's Block as `ValueProp.Move` "so Frail and Dexterity read it as the carry-out will" (the Kind.Block branch). Lane 5's "Kelp Wall's plan Block lands at my turn start, bypassing Frail" is true only when the Frail was at 1 when the Plan was written and expired before the morning, and the seat generalised it. This is the base game's act-2/3 pressure on every character; her own answer is Weak (Slack Water's Plan, the Ward's Plan, War Council, Undercurrent Snare), which Aeonglass's Artifact 3 ate (lane 5). The last review audited her Block against the base five and found nine blocking Commons at the base rate; nothing this round changes that audit, so no generic Block goes in.
2. **Wither against a Sting deck.** Aeonglass adds a Wither every six cards played; lane 5 fed it "about 1.5 Withers a turn" and still took the boss from 512 to 159 in four turns. That is the base game's counter to the Silent's Shivs too (Ringing, Tender and Hard To Kill all showed up this round and all favour or punish small hits the same way: lane 5 act-1 boss, lane 2 F16, lane 2 F12). A kit that has a counter is a kit with an archetype; nothing to change.
3. **Wards exist only where drafted.** Only two rows make a Ward (Watatsumi Drill and Bubble Ward, both Common) against seven that make Stings. Lanes 1 and 5 both drafted Watchful Shoal ("Your Stings deal 2 additional damage. Your Wards gain 2 additional Block.") and never saw a Ward all run (lane 1 F13: "Watchful Shoal says Ward but I never saw a Ward in hand this run"; lane 5: "Watchful Shoal's Ward half was dead text"). Where Wards existed they were used every fight: lane 2 covered an 8 exactly with Ward + Defend (F8) and reached exactly 24 Block in the Kin Priest crisis with one (F10 T7); lane 4 wrote the Ward's Weak Plan in nearly every fight ("Drill each turn for the Ward", (b)).

## 3. What works and is kept

- **The Plan-or-now fork, learned on turn one, decided on the turn.** All five seats answered (e) yes or "mild yes" for fight 1 turn 1 (lane 1: Oath Plan vs 6 Block; lane 5: Steady Tide Plan vs Defend). Five fights later the fork has grown: Plans dodge Shrink (lane 5 F2, planned Stings at 3 over played at 2), Thorns (lane 3 F16), Weak and Ringing (lane 5 act-1 boss), and land into an enemy's new Block if written on its Defend turn (lane 4 F10, F11, "Plans land in whatever Block the enemy is still standing in").
- **Order riders.** Second Wave then Wake (lane 4 F4, F15), Gambit then Oath (lane 2 F22), Sting then Oath to kill both crabs together (lane 2 F17, its MOST WANTED). Kept as written; the one text defect is in section 4.
- **Coral Crash (C, 1 [0]: "Deal Hydro damage equal to your Block.")**, reconciled. Lane 5's NEVER AGAIN ("damage equal to Block, which this kit never has") came from a Sting deck whose only Block was four Defends and Steady Tide, took blind from a Neow box and removed at the first shop before any Block card was drafted. Lane 2 named it happiest-to-draw and lane 4 hit 13, 20 and 30 with it off Tidal Screen+ and Riptide Guard (F12, F14, F15); round 1 had it as the best card in three runs. A Common that is dead in one build and the best card in another is a build card doing its job. Keep.
- **Tidal Surge (C, 1, Ethereal: 11 [14], Plan 8 [10] to ALL).** Lane 2's NEVER AGAIN ("Ethereal Strike that vanishes when the turn has better things to do"); lane 1 carried two and used them to strip Tunneler's 32 Burrowed Block on Vulnerable for a stun (F12) and as an 8-to-ALL Plan (F4), and listed "ethereal Tidal Surge forcing use" under real choices. Eleven for 1 is above any base Common Strike-shape; Ethereal is its price, the same price Riptide Guard pays for 10 Block. Keep.
- **Kelp Wall (C: 5 Block, draw 1, Plan 12 Block).** Lane 1's NEVER AGAIN; lane 2 planned it on three no-attack turns for the 12 to 20 Block that fed Coral Crash (F6, F10, F13) and lane 5 ran two. Keep.
- **The Casket at start of turn.** Counted into exact-Block turns (lane 2 F5 "18, then Coral Crash"); lane 3's only note is "easy to forget". Kept.
- **Companions on her Hydro.** Charlotte's Cryo froze a 16 and a 30-plus hit (lane 1 F9, F13), Shinobu's Ring ran poison (lane 4 F8), Albedo closed four fights at end of turn (lane 2 F7, F17), Call the Generals gave Ayaka for an Imbalanced stun and Mizuki for a Reattach wipe (lane 5 A2). Kept.
- **For the probe's known set:** Shoal Call x2 + Watchful Shoal+ + The Shape of Water: eight Stings at 8 plus 16 from the Shape for 3 Energy, a one-turn 80 that exhausts both Calls (lane 5 A2 F5). Four Shoal Calls took a Neow box, two drafts and an event; not trivial, and the deck still lost. Keep, list.

## 4. Defects, each classified from evidence

| Item | Evidence | What it is |
|---|---|---|
| A Sting made into a full hand "silently lost" | lane 4 F4 (6 made, 5 in hand); lane 5 F4, A2 Mytes | **Page receipt, not code.** `KokomiRefounding.AddJellyfish` sends the overflow to the discard pile, the base game's rule for a generated card; the card is drawn later, not lost. The "Since last page" line should print "1 Sting to the discard pile (hand full)". |
| A planned Sting printed 3, dealt 4 | lane 1 F8 (Feint's Vulnerable was planned the turn before) | **Seat reading.** 3 x 1.5 under Vulnerable; the carry-out log prints asked and landed on purpose. No change. |
| Ethereal Stings and Wards "vanish silently" | lane 2 (c); lane 1 (b) | **Page receipt.** The faces print Ethereal; the end-of-turn exhaust has no line on the page. Print "exhausted (Ethereal): Sting x2". |
| "Sting (1)" renumbers after each play | lane 5 F6 (a Shape of Water wasted) | **Harness defect** (understudy bridge), not the kit: card handles must be stable within a turn. |
| Opening Gambit+ "no Plan followed" | lane 2 F25 (Gambit alone fizzled) vs F22 (Gambit then Oath: 22 + 18 each) | **Text fix.** The engine is right: `KokomiPlan.Drain` holds a rider in a drain-local flag, so "next" means the Plan written after it on the same turn and never the next morning. The face says only "Your next Plan deals double damage." The same window is missing from Second Wave. Texts in section 5. |
| Albedo picks "sometimes the front enemy, sometimes the one with an aura" | lane 2 (c), F17 | **Text fix.** `SolarIsotomaBloomPower` uses `CompanionOverhaulTargeting.MostAuras`; the face says "that enemy". |
| Tablet event: "Give Up" still cost 3 Max HP | lane 2 F2 (80 to 77) | **Outside the kit:** a base-game event. Not ours. |
| Vambrace shows doubled Block on cards that will not be first | lane 5 (c) | **Outside the kit:** base relic; the bridge's hand preview applies the relic to every Block card. A preview note, not a card change. |
| Second Sanctifying Ring only extends the first | lane 4 F14, NEVER AGAIN | **Seat reading.** "For 3 turns" is the base template and a second copy adds turns, as every timed power does. No change; the seat's own "I misread the buff". |
| Sown refunded Energy only on the first Oath | lane 4 (c) | **Seat reading.** The enchantment says "first play each combat". |
| Change of Plans "unplayable with no Energy" with four Plans waiting | lane 4 F6 | **Unexplained; reproduce.** The card costs 0 and its only gate is a waiting Plan. One lane, one turn. |
| When a Plan reads Strength | lane 4 F8 ("Strength is read when written") vs lane 2 F16 (Masterstroke 40 not 42 under Tender's this-turn loss) | **One test, then a tip line.** The brief (rule 3) says Strength counts and does not say when. |
| Yoimiya preview "19" on an aura that expired before the hit | lane 3 F6 | Companion preview reads the aura now, not at the hit. Minor; log it. |

## 5. Changes

### A. Build now (no pick needed)

1. **Opening Gambit (U).** "Deal 7 Hydro damage. Plan: Apply 1 Vulnerable to ALL enemies. The Plan written after it this turn deals double damage." Numbers unchanged (9 upgraded).
2. **Second Wave (U).** "Deal 7 Hydro damage. Plan: The Plan written after it this turn is carried out twice." Numbers unchanged.
3. **Bubble Ward (C).** "Gain 6 Block. Add a Ward to your Hand." (upgraded 9). Today 5 [8]. Yardstick: Cloak and Dagger is 6 Block and a Shiv at Common (`game_ref/silent.json`); under Frail today's 5 + 4 rounds to 3 + 3 against Coral Bulwark's 6, which is lane 3's "worse than Coral Bulwark at the same cost" (NEVER AGAIN). At 6 the Ward's Weak line is the choice and the Block line is not behind.
4. **Kurage Canopy (U Power).** "Whenever the Bake-Kurage carries out a Plan, add a Ward to your Hand." Today "gain 2 Block" (3 upgraded; upgrade becomes the Ward upgraded). This is Endless Shoal's Ward twin (Endless Shoal: "...add a Sting to your Hand") and gives the Ward a third source so Watchful Shoal's second half is live in a Plan deck (lanes 1 and 5 held Watchful Shoal with zero Wards). Evidence against: lane 4 played Canopy+ once (F15). The one taste call on this list; leave it if the main session disagrees.
5. **Albedo, Solar Isotoma (Companion, R).** "At the end of your turn, if any enemy has an aura, deal 8 damage to the enemy with the most auras and gain 4 Block." Matches the code.
6. **Page receipts (bridge, not cards):** the hand-full discard line, the end-of-turn Ethereal line, stable card handles within a turn, the Change of Plans reproduction, and the Strength-moment test with a line in the Plan tip.

Not changed, with the reason: Tidal Surge, Coral Crash, Kelp Wall (section 3); Sanctifying Ring, Sown, the tablet event, Vambrace (section 4); Watchful Shoal's numbers (+2 [+4] against Accuracy's +4 [+6], but it also pays the Ward); the Sting token (4 [6], Plan 3 [4] to ALL, the Shiv's 4 [6]); Kurage's Oath and Slack Water (starter; ruled 2026-10-13). No Block card gains a number beyond item 3, by the audit in section 2.

### B. Picks

No starter change and no new direction is raised by this round. One stage-gate question is the user's:

1. **Kokomi's Prototype finish line.** Three rounds in: the act-1 chip is fixed, the jellyfish half is drafted and compounds in four of five runs, every seat's MOST WANTED turn was kit-specific (section 1), and the deaths are five different fights with seat errors in four. **(a) Default:** build the A-list, redeploy, and the next Kokomi play is the user's own finish-line run (CLAUDE.md: the user plays at a kit's finish line; no rule changes here, so no earlier run is owed); a further Sonnet round only if that run finds something. (b) One more five-seat round on the A-list build first, read for Wards made and played the way this one was read for Stings. (c) Hold at Prototype and open a Block paper; not recommended, the audit does not support it.

## Ruled

[USER], 2026-10-13: "On Kokomi - have we already done a review pass today for her least-played cards to bring them up to snuff? ... If we did, then I think we build the A-list and run another seat round to be sure (I'm out for a few more hours)." The least-played pass was the level pass (`review/ruled/kokomi-level-pass-2026-10-12.md`, ruled all defaults). So pick 1 is (b): the A-list is built (#1218) and five more seats play it, read for Wards made and played.

On Albedo, Solar Isotoma: "we can only have one aura, right? So that just reads 'deal 8 damage and gant 4 block to one enemy with an aura,' which sounds underwhelming at Rare." Then: "Not that the numbers are bad (free block is very good), but that a Rare should be more dramatic and the Mondstadt pool already has powers for free block." One aura per enemy is right (`AuraCmd`), so "most auras" was wrong on two faces. Albedo is redesigned in its own PR, and Jean's Dandelion Breeze says "an enemy with an aura".
