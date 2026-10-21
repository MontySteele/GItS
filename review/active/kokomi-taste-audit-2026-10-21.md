# Kokomi: taste audit and art pass (draft, 2026-10-21)

Her promise, as ruled 2026-10-18: "She makes room to prepare, protects the
preparation, and chooses the moment to take control." Three archetypes:
Grand Strategy (Plans fire in sequence), Read the Tide (commit an answer
before the enemy acts), The Shoal (many Stings).

Evidence: a census of all 75 solo pool cards against every base-five card
and every other kit and Companion card
(`scratchpad census (not in repo)`). It found 8 cards that are the
same as a base card apart from numbers and names, and 17 that use none of
Plan, Sting, Ward, Bake-Kurage, Companion or Mend.

## Part 1. Cards that are someone else's

**A. The Shoal is the Silent's Shivs.** Shoal Call is Blade Dance ("Add 3
Stings"), Kurage Bloom is Infinite Blades, Watchful Shoal is Accuracy, and
Kurage Barrage is Leading Strike. Stings already carry their own idea: a
Sting can be Planned, and its Plan line hits ALL. Nothing in the
archetype asks you to use it. The fix: move the payoff to the swarm on
the Bake-Kurage. Shoal Call would Plan its Stings instead of adding them
to Hand, and Kurage Bloom would Plan a Sting at the start of your turn.
Watchful Shoal and Kurage Barrage stay as they are. Watchful Shoal was
tuned this morning, and Kurage Barrage is fine filler once the payoffs
are hers.

**B. Ironclad's toolkit.**
- **Resolve of Watatsumi** is Inflame ("Gain 2 Strength"). It is also the
  Strength source behind the multi-hit AoE you flagged after your run.
  Replace it with a Grand Strategy power. Candidate: "At the start of your
  turn, look at the top 3 cards of your draw pile. You may Plan one."
- **Coral Crash** is Body Slam. Tidal Rebuke (Rare) already covers
  Block-to-damage, and so does Noelle. Replace it with a Common Read the
  Tide attack.
- **Watatsumi's Grace** keeps up to 10 Block, a Barricade-lite that is
  the same card as Thoma's Crimson Ooyoroi. Make it protect the
  preparation: "At the end of your turn, gain 3 Block for each Plan
  waiting."

**C. Varka's Weak and Vulnerable engine.**
- **Sea's Reproach** is Sadistic Nature, and close to Varka's Absolute
  Zero.
- **Suffocating Deep** doubles Weak and Vulnerable, the same move as
  Varka's Deep Freeze.

Read the Tide is about reading intent, not stacking debuffs. Proposed:
- Undertow: "if the enemy intends to attack" in place of "if it has a
  debuff". This is a text-level change.
- Suffocating Deep: drop the doubling and apply Weak only to enemies that
  intend to attack.
- Sea's Reproach: becomes a Rare Read the Tide power.

Drowning Pressure stays. It is the one debuff card, and it is fine.

**D. Klee's status trick.** Flotsam Surge is the same card as Klee's
Fish Blasting (AoE plus Dazed into your Discard). Self-inflicted statuses
are Klee's, so replace it with an Uncommon AoE that has a Plan line.
Tidecleanse fits her canon as a purifier and stays. Sea Glass Harvest
also stays: its Plan line makes it hers, and it was just tuned.

**E. Plain stat cards.**
- **Riptide Ruin** is Astral Pulse with bigger numbers. Proposed: it hits
  ALL once more for each Plan carried out this turn. That puts the
  Grand Strategy payoff on her biggest AoE.
- **Coral Bulwark** ("Gain 8 Block") stays as Common filler. Every kit
  has one.

**Left alone, and clearly hers:** Tide Wall, Change of Plans, Evening
Watch, Tidal Surge, Brine Spray, Unbroken Tide, Turnabout, Kelp Wall,
Masterstroke, Undercurrent Snare, Grand Design, Battle Formation,
Following Current, Kurage Vanguard, Breakwater, Tideturn and Press the
Advantage. Some of these resemble other cards only in mechanism; for
example, Nereid's Ascension is like Echo Form. Grand Strategist and All
Streams Flow are the mod's shared element layer, not a borrowing.

**Cost:** about 10 cards change, so the Balance suite runs again after
the build. Numbers are set at build time and tuned in that suite.

## Part 2. Art and animation gap (`scratchpad census (not in repo)`)

What Klee, Furina and Varka have that she lacks:
- **A signature clip.** Klee has Set off and Jumpy Dumpty, Furina has
  Rejoice, Varka has Ascension. Kokomi plays her generic cast clip for
  everything.
- **Effects on her body beyond the attack.** Her only effect is a water
  jet on the attack.
- **A custom effect for her mechanic.** A Plan carried out is a tween
  lunge by a static 64x128 Bake-Kurage sprite, then the base game's speech
  bubble.
- **A counter beside the Energy orb.** Each of the others has one.
- **A close-up still on the select screen.** Hers is missing
  (`select_closeup_static.png`).

Proposed, cheapest first:
1. **Select close-up still.** Hygiene; I just make it.
2. **Plan carry-out effect (code only).** The Plan's thumbnail flies from
   the strip into the Bake-Kurage, which pulses. Then a water bolt arcs to
   the target for damage, or a pearl-shell flash lands on Kokomi for
   Block. A small caption replaces the speech bubble.
3. **The visible swarm (code only).** Each Planned Sting or Ward shows as
   a small jellyfish orbiting the Bake-Kurage: coral-pink for a Sting,
   pale blue for a Ward. On carry-out they dart at the enemies. This is
   the visual half of Part 1A.
4. **Bake-Kurage frame sheet (Blender, after seats).** It replaces the
   tweened sprite with idle drift, tentacle sway, a squash-and-stretch
   attack and a glow that grows with Plans waiting.
5. **Signature clip, Nereid's Ascension (Blender, after seats).** About
   26 frames, as long as Varka's. She raises the Bake-Kurage, and a ring
   of water rises around her with jellyfish lights. It also plays for
   Kurage's Oath carried out.
6. **Cast clip effects.** A Hydro sigil ring on the cast clip, and a
   pearl flash when the Casket pays.

## Picks

1. **The Shoal moves to the Kurage** (A): (a, default) Shoal Call and
   Kurage Bloom Plan their Stings. (b) Leave the Shoal as Shiv-like.
2. **Ironclad borrowings** (B): (a, default) replace Resolve of Watatsumi
   and Coral Crash, and rework Watatsumi's Grace as above. (b) Replace
   Resolve of Watatsumi only.
3. **Debuffs to intent** (C): (a, default) Undertow, Suffocating Deep and
   Sea's Reproach read intent. (b) Leave them.
4. **Flotsam Surge and Riptide Ruin** (D, E): (a, default) replace Flotsam
   Surge, and make Riptide Ruin scale with Plans carried out. (b) Leave
   both.
5. **Art** (Part 2): (a, default) build items 1-3 and 6 now, then 4-5 with
   Blender once suite 3 finishes. (b) Code items only. (c) A different
   signature-clip idea from you.

## Ruled 2026-10-21: all five (a)

[USER]: "That's a lot of card changes, but we can do that and rerun the
balance suite to see how it feels." Then: "Agreed on all 5 defaults."

The cards as built (same cost, type and rarity as the row they replace;
upgrades in brackets):

1. **Shoal Call** (Common Skill, 1, Exhaust): "Plan 3 [4] Stings."
2. **Kurage Bloom** (Uncommon Power, 1; upgrade Innate, as now): "At the end
   of your turn, Plan a Sting."
3. **Resolve of Watatsumi** (Uncommon Power, 1): "When a Plan is carried
   out, it deals 2 [3] additional damage and gains 2 [3] additional Block."
   (Per damage hit and per Block line of the Plan; Stings and Wards
   included.)
4. **Coral Crash** (Common Attack, 1): "Deal 8 [11] Hydro damage. Plan: Deal
   8 [11] Hydro damage to each enemy that intends to attack." (Intent read
   when carried out, as Tide Wall does.)
5. **Watatsumi's Grace** (Rare Power, 1): "At the end of your turn, gain 3
   [4] Block for each Plan waiting."
6. **Sea's Reproach** (Rare Power, 1): "At the start of your turn, apply 1
   Weak to each enemy that intends to attack [and deal 5 damage to it]."
   (After this turn's Plans are carried out, so intents are current.)
7. **Suffocating Deep** (Rare Attack, 2, Exhaust): "Deal 10 [13] Hydro
   damage to ALL enemies. Apply 2 Weak and 2 Vulnerable to each enemy that
   intends to attack."
8. **Undertow** (Common Attack, 1): "Deal 7 [10] Hydro damage. If the enemy
   intends to attack, deal 10 [13] instead."
9. **Flotsam Surge** (Uncommon Attack, 1): "Deal 9 [12] Hydro damage to ALL
   enemies. Plan: Deal 9 [12] Hydro damage to ALL enemies and Plan a
   Sting." No Dazed.
10. **Riptide Ruin** (Rare Attack, 2): "Deal 9 [12] Hydro damage to ALL
    enemies, once more for each Plan carried out this turn. Stings and Wards
    don't count."

Left alone: Watchful Shoal, Kurage Barrage, Drowning Pressure, Coral
Bulwark, Tidecleanse, Sea Glass Harvest. Numbers are first guesses; the
Balance suite reruns on the same five seeds after the deploy.

Art (pick 5 (a)): code now (select close-up still if it needs no render,
Plan carry-out effect, the visible swarm, Hydro cast sigil and Casket pearl
flash); the Bake-Kurage frame sheet and the Nereid's Ascension clip render
in Blender after suite 3.

## Built 2026-10-21

The ten cards are built in the mod and the sim
(`docs/notes/prototype-surface-provenance.md`, "Kokomi taste audit,
2026-10-21"). One wording differs from the list above: Sea's Reproach's
upgrade prints "and deal 5 damage", because "and deal 5 damage to it" is
over the text lint's 20-character ceiling for an upgrade clause. "Plan a
Sting" writes the Sting's own Plan line and pays the Casket once per Sting,
inside a carry-out too (Flotsam Surge). Next: the Balance suite on the same
five seeds after the deploy. The art items are not in this build.
