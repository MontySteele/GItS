# Tooltip trim, all four kits, 2026-10-14

[USER], during the 2026-10-14 Furina run: "her cards still make a million words
of tooltips come up ... if at all possible, I think it's worth trying to figure
out how to make this cleaner / simpler so the tooltips aren't half the
screen." Then: "let's do the same thing for Klee, Varka and Kokomi while we're
at it. Furina is the perennial worst offender, but the tooltips all came from
the same source."

Numbers are from two read-only censuses of the code and loc tables (session
scratchpad, `furina-tooltip-census.md` and `kits-tooltip-census.md`; the
scripts are beside them). This changes text only: no number, no rule.

## 1. What a hover costs today

Characters of tip text per card, median / worst:

| Kit | Always shown | With every conditional tip up |
|---|---|---|
| Klee | 118 / 535 (Flash Point, 5 boxes) | 222 / 894 (10 boxes) |
| Varka | 209 / 485 (Barbara: Wellspring Hymn) | 262 / 964 (11 boxes) |
| Kokomi | 135 / 347 | 213 / 667 (7 boxes) |
| Furina | 117 / 449 (Guest Star: Navia, 4 boxes) | Guest Stars plus Exhaust plus a reaction preview |

A base-game card raises zero to two boxes, each one short line.

## 2. Where the words come from

Four sources, in order of size:

1. **Reaction previews.** One box per reaction the card *could* cause against
   any aura on the board: Vaporize, Melt, Frozen, Overloaded, Superconduct,
   Swirl, Electro-Charged, Crystallize, 53 to 117 characters each. With three
   enemies wearing three auras, an elemental card grows three boxes. This is
   most of the "max context" column: Barbara's 964 is 5 static boxes plus 6
   previews.
2. **Restated base words.** Our own Strength, Weak, Vulnerable and Frail
   boxes (96 to 117 characters) sit beside the base game's own tip for the
   same word. They were written because a seat misread "Attacks" in the base
   line as the card type (`EB-469`, `EB-377`).
3. **Stacked kit words.** One card raises its kit's whole vocabulary: Flash
   Point raises Applies Pyro, Bomb, Set off, Spark and Elemental Reaction; a
   Guest Star raises Summon (118), Guest Star (92), the guest's own sentence
   (95 to 170, usually the card face again) and often Spend or Repay.
4. **Seat riders.** Edge-case sentences added when a blind seat misread a
   card: Bis! ("does not count, even if it empties your Fanfare"), Final Bow
   ("its acts happen one after another"), Oldest guest, Superconduct's "applies
   before this hit". Each is right, and each answers a seat's question rather
   than a player's.

## 3. The proposal

**A house rule for player hovers**, enforced by a lint so it cannot drift
back (the same pattern as the other "structurally invisible" checks):

- At most **3 boxes** on a card's static hover, and **about 90 characters** a
  box, in base-game style: what the word does, in one sentence.
- **Never restate a base word.** Strength, Weak, Vulnerable, Frail, Exhaust,
  Retain and the rest show the base game's own tip only.
- **Seat riders move to the seat page.** The blind seats read their own
  glossary (`blindplay`'s word definitions), which already opens most rows
  with the same sentence. Every rider moves there word for word, so seat
  results do not drift.

**Per family:**

| Family | Now | After |
|---|---|---|
| Reaction previews | one box per possible reaction | **one box, only for the enemy you are aiming at** ("Vaporize: this hit deals 1.5x"); none while the card is only hovered in hand |
| Applies Pyro / Hydro / Cryo / Electro / Anemo / Geo | 94 to 122 chars, plus a separate Elemental Reaction box | "Applies Pyro for 2 turns. On another aura, they react." (about 55); the Elemental Reaction box is dropped wherever an Applies box is already up |
| Base words (Strength, Weak, Vulnerable, Frail) | ours plus the base game's | the base game's only |
| Guest Star cards | Summon + Guest Star + the guest's sentence (+ Spend/Repay) | one **Guest Star** box ("Joins at the back and acts at the end of your turn. A fourth guest pushes out the oldest."); the guest's sentence only where the face does not already say it |
| Klee's Bomb words | Bomb + Set off + Spark on most cards | Bomb and Set off kept, each cut to one sentence; Spark only on cards that print a Spark cost |
| Varka's Oath words | Oath + Current element + The second hit | Oath and Current element kept, each one sentence; "The second hit" moves to the seat page |
| Kokomi's Plan tip on Companions | 118 chars | about 70: "Play it on the Bake-Kurage to carry it out next turn." |

## 4. What it should come to

Estimated from the census bodies, not measured: every card at 3 boxes or
fewer; medians near 100 characters; the worst static hover near 270 (now 535);
the worst in combat near 350 (now 964), because only one preview can show.
The build pass re-runs both censuses and prints the before and after per kit
in its PR.

## 5. What it does not touch

Card faces, numbers, rules, and the seat page's own text (it gains the
riders). Klee and Varka are frozen at Balance; text-only changes land on
`main` under `operations/stage-gate.md`.

## Picks

1. **The house rule (3 boxes, about 90 characters, no restated base words,
   riders to the seat page, a lint to hold it):** **(a) yes**; (b) yes, with
   a different cap you name.
2. **Reaction previews:** **(a) one box, only for the enemy being aimed at**;
   (b) keep every matching aura, merged into one box; (c) none on cards (the
   enemy's aura badge explains its reactions).
3. **Guest Star cards:** **(a) one merged Guest Star box, the guest's sentence
   only where the face leaves it out**; (b) keep Summon and Guest Star as two
   boxes.
