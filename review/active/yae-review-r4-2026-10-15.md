# Yae review, round 4, 2026-10-15

Five blind Sonnet seats, whole runs at A0, on build 0.2.5561. This is the first
round on the round-3 build: Sakura kinds, the Masterpiece and the signature
cards. Seats 4 and 5 were told to take every Elite they could reach. The
records are in the session scratchpad (`seats/archive/yae-r4-l1` to `-l5`).
Take rates come from `tools/offer_report.py --character "Yae Miko" --since
2026-10-15T01:00` (82 card rewards, 10 shop offers). This is the first round whose
records end with the seats' own words; they are quoted below.

## Result: 1 win in 5

| Seed | End |
|---|---|
| N45FRGNDPQ77 (elites) | **Won**: beat the Queen on floor 48; 5 Elites |
| 03MQ9LB25NLC (elites) | Died to Kaiser Crab (act-2 boss), floor 33; 5 Elites won |
| 1KJWXMJU3GSE | Died to Knowledge Demon (act-2 boss), floor 33, Demon at 222/379 |
| KYYHZGSNTTEB | Died to the Entomancer (act-2 Elite), floor 24, entered at 24/72 |
| QYL2T6QNFJE9 | Died to four Exoskeletons, floor 23, by 4 HP |

Round 3 also won 1 of 5. All five seats beat the act-1 boss, and four of the
five died in act 2.

## What plays well: the shrine

All five seats named the same core. In their words:
- "The Tenko turn (play Thunder Rite or Kenshin, everything acts, then it acts
  again at end of turn) was the thing I wanted to do every turn."
- "The Proofread + Tenko double-fire turns are the thing I would play again."
- "I enjoyed the Sakura timing puzzles (exact lethal off an end-of-turn strike)."

Sakura kinds made a real decision: "a levelled Kitsune Sakura is something
you protect," because planting a different kind withers the oldest. Red Ink
on a planting card was "worth far more than on a Strike." The shrine cards
are drafted: Tenko Kenshin 4 of 5, Yakan Offering 3 of 4, Thunderbolt Tithe 3
of 5, Shrine Maiden's Guard 8 of 14, Foxfire Sweep 7 of 14.

## What does not: the publishing half is never drafted

The cards that pay off for holding Annotated cards were offered about 50 times
and **taken 0 times**: Serialization 0 of 13, Second Printing 0 of 8, Print Run 0
of 7, Bestseller, Royalties and Serial Novel 0 of 5 each, Author's Copy 0 of 4,
Editor-in-Chief and Footnote 0 of 3. The Edits themselves are wanted:
Margin Note was taken 7 of 12, and Proofread was "the best decision in the kit."
So the seats like Annotating a card and do not want cards that count
Annotations. Early in a run, a card like Print Run ("6 Block, plus 2 for each
Annotated card in your hand") is a Defend.

The Masterpiece could not be judged this round, because its reward was broken
(item 1 below). The winning seat said its Publishes made Twin Sakura and
Sakura Grove "permanently better". The other elite seat found its Elite relics
did more than its Publishes.

## What loses: Block arrives by chance

Four of five seats said the same thing: "the deck's block arrives on a dice
roll"; "a fight turned on whether I drew a Block card". Her Block cards are
Defends, Shrine Maiden's Guard and the Kitsune Sakura. Two of her few other
Block cards were also never-again picks: Deadline (5 Block and an Edit) and
Evergreen Charm (5 Block that overwrote a Red Ink).

## Changes Claude builds (no pick)

**Bugs.**
1. **The "Publish an Annotation" reward must always open its chooser.** Two
   seats saw it open twice, then vanish and publish a card nobody chose (a Red
   Ink onto a Defend, Yakan Evocation).
2. **Red Ink on a planting card into a full shrine.** When the plant refreshes
   the oldest Sakura instead of adding one, the refreshed Sakura gets the
   Red Ink. The tip says "its Sakura get it too".

**Cards.** Yae is at Prototype, so these are Claude's.
3. **Deadline** (Common, 1): "Gain **8** [11] Block. Edit a card in your hand:
   Deadline Extension." It was 5 Block, two seats' never-again.
4. **Evergreen Charm** (Common, 1): "Gain **7** [10] Block. Edit your oldest
   Sakura: Deadline Extension. **It keeps its Red Ink.**" It was 5 Block and
   could erase the Sakura's Red Ink.
5. **The Seven Glamours** (Rare, 1 [0], Exhaust): "Publish **every** Annotated card in your
   hand." Publishing one card cost a Rare slot to do what an Elite reward does
   for free; one seat's never-again. With Reborn as Guuji Yae (Edit every other
   card in your hand) it makes a whole hand permanent. That two-Rare combo is
   the "super card" result [USER] asked the Masterpiece to reach.

**Text.**
6. An **Edit chooser shows each card's current Annotation** and warns when the
   Edit replaces one ("replaces Red Ink").
7. **Foxfire Lure** and **Fox Trick** say that a Kitsune Sakura does not
   strike: "your striking Sakura".
8. **Margin Note** (and any Edit) with no card to Edit says so on the play
   rather than silently doing nothing.

## The Seven Glamours, again (no pick)

Item 5 shipped as "Publish every Annotated card in your hand." [USER]:
"Reading The Seven Glamours more carefully, it looks obviously OP - I thought
it was Publishing one card per fight, not the whole hand. There is precedent
for this cards giving permanent benefits, such as The Hunt or Hand of Gold, but
they generally require a condition of some kind." It becomes a kill card, the
way Hand of Greed pays only on a kill:

- **The Seven Glamours** (Rare Attack, 2, Exhaust): "Deal 12 [16] Electro
  damage. If this kills an enemy, Publish an Annotated card in your hand."

At most one Publish a fight, and only when it lands the kill.

## Pick

**Pick 1: the publishing half.** Rewritten 2026-10-15 after [USER]: "perhaps
the issue is that we are trying to assemble an engine but the pieces are
individually not working, so I'm not sure the fix is to just print a lot of
block on them. What if instead we make some of the stronger Edit effects
Exhaust (at either a lower price, or a stronger effect) so that future deck
cycles are smaller?"

The reading: an Annotation lasts the combat, so the engine is "Edit your good
cards early, then see them again". An Edit card that stays in the deck dilutes
the cycle it is trying to feed. Exhausting it does two jobs: each Edit hits
harder, and the Annotated cards come round sooner.

- **(a) Default: Edits that Exhaust.**
  - **Sakura Seal** (Uncommon, 0): "Edit 2 [3] cards in your hand: Sakura
    Seal. Exhaust." (was 1 [2] card, no Exhaust)
  - **Footnote** (Uncommon, 0, already Exhausts): "Edit 2 [3] cards in your
    hand: Footnote." (was 1 [2])
  - **Inked Branches** (Uncommon, **0**, was 1 [0]): "Edit every Sakura [and a
    card in your hand]: Red Ink. Exhaust."
  - **Royalties** (Rare, 1 [0], already Exhausts): "Edit 2 cards in your hand:
    Royalties." (was 1)
  - Margin Note and Deadline stay repeatable, as the Common Edits. Proofread is
    a starter card and is unchanged.
  - The counting payoffs keep their jobs. Only their floors rise, so that one
    Annotated card already pays:
    - Bestseller: "Deal 8 [10] Electro damage, plus 3 [4] for each Annotated
      card in your hand." (was 5 [7])
    - Print Run: "Gain 6 [8] Block, plus 3 [4] for each Annotated card in your
      hand." (was plus 2 [3])
  - Serialization, Editor-in-Chief, Serial Novel, Second Printing and Author's
    Copy are unchanged. With more cards Annotated per Edit, they get their
    first fair test.
- (b) The first plan: rework the nine payoffs so each makes or uses one
  Annotation as it plays, and turn three slots into Kitsune and Block cards.
- (c) Keep everything for one more round, now that item 1 has fixed the
  Masterpiece reward.

## Next

Items 1 to 8 are built (#1321). The Seven Glamours fix is built now. Pick 1
(a) is built (PR_PENDING): the six cards above, and every multi-card Edit is
one chooser of up to that many different cards, which the player may stop
short of (Inked Branches+ Edits one card in hand). Next is a Yae round of
five seats, two of them elite-heavy again.

## Ruled 2026-10-15

[USER]: "Otherwise I'm good with it." Pick 1 (a), Edits that Exhaust. The
"otherwise" is GPT's note, relayed by [USER]: "Multi-card Edits should offer
up to the printed number of distinct targets. A player should be able to stop
rather than overwrite an Annotation they want to keep. Ideally this is one
selection screen." The build makes every multi-card Edit one chooser of up to
that many different cards, and the text reads "Edit up to 2 [3] cards".
