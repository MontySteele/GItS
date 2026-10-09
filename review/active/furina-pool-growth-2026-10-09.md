# Furina: the pool to 75, and Guests as an archetype

Paper, 2026-10-09. **RULED 2026-10-09, all picks at their defaults,** after a Fable design review ended with "no further critiques". [USER]: "If they have no further critiques, then I'm good to approve it." Main session design. It comes from the human co-op run
(`review/records/coop-human-playtest-2026-10-09.md`, pick 4) and [USER]'s
ruling: "start with these trims and readjust after the card pool expands."
The counts are from a census of `docs/prototype-surface.yaml` and
`game_ref/*.json`, with the 2026-10-09 trims applied (PR #988). Card rows go
in `docs/prototype-surface.yaml` once ruled.

## 1. What the play asked for

- **Guests should be a plan of their own.** They were "insane" in act 1 and
  faded by act 3. The friend's suggestion was to let them spend Fanfare.
- **She needs scaling outside the Fanfare bank.**
- **Drain should sometimes put her in danger,** and Repay should matter
  more.
- **The pool is small.** It has 34 cards, against 78 for the other kits.

## 2. Where the gaps are

| | Furina now | Base five | Klee / Kokomi / Varka |
|---|---|---|---|
| Common / Uncommon / Rare | 10 / 17 / 7 | 20 / 38 / 27 | about 21 / 34 / 21 |
| Common Skills | 3 | 7–11 | — |
| Uncommon / Rare Powers | 4 / 4 | 7–10 / 9–10 | 4–8 / 10–14 |
| Scaling sources | 8 | 18–22 | 15–26 |
| Common AoE attacks | 2 | 1–2 | 0–2 |

- **Archetype sizes:**
  - Drain (Ousia): 9.
  - Repay (Pneuma): 6, the smallest, with 2 Commons.
  - Fanfare (the Crowd): 10.
  - Guests: 7.
  - Bridges: 2.
- **What this means:** Common Skills, Powers and Pneuma are the holes.
  Common AoE is already full, so none is added.

## 3. Guests: a cast you draft, then rotate

**Revised 2026-10-09 on [USER]'s read.** He said: "I don't think the deck
should devolve into spamming random Guest Stars." His idea was a new guest
rule, which this section proposes (pick 1).

**The rule:**
- A Guest Star card **exhausts** when played.
- When its guest **leaves the stage**, the card goes to your discard pile.
  This happens when a fourth summon removes the oldest guest, or when Final
  Bow sends one off. The card can then be drawn and played again, but only
  to bring that guest back.
- While on stage, each guest has a **line**, a passive like a Power's, and
  an **act** at the end of your turn. It has no effect on summon.
- The current "play a guest who is already on stage and it acts at once"
  path goes away. In the co-op run, that path read as guests acting twice.
  A second copy played while its guest is on stage moves that guest to the
  newest seat, with no act.
- **End-of-turn order:** each guest acts, oldest first. Then Showstopper
  Spends and the guests act again. Then Salon Solitaire Repays.
- In shape a guest is now a Power with a seat cap and an end-of-turn act.
  Its numbers never grow, which keeps it off the "Focus" line.
- A guest's line effect gets a small cue and a log line of its own, so it
  is not read as a second act. This answers the co-op record's first
  question.

**What this changes in play:** the first few Guest Stars you draft decide
the cast, so you draft them for the deck you are building. Each guest plan
is one of these:
- **Drain support:** Wriothesley, Lyney, Neuvillette.
- **Defence and Drain cover:** Charlotte, Sigewinne, Freminet.
- **Fanfare payoff:** Chevreuse, Lynette, Navia.
- **Repay damage:** Clorinde. **Guest synergy:** Escoffier.

Rotation still happens, but less often.

**One Common guest: Charlotte (pick 2).** The other guests are stronger
than a Common should be. Charlotte's act is Repay 2 and her line is a
once-a-turn draw, which is Common power. Without her, a 3-card reward holds
a guest about 22% of the time, and about 1 run in 4 ends act 1 with no
guest offered. Every base archetype has a Common way in, and Encore! does
nothing until a guest is on stage. **Upgrades raise the line or the act,
never the cost.** The full list is in sec.5.

**How Guests scale: they act more often, paid for with Fanfare.** A guest's
own numbers never grow. That keeps the line from 2026-09-07: "must not be a
Defect with Fanfare for Focus." Fanfare grows across a fight, so a bought act
is worth more in act 3 than in act 1, which answers the fade the play
reported.
- Encore! (Common): one bought act.
- Tutti! (Uncommon): every guest acts.
- Final Bow (Uncommon): a guest you choose acts twice and leaves, and its
  card returns.
- Showstopper (Rare): every turn's acts are bought again.
- Ensemble Cast (Rare): a fourth seat.

**Casting Call becomes an Uncommon tutor, not a random guest.** Under the
new rule, finding the guest you drafted is worth more than finding a random
one.

**Fanfare still comes only from HP.** Every new source goes through Drain,
Repay or HP lost.

## 4. Scaling outside the bank

Each archetype gets one permanent scaler at Rare and one Uncommon Power:
- **Ousia:** Regina of All Waters, Strength paid for with a Drain each
  turn.
- **Pneuma:** Hymn of Renewal, Strength from large Repays.
- **Crowd:** Standing Room Only, Strength from cashing everything in.

Two cards reward being within 5 HP of the Drain line: Against the Tide and High Stakes.
That is the danger the play asked for, kept inside the line, which stays
(ruled pick 3).

## 5. The 41 new cards

Upgrades are in brackets. "Oldest guest" is the one a fourth summon would
remove; cards that name it carry a tip saying so.

**Guests and stage (11): 1 Common, 5 Uncommon, 5 Rare**

| Card | Type, cost, rarity | Text |
|---|---|---|
| Casting Call | Skill 1, U | Put a Guest Star from your draw pile into your hand. [Draw 1 card] |
| Encore! | Skill 0, C | Spend 4. Your oldest guest acts. Draw 1 card. [Spend 3] |
| Tutti! | Skill 1, U | Each guest acts. Retain. [cost 0] |
| Final Bow | Skill 1, U | Choose a guest. It acts twice, then leaves. [3 times] |
| Grand Entrance | Power 1, U | Whenever you play a Guest Star, Repay 4. [6] |
| Guest Star: Freminet | Skill 1, U | Line: whenever you Drain, gain that much Block. Act: deal 5 Cryo damage to a random enemy. [Act 8] |
| Showstopper | Power 2 [1], R | At the end of your turn, Spend 5: your guests act again. |
| Ensemble Cast | Power 2 [1], R | You have 4 guest seats. |
| Guest Star: Navia | Skill 1, R | Line: your first Spend each turn costs 2 less (a spend-all keeps 2). Act: deal Geo damage to a random enemy equal to the Fanfare you spent this turn. [Line: 3 less] |
| Guest Star: Neuvillette | Skill 2, R | Line: your Hydro damage deals 2 more. Act: deal Hydro damage to ALL enemies equal to the HP you Drained this turn. [Line: 3 more] |
| Guest Star: Escoffier | Skill 1, R | Line: whenever a guest acts, Repay 1. Act: deal 4 Cryo damage to ALL enemies. [Act 6] |

**The seven built guests, under the new rule.** All cost 1 and exhaust. The
upgrade replaces today's 0 cost.

| Guest | Rarity | Line | Act | Upgrade |
|---|---|---|---|---|
| Charlotte | C (pick 2) | The first time you Repay each turn, draw 1 card | Repay 2 | Act: Repay 4 |
| Sigewinne | U | Whenever you Repay, gain that much Block | Repay 2 | Act: Repay 4 |
| Wriothesley | U | Whenever you Drain, deal that much Cryo damage to a random enemy | 4 Cryo to a random enemy | Act: 7 |
| Lyney | U | Your Drain line is 10 HP lower | Drain 2: 8 Pyro to ALL enemies | Act: 11 |
| Lynette | U | The first time each turn an enemy makes you lose HP, gain that much Fanfare again | 3 Anemo to an enemy with an aura | Act: 6 |
| Chevreuse | U | Whenever you Spend, apply 1 Vulnerable to a random enemy | 4 to a random enemy | Line: also 1 Weak |
| Clorinde | R | Whenever you Repay, deal twice that much Electro damage to a random enemy | 6 Electro to a random enemy | Act: 9 |

**The Crowd (9): 3 Common, 3 Uncommon, 3 Rare**

| Card | Type, cost, rarity | Text |
|---|---|---|
| Crashing Waves | Attack 1, C | Deal 4 Hydro damage twice. Spend 4: three times instead. [5] |
| Bubble Aria | Skill 1, C | Gain 6 Block. Spend 3: also draw 2 cards. [8] |
| Commanding Gaze | Skill 1, C | Apply 1 Vulnerable. Spend 4: apply 2 Vulnerable and 2 Weak instead. [3 and 2] |
| Star Turn | Attack 2, U | Deal 15 damage. Costs 1 less for every 6 Fanfare you have. Exhaust. [20] |
| Sold Out | Skill 1, U | Spend 6. Draw 2 cards. Gain 1 Energy next turn. [Spend 4] |
| Crescendo | Power 1, U | The first time you Spend each turn, draw 1 card. [Innate] |
| Prima Donna | Power 2 [1], R | At the start of your turn, if you have 10 or more Fanfare, gain 1 Energy. |
| Standing Room Only | Power 2 [1], R | Whenever you Spend all your Fanfare (at least 1), gain 1 Strength. |
| Bring the House Down | Attack 2 [1], R | Spend all your Fanfare. Deal that much damage. Each guest acts. |

**Ousia, Drain (10): 3 Common, 4 Uncommon, 3 Rare**

| Card | Type, cost, rarity | Text |
|---|---|---|
| Undercurrent | Attack 1, C | Drain 2. Deal 5 damage, plus 1 for each time you have Drained this combat. [7] |
| Overdraft | Skill 0, C | Drain 4. Gain 1 Energy next turn. [Drain 3] |
| Ousia Pledge | Skill 1, C | Drain 3. Draw 2 cards. [3 cards] |
| Against the Tide | Attack 1, U | Deal 8 damage. If you are within 5 HP of your Drain line, deal 14 instead. [11 / 18] |
| Pay the Tab | Skill 1, U | Drain 6. Draw 3 cards. [4 cards] |
| Riptide Lunge | Attack 1, U | Drain 3. Deal 10 damage. If this kills an enemy, Repay 6. [13] |
| High Stakes | Power 1, U | While you are within 5 HP of your Drain line, your Attacks deal 4 more damage. [6] |
| Regina of All Waters | Power 2 [1], R | At the start of your turn, Drain 3. If you do, gain 1 Strength. |
| The Deluge | Attack 2 [1], R | Drain 8. Deal 24 damage to ALL enemies. Exhaust. |
| All In | Skill 0, R | Drain 8. Gain 2 Energy. Exhaust. [Drain 6] |

**Pneuma, Repay (10): 3 Common, 5 Uncommon, 2 Rare**

| Card | Type, cost, rarity | Text |
|---|---|---|
| Soothing Waters | Skill 0, U | Repay 2. Draw 1 card. [Repay 3] |
| Gentle Current | Skill 1, C | Gain 5 Block. Next turn, Repay 4. [7 and 5] |
| Clean Slate | Attack 1, C | Deal 7 damage. Repay 3. If you have no drained HP left, draw 1 card. [10] |
| Hydro Lance | Attack 2, C | Deal 14 Hydro damage. Repay 4. [18] |
| Cleansing Torrent | Attack 2, U | Deal 10 Hydro damage to ALL enemies. Repay 4. [14] |
| Balance the Books | Skill 1, U | Deal damage to ALL enemies equal to half your drained HP. Repay 4. [Repay 6] |
| Rising Tide | Attack 1, U | Deal 6 damage, plus 3 for each time you Repaid this turn. [4 per] |
| Pneuma Tides | Power 1, U | At the start of your turn, Repay 2. [3] |
| Hymn of Renewal | Power 2 [1], R | Whenever you Repay 4 or more HP at once, gain 1 Strength. |
| Grand Absolution | Attack 2 [1], R | Repay all your drained HP. Deal that much damage to ALL enemies. Exhaust. |

**Bridge (1):** Ebb and Flow (Skill 1, U): "Drain 4, then Repay 2."
[Drain 6, Repay 3] It costs 2 HP and makes 6 Fanfare, so the HP limits it.

**After this batch:**

| | Common / Uncommon / Rare | Common Skills | Uncommon / Rare Powers | Common AoE |
|---|---|---|---|---|
| Furina | 20 / 35 / 20 (75) | 9 | 8 / 10 | 2 |

Three slots, one at each rarity, are held for what the first seat round
shows is missing.

## 6. Risks, checked before seats

- **Loops.** The build runs the loop probe on these combinations:
  - Encore! with Escoffier;
  - Tutti!, Showstopper and Bring the House Down together;
  - Final Bow with Grand Entrance: a guest leaves, its card returns, and it is played again;
  - Overdraft, Soothing Waters, Sold Out and Crescendo together. This is
    the one cycle not bounded by HP.

  Guest Stars exhaust, so a guest card cannot be replayed in a loop. It
  comes back only when its guest leaves.
- **Draft read before build.** The `--picks` draft read runs on the 75,
  as pool-40's did. Lyney took 94.8% of the picks there.
- **Clorinde keeps reading every Repay,** the relic's included. That is the
  co-op record's second question. With the relic at Repay 1 and Pneuma
  Tides, that is 6 free Electro a turn, which is fair for a Rare.
- **Pneuma is a sub-plan of Ousia.** Repay only returns drained HP, so a
  Repay deck always Drains as well.
- **Guests react most to the Drain line.** In the 2026-10-09 Drain-line
  sim the built guest deck won act 1 57% of the time, below the balanced
  deck's 64%. With the line at 1 HP it rose to 76%, and its act-2 boss wins
  went from 8% to 57%. Seats are asked whether a guest deck still needs
  Fanfare by act 3.
- **More Energy cards.** Overdraft, Sold Out, Prima Donna and All In bring
  her to 6, within the base range of 3 to 7. The play asked whether
  Fanfare has become a second Energy; the seats get that question.

## Review (2026-10-09)

A Fable design review read this paper. Its verdict was "approve with
revisions before build". Every critique is now taken in the text:
- **The "Drain down to your line" cards are capped.** Because drained HP
  returns at the curtain call, they turned 39 free HP into 39 AoE, 6
  Energy or 9 cards. The Deluge, All In and Pay the Tab now Drain fixed
  amounts.
- **Balance the Books** deals half your drained HP.
- **"At your line" becomes "within 5 HP".** The relic Repays every turn,
  so she never stays exactly on the line.
- **Hymn of Renewal** now gives Strength, not Vigor.
- **Ebb and Flow** nets −2 HP.
- **Star Turn** exhausts.
- **Prima Donna** costs 2 [1].
- **Final Bow** chooses its guest.
- **The guest rule's gaps are closed:** duplicate copies, end-of-turn
  order, line cues.
- **Charlotte returns to Common,** as pick 2.
- **Hymn of Renewal counts HP actually returned,** not the number printed on the card. This goes in the sheet comment and the tip, not on the card face.
- **All In costs 0.**
- **The loop probe gains the Energy cycle,** and the `--picks` draft read
  runs before the build.
- 2026-10-09 build: Overdraft and Sold Out give their Energy next turn; the loop probe found 16 thin-deck cycles.

## Picks

1. **The new guest rule** (sec.3): a Guest Star exhausts, its card returns
   to your discard pile when the guest leaves, and it has no effect on
   summon. Upgrades raise the line or the act, never the cost. It is a rule
   change, so it gets a seat round and then [USER]'s play. **Default: yes.**
2. **Charlotte stays Common** as the guest plan's way in (sec.3). This
   answers [USER]'s worry about never seeing a guest. **Default: yes.**
3. **Guests scale by acting more often, paid in Fanfare,** never by a guest
   stat. The other way would reopen the 2026-09-07 "not Focus" ruling.
   **Default: yes.**
4. **Fanfare still comes only from HP.** **Default: yes.**
5. **The pool targets 75, with 3 slots held,** and the 41 cards above are
   built as one batch. Then the loop probe, then a solo Furina seat round
   with an Ironclad control. **Default: yes, as written.**

Already taken on [USER]'s read (2026-10-09), not picks:
- Casting Call becomes an Uncommon tutor.
- Soothing Waters becomes Uncommon.
- Every guest except Charlotte is Uncommon or Rare.
