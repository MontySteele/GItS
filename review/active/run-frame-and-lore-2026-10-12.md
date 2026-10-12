# The run around the kits: a Spiral Abyss layer, and each character's story in the run (2026-10-12)

**Why.** [USER], after a debrief with the friend who co-op tests:

> look at what other Slay the Spire mods do to try and expand the wealth of our design space. This could include supporting some add-on ideas that modify the run rather than the characters (which would tie in nicely with our older ideas to make the run mimic a Spiral Abyss run) ... I really don't want to just steal someone else's homework - every character should feel 'ours'

> Since he doesn't play Genshin, he doesn't feel as attached to the lore of a given character, and it would help him to feel more immersed if the character's own lore came through cleaner in the run somehow, whether through dialogue, events, in-combat lines, etc.

> I think that we're getting close to the point where looking into some non-character changes would make sense, so perhaps we tie 2) into 1)

**This reopens a hold.** `STATE.md` parks the Teyvat run frame: it "returns only as elemental enemies ... when the kits are done". The new fact is your "getting close to the point".

**Sources:**
- A census of the StS1 and StS2 modding scene, in the session scratchpad (`mods-census/sts-mods-census.md`). Steam Workshop and Reddit refused most fetches; it leans on wikis, GitHub and sts2.gg and marks what it could not check.
- A Fable review of this paper's first draft (`mods-census/fable-review-runframe.md`). It corrected the Genshin facts, replaced both example Disorders and reordered the lore section.
- The ruled frame (`review/ruled/teyvat-run-frame-2026-09-14.md`) and the Genshin boss dossiers (`docs/current/dossiers/bosses/dossiers.md`).

## 1. What the mod scene shows

- **Downfall** makes its characters known through its run.
  - You descend the Spire as one of its bosses, and the heroes are the bosses you fight.
  - Souls replace gold, and familiar events are rewritten from the villain's side.
  - Its villain content also enters the normal mode as events, relics and curses. That is a model for add-ons that don't need a separate mode.
- **Smaller mods give a character an event or curse of their own** (Packmaster). New StS2 Ancients come with their own dialogue, offers and relic paths (Better Slay the Spire 2), and new bosses come with their own intents and music (Library of Ruina).
- **Kinds of mechanic the census found in mods and rarely in the base games:**
  - Hand position (Hermit).
  - Fusing cards in combat (Automaton).
  - A side deck (Collector).
  - Several allies with their own HP (Gremlins).
  - Socketing cards at a campfire (Guardian).
  - Fading memories (Jorbs' Wanderer).
  - Death and a second form (The Wanderer, StS2).

  Our four already own some of this ground: Furina's guests are allies, Kokomi's Plans are delayed cards, Varka's element is a stance, and Klee's Bombs sit on the field.
- **Other Genshin character mods exist for StS2:** Neuvillette, Ganyu, Layla, and a "GenshinSpire2" pack ([Neuvillette](https://www.nexusmods.com/slaythespire2/mods/1319), [Ganyu](https://www.nexusmods.com/slaythespire2/mods/1102)). Neuvillette's is described as built on "HP fluctuation", which is close to Furina's ground. That is a reason to keep reading other mods for their run-level ideas and not their character cards.
- **No mod we saw gives enemies an element.** That is the one thing a Genshin mod can own.

**Why our first frame was flat.** The frame ruled on 2026-09-14 changed names, art, music and event words, and froze every enemy mechanic, so nothing in it changed a decision.

## 2. The Spiral Abyss layer (the run)

**In Genshin:**
- The Spiral Abyss is floors of chambers. Each floor has a **Ley Line Disorder**, a rule on every fight there.
- Floors 9 to 12 also carry the **Blessing of the Abyssal Moon**, which changes each cycle and is not chosen.
- The pressures are a clock (stars for clear time) and, on floors 9 to 12, **two teams taking alternate halves**. That is a natural co-op hook.
- Abyss Mages carry elemental shields: plain hits chip them, and the right element breaks them fast.

**For us,** five Disorders. Each changes a decision for the base five and all four kits:

| Disorder | Rule | What it changes |
|---|---|---|
| **The Clock** | From turn 4, every enemy gains 2 Strength at the start of each turn. | Speed beats turtling. Klee's tempo pays; Kokomi's one-turn Plan delay is taxed; Furina Drains early and races; Varka casts Four Winds' Ascension sooner. |
| **Corrosion** | The first 3 damage of every enemy attack ignores Block. | HP becomes the resource. Furina's Drain buffer is contested and Block is worth less; drafting shifts to kill speed. |
| **The act's Ley Line** | Each enemy turn, every enemy without an aura takes the act's element. An enemy wearing an aura deals 1 less. | The base five get a damage cut. Every kit gets a reaction target each turn: Klee's Pyro, Varka's Swirl, Kokomi's Hydro, Furina's guests. |
| **Elemental shield** (on the act's elites) | A shield counted in hits. Each hit removes 1, any reaction 3, and the counter element breaks all of it. | The base five answer with multi-hit cards; the kits answer with reactions. This is a Genshin shield, not Plated Armor. |
| **Halves** (co-op) | Each enemy attacks the player who hit it last. | Who draws aggro, the thing a co-op pair talks about. |

- **How you enter it:** a Neow boon, "Enter the Abyss". That needs no new screen, and in co-op it is a shared run setting. The frame's code is behind a compile flag today (`Teyvat/TeyvatFrame.cs`), so a run-level switch is new work.
- **Why opt-in first:** every kit is measured against the base five on the normal run (`EXPERIMENTS.md`).
- **Where it can go later:**
  - the Disorders move onto the normal run at an ascension;
  - or the Abyss becomes act 3's alternate zone, the way Underdocks is act 1's (the old frame's spike was built for that fork).
- **Not in the first build:** enemies putting an element on you. The mod has no player-side aura; that would be the largest new system here, so it waits.
- **Starting point:** the Disorder paper starts from the Genshin boss dossiers, which already describe Andrius and others in StS terms. This layer breaks the enemy-mechanics freeze of R272, sec.1.1, and it says so.

## 3. Each character's story in the run

Ordered by what your friend meets first in a run:

1. **A two-line introduction** at character select or in Neow's greeting: who she is, and why she is climbing.
2. **The Ancients greet her.**
   - **What:** one line per character from Neow and each act's Ancient.
   - **The work:** StS2 keys its Ancient lines to the base five, and modded characters get the generic text (`tools/gen_teyvat_ancients.py`), so this needs a lookup patch, not just text.
3. **A story event each act:** three per character, a short arc from her own story, each with a choice in her mechanic.
   - Klee: the fish-blasting and her confinement, Jean's letter, then the Knights.
   - Kokomi: the war council, the peace talks, then the shrine.
   - Furina: the prophecy, the trial, then the curtain call.
   - Varka: a letter from the expedition, the Wolf of the North (Andrius), then a return to Mondstadt. The last beat is our invention.
4. **Lines in combat.**
   - **When:** the start of a boss fight, low HP, a boss kill, and each kit's signature play (Klee's biggest Bomb, Furina's full Spend, Kokomi's Nereid's Ascension turn, Varka's Four Winds' Ascension).
   - **How:** the game already draws them; Kokomi's jellyfish uses `NSpeechBubbleVfx` (`Vfx/Prototype/KurageBeat.cs`).
5. **A death line and a victory line** per character. The end of a run is a moment.
6. **Co-op pair lines:** one line per pair of characters at each boss, the one channel both players see. With four characters that is six pairs.
7. **After each kit's Balance:** a boss of her own story (Varka's Andrius is already in the dossiers). It is enemy code, so it waits for the freeze to lift.

**Constellations: naming now, mechanics later.** Two channels already carry a character's run-level upgrades:
- the starter relic that Touch of Orobas upgrades (`Relics/UpgradedStarterRelics.cs`);
- each kit's two Ancient cards (Varka has none yet).

My plan is to name them after her constellations, as card names already use the game's names; the prose stays ours. Klee's waits for her next branch, because she is at Balance. Six measured relic upgrades per character would be four relic trees and is not proposed.

**All the words are ours.** I write every line in each character's voice, never quoting the game's dialogue. The first batch, Klee's introduction, greetings, act-1 event and lines, goes to you and your friend before the rest is written.

## 4. Cost

| Layer | Work |
|---|---|
| Introductions, combat lines, death and victory lines, pair lines (all four) | One build: text plus about six hooks |
| Ancient greetings | One build: the lookup patch plus 4 × 4 lines |
| Story events | One build per character: three event classes each, 12 in all |
| Constellation names | Text only; Klee's on her next branch |
| The Abyss layer | Its own paper, then the toggle, the five Disorders and the shields over two or three builds |

## For [USER]

1. **The run layer.**
   - **(a) Default:** lift the hold now. The Abyss is an opt-in mode entered through a Neow boon: five Disorders, hit-counted elemental shields on elites, and Halves in co-op. Its own paper comes next.
   - (b) The Abyss as act 3's alternate zone in the normal run.
   - (c) Keep the hold: elemental enemies only, when the kits are done.
2. **Her story in the run.**
   - **(a) Default:** all of section 3's items 1 to 6, Klee first, her batch read by you and your friend before the rest.
   - (b) Introductions and combat lines only, for now.
