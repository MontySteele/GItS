# Shared text audit, 2026-10-23

The writing review, the shared text (ruled 2026-10-23,
`localization-2026-10-19.md`; format: `kokomi-text-audit-2026-10-22.md`):
the 110 Companion cards (Mondstadt, Inazuma, Fontaine), the shared powers,
potions, keyword tips and selection prompts, and the Spiral Abyss. The
Teyvat frame events and Ancient dialogue are prose and go with the story
pass. Read from `tools/player_text_census.py` against
`docs/current/text-conventions.md`.

## 1. Fixes (no number or rule changes)

1. **"Companion", not "Companion card"** (the Klee ruling, 2026-10-23,
   applied to the shared text): Nicole's Ladder of Divine Ascent (face and
   badge), the Study Buddy badge, and the prompts "Choose a Companion card
   to put into your Hand" and "Choose 2 Companion cards to add to your
   Hand" (which also takes the base's "add into").
2. **"Hand" capitalised:** the Sly prompt, "Choose a Skill in your hand."
3. **Grows "by":** Blasting Powder, "Every Bomb on ALL enemies grows 6."
   becomes "grows by 6."
4. **An article:** Amber's Explosive Puppet, "Enemy loses 3 Strength this
   turn." becomes "The enemy loses 3 Strength this turn."
5. **The base's shapes for ALL and for durations.**
   - Ayaka's Hyouka: "Deal 5 [8] Cryo damage to ALL enemies and apply 1
     Weak to each." becomes "Deal 5 [8] Cryo damage and apply 1 Weak to ALL
     enemies." (as `THUNDERCLAP`).
   - Gorou's Juuga: "For 3 [4] turns, deal 7 Geo damage to a random enemy at
     the end of your turn." becomes "For 3 [4] turns, at the end of your
     turn deal 7 Geo damage to a random enemy." (the conventions' repeating
     shape, as Kaeya's Glacial Waltz reads).
   - Raiden's Musou: "ALL enemies and you lose 3 Strength this turn."
     becomes "You and ALL enemies lose 3 Strength this turn."
6. **One spelling of an aura'd enemy:** Clorinde's Impale the Night and its
   Night Vigil badge, "enemies holding an aura", become "enemies with an
   aura", as Varka's and Yae's cards read. "Your later Attacks" becomes
   "This combat, your Attacks".
7. **"Attack", not "Attack card"**, as the base writes it: Kujou Sara's
   Crowfeather Cover and Bennett's Passion Overload, "Your next Attack card
   this turn", become "Your next Attack this turn" (faces and badges).
8. **No capitals for emphasis:** the Lightning Fang badge's "INSTEAD"
   becomes "instead".
9. **Lightfall Sword's badge:** "for each Attack you play first" becomes
   "for each Attack you play before then", as Eula's face reads.
10. **The keyword tips, in sentences** (rule 14).
    - Vulnerable: "An attack or card hit on it deals 50% more, a Skill's
      too. A potion's does not." becomes "Takes 50% more damage from cards,
      Skills included, but not from potions."
    - Weak: "Every hit the wearer lands, a Skill's too, deals 25% less."
      becomes "Deals 25% less damage with every hit, Skills included."
    - Strength: "It does not decay; it lasts for the rest of this fight."
      becomes "It lasts for the rest of this combat."
    - Contractions out: the Spend tip's "you can't", the boss Frozen
      preview's "can't be Frozen".
11. **The Spiral Abyss.**
    - Elemental Mark: "add a Burn to your discard pile" becomes "add a
      Burn into your Discard Pile" (the base's pile spelling).
    - Rally: "When an enemy dies" becomes "Whenever an enemy dies" (a
      repeating trigger).
    - Fatui Skirmishers: "3 Plated Armor (more in co-op)" becomes "3 Plated
      Armor, more in co-op".
    - Riptide: "up to 3 times per combat" becomes "up to 3 times each
      combat".
    - The Abyss Shield badge reads "A reaction or a None hit removes 3" in
      the census: its counter-element is blank before an element is set.
      The build checks whether a player can see it, and if so the badge
      prints "a reaction removes 3" until the element is known.

## 2. "Electro from Sara wins." on Bennett's face

Passion Overload ends with a rule for one pairing (Bennett and Kujou Sara
in the same turn). It is an edge case on a face (rule 15); the badge keeps
it, where it applies.

## 3. Two cards named Riptide

The Abyss Shadow "Riptide" (enemies gain Strength when they hurt you) shares
its name with Kokomi's Common Attack "Riptide". The Shadow is the one to
rename; it is about enemies growing angry, so "Undertow" keeps the water and
not the card.

## Picks

1. **Section 1's eleven fixes.** (a, default) build them all. (b) all but
   named ones.
2. **Bennett's Sara clause.** (a, default) it leaves the face and stays on
   the badge. (b) keep it on the face.
3. **The Shadow named Riptide.** (a, default) renamed "Undertow". (b) keep
   the name.
