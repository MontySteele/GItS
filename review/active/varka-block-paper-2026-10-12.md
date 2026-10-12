# Varka: where his Block comes from (2026-10-12)

**Why.** Two notes from the human co-op of 2026-10-11 (`review/records/coop-human-playtest-2026-10-11.md`): "Solid! But reliant on powers for Block." and [USER]: "Varka's still in a weird situation on Block - it was hard until I was able to power spam." Then the seat round of 2026-10-12 (`review/records/furina-varka-round-2026-10-12.md`): both Varka seats had no Block once their openers were spent, and both deaths were turns with no Block in hand. The other two co-op notes are already built (#1114): Vow of the Blade gains 2 Oath, and The Order Answers lets you choose 1 of 3 Knights, upgraded.

**Sources.**
- Lane fight telemetry since 2026-10-08, solo fights only: Varka 551 fights, the base five 535.
- [USER]'s co-op run: `%APPDATA%\SlayTheSpire2\gits_telemetry\play-20261011-161711.jsonl`, 22 Varka fights.
- Offers: `tools/offer_report.py --character Varka --since 2026-10-03`.
- The scripts are in the session scratchpad: `block_by_turn.py` and `block_by_elem.py`.

## 1. He is not short of Block

**Block gained per turn as a share of the damage coming in**, in normal fights:

| Turn | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Varka | 1.10 | 0.66 | 0.61 | 0.42 | 0.38 |
| Base five | 1.13 | 0.42 | 0.27 | 0.27 | 0.28 |

- **Elites and bosses:** Varka covers 0.59 to 0.67 after turn 1; the base five cover 0.40 to 0.57.
- **Median HP lost per fight:** Varka 5% in normal fights and 31% against elites and bosses; the base five 12% and 46%.
- **By starting element:** in normal fights after turn 1, Hydro starts cover 0.67, Pyro 0.58 and Cryo 0.51. All three are above the base five.
- **In the co-op:** Varka lost less HP than Furina in every act (act 2 normal fights: 10.2 against 11.0).

The "no Block after the opener" shape is the base game's own: everyone's Block falls off after turn 1, and the base five's falls further. Lane 4's seat also traded its Defends into Mauls with Claws.

**So this paper does not raise his Block.**

## 2. What is real: Block that fits only some decks

**His pool has 16 Block cards: 7 Common, 6 Uncommon, 3 Rare, including 3 powers.** The base pools hold 11 or 12 (`review/active/project-review-2026-10-08/varka-review-2026-10-08.md`). The count is fine. Two things about which cards they are matter:

**1. A Block card that applies another element switches him off his own.** His current element is the last Pyro, Hydro, Cryo or Electro he applied (`STATE.md`), and his cards read only its Oath. That gives three groups:

- **Pyro:** one Block card, Amber: Baron Bunny (Common).
- **Electro:** one, Lisa: Infinite Circuit (Common).
- **Hydro:** four: Rippling Guard and Barbara: Gleeful Songs (Common), and Whisper of Water and Wellspring Hymn (Uncommon). Hydro's Swirl also pays Block.
- **Cryo:** none outside Kaeya, the starter Knight.

In a Pyro or Cryo deck, Rippling Guard turns his Oath cards off for the turn.

**2. Seats take the Block that does his loop and pass the Block that waits on the board.**

| Card | What it is | Taken |
|---|---|---|
| Crosswind | Common Attack, Block if it Swirls | 28 of 55 (51%) |
| Jean — Wind Companion | Common, Block and Swirl | 32 of 64 (50%) |
| Noelle: Steadfast Maid | Uncommon, Block and draw | 17 of 36 (47%) |
| Eye Wall | Uncommon | 30% |
| Lisa: Infinite Circuit | Common, Electro | 23% |
| Barbara: Gleeful Songs | Common, Hydro | 21% |
| Amber: Baron Bunny | Common, Pyro | 5 of 53 (9%) |
| Frost Ward | Common, needs auras on the board | 6 of 76 (8%) |
| Rippling Guard | Common, Hydro, scales with cards played | 2 of 50 (4%) |

The window spans #1114, which raised Rippling Guard's floor. Seat take rates on Block run low across the board, so these are leads, not verdicts.

**[USER]'s Pyro run matches.** His card Block in act 1 came from Defend, Amber: Precise Shot (his starter Knight) and Mika, a Companion. The only Varka Block card he took was Eye of the Storm, an Uncommon that gives 10 Block over two fights. He took none of the Common ones. By the act-3 boss, 162 of his 345 Block came from something other than a card played. That is "hard until I was able to power spam": the early Block was the starter's.

## 3. The proposal

**Turn Rippling Guard into a Block card that works in every element:**

> **Rippling Guard** (Common Skill, 1): Gain 7 [10] Block. Apply your current element to an enemy.

**Why this card:**
- **It is the generic form of his four starter Knights,** which give 5 or 6 Block and apply one element. A Common should beat a starter, which "stays bad".
- **It never switches him.** It applies the element he already has.
- **It sets up the Swirl,** so it does his loop in any deck: Pyro, Cryo, Electro or Hydro.
- **On rate:** the base median 1-cost Common Block Skill is 6 (`varka-review-2026-10-08.md`), and the element is the rider.
- **Hydro is not short.** It keeps Gleeful Songs, Whisper of Water, Wellspring Hymn and its Swirl's Block.
- **Cut:** Rippling Guard's current text ("Apply Hydro. Gain 6 Block, plus 1 for each other card you played this turn"), taken 4%.

**Claude's calls, no pick needed:**
- **Stormward Stance:** "Your Anemo Attacks deal 3 [5] additional damage" becomes 4 [6]. That is Accuracy's number (the Silent's Uncommon power, for Shivs). Both seats named it weakest; lane 3 said it "did nothing next to Converging Winds+". It is a damage card, so it moves only a number here.
- **Unchanged and watched in your next Varka run:** Frost Ward, Baron Bunny, and Noelle — Breastplate. Breastplate is a shared Companion, not his card.

## 4. Risks

- **A 1-cost Swirl setup at Common could crowd out his element cards,** if every deck takes two. Watch for this; it is the same job his starter Knights already do.
- **The numbers above are solo seats on A0.** Co-op is read from one run.

## For [USER]

1. **How much Block.**
   - **(a) Default:** no raise. He out-blocks the base five on every turn and in every starting element. Fix which decks his Block fits, not the amount.
   - (b) Raise his Common Block by 2 across the board.
   - (c) Leave Block alone entirely.
2. **The any-element Block card.**
   - **(a) Default:** Rippling Guard becomes "Gain 7 [10] Block. Apply your current element to an enemy."
   - (b) Frost Ward becomes that card instead, and Rippling Guard stays.
   - (c) Something else (say what).

## Ruled 2026-10-12: both picks (a)

[USER]: "On Varka - agreed on both defaults"

- **Pick 1 (a):** no raise to his Block.
- **Pick 2 (a):** Rippling Guard becomes "Gain 7 [10] Block. Apply your current element to an enemy." Stormward Stance goes to 4 [6] with it (Claude's call).
