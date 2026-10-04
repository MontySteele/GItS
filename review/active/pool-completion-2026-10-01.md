# Filling the pools: Klee, Furina, Kokomi

Paper, 2026-10-01. Main session design. **Picks 1 to 5 RULED at their
defaults, 2026-10-01, [USER]: "Overall this looks good, but one balance
note"** (the Body Slam note, §6).

## 1. Why

[USER], 2026-10-01: "I want to get both of their card pools up to full,
meaning 78 + the two Ancient rewards + 5 multiplayer cards each. Varka might
wait til the current batch is tested - Klee should be done already, let's
double check."

The shape is the base game's. Each base character has 20 Common, 35
Uncommon and 25 Rare cards, plus 2 Ancient cards and 5 multiplayer cards (3
Uncommon, 2 Rare), which `game_ref/<char>.json` marks `mp_only`.

## 2. Where each pool is (census, origin/main 82ef6008)

| Kit | Common / Uncommon / Rare | Pool | Ancient | Multiplayer | Missing |
|---|---|---|---|---|---|
| Klee | 24 / 36 / 18 | 78 | 1 | 5 | 1 Ancient |
| Furina | 23 / 32 / 17 | 72 | 1 | 5 | 3 U, 3 R, 1 Ancient |
| Kokomi | 19 / 37 / 14 | 70 | 1 | 3 | 1 C, 7 R, 1 Ancient, 1 U + 1 R multiplayer |
| Varka | 20 / 35 / 23 (#788) | 78 | 0 | 0 | 2 Ancient, 5 multiplayer, after his round |

- Furina's 72 is the 60 Stage cards plus 12 cards from her old kit. The 12
  are An Invitation, Command Performance, Commanding Gaze, Courtroom Drama,
  Crashing Waves, Duet, The Guest List, Quick Change, Singer of Many Waters,
  Undercurrent, Stage Combat and The Witness Stand. They passed the Stage's
  filter only because they print no retired word (pick 3).
- Kokomi's Rares are the thinnest of any kit (14, against 25 in the base
  game). Her batch goes almost all to Rare, and it gives one Rare to each of
  her decks.

**How Ancient cards work here.** The Darv event's Dusty Tome is the only
way to get one. It hands over one of the character's Ancient cards already
upgraded, so these are read at their bracketed numbers. The base game's
Ancient cards bend a rule (Corruption, Wraith Form, Biased Cognition). Each
kit's first Ancient is a bigger version of something it already does. The
second bends one of the kit's own rules.

## 3. The Ancient cards

- **Klee: Alice's Masterpiece** (Power, 3 [2]). "When one of your Bombs goes
  off, it stays on the enemy at half its size, rounded down." This bends
  rule 2, under which a set-off Bomb is gone. Cooking and cashing stop being
  either/or: each cash still costs half the Bomb. The damage stays bounded
  because set-offs in one turn shrink geometrically (S, S/2, S/4). The half
  that stays on a dead enemy jumps (rule 3).
- **Kokomi: Divine Strategy** (Power, 2 [1]). "The first time each turn you
  play a card on the Bake-Kurage, its now-line happens too." This bends rule
  2, where a card does one half or the other. Cards with no now-line (Nip)
  don't use up the once.
- **Furina: Center of Attention** (Power, 2 [1]). "The first Spend you choose
  each turn takes no Fanfare, and you can choose it even when your back
  performer has too little." This bends rule 8. Someone must still be on
  stage. It fits your fade-pass direction: "Spend cards strong".

## 4. Kokomi: 1 Common, 7 Rares, 2 multiplayer (pool 70 → 78: 21 / 36 / 21 with §6)

Every damaging card applies Hydro (brief §4). On the cards with two halves,
the Plan line buys only what a head start can buy.

| Card | For | Type, cost, rarity | Text |
|---|---|---|---|
| Tidal Screen | all | Skill, 1, C | Gain 7 [10] Block. Plan: Draw 2 cards. |
| Spring Tide | volume | Skill, 1 [0], R | Exhaust. The Bake-Kurage carries out all your Plans now. |
| Kurage School | volume | Skill, 1 [0], R | Exhaust. Add a copy of each 0-cost card with a Plan line in your hand to your hand. |
| Shoal of Spears | volume | Attack, 1, R | Deal 4 [5] damage to ALL enemies for each Plan you wrote this turn. |
| Patient Tide | Big Plan | Power, 1, R | At the end of your turn, keep up to 2 [3] unspent Energy. |
| Sea's Reproach | Tide Control | Power, 2 [1], R | Whenever you apply Weak or Vulnerable to an enemy, deal 3 damage to it. |
| Tidal Rebuke | Dusk Guard | Attack, 2 [1], R | Deal damage equal to your Block to ALL enemies. (Exhaust dropped, §6.) |
| Watatsumi Resistance | Companions | Power, 1 [0], R | Whenever you play a Companion card, add a Nip to your hand. |
| Tactical Relay | multiplayer | Skill, 1, U | Plan: Each player gains 1 Energy [and draws 1 card]. |
| Kurage's Mercy | multiplayer | Skill, 2, R | Exhaust. Each player Mends 8 [12]. |

- **Spring Tide** is Change of Plans (Common, first Plan only) at Rare for the
  whole queue. Each carry-out counts for the Casket and for Kurage Canopy, and
  the empty queue can be written again for the morning, so a volume turn can
  pay twice.
- **Kurage School** copies only Plan cards. That keeps Open the Casket, Coral
  Tithe and Salt in the Wound out of it.
- **Shoal of Spears** counts Plans written this turn. Sango Isshin counts
  Plans carried out this turn, so the two are different turns.
- **Patient Tide** saves Energy for Masterstroke (3) and Undertide Lance.
  The cap stops the bank from growing forever.
- **Sea's Reproach** is Silent's Sadistic Nature at her pace. Tide Control
  has ten Weak and Vulnerable sources and three payoffs.
- **Tidal Rebuke** gives Dusk Guard an AoE finisher to sit beside Coral
  Crash: Body Slam to ALL enemies, a rarity and a cost above Ironclad's.
- **Watatsumi Resistance** connects her companion cards (Banner, Chain of
  Command, Rally) to the Plan-volume deck.
- **Kurage's Mercy**: healing is hers in the lore. The law keeps Mend to Rare
  Exhaust cards.

## 5. Furina: 3 Uncommons, 3 Rares (pool 72 → 78: 23 / 35 / 20)

| Card | For | Type, cost, rarity | Text |
|---|---|---|---|
| Aria for One | Solo | Attack, 1, U | Deal 5 [7] damage twice. If no one is on stage, deal it three times. |
| Interval Bell | Ovation (Spend) | Skill, 0, U | Draw 1 card. Spend 3 [2]: draw 1 card and gain 1 Energy next turn instead. (Next turn since the 2026-10-04 loop fix.) |
| Casting Agent | Guest Cast | Skill, 1, U | Exhaust. Choose 1 of 3 random Guest Star cards and add it to your hand. It costs 0 this turn [and is upgraded]. |
| The Last Act | Solo | Attack, 3, R | Costs 1 less for each empty seat. Deal 24 [30] damage. |
| Critics' Darling | Ovation (Spend) | Power, 1, R | Whenever you choose a Spend mode, deal damage equal to the Fanfare spent to ALL enemies. [Innate.] |
| Star Turn | Guest Cast | Power, 2 [1], R | Whenever a Guest Star joins the stage, it performs at once. |

- **Solo** has had one Rare (One-Woman Show) and now has a finisher. The Last
  Act costs 0 on an empty stage and 3 on a full one.
- **Critics' Darling** pays for the stronger Spend modes the fade pass made.
  Center of Attention's free Spend spends nothing, so it pays nothing here.
- **Star Turn** bends rule 3, under which a newcomer never acts on arrival,
  at Rare for the deck that pays for guests.
- **Casting Agent** gives the Guest Cast the consistency it lacked; today a
  Guest Star can only be drawn.

## 6. Body Slam is priced too high (the balance note)

[USER], 2026-10-01: "My friend pointed out that the Ironclad Body Slam card
(deal damage equal to your block) is non-exhausting, common, and costs 1
(upgrades to 0 cost), so we're probably systemically over-pricing this
effect." The census of the sheet finds three cards printing it:

| Card | Was | Now |
|---|---|---|
| Coral Crash (Kokomi) | Uncommon, 1, no upgrade | **Common, 1 [0]**: Body Slam exactly |
| Tidal Rebuke (Kokomi, new) | Rare, 2 [1], Exhaust | Rare, 2 [1], no Exhaust |
| Noelle — Sweeping Time (Mondstadt companion) | Uncommon, 2, no upgrade, ALL enemies | Uncommon, **2 [1]**, ALL enemies |

The AoE versions sit one rarity and one cost above Body Slam, which is what
the base game charges for hitting every enemy (Cleave against Strike).
Kokomi's counts after the batch: 21 / 36 / 21, still 78.

## 7. What the sim must show before the build

1. Kokomi: each of her four decks reaches act-won within 10 points of Plan
   volume (the expansion's check 1), with the new Rares granted.
2. Furina: Solo, Spend and Guest decks each within 10 points of the default
   drafter.
3. No new card is taken from over 70% of offers, or played in under 5% of
   the fights where it is held.
4. The Ancient cards are game-side only, as the first three were (the sim
   models no events).

## Picks

1. **Kokomi's batch (§4): 1 Common, 7 Rares, 2 multiplayer cards.** Default:
   yes.
2. **Furina's batch (§5): 3 Uncommons, 3 Rares.** Default: yes.
3. **Furina's twelve old-kit cards.** (a) Keep them for now and audit them in
   a later pass, replacing the ones that read poorly under the Stage. (b)
   Replace all twelve in this batch, making 18 new cards. Default: (a). Six
   cards can be tested now; eighteen is its own paper.
4. **The three Ancient cards (§3), each bending a rule.** Default: yes.
5. **Varka's 2 Ancient and 5 multiplayer cards wait** until the seat round on
   his 78-card build is read. Default: yes (your call this morning).
