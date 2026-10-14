# Kokomi review, round 6, 2026-10-14

Eight blind Sonnet seats, whole runs at A0, on build 0.2.5435. This is the
first round on the r5 A-list (#1275) and the numbers pass (#1276). The seat
records are in the session scratchpad (`seats/archive/kokomi-r6-*`). The draft
counts come from `tools/offer_report.py` over the eight seeds'
`card-offers-lane*.jsonl`. A Fable reviewer drafted this page and Claude edited
it; the edits are marked "Claude:".

## Result: 1 win in 8

| Seeds | End |
|---|---|
| 7JV40NKL3YZ1 | **Won** against the Queen, with 14 HP left |
| J2DD4S6TMRCW, B1W139M3X6PH | Died to the Queen, on floor 48 |
| M8EVF6ZCN0N3, J1R9JYU5TSAJ, HJ0EXFNQ9JE0 | Died to the Knowledge Demon, on floor 33 |
| GKH5XRSHUGYG / 8X40A49ETDEF | Died to the Kaiser Crab / The Insatiable, on floor 33 |

In round 5 she won 1 of 5. Her act-2 boss is now the wall: she lost there in 5
of 8 runs.

## 1. Did the last pass show up?

**Yes, at the draft.**
- **The nine cards whose numbers changed:** taken 28% of the times they were
  offered (22 of 78). Each of the nine made at least one final deck.
- **The five cards left alone:** taken 0 of 28. They are Coordinated Tide, Read
  the Field, Grand Strategist, Jellyfish Current and Turnabout. Over two rounds
  the reaction Powers are 0 of 25.
- **The condition from round 5 is met.** Those Powers were to move only if a
  deck full of Companions still passed them. Two such decks did.

The display fixes show up in the seats' own words: Energy "4 left of 3", the
Tide Wall receipt and Breakwater's live number.

## 2. What wins, what loses

**What wins** is unchanged. The first real decision in every run is whether to
Plan Kurage's Oath now or play it now. The other wins came from:
- stacked Plans against several enemies;
- Feint's chain (8 Plans for 64 damage);
- Masterstroke+ and Tamakushi's Wrath;
- Nereid's Ascension, which made three runs' best turns.

**What loses** is the act-2 boss. In all five of those losses the deck arrived
at 38 to 74 HP and could not end one big body fast enough.

**The Knowledge Demon** has 379 HP and never Blocks. Every four turns it heals
30 and gains 2 Strength. Each cycle it gives a curse: Disintegration (stacking
damage at the end of your turn, which Block absorbs), Sloth (3 cards a turn)
or Mind Rot or Waste Away. The fight is a bar: about 45 damage a turn from turn
2 on.
- **The three wins** cleared that bar with one concentrated source: poison, a
  Feint and Masterstroke morning, or a Thoma Vaporize deck.
- **The three losses** dealt 25 to 38 a turn.
- **Her Hydro cards have no damage that ticks on its own.** The two ticking
  sources that won were poison (an event card) and Neuvillette.

**The Queen** binds the first 3 cards drawn each turn. Both seats that lost to
her called it a Block problem. Cards **added** to the hand are not drawn, so
Stings, Wards and Shoal Call are free under Chains. Her kit already answers the
Queen; nothing on the cards says so.

## 3. Changes Claude builds (no pick)

**Numbers.** Each line gives the card's take rate this round, then the change.
1. **Watatsumi Drill** (1 of 16): "Deal **7** [10] Hydro damage. Add a Ward."
   It was 6. *Claude:* the reviewer asked for 8. With a free 4-Block Ward, 8
   beats Iron Wave by too much at Common.
2. **Kurage's Wake** (1 of 15): 5 twice (was 4 twice), the same as Twin Strike.
3. **Watchful Shoal** (1 of 9): Stings and Wards get **4** [6] more (was 3
   [5]), the same as Accuracy.
4. **Grand Strategist** (0 of 5): 6 [8] damage to ALL per reaction (was 4).
5. **Tidal Riposte** (0 of 6): 8 [11] (was 5). It pays once per hit of a
   multi-hit attack, which the build confirms.
6. **Sea Glass Harvest:** "Plan: Transform every Status and Curse you have into
   Sea Glass." This adds the Discard Pile and makes the line shorter.

Left alone: Turning Tide, Coral Crash, Kurage Bloom, Tide Wall, the three
Companion summoners, every Block number and the starter.

**Text and display**, in her own text:
7. **The Plan strip warns** when a Plan reads an intent its target does not
   have, for example "Sculptor does not intend to attack: Brine Sting's Plan
   hits no one."
8. **At Water's Edge** says "(a Plan counts)".
9. **Plan previews include the target's Vulnerable.** A receipt names a bonus
   the way it already names a cap ("asked for 3, 4 landed: Watchful Shoal").
10. **The Energy line names relic Energy:** "Energy 4 (3 a turn, +1 Lantern)".
11. **The strip says** "Plans carry out after your draw." Ripple Basin's bonus
    greys out once an Attack is planned.
12. **Checks:**
    - Does Kelp Wall's "damage you blocked" count Disintegration that Block
      absorbs? Decide, then print it either way.
    - Does Sea's Reproach fire on Weak applied by a Plan?
    - Does Heizou count his own Swirl?
13. **Harness:** `play Sting` takes any copy, and ALL-target cards take no
    target.

## Picks

1. **Mend's cap.** Mend heals only up to the HP you started the combat with.
   At near-full HP, The Moon's Plan prints 6 and heals 1. All three Mend cards
   are Rare and Exhaust: The Moon, Kurage's Mercy and Mizuki. `LAW.md` already
   allows true healing on such cards, so this changes the arm, not LAW.
   - (a) Keep the cap and print it on the card and receipt: "Mend 6 (1 will
     land)".
   - **(b, default) Mend heals up to Max HP**, as a plain Heal.

2. **The reaction Powers** (0 of 25 over two rounds).
   - (a) Move only the numbers (items 4 and 5 above) and watch one more round.
   - **(b, default)** Keep Grand Strategist at its new numbers. Cut **Jellyfish
     Current** and **Coordinated Tide**, which are two shapes of "add Stings
     on a reaction". Add two Hydro-only Uncommon Powers at 1 Energy, built
     for the Demon fight:
     - "At the start of your turn, the Bake-Kurage deals 4 [6] Hydro damage
       to the front enemy."
     - "Whenever a Plan is carried out, the Bake-Kurage deals 3 [4] Hydro
       damage to the front enemy."

     *Claude:* the reviewer asked for 5 [7] on the first. 4 is still a
     per-turn source, and Neuvillette is the Rare version. The pool stays at
     78, and Claude names both cards.

3. **Read the Field** (0 of 8) **and Treatise** (0 of 10).
   - **(a, default)** Read the Field's Plan becomes "Put a card from your Draw
     Pile into your Hand. It costs 0 this turn." Treatise stays as it is for
     one more round.
   - (b) Cut both. Claude writes a replacement Common Attack and Uncommon
     Skill.

4. **What follows.**
   - (a) Your run now, on this build.
   - **(b, default)** Claude builds section 3 and your picks, runs five to
     eight seats overnight, then you play.
