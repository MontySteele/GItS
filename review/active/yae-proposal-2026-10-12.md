# Yae Miko: the Shrine and the Publishing House (character five proposal)

**Ask ([USER], 2026-10-12):** "Can you kick off a research agent and see if we can come up with a genuinely engaging, well-rounded Yae proposal for character #5? Something that taps yet-unused design space."
- The co-op tester's favorite character is Defect, so Yae should scratch that itch: a board that works for you every turn.
- "I do want to avoid just ripping off Defect."
- Our September note still holds: "she has to avoid being another turret spammer."

**Stage:** Paper, a direction to rule on. Numbers below are placeholders that show the shape. Building waits on Varka finishing, as you said. The research packet is `scratchpad/yae-research/packet.md` (gitignored); every claim below is in it.

## 1. What Defect players like, and what is his alone

**What makes Defect fun:**
- a machine that keeps paying every turn;
- choices about when to cash it in;
- a scaling number;
- several ways to build it.

**What is Defect-signature**, read from the game's code (`Defect.cs`, `OrbCmd.cs`):
- the ordered orb queue;
- Channel and Evoke, where pushing an orb out pays it;
- five orb types;
- Focus;
- "cast twice" cards.

Yae should have the first list and none of the second.

## 2. The unused space

The packet's census covers the five base characters and our four kits (section 4.3). Three gaps stand out:
- **No one edits their deck as a kit identity.** In the base game only one card, Silent's Blade of Ink, gives a card an Enchantment. Enchantments otherwise come from events and relics. The engine already does the hard part:
  - `CardCmd.Enchant` exists;
  - an Enchantment is saved on the card and lasts the run (`SerializableCard`);
  - a card holds one Enchantment at a time.
- **Nobody turns ordinary cards into new ones over a run.** Base characters upgrade or transform in combat (about 30 cards), and that resets every fight.
- **No one manipulates intents.** That's a gap, but hard control is payoff-tier by `LAW.md`, so it stays a flavor at most (see section 6).

The lore fits the first gap: Yae is the editor-in-chief of a light-novel house. She tells an author his manuscript is "not free enough", runs a "Reborn as Guuji Yae" contest, and enjoys "frazzled authors scraping the bottom of their barrel." **An editor who revises her own deck over the run is new to Slay the Spire, and it is her.**

## 3. The promise

Yae runs a shrine and a publishing house.
- **The shrine** is her turret: up to three Sesshou Sakura that strike every turn and grow stronger together.
- **The publishing house** is her deck: she annotates her cards, and the best annotations are kept for the rest of the run.
- They meet in one annotation, **Sakura Seal**: a card carrying it plants a Sakura when played. Over a run, Yae writes her turret into her deck.

## 4. The two rules

**Rule 1, Sesshou Sakura.**
- Yae plants Sakura beside herself, up to 3.
- At the end of her turn, each Sakura strikes a random enemy for Electro damage. Its damage rises with the number of Sakura out, because in Genshin nearby Sakura level each other.
- Placeholder: 2 each with one Sakura out, 3 each with two, 4 each with three (2, 6, 12 a turn).
- A Sakura lasts 3 of her turns. Planting a fourth replaces the oldest.
- **Tenko cards** make every Sakura strike now and reset their timers. This follows Genshin's 6.7 change, which stopped her Burst from consuming the Sakura. Her payoff keeps the board instead of spending it.

**How this differs from Defect:**
- there is one object, not five;
- there's no queue and no Evoke;
- the scaling is the count of Sakura, which is capped, not a Focus number;
- the decision is keeping three alive and timing the Tenko, not choosing what to push out.

**How it differs from Klee's Bombs:**
- Bombs sit on enemies, grow on their own and go off only when she sets them off;
- Sakura sit on Yae's side, fire every turn by themselves and expire.

**Rule 2, Annotations.**
- Some of her cards say **"Edit a card in your hand"**. That card gains one Annotation for the rest of the combat, overwriting any it had.
- The Annotations are Yae's own Enchantments, with lore names. Placeholders:
  - Red Ink: +3 damage or Block;
  - Footnote: draw 1 when played;
  - Deadline Extension: Retain;
  - Fox Fire: applies Electro;
  - Sakura Seal: plants a Sakura.
- **Publishing makes an Annotation permanent.** Her starting relic adds a rest-site choice, "Publish": make one card's Annotation permanent, in place of Rest or Smith. A few Rares also Publish in combat.
- This is the run-long arc: Yae can't hold more permanent Annotations than she has deck cards, and every Publish costs a rest. (Whether the mod can add a rest-site choice is to be checked; base relics such as Shovel add one.)

**Why two rules aren't too many:**
- the turret half plays like Defect from the first fight;
- the editing half adds a choice at each campfire;
- Sakura Seal ties them together.

Kokomi already carries two (Plans and the jellyfish).

## 5. Archetypes and fit

**Three ways to build Yae**, like Defect's several:
- **The Shrine:** Sakura count, Tenko timing, timer refreshes.
- **The Publishing House:** "for each Annotated card" payoffs, such as a "Bestseller" Attack that grows with them.
- **Kitsune mischief:** Weak, card draw and tricks.

**Electro and partners.**
- Sakura strikes apply Electro to random enemies every turn. That is her Genshin role, "off-field Electro marks".
- In co-op she feeds her partner's reactions: Overload with Klee, Electro-Charged with Kokomi or Furina, and Varka's switching.
- The 6.7 rework keys her payoffs to reactions others trigger. A Power in her pool, "Edict of Cleansing", can make the next Sakura strike hit harder whenever an Electro reaction happens.

**Co-op card:** "Editor's Note: Edit a card in an ally's hand." The engine can already hand cards between players.

**Lore through the run**, for the tester who doesn't play Genshin:
- greeting and story lines in her voice: "Alright, amuse me", "Not the sharpest tengu in the forest", "So much for 'eternity'";
- Ei, Kitsune Saiguu and the Fire-Soothing Festival budget she "borrowed";
- the Ancient lines can play the editor reading your "manuscript".

**Her starting deck follows the house rule:** base Strike ×4 and Defend ×4, plus two teaching cards:
- Yakan Evocation: plant a Sakura;
- an Edit card.

Her existing Companion card (Sesshou Sakura, Inazuma Uncommon) would become hers. By the ruling on character-only cards, it moves into her pool.

## 6. What this does not do

- **No new global reaction.**
  - Genshin's Stellar-Conduct (Cryo and Electro) needs a "Linchpin" character, and none of our kits is Cryo.
  - Porting it would change Superconduct for everyone.
  - Pick 3 asks.
- **No intent control.** A trick that redirects an attack into a Sakura would make Sakura need HP, like Furina's guests and Osty. It's left out.
- **No cards past 78.** The pool target holds.

## For [USER]

1. **Direction.**
   - **(a) Default:** the Shrine and the Publishing House, as above. A Defect-like turret, plus deck editing nobody has done.
   - (b) The Shrine alone, a pure turret kit with more Sakura variety. Closer to Defect, less new.
   - (c) The Publishing House alone, no turret. Most new, least Defect-like.
2. **How long an Annotation lasts.**
   - **(a) Default:** the combat, unless Published at a rest site (her relic) or by a few Rares.
   - (b) Every Edit lasts the run. Bold, and it snowballs by act 2.
   - (c) Always the combat; no Publishing.
3. **Stellar-Conduct.**
   - **(a) Default:** no new reaction; her payoffs key off Electro reactions others trigger, as in 6.7.
   - (b) Add Stellar-Conduct as a Yae-only upgrade of Superconduct.
4. **Sakura timers.**
   - **(a) Default:** 3 turns, with Tenko refreshing them (Genshin's rhythm, and a reason to recast).
   - (b) Permanent, like orbs: simpler, closer to Defect.
