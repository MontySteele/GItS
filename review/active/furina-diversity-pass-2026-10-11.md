# Furina: two guest playstyles and a pool pass (2026-10-11)

**Why.** From the co-op playtest (`review/records/coop-human-playtest-2026-10-11.md`), Furina "didn't have enough 'oomph'" in act 3. [USER], after the first draft of this paper:

> I would like Furina to have two basically functional playstyles: 1) Draft guest stars that feed Furina's personal damage, with the Stars providing support passives. 2) Draft guest stars that are the primary form of offense, with Furina focusing on Fanfare generation to keep them fed. On top of that, there should be at least one if not two additional styles of archetypes that can run as smaller components.

**Sources,** all in the session scratchpad:
- the census, `furina-diversity-census.md`;
- per-card offers, takes and plays over seat rounds 1 to 5 plus your run, `furina-card-lifetime.md`;
- a Fable review of the first draft, `furina-diversity-review-fable.md`. Its main points are taken below.

Guest numbers are from `FurinaStageLaw.cs:30-170`; guest text is from `FurinaStageBadges.cs:88-155`.

## 1. Where the pool stands

- **Every guest has a line and an act, but nothing builds on either.**
  - **Lines.** Each of the 11 guests has a line that helps Furina. Four raise her own damage:
    - Wriothesley: Drain becomes that much Cryo.
    - Chevreuse: a Spend applies Vulnerable.
    - Neuvillette (Rare): +2 Hydro.
    - Clorinde (Rare): Repay becomes twice that much Electro.

    The rest are economy or defence: Charlotte, Navia, Lyney, Lynette, Sigewinne, Freminet and Escoffier.
  - **Acts** are flat, from 3 to 8 damage. Strength does not apply to them (`FurinaStage.cs:859-860`).
  - No card rewards keeping stars on stage, apart from Private Box's Block. Nothing feeds an act.
- **Your run was a style-2 deck that couldn't feed its stars.**
  - Lyney, Clorinde and Lynette did 44% of Furina's damage.
  - The act-3 boss fight ended with 144 Fanfare banked, because every spender in the deck had a small cap: Hold the Stage 12, Tidal Flourish 10, Encore! 4. Rising Applause was played twice in act 3.
- **Seats draft Guest Stars, but never guest support.**
  - They took 15 Guest Stars (9 in act 1), with 32 plays in round 4.
  - Casting Call, Tutti!, Final Bow, Grand Entrance, Showstopper and Ensemble Cast together had 45 offers and 0 takes.
- **When the styles come online.** Act 1 offers a Guest Star on about 2.4 of 8.4 reward screens, so a deck ends act 1 with one or two guests. Both styles come online in act 2, which is when your run said she started to need them.
- **Cards that do nothing without their combo:**
  - Casting Call, with no Guest Star in the draw pile;
  - Tutti! and Final Bow, with no guest on stage;
  - Ensemble Cast, below 4 guests;
  - Lynette's act, with no enemy holding an aura.
- **Redundant cards.** Each card in these sets does the same job as the others:

| Set | Texts | Seat takes | Your run |
|---|---|---|---|
| Gentle Current (C) / Hymn of Many Waters (C) | "Gain 5 Block. Repay 3. Gain 1 Block for any HP it could not Repay." / the same with 6 Block | 9 of 26 / 13 of 30 | 0 / 46 plays |
| Surging Waters (C) / Clean Slate (C) | "Repay 3. Deal 6, plus 1 per HP not repaid." / "Deal 7. Repay 3. If no drained HP is left, draw 1." | 3 of 26 / 5 of 26 | 0 / 0 |
| Pay the Tab (U) / Ousia Pledge (C) | "Drain 6. Draw 3." / "Drain 3. Draw 2." | 0 of 6 / 4 of 25 | 0 / 0 |
| Sold Out (U) / Interval Bell (U) / Salon's Tab (U) | each pays to draw and gain Energy next turn | 2 of 9 / 0 of 6 / 3 of 8 | 0 / 0 / 2 |
| Bravura (U) / Rising Applause (basic) | "Spend all. Deal 6, plus 2 a point." / "Gain 5 Block. Spend all. Deal 1 a point." | 10 of 12 / starter | 0 / 19 |
| The Masquerade (U Power) / Freminet's line | "Whenever you Drain, gain that much Block." twice | 3 of 11 / 2 of 10 | 0 / 0 |
| Rares: The Deluge / Grand Deluge; All In / Overdraft; Singer of Many Waters / Grand Absolution | each Rare is a bigger version of the lower card | | |

## 2. The archetypes

**Rule:** a new or changed card has a floor (it does something with no setup) and more inside its archetype. Payoffs read counts every deck has: guests on stage, Fanfare. A build-around Power (Full House, Showstopper) is the stated exception, as in the base game.

**The two main styles draft from the same 11 guests but want different ones:**
- Style 1 wants the line guests: Neuvillette, Chevreuse, Wriothesley, Clorinde and Charlotte.
- Style 2 wants the act guests: Lyney, Escoffier, Clorinde, Wriothesley and Navia, whose act spends half your Fanfare.

### Main style 1: the leading lady (stars support, Furina hits)

| Card | Status | Text |
|---|---|---|
| **Headliner** | new, Common Attack, 1 | "Deal 6 damage, plus 2 for each guest on stage." [9 + 2] |
| **Leading Lady** | new, Uncommon Power, 1 | "Gain 1 Strength. Your Attacks deal 1 more damage for each guest on stage." [2 Strength] |
| **Bravura** | changed, Uncommon | "Spend all your Fanfare. Deal 7 Hydro damage for every 3 spent." [9] |
| Private Box; the line guests | existing | |

Notes:
- **Leading Lady** has an Inflame-style floor, and its Strength stays with her side of the board because guest acts ignore Strength.
- **Bravura:**
  - Alone, at the seats' mean spend of 22, it deals 49 (51 today).
  - Its ceiling is high. At 60 Fanfare with Leading Lady at 3 guests and Neuvillette, it deals 20 hits of 12, which is 240. Today's ceiling is 126.
  - That ceiling needs a Rare, a Power and a full stage, so it is the act-3 oomph. It is the number to watch.

### Main style 2: the company (stars hit, Furina feeds them)

| Card | Status | Text |
|---|---|---|
| **Full House** | new, Uncommon Power, 1 | "Whenever a guest's act deals damage, Spend up to 4: it deals that much more." [up to 6] |
| **Tutti!** | moved to Common, floor added | "Each guest acts. Draw 1 card." (Retain; upgrade costs 0.) |
| **Guest Star: Wriothesley** | moved to Common | The company gets a Common damage star. |
| **Guest Star: Lynette** | act fixed | "Act: deal 3 Anemo damage to an enemy, one with an aura if able." |
| **Final Bow** | floor added | "Draw 1 card. Choose a guest. It acts twice [3 times], then leaves." |
| **Casting Call** | floor added | "Put a Guest Star from your draw pile into your hand. If you can't, draw 2 cards." |
| **Ensemble Cast** | floor added (Rare) | "You have 4 guest seats. Summon a random guest." |
| Lyney, Clorinde, Escoffier, Navia, Encore!, Showstopper, Bring the House Down | existing | |

**Full House is the feed.**
- Three damage guests eat up to 12 Fanfare a turn for +12 damage. Lyney and Escoffier get +4 to ALL.
- Generation runs at about 10 Fanfare a turn (sim: 29 a fight), so the bank empties into the stars, and drafting Drain and Repay cards is what keeps them fed.
- Its rate is 1 damage per Fanfare, half of Bravura's. That sets up the choice between the styles: Furina cashes the bank herself, or the company does.
- A guest's Spend also triggers Chevreuse, Thunderous Applause and Crescendo (`FurinaStageDirector.cs:210-252`).

### Small component A: the hoard

Hold Fanfare instead of spending it. The existing cards are Prima Donna, Star Turn and The Show Must Go On.

| Card | Status | Text |
|---|---|---|
| **Packed House** | new, Common Attack, 1 | "Deal 4 damage, plus 1 for every 5 Fanfare you have." [7 + 1] |

At a bank of 25 it deals 9; at 60, 16; at 144, 32. A Common floor without making never-spending dominant.

### Small component B: close to the line

Against the Tide, High Stakes, Regina, A Five-Century Act and Lyney's bigger buffer. Nothing is added. Against the Tide had 0 takes in 7 seat offers but 19 plays in your run.

**Unchanged:**
- The starter.
- The Spend core: Rising Applause, Standing Ovation at "Spend half", and the capped "Spend up to" cards.
- The Drain line.

## 3. What makes room

4 new cards and 4 cuts, so the pool stays at 78 plus 2 basics.
- **Cuts, all redundant:**
  - Gentle Current (C);
  - Surging Waters (C);
  - Pay the Tab (U);
  - Sold Out (U), the weakest of the three Energy-next-turn cards.
- **Rarity:** Commons go from 21 to 23 (Headliner, Packed House, Tutti! and Wriothesley in; two out). Uncommons go from 37 to 35. Rares stay at 20.
- **Dead but not redundant:** Rising Tide (0 of 7 offers) and Fountain of Lucine (0 of 9), with 0 plays anywhere. They stay unless you say otherwise (pick 4).

## For [USER]

1. **The archetype map.**
   - **(a) Default:** the two guest styles, the Spend core as it is, and the hoard and the line as small components.
   - (b) Only the two guest styles.
2. **Full House as the feed.**
   - **(a) Default:** "Whenever a guest's act deals damage, Spend up to 4: it deals that much more."
   - (b) The first draft's version: acts +1 per 10 Fanfare held, with no spending.
3. **The rest of section 2,** as one set: Headliner, Leading Lady, Bravura at 7 per 3, Packed House, Tutti! and Wriothesley to Common, Lynette's act, and the four floors.
   - **(a) Default:** all of it.
   - (b) All but Packed House, if pick 1 is (b).
4. **Cuts.**
   - **(a) Default:** the four redundant cards.
   - (b) Also cut Rising Tide and Fountain of Lucine, leaving the pool at 76 for now.
5. **The three Rares that repeat a lower card:** The Deluge, All In, and Singer of Many Waters.
   - **(a) Default:** a follow-up paper giving each a rule-bend in its slot.
   - (b) Leave them.
