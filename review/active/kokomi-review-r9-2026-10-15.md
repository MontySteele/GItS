# Kokomi review, round 9, 2026-10-15

Five blind Sonnet seats, whole runs at A0, on build 0.2.5538 (the round-8
build: Shell of Sanctuary, Evening Watch, Undercurrent Snare, Surging Shoal and
Feint changes, plus ten display fixes). The seat records are in the session
scratchpad (`seats/archive/kokomi-r9-l1` to `-l5`). Take rates come from
`tools/offer_report.py --character kokomi --since 2026-10-14T23:15` (91 card
rewards, 15 shop offers).

## Result: 2 wins in 5

| Seed | End |
|---|---|
| ARMU2JSQJ7XL | **Won**: Soul Fysh, Kaiser Crab, Aeonglass. Lowest HP 23 |
| LNYY2S8E9X6C | **Won**: Waterfall Giant, The Insatiable, Test Subject. Ended about 60/80 |
| UU4ZHAR84QVV | Died in act 3 (floor 46) to the Slimed Berserker, left at 23/261 |
| 32V170EHU5BP | Died to Kaiser Crab (act-2 boss), floor 33, by 2 HP |
| K565PR61DY54 | Died to Kaiser Crab (act-2 boss), floor 33 |

Round 8 won 0 of 7, and round 6 won 1 of 8. This is her best round. Three of
five seats reached act 3, and act 2 is no longer where most runs end.

## What wins

There are two different winning routes, and both are the kit's own:
- **Stacked Plans.** Nereid's Ascension (the first Plan is carried out twice)
  and Opening Gambit (the next Plan deals double) with an area Plan. The best
  turns were 93 damage from Tideturn+ with five Plans waiting (The Insatiable),
  54 to every enemy from Gambit then Tamakushi's Wrath, and 68 from two Lance
  Plans under Strength.
- **Electro-Charged poison.** Shinobu's Sanctifying Ring ticks Electro on every
  enemy at the end of each turn, and her Hydro Stings react with it. One seat
  poisoned three Gardeners in a single turn and won the run on this engine.

The round-8 Block changes landed: Surging Shoal was taken 4 of 7 times (was a
skip), Shell of Sanctuary 3 of 12, Kelp Wall 5 of 14. No death this round was
"a hand with no Block card" against an ordinary act-2 fight.

## What loses

- **Kaiser Crab, twice.** Its Surrounded rule adds 50% damage from the enemy
  behind you, and only a card played on an enemy turns you. Both losing seats
  understood facing and tried to control it. Lane 1 turned toward each
  attacker but was dealt a hand with no targeted card on the turn Rocket was
  behind it. Lane 3 turned on several turns, but it dealt only 80 of 408 HP in
  seven turns and left two potions unused. The winning seat chose its facing
  every turn and took a 49 back attack down to 24. So the losses mix execution,
  hands with no way to turn, and too little damage. Kokomi plays many cards on
  the Bake-Kurage and defends with untargeted Block, so turning may cost her more
  than it costs the base characters. No rule change yet. The next round asks
  whether the seat could reach the facing it needed with its hand, and what
  turning cost its Plans.
- **Status floods.** The act-3 death was ten Slimed cards from the Berserker
  crowding out her Block cards. Toxic and Dazed did the same in round 8. Her
  card for this, Tidecleanse, is the least-taken card in her pool (below).

## Changes Claude builds (no pick)

**Cards.** Kokomi is at Prototype, so these are Claude's.
1. **Tidecleanse** (Common, 0): "Exhaust up to 2 [3] Statuses or Curses in
   your Hand. **Draw 1 card for each.** Apply 1 Weak." Taken 1 of 18 this
   round and 0 of 7 in round 8. A status flood is the one time she needs it, and
   then it should give the hand back. With no statuses in hand it draws nothing,
   so it is not a Common cantrip.
2. **Orders from the Shrine** (Common, 1 [0]): "Choose 1 of 3 random Common
   Inazuma Companions to add into your Hand. **It costs 0 this turn** and is
   Ethereal." It cost a card and an Energy to make a card that cost another
   Energy. Taken 1 of 9; one seat's "never again".
3. **Sangonomiya's Orders** (Uncommon Power, **2**; upgrade Innate): "At the start of
   your turn, add a random Common Inazuma Companion to your Hand. **It costs
   0** and is Ethereal." Taken 0 of 7, and 0 of 6 in round 8. A free card every
   turn is strong, so the Power costs 2.

4. **Shell of Sanctuary** (Common, 1): "Gain 6 [9] Block. **Retain.**" Its
   round-8 text (7 Block plus 2 per Plan waiting) sat on top of Breakwater (6
   plus 3 per Plan); the two gave the same 9 Block at one Plan. Shell now does
   a different job: it keeps defence in hand for the turn that needs it. Five
   round-8 deaths were a final hand with no Block card.

Left alone, with the reason:
- Coral Crash (0 of 13) is a Body Slam; the winning seat used it for 69 against
  Test Subject.
- Gorou Inuzaka (0 of 12) was praised in round 8.
- Press the Advantage pays 11 only if a Plan is written first, which is the
  design.
- Bubble Ward (one "never again") and Endless Shoal (one "never again") were
  both taken every time they were offered.
- Feint (2 of 16) is filler at Common.

**Text and display.**
5. **Opening Gambit's doubling** goes into the Plan preview. Three seats saw it
   print 10 or 13 and land 27 or 30. The preview must show the number that will
   land.
6. **An overridden element** prints in the card text. Surging Shoal+ under Razor
   showed the Electro tag and still read "Deal 13 Hydro damage".
7. **End-of-turn reactions** print a receipt. Poison appeared on enemies after
   the Ring's tick with no reaction named.
8. **One wording for "no aura".** Sucrose says "(no aura: no Swirl)" and Varka
   still says "(No aura to Swirl)". Use Sucrose's wording for both (text only;
   Varka's numbers do not change).

**Seat harness only.**
9. A **card-limit page** (Smoggy, Sloth) says that writing a Plan counts as
   playing that card, and that a planned **Companion** is played again when its
   Plan lands. Ordinary Plans only carry out their effect, so card limits and
   "whenever you play" triggers treat the two differently. The Plan hover gains
   one short sentence on the Companion case if it fits the tip limit; if not,
   the seat page carries it alone. *(Pick 1 (a), 2026-10-15: the Companion
   sentence is gone from both, with the rule; the page keeps "writing a Plan
   counts as playing that card".)*
10. The **"last carry-out" box** clears between fights. It once showed a Plan
   from an earlier fight at a rest site.
11. The **Energy line** names the source of each extra Energy that turn, not a
    fixed list.

## Next

Build 1 to 11 on this branch. No Kokomi seat round follows at once. Her next
round waits until Yae's round-3 build has been played, because seat time is
the scarce budget. The next Kokomi review judges decision quality more than the win rate:
- whether setup turns leave affordable defence and a way to turn;
- whether Sangonomiya's free Companions make interesting choices;
- whether feeding the Plan queue starts to beat choosing which Plan to write.
  Free Stings, per-Plan rewards and the new free Companions all push that way.
  Then it checks whether act 3 becomes the new wall. She is not ready for
  Balance until those answers are in.

## Pick (added 2026-10-15, after [USER] asked whether seats use it)

**Pick 1: planning any Companion.** [USER]: "I'd be curious to know if seats
actually make use of that or if we're overcomplicating them for no gain." In the
six Kokomi seat transcripts still readable (rounds 8 and 9), Companions were
played 241 times and written as a Plan 22 times (9%, about four a run). Several
of those 22 were her own Companions that print a Plan line anyway (Gorou,
Qiqi). Planning a Companion is also the one Plan that plays its card a second
time, which is the rules wrinkle in item 9.
- **(a) Default.** Drop the general rule. A Companion can be written as a Plan only if
  it prints its own Plan line. Item 9's Companion sentence goes with it.
- (b) Keep it.

**Ruled 2026-10-15: (a).** [USER]: "Agreed on Kokomi - let's get rid of
Companions as Plans unless we make a card that specifically has a Plan line."
Built 2026-10-15: the Bake-Kurage refuses a Companion with no Plan line (it
keeps its printed target), the planned-Companion carry-out and its hover tip
are removed, and the seat page's hand tag and Plan-row clause go with them.
Treatise's face is unchanged and still true: every play of a plain Companion
counts.
