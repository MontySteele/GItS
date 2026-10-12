# The run around the kits: a Spiral Abyss mode, and each character's story in the run (2026-10-12)

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

## 2. The Spiral Abyss mode (the run)

**Ruled 2026-10-12.** [USER]: "I know that StS2 does have a 'custom mode' screen ... Could we hijack the UI entirely and add a 4th option for Spiral Abyss runs? I'm thinking that the start of the run offers a choice of 3 boons and then grants enemies one of three power ups based on what you didn't take, per floor. stacking. This would be a new screen before each act's Ancients." Dropped: Corrosion ("leads to a very quick death basically always (you probably take more than 30 enemy hits to block in a floor)") and Halves ("in co-op, every enemy hits both players, so that idea wouldn't work").

**In Genshin:**
- The Spiral Abyss is floors of chambers. Each floor has a **Ley Line Disorder**, a rule on every fight there.
- Floors 9 to 12 also carry the **Blessing of the Abyssal Moon**, which changes each cycle.
- Abyss Mages carry elemental shields: plain hits chip them, and the right element breaks them fast.

**What the game's code already gives us** (decompiled StS2 0.111.0):
- **The fourth button.** The single-player menu builds its Standard, Daily and Custom buttons in `NSingleplayerSubmenu._Ready`. A Harmony patch adds "Spiral Abyss" beside them. The co-op host menu (`NMultiplayerHostSubmenu`) gets the same button.
- **The mode.** The game has only three run modes (`GameMode`: Standard, Daily, Custom). An Abyss run is therefore a Custom run that carries one modifier, `SpiralAbyss`, with that modifier preset and locked. Custom runs already work in co-op: the host lobby runs in `GameMode.Custom` (`NCustomRunScreen.InitializeMultiplayerAsHost`).
- **The rules engine.** A run modifier (`ModifierModel`) gets every combat hook and is saved with the run, along with its own properties. The base game's Murderous modifier gives every enemy 3 Strength this way. So the Blessings and power-ups held so far live in one saved modifier.
- **How other mods do it** (census of their public source, `mods-census/run-modifier-impl.md` in the session scratchpad):
  - A mod's modifier is registered with the game automatically, but it shows in the Custom list only if added there. BaseLib's `CustomModifierModel` does that for you; StsNemesisDraft does it with a single patch.
  - The co-op lobby already sends each player the chosen modifiers.
  - CuratedChallenges2 adds a main-menu button the same way we would: it copies the Custom button in `NSingleplayerSubmenu._Ready`.
  - Our button opens the Custom screen with the Abyss modifier already ticked (`NCustomRunScreen.SetTickedModifiers`), so no new lobby code is needed.
  - No mod we found has a per-act choice of Blessings.

**The structure:**
- **Before each act's Ancient** (Neow in act 1), a screen offers three **Blessings**. Each one shows its **Shadow**: the enemy power-up it brings if you pass it over.
- You take one Blessing. The enemies take one of the two passed Shadows at random; both are shown before you choose, so you know the risk.
- **Both stack:** by act 3 you hold three Blessings, and every enemy carries three Shadows.
- **The first build reuses the event screen** for these choices: three options, a portrait, and co-op sync that already works. A bespoke screen follows if that reads poorly.
- **In co-op,** the party agrees on one Blessing, and the enemies take one Shadow, as in solo.

**First-draft pools.** The Abyss paper fills these out, about eight of each. Every entry changes a decision for the base five and for the kits.

| Blessings (yours) | Shadows (the enemies') |
|---|---|
| **The act's Ley Line:** each enemy turn, every enemy without an aura takes the act's element, and an aura-wearer deals 1 less. | **The Clock:** from turn 4, every enemy gains 2 Strength at the start of each turn. |
| **Abyssal Moon:** every third card you play in a turn deals 4 damage to ALL enemies. | **Elemental shield** on elites: a shield counted in hits. Each hit removes 1, a reaction removes 3, and the counter element breaks all of it. |
| **Heal 4 HP** after each combat. | Enemies have **15% more HP**. |
| Your **first Attack** each combat is played twice. | Enemies start each combat with **Block equal to their Strength × 3**. |

- **Why a separate mode:** every kit is measured against the base five on the normal run (`EXPERIMENTS.md`), so the Abyss stays out of that run.
- **Later,** the Abyss could become act 3's alternate zone in the normal run, the way Underdocks is act 1's.
- **Not in the first build:** enemies putting an element on you. The mod has no player-side aura, and that would be the largest new system here.
- **Starting point:** the Shadow pool starts from the Genshin boss dossiers. This mode breaks the enemy-mechanics freeze of R272, sec.1.1, and it says so.
- **An idea for later, not a pick: a split run.** [USER]: "two distinct teams going up the same floor with some kinds of shared resources". It would double a run's length (about 1 hour solo and 2 hours in co-op today).

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

**Ruled 2026-10-12** (all of items 1 to 6, Klee first): "Otherwise agreed on adding more dialogue to flesh out each character further."

**All the words are ours.** I write every line in each character's voice, never quoting the game's dialogue. The first batch, Klee's introduction, greetings, act-1 event and lines, goes to you and your friend before the rest is written.

## 4. Cost

| Layer | Work |
|---|---|
| Introductions, combat lines, death and victory lines, pair lines (all four) | One build: text plus about six hooks |
| Ancient greetings | One build: the lookup patch plus 4 × 4 lines |
| Story events | One build per character: three event classes each, 12 in all |
| Constellation names | Text only; Klee's on her next branch |
| The Abyss mode | Its own paper (the two pools), then the menu button and modifier, the choice screen, and the pools, over two or three builds |

## Ruled

[USER], 2026-10-12: "I'm thinking that the co-op party has to agree on the blessing (just one blessing), and the enemy gets one Shadow selected at random." No picks remain. Next comes the Abyss paper (the two pools, about eight each), then the build: the menu button and modifier, the choice screen, the pools. The story work starts with Klee's first batch, for you and your friend to read.
