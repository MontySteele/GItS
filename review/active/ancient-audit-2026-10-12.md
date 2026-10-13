# Ancient cards and starter-relic upgrades: an audit, 2026-10-12

[USER]: "Let's do an audit for the other characters on this to make sure their Ancient cards and Ancient relic upgrade make sense in their current builds."

**Evidence.** The census is `scratchpad/ancient-audit/census.md` (gitignored), with file:line for every claim. The game's own rules come from the decompiled `DustyTome.cs` and `ArchaicTooth.cs`.

## How the base game does it

- **Each base character has two Ancient cards** (`game_ref/defect.json`: Ancient 2).
  - **One is added by Darv's Dusty Tome:** a random Ancient card of your character, upgraded.
  - **The other is the "Transcendence" of the character's signature starter card,** which Orobas's Archaic Tooth swaps in: Bash to Break, Neutralize to Suppress, Unleash to Protector, Falling Star to Meteor Shower, Dualcast to Quadcast. The Tome never offers the Tooth cards.
- **Touch of Orobas upgrades the starter relic.**

## What we have

- **None of our kits has a Tooth card.** All six of our Ancient cards are Tome cards.
  - Archaic Tooth looks for Bash, Neutralize and the rest, and finds none of them in our starters. So Orobas never offers it to our characters.
  - In co-op it was offered six times, always to the base-character partner.
- **All four relic upgrades are live and current:**
  - Dodoco Tales: 4 more Sparks to start each combat;
  - Watatsumi Casket: 5 Block at the start of her turn while a Plan waits, after today's change;
  - The Curtain Never Falls: Repay 2;
  - Wolf's Gravestone: an upgraded Ascension that costs 0 that turn.
  - All four are reachable through Orobas in act 2. The "never rolled" comments only mean they are never in reward or shop rolls.
- **Varka** (built today): All Four Winds is his Tome card, and Dandelion Gale is his Tooth card (Windbound Execution). That makes him the template.

## Card by card

| Kit | Card | Text | Finding |
|---|---|---|---|
| Klee | Jumpy Dumpty Mk.Omega (2) | Deal 12 Pyro to a random enemy 3 times. Place a Bomb 12 on ALL enemies. | **It is already Jumpy Dumpty's bigger self.** It belongs as the Tooth card for her starter Jumpy Dumpty. |
| Klee | Alice's Masterpiece (3 [2]) | When one of your Bombs goes off, it stays at half its size. | Fine, and it bends her rule as an Ancient should. **The text says Bombs, but the code also keeps Mines;** the text should say "Bombs and Mines". |
| Kokomi | Princess of Watatsumi (1) | Whenever the Bake-Kurage carries out a Plan, gain 2 [3] Block and draw 1. | **Overlaps a pool card:** Kurage Canopy is "Whenever the Bake-Kurage carries out a Plan, gain 3 Block". A run-defining reward shouldn't be a pool Uncommon plus a draw. |
| Kokomi | Divine Strategy (2 [1]) | The first time each turn you play a card on the Bake-Kurage, the line above its Plan happens now too. | Fine. It is her rule-bender. |
| Furina | All the World's a Stage (1) | At the start of your turn, gain 2 [3] Fanfare. | **Thin.** It is her Rare relic Grand Theater Program (1 a turn) doubled. Its code and sim still carry the retired Encore drip. |
| Furina | Center of Attention (2 [1]) | The first Spend you choose each turn takes no Fanfare. | Fine as a bend, but **the code skips "Spend all" (Rising Applause, Bravura).** That's right, since a free spend-all would be a second Bis!, but the text doesn't say so. |

**Hygiene, my calls, no pick:**
- **Stale comments, sim rows and docs:**
  - comments and sim rows still name Kokomi's retired Charge and Furina's retired Encore (`tier0/content/cards/ancients.yaml`, `docs/ancient-upgrades.yaml`, `lint_handwritten_parity.py`);
  - the Curtain Never Falls class doc describes an old relic;
  - a Dodoco Tales comment says the opening bank is off and she opens at 5 Sparks. It's on, and 7.
- **A double-fire check:** I'll confirm that Dodoco Tales pays once per explosion, not twice; its relic listens on two event channels.
- **The sheet comment on Four Winds' Ascension** saying "never in the deck" goes with Varka's build.
- **`LAW.md` lines 218 to 225** still name the retired Charge and Encore in the Ancient carve-out. That's a LAW text change, so this PR is yours to merge.

## Proposal

Give each kit one Tome card and one Tooth card, like the base characters and Varka. The Tooth card takes the place of the weaker or overlapping Ancient:
- **Klee:** Jumpy Dumpty Mk.Omega becomes the Tooth card for Jumpy Dumpty. It gains Innate, since the card it replaces is Innate. Its text doesn't change otherwise. Alice's Masterpiece stays her Tome card, with the "Bombs and Mines" fix.
- **Kokomi:** Princess of Watatsumi becomes the Tooth card for Kurage's Oath ("Gain 6 Block. Or plan: Deal 9 Hydro damage to ALL enemies."). It turns into a bigger Oath: "Gain 9 [12] Block. Draw 1 card. Or plan: Deal 9 [12] Hydro damage to ALL enemies twice." That ends the Kurage Canopy overlap. Divine Strategy stays her Tome card.
- **Furina:** All the World's a Stage becomes the Tooth card for Rising Applause ("Gain 5 Block. Spend all your Fanfare and deal that much Hydro damage."). It turns into: "Gain 8 [11] Block. Spend all your Fanfare and deal that much Hydro damage to ALL enemies." Center of Attention stays her Tome card, with "The first Spend N or Spend up to N each turn takes no Fanfare."

Your rulings to leave Klee's deck and Furina alone apply here. These are rewards from two act-2 Ancients, not pool cards, and Mk.Omega's text doesn't change. Pick 1 lets you hold either kit back.

## Ruled 2026-10-12

[USER]: "Watastumi Casket is a bit weak for an Ancient relic - perhaps bump it to "3 Block per Plan" instead of just "3 block if there was a Plan". Princess of Watatsumi needs to do more as an Ancient. Perhaps "Gain 9 [12] Block. Draw 2 cards. Or plan: Deal 3 [5] Hydro damage to ALL enemies five times." All the World's a Stage likewise needs a bump - "Gain 8 [11] Block. Spend all your Fanfare and deal that much Hydro damage to ALL enemies twice." Otherwise agreed.- let's fix them all"

- **Pick 1 (a):** all three kits get one Tome card and one Tooth card.
  - **Klee:** Mk.Omega becomes the Tooth card for Jumpy Dumpty and gains Innate. Alice's Masterpiece says "Bombs and Mines".
  - **Kokomi:** Princess of Watatsumi becomes the Tooth card for Kurage's Oath: "Gain 9 [12] Block. Draw 2 cards. Or plan: Deal 3 [5] Hydro damage to ALL enemies five times."
  - **Furina:** All the World's a Stage becomes the Tooth card for Rising Applause: "Gain 8 [11] Block. Spend all your Fanfare and deal that much Hydro damage to ALL enemies twice." Center of Attention's text says it skips "Spend all".
- **Pick 2 (a):** Rising Applause is Furina's Tooth card, at your numbers.
- **Watatsumi Casket** (the Orobas upgrade): "At the start of your turn, gain 3 Block for each Plan waiting." The Tamakushi Casket stays at 3 if any Plan is waiting.
- **Hygiene** as listed, and the `LAW.md` Ancient carve-out loses the retired Charge and Encore.

## For [USER] (ruled above)

1. **One Tome card and one Tooth card per kit.**
   - **(a) Default:** all three as proposed.
   - (b) Kokomi and Furina only; Klee's two Ancients stay as they are until her feedback.
   - (c) Kokomi only.
2. **Furina's Tooth card.**
   - **(a) Default:** Rising Applause becomes a spend-all to ALL enemies with more Block.
   - (b) Curtain Rise instead: "Deal 10 damage. Drain 3: deal 20 instead, to ALL enemies."
