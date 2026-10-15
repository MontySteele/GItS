# Yae review r5 (2026-10-15)

Five Sonnet seats on 0.2.5601, after review r4 pick 1 (a), Edits that Exhaust
(#1330), and the single "up to N" Edit chooser. Lanes 4 and 5 took every Elite
they could. Records: scratch `seats/archive/yae-r5-l1` to `-l5` (gitignored).
Offers: `tools/offer_report.py --since 2026-10-15T13:00`.

## Result: 1 win in 4 finished runs, plus one cut

| Lane | Route | End | Bosses beaten |
|---|---|---|---|
| 1 | normal | died F28, act 2, Hunter Killer (3 HP short) | Ceremonial Beast |
| 2 | normal | **won**, F48, the Queen | Vantom, The Insatiable, the Queen |
| 3 | normal | died F17, act 1 boss The Kin (Priest at 52/190) | none |
| 4 | Elites (3) | **cut** F39, act 3: the game froze (below) | Soul Fysh, Knowledge Demon |
| 5 | Elites (6) | died F48, act 3 boss Test Subject | Vantom, Knowledge Demon |

Review r4 was 1 win in 5. Two of the three deaths (lanes 1 and 3) were a hand
with no Block card at low HP; lane 5 lost to Test Subject's Enrage (+2
Strength per Skill) with a Skill-heavy deck.

## What plays well

- **Proofread and Publish.** Every seat named the Reprint target as a real
  decision from turn 1. Lane 2's win came from Publishing Reprint onto
  Thunderbolt Tithe+ after its first Elite: "That one Publish choice later
  defined the whole deck."
- **The shrine.** Sakura Grove levelling the shrine, then Kitsune Guile, Thunder
  Rite or Tenko Kenshin pulling Tenko on a full shrine. Kitsune Guile (5 of 7
  offers taken), Tenko Kenshin (5 of 7) and Twin Sakura (6 of 9) are the most
  taken cards.
- **The new chooser works.** Lane 1 used Footnote on two different cards from
  one screen several times ("Footnote on Bestseller and Defend").

## What does not: the publishing payoffs are still not drafted

Exhausting Edits did not move the draft. This round's offers:

| Card | Text | Offered | Taken |
|---|---|---|---|
| Print Run (U, 1) | Gain 6 Block, plus 3 for each Annotated card in your hand. | 12 | 0 |
| Manuscript Pile (U, 1) | Draw 2 cards. Each Sakura lasts 1 more turn. | 7 | 0 |
| Sakura Seal (U, 0) | Edit up to 2 cards in your hand: Sakura Seal. Exhaust. | 5 | 0 |
| Second Printing (U, 0) | Put an Annotated card from your Discard Pile into your Hand. Exhaust. | 5 | 0 |
| Serialization (U Power, 1) | Whenever you play an Annotated card, gain 3 Block. | 5 | 0 |
| Serial Novel (R Power, 2) | At the start of your turn, put a random Annotated card from your Discard Pile into your Hand. | 5 | 0 |
| Reborn as Guuji Yae (R, 1) | Choose an Annotation. Edit every other card in your hand with it. | 5 | 0 |
| Author's Copy (U, 1) | Add a copy of an Annotated card in your Hand to your Hand. | 3 | 0 |
| The Seven Glamours (R, 2) | Deal 12 Electro. If this kills an enemy, Publish an Annotated card in your hand. | 3 | 0 |
| Royalties (R, 1) | Edit up to 2 cards in your hand: Royalties (when played, gain 1 Energy). | 2 | 0 |
| Bestseller (U, 1) | Deal 8 Electro, plus 3 for each Annotated card in your hand. | 7 | 1 |
| Footnote (U, 0) | Edit up to 2 cards in your hand: Footnote. Exhaust. | 3 | 1 |
| Inked Branches (U, 0) | Edit every Sakura: Red Ink. Exhaust. | 6 | 2 |

Print Run went untaken in 12 offers while two seats died for want of a Block
card.

**Claude's reading.** The cards that count "Annotated cards in your hand" ask
for a state the engine rarely produces. An Edit lands on a card in hand, and
that card is usually played the same turn, so by the time Bestseller or Print
Run is played the hand holds zero or one Annotated card. Lane 1's best
Bestseller (14) needed Footnote to put two Annotations in hand and keep them
there. The seats that drafted Edits liked them for what the Edited card did
(Reprint, Red Ink), not for anything they counted.

## Changes Claude builds (no pick)

**Bugs and harness.**
1. **The seat page still says a 2-card Edit opens a second chooser.** It now
   opens one chooser of up to N cards; the note is rewritten.
2. **Inked Branches+ with nothing to Edit** shows "Nothing to Edit" twice; once.
3. **A Reprinted attack whose first hit kills its target** showed "played two
   times" with one hit (lane 2). Find what the game does with the second play
   and match the base game's Replay; if the second play is lost, say so on the
   page.
4. **The lane 4 freeze.** The game thread stopped right after the window
   regained focus ("Restored foreground FPS"); a managed stack dump shows no
   game or mod code on it, so the hang is in the engine. Added to the `EB-489`
   hang shapes; the run could not be resumed, since embarking abandons the save.

**Text.**
5. **Full shrine.** Four of five seats could not read the rule until it bit
   them (lane 1 withered two Sakura with one Reprinted Foxfire Sweep). New text:
   "Full shrine: planting makes your oldest Sakura act. If the new Sakura is
   the same kind, the oldest stays and gains a Level. If not, the oldest withers
   and the new one takes its place."
6. **Meditations of a Yako** only offers Publish when the fight left an
   Annotation to Publish; lane 5 saw it after 3 of 7 Elites and bosses and
   could not tell why. New text: "After an elite or boss fight, you may Publish
   an Annotation you made that fight." (and "up to 2" on the upgrade).
7. **Sakura Seal and Footnote** name their Annotation without saying what it
   does; Royalties already does. New: "Edit up to 2 [3] cards in your hand:
   Sakura Seal (when played, plant a Sakura)." and "...: Footnote (when played,
   draw 1 card)."

**Not changed.** Fallen Petals was one seat's never-again (it withered a fresh
Sakura); one record is not a cut. Sakura Channeling lasts the combat like
every Power.

## Pick

**Pick 1: what the publishing payoffs count.**
- **(a) Default: count Edits, not hands.** The payoffs read what you did this
  combat, so the engine is "Edit early, cash in later":
  - Bestseller: "Deal 8 [10] Electro damage, plus 2 [3] for each card you
    Edited this combat."
  - Print Run: "Gain 6 [8] Block, plus 2 [3] for each card you Edited this
    combat."
  - Serialization, Serial Novel, Second Printing and Author's Copy keep their
    text: they already read played or discarded cards, not the hand.
- (b) Cut the ten zero-take cards and refill those slots with shrine and Block
  cards, leaving the Edits (Proofread, Margin Note, Deadline, Footnote, the
  Publish reward) as the whole publishing half.
- (c) No change. Another round as is, or your own Yae run first.

## Next

Items 1 to 7 are built now. Pick 1 is built once ruled, then a Yae round of
five seats.
