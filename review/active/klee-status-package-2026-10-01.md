# Klee status package and dedupe (2026-10-01)

**Ruled 2026-10-01.** [USER]: "1) I think a) is fine - we can keep tho the
game's conventions 2) and 3) agreed on your defaults." So: Dazed for the fair
loaders and Confiscated for the busted ones (1a); the eight new cards and
Albedo's card as written (2a); the eight cuts (3a).

[USER]'s idea: "an Ironclad or Regent-style engine where you play cards with
excellent cost-to-effect ratios that load your deck with status duds." Also
ruled into this paper: Albedo's Klee card gets an alchemy hook (lore pass,
pick 3), and a dedupe makes the room. The pool stays at 78.

## 1. Two statuses, priced by how busted the card is

[USER], on the first draft: "Defect cards add a mix of defects depending on
their power level ... it's worth drawing a distinction between the completely
busted cards which are 'mega turn now, suffer later' like Lisa's Treats or Red
Knight and the simpler ones like It Wasn't Me!" Defect does exactly this: Boost
Away adds a Dazed, Turbo a Void, Overclock a Burn, Fight Through a Wound.

- **Light tax: Dazed** (the base game's: Unplayable, Ethereal). It clogs one
  hand and leaves. It goes on the simple, fairly priced loaders. Using the
  base card means nothing new to learn; Kokomi's Flotsam Surge already uses it.
- **Heavy tax: Confiscated** (hers, unchanged). It costs 1, "Does nothing,"
  and is not exhausted when played, so it comes back every shuffle all combat
  (`klee-mod/KleeCode/Cards/Confiscated.cs`). It goes on the "mega turn now,
  suffer later" cards. It is her lore exactly: Jean confiscates her bombs once
  or twice a week (character story 2). Fish Blasting (Common, 8 [11] to ALL
  for 1, above the Common AoE rate) already pays it and keeps paying it.

**Payoffs read the tier they care about.** The answers (Klee Can Explain!,
Albedo, Damage Report) read any status, the way Compact and Fire Breathing do.
The bend-the-rule pair (Finders Keepers, Solitary Confinement) reads
Confiscated only, because only Confiscated is played.

## 2. The new cards (8 in the pool, plus Albedo)

**Loaders.** The two Commons pay the light tax; the two busted cards pay the heavy one.

| Card | Type, cost, rarity | Text | Base yardstick |
|---|---|---|---|
| **Forbidden Fun** | Attack, 0, C | Deal 10 [14] damage. Shuffle a Dazed into your draw pile. | Regent's Collision Course: 0, 10 [14], plus a Debris |
| **It Wasn't Me!** | Skill, 0, C | Gain 6 [9] Block. Shuffle a Dazed into your draw pile. | Defect's Boost Away: 0, 6 [9] Block, plus a Dazed (exact parity) |
| **Lisa's Treats** | Skill, 0, U | Gain 2 [3] Energy. Add 2 Confiscated to your draw pile. | Defect's Turbo (Common): 0, 2 [3] Energy, plus a Void |
| **Red Knight** | Attack, 2, R | Deal 22 [28] damage to ALL enemies. Add 2 Confiscated to your draw pile. | Kokomi's Riptide Ruin: 2, 9 [12] to ALL twice, plus 3 Dazed |

**Payoffs and answers.**

| Card | Type, cost, rarity | Text |
|---|---|---|
| **Finders Keepers** | Power, 1, U | Whenever you play a Confiscated, place a Bomb 5 [7] on a random enemy. |
| **Klee Can Explain!** | Skill, 1, U | Gain 6 [8] Block. Transform every status in your hand into Pop!. |
| **Damage Report** | Power, 1, R | Whenever you draw a status, deal 5 [7] damage to ALL enemies. |
| **Solitary Confinement** | Power, 1, R | Your Confiscated cost 0. [Innate.] |

**Albedo's Klee card** replaces "Albedo — Tectonic Tide" (it stands in for
Solar Isotoma, Rare, as now):

| Card | Type, cost | Text |
|---|---|---|
| **Albedo — Dust of Purification** | Skill, 1 | Exhaust every status in your hand. Your largest Bomb grows by 6 [8] for each. |

Dust of Purification is his sixth constellation. He cleans up after her and
turns the mess into gunpowder, which is the brief's planned hook (§7.1, "the
man who cleans up after her").

**How the pieces fit.**

- **On their own,** the Commons are fair cards at base-game parity (a Dazed
  each). Lisa's Treats and Red Knight are the mega turns, and the bill is two
  Confiscated that stay all combat.
- **Finders Keepers** turns each Confiscated into a 1-cost Bomb 5: a bad
  card, not a dead one.
- **Klee Can Explain!** is her Compact: every status in hand becomes a Pop!.
  Base Compact is 6 [7] Block, Uncommon.
- **The Rares bend the rule.** With Solitary Confinement, Confiscated cost 0,
  so with Finders Keepers each is a free Bomb 5. With Damage Report, every
  status drawn (a Dazed too) hits everything for 5. Damage Report drops from
  6 to 5 because it now reads Dazed as well. That is the high roll. It is
  bounded by how many statuses the loaders put in, and none of the payoffs
  draws cards, so there is no draw loop.
- **Lore:** Jean confiscates, Klee swears it wasn't her, explains, gets
  grounded, writes the damage report, and sneaks her bombs back. Lisa slips
  her treats, and Albedo cleans up.

**Two things I checked.**

- **The status-batch lesson:** Kokomi's Flotsam Surge drew an 82% pick rate
  because the sim's pilot does not count Dazed as a cost. These loaders will
  look better in the sim than in play for the same reason, so the seats judge
  them.
- **Sparks still come only from explosions.** Confiscated makes Bombs, not
  Sparks; the Spark comes when the Bomb goes off.

## 3. The dedupe: eight cuts

| Cut | Rarity | Why |
|---|---|---|
| Careful Now | U | Block capped at 10; a seat's NEVER AGAIN; Sorry, Jean... does it at 0 with no cap. You dislike caps. |
| Friendship Bracelet | U | The third "Companion played: a Bomb 3" Power, next to Little Hexenzirkel. |
| Pocket Fireworks | C | Plain 9 damage for 1; nothing of hers. Forbidden Fun takes the slot. |
| Fish Fry | U | 2 Energy, 7 to ALL (12 to bombed enemies): below Fish Blasting, a Common. |
| Dodoco Cover | C | The same card as Windtrace (Common, 1, Block plus a small charge). It also drops the Dodoco count from five to four. |
| Flame Dance | U | The React shelf's weakest: without a reaction it is 5 to ALL for 1. |
| Rapid Fire | U | Already "watched"; 2 Energy for 12 on one random target. |
| Split Charge | U | Random halves on random enemies; nobody built around it. |

**Rarity after the swap:** 24 / 33 / 21 (Common / Uncommon / Rare), from
24 / 36 / 18. That moves toward the base game's thicker Rares (about 20 / 38 /
27; the earlier audit's point 6).

**Kept although they were near-duplicates:** Pocket Match beside Ka-pow!
(you asked for that redesign on 09-24); Tag Along beside Adventure Club (the
companion path needs both rarities); Look Out! beside Clover Charm (a card
and a relic can share an effect).

## 4. What it costs to test

There is no rule change, so this is a seat round: two seats, the record and
the fixes. You play at the finish line, which is the final pass before
Balance.

## 5. Defence in the status pile (ruled 2026-10-01)

[USER]: "Ok Klee - I'd say we go for option 1 and add the defensive utility
into her status pile, which gives some incentive for players to engage with
it. We can give a mix of weak, high-block cards (already present) and perhaps
an alchemy-flavored Strength reduction?"

| Name | Type, cost, rarity | Text | Upgrade |
|---|---|---|---|
| **Up in Smoke!** | Skill, 1, Common | Apply 2 [3] Weak to ALL enemies. Shuffle a Dazed into your draw pile. | Weak +1 |
| **Behind Jean's Desk** | Skill, 1, Uncommon | Gain 14 [18] Block. Add a Confiscated to your draw pile. | Block +4 |
| **Kitchen Alchemy** | Skill, 1, Uncommon, Exhaust | Exhaust a status in your hand. ALL enemies lose 2 [3] Strength. | Strength loss +1 |

Kitchen Alchemy is unplayable with no status in hand, the way base-game cards
with a play condition are. With several statuses in hand the player chooses
which to exhaust. The Strength loss is permanent, as Malaise's is.

**The three swaps** (rarity stays 24 / 33 / 21):

- Fish-Flavored Bait (Common) → Up in Smoke!
- Nova Burst (Uncommon) → Behind Jean's Desk
- Spinning Sparkler (Uncommon) → Kitchen Alchemy

Why: the census (2026-10-01) found her pool had no Weak, no Strength loss and no card giving 10+ Block outright; all three now live in the status pile, so engaging with it is how she defends.

[USER], on the three cards: "Up in Smoke and Behind Jean's desk look quite
strong, but we can always nerf them later. Looks good for now!"

Watch: Up in Smoke! and Behind Jean's Desk (strong; nerf candidates after the
seat round).

## Picks

1. **Two tiers: Dazed for the fair loaders, Confiscated for the busted ones**
   (a, default). (b) a Klee-flavoured light status (a "Dud": Unplayable,
   Ethereal) instead of the base Dazed. That is the same rules with her name
   on it, but one more card to learn.
2. **The eight new cards and Albedo's card as written** (a, default), or name
   the ones to change.
3. **The eight cuts** (a, default), or name the ones to keep and a
   replacement cut.
