# Klee status package and dedupe (2026-10-01)

[USER]'s idea: "an Ironclad or Regent-style engine where you play cards with
excellent cost-to-effect ratios that load your deck with status duds." Also
ruled into this paper: Albedo's Klee card gets an alchemy hook (lore pass,
pick 3), and a dedupe makes the room. The pool stays at 78.

## 1. The status: Confiscated, unchanged

Klee already has a status. **Confiscated** costs 1 and "Does nothing." It is
not exhausted when played, so it stays in the deck all combat. Fish Blasting
adds it today (`klee-mod/KleeCode/Cards/Confiscated.cs`).
It is her lore exactly: Jean confiscates her bombs once or twice a week
(character story 2). So the engine is built on it: no new status and no rule
change.

It is harsher than the base game's duds. Dazed vanishes at the end of turn,
and Slimed exhausts when you pay for it; Confiscated costs 1 every time it
comes around. The loaders' ratios are priced against that.

## 2. The new cards (8 in the pool, plus Albedo)

**Loaders: an excellent ratio, paid in Confiscated.**

| Card | Type, cost, rarity | Text | Base yardstick |
|---|---|---|---|
| **Forbidden Fun** | Attack, 0, C | Deal 10 [14] damage. Add a Confiscated to your draw pile. | Regent's Collision Course: 0, 10 [14], plus a Debris |
| **It Wasn't Me!** | Skill, 0, C | Gain 7 [10] Block. Add a Confiscated to your draw pile. | Defect's Boost Away: 0, 6 [9] Block, plus a Dazed |
| **Lisa's Treats** | Skill, 0, U | Gain 2 [3] Energy. Add 2 Confiscated to your draw pile. | Defect's Turbo (Common): 0, 2 [3] Energy, plus a Void |
| **Red Knight** | Attack, 2, R | Deal 22 [28] damage to ALL enemies. Add 2 Confiscated to your draw pile. | Kokomi's Riptide Ruin: 2, 9 [12] to ALL twice, plus 3 Dazed |

**Payoffs and answers.**

| Card | Type, cost, rarity | Text |
|---|---|---|
| **Finders Keepers** | Power, 1, U | Whenever you play a Confiscated, place a Bomb 5 [7] on a random enemy. |
| **Klee Can Explain!** | Skill, 1, U | Gain 6 [8] Block. Transform every Confiscated in your hand into Pop!. |
| **Damage Report** | Power, 1, R | Whenever you draw a Confiscated, deal 6 [9] damage to ALL enemies. |
| **Solitary Confinement** | Power, 1, R | Your Confiscated cost 0. [Innate.] |

**Albedo's Klee card** replaces "Albedo — Tectonic Tide" (it stands in for
Solar Isotoma, Rare, as now):

| Card | Type, cost | Text |
|---|---|---|
| **Albedo — Dust of Purification** | Skill, 1 | Exhaust every Confiscated in your hand. Your largest Bomb grows by 6 [8] for each. |

Dust of Purification is his sixth constellation. He cleans up after her and
turns the mess into gunpowder, which is the brief's planned hook (§7.1, "the
man who cleans up after her").

**How the pieces fit.**

- **On their own,** the four loaders are good cards with a tax. That covers
  most drafts: a Common 0-cost 10 damage is worth one Confiscated.
- **Finders Keepers** turns each Confiscated into a 1-cost Bomb 5: a bad
  card, not a dead one.
- **Klee Can Explain!** is her Compact: the duds in hand become Pop!s. Base
  Compact is 6 [7] Block, Uncommon.
- **The Rares bend the rule.** With Solitary Confinement, Confiscated cost 0,
  so with Finders Keepers each is a free Bomb 5. With Damage Report, each draw
  of one also hits everything for 6. That is the high roll. It is bounded by
  how many Confiscated the loaders put in, and none of the payoffs draws
  cards, so there is no draw loop.
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

## Picks

1. **Build on Confiscated as it is** (a, default), or make it exhaust when
   played, like Slimed (b). (b) is gentler and makes the loaders weaker, but
   then Finders Keepers fires once per Confiscated, not once per cycle.
2. **The eight new cards and Albedo's card as written** (a, default), or name
   the ones to change.
3. **The eight cuts** (a, default), or name the ones to keep and a
   replacement cut.
