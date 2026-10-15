# Kit census: four kits against the base five, 2026-10-15

[USER] asked (2026-10-15) for a census of Klee, Varka, Furina and Kokomi against
Ironclad, Silent, Defect, Regent and Necrobinder. He wanted three answers: are
there standalone mechanics left over from old builds, are our cards more
complex than the base game's, and did we miss or orphan any relics and potions.
The numbers come from a Sonnet census (scripts and the full 5,000-word table
in the session scratchpad, `census/`; rerun with `extract_base.py` then
`census.py`). Base text is read from the game's pck; our pools from each kit's
roster (78 draftable each). Generic Strike and Defend are left out on both
sides. Yae is staged and not counted.

## 1. Are our cards more complex? Somewhat: three words longer

| | words per card (mean / median) | has a condition* | keywords per card | cards with no keyword |
|---|---|---|---|---|
| Base five | 9.7 / 9.5 (Silent 8.7 to Necrobinder 10.4) | 24% | 1.26 | 21% |
| Klee | 13.9 / 14 | 31% | 2.06 | 2% |
| Varka | 12.4 / 12 | 44% | 2.07 | 2% |
| Furina | 11.5 / 12 | 41% | 1.83 | 5% |
| Kokomi | 13.2 / 13 | 28% | 2.28 | 2% |

\*"if", "for each", "whenever" or "instead".

Some of the gap is structural and intended. "Hydro" in "Deal 7 Hydro damage" counts
as a keyword, and Kokomi's 52 Plan cards carry a second line by design. The
rest is wording. The longest base card has 23 words (Right Hand Hand). Ours
include Read the Field (26), Gorou Juuga (25), Simmer (24), and Flash Point and
Taste Test (23 each). Seven of our ten longest cards are Klee's. Varka's and
Furina's high condition rates are their identities (Oath dials, Spend and
Repay), not drift.

**Keyword count is not the problem.** Our kits use 17 to 22 distinct keywords
each; the base five use 14 to 21.

## 2. Standalone mechanics: few

A keyword on only one or two of our cards that nothing else names:
- **Flip** (Furina, Ousia / Pneuma: "Gain N Block. Flip."). Her design is
  final and this is her lore's duality, so it stays. **Ruled 2026-10-15:**
  each face does its half of her kit, so Flip stops being standalone. Ousia:
  "Drain 2. Deal 10 damage." Pneuma: "Repay 2. Gain 8 Block." (numbers set in
  the build). [USER]: "Makes sense - I like it!" Built in her next card pass.
- **Mend** (Kokomi, The Moon and the co-op Kurage's Mercy). It is the healer's
  identity, so it stays. The Moon was one seat's "never again" in round 8, so
  it is watched.
- **Geo** (Kokomi's two Gorou cards) is an element name, not a mechanic.
- **"Oldest guest"** (Furina, Encore!) is a selector over her guests, not a
  rule.

Sixteen non-Power cards create a one-turn effect of their own, for example
Boom Badge, Objection!, Plot Twist and Eye Wall. Each is fully explained by its card text, the
way base one-turn cards are, so none is a leftover. Nothing here needs cutting.

## 3. Relics and potions: two kits are short, and two borrowed relics are dead

| | own relics (starter + others) | own potions |
|---|---|---|
| Each base character | 1 + 7 (Common 1, Uncommon 2, Rare 3, Shop 1) | 3 (Common, Uncommon, Rare) |
| Klee, Varka | 1 + 8 (base shape plus an Ancient) | 3 |
| Furina | 1 + 3 (Common, Rare, Ancient) | 1 |
| Kokomi | 1 + 1 (the Ancient casket) | 0 (she rolls Silent's) |

Every kit also rolls Silent's relics, minus Helical Dart and Snecko Skull
(dropped earlier). Two of the borrowed relics, **Tingsha** and **Tough
Bandages**, pay only when you discard a card. No Klee, Furina or Kokomi card
discards (Varka has two), so for those three kits both relics are blank. One
Kokomi seat this week held Tingsha all run.

All 29 of our own relics and potions still fit their kits. The census flagged Klee's Fresh Catch
and Alice's Teapot because no Klee card says "Hydro". Both are there so her
Pyro Bombs Vaporize, which is working as designed, so they stay.

## 4. Hygiene Claude builds (no pick)

1. Delete code that nothing uses, after confirming no sheet row applies it by
   name: the Dexterity and Vigor tip builders, `OathLeftPower`,
   `KurageCanopyBasePower`, Alice's Detonator's two powers, and the Pounding
   Surprise II relic class. Abyss code stays (the mode is in progress); Yae's
   is rechecked after her round-3 build.
2. `Furina.cs` says "her own three potions"; her pool holds one. Correct the
   comment.

## Picks

**Ruled 2026-10-15, all three (a).** [USER]: "Agreed on all of the above!"

**Pick 1: the relic and potion gap.**
- **(a) Default.** Claude designs Kokomi a full set (7 relics, 3 potions) and
  completes Furina's (4 more relics, 2 more potions), each in the base shape,
  before the Workshop release. Kokomi goes first because her gap is larger.
- (b) Kokomi only.
- (c) Leave both as they are.

**Pick 2: the borrowed Silent relics.**
- **(a) Default.** Both. Drop Tingsha and Tough Bandages now for Klee, Furina
  and Kokomi. Then drop the whole Silent borrow from each kit once it has its own full set. For Klee and Varka
  that is a relic-pool change at Balance, so it is staged on their `-next`
  branches.
- (b) Only drop the two discard relics.
- (c) Leave the borrow as it is.

**Pick 3: card wording.**
- **(a) Default.** Run a wording pass on every card over 18 words, all four kits.
  It changes text only: no numbers and no behaviour. That is allowed on Klee and
  Varka at Balance. The aim is the base game's longest card, about 23 words, as
  a ceiling.
- (b) Prototype kits only (Kokomi, Furina).
- (c) Leave it.
