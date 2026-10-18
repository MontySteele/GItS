# The Spiral Abyss mode: Blessings, Shadows and the build (2026-10-12)

**Why.** The run-frame paper is ruled (`run-frame-and-lore-2026-10-12.md`):
- a fourth main-menu mode;
- before each act's Ancient, you take one of three Blessings and the enemies take one of the two passed Shadows at random;
- both stack, and a co-op party agrees on one Blessing.

This paper fills the two pools and sets the build. It has no picks. Tell me if any entry should go, and it is swapped before the build lands.

## 1. The rules for both pools

- **Every entry changes a decision** for the base five and for at least two of our kits.
- **No entry repeats in a run.** Three acts mean three Blessings and three Shadows at most.
- **Numbers are first guesses.** The mode is not measured against the base five (`EXPERIMENTS.md` binds the normal run), so it is tuned by play.
- **Genshin first:** each entry is named for, and shaped by, a real Abyss rule or boss in `docs/current/dossiers/bosses/dossiers.md`.

## 2. Blessings (eight)

| Blessing | Text | Where it comes from |
|---|---|---|
| **The Ley Line** | Each enemy turn, every enemy without an aura takes this act's element. An enemy wearing an aura deals 1 less damage. | Ley Line Disorders. For the base five it is a defence; for the kits it is a reaction target every turn. |
| **Abyssal Moon** | Every third card you play in a turn deals 4 damage to ALL enemies. | The Abyssal Moon's shockwaves. It rewards cheap cards: Stings, Sparks, Shivs. |
| **Moonlit Rest** | Heal 2 HP at the end of each combat. | Abyss healing between chambers. Healing is rare outside Ironclad, which makes this the safe pick. |
| **First Strike** | Your first Attack each combat is played twice. | Burst openers. |
| **Elemental Burst** | Whenever you play a Power, deal 6 damage to ALL enemies. | Burst blessings. Powers stop being a turn's dead tempo. |
| **Resonance** | On turn 1 of each combat, gain 1 Energy and draw 1 card. | Elemental Resonance. It answers the "starter hand with no decision" opening our seats keep reporting. |
| **Jade Shield** | Start each combat with 8 Block. | Geo shields. Renamed from Crystallize: the name collided with the Crystallize reaction. |
| **Fateful Fortune** | Gain 12 Max HP. | A plain pick, for a party that is losing. |

2026-10-18: Moonlit Rest 4 / 6 / 8 -> 2 / 3 / 5 by act taken, see review/records/spiral-abyss-round-3-2026-10-18.md.

## 3. Shadows (eight)

| Shadow | Text | Where it comes from |
|---|---|---|
| **The Clock** | From turn 5, every enemy gains 2 Strength at the start of its turn. | Abyss stars for clear time. Turtling loses. |
| **Abyss Mage Shield** | Elites enter combat with a shield of this act's element, 8 hits deep, that stops all damage. Each hit removes 1, a reaction removes 3, and the counter element breaks it. | Abyss Mages. The base five answer with multi-hit; the kits answer with reactions. |
| **Sheer Cold** | If you end your turn with no Block, lose 3 HP. | La Signora's Sheer Cold. Klee and Furina's Drain turns pay for it. |
| **Elemental Mark** | Whenever an enemy attack deals you unblocked damage, add a Burn to your discard pile. | Azhdaha's mark: a Shield stops it entirely. Block decides whether it lands. |
| **Abyss Herald** | Enemies have 15% more HP. | Abyss enemy levels. |
| **Rally** | When an enemy dies, every other enemy gains 2 Strength. | The Abyss Lector's rally. Kill order matters. |
| **Riptide** | Whenever an enemy attack deals you unblocked damage, that enemy gains 1 Strength. | Childe's Riptide: a mark that makes his next blows harder. Failing to Block feeds the enemy. |
| **Fatui Skirmishers** | Elites and bosses enter combat with 3 Plated Armor. | Fatui shields. Multi-hit and Block strip pay. |

Ruled 2026-10-12, [USER]: "Riptide sounds insanely dangerous for enemies that open with a single very high hit as a block check; the rest all look good." Riptide was rewritten.

**Shadows do not grow by act** (ruled 2026-10-12). Each act adds one Shadow at its printed strength; three stacked by act 3 are the ramp. [USER], on that pick: "Let's go with a) and see how that plays". For comparison, the ARAM: Mayhem mod gives enemies 1, 2 and 3 runes by act, scaled by act (census `mods-census/aram-mayhem.md` in the session scratchpad).

## 4. The build

- **The menu button.** A patch on `NSingleplayerSubmenu._Ready` and `NMultiplayerHostSubmenu` copies the Custom button as "Spiral Abyss". The button opens the ordinary character select (character and ascension) with a "Spiral Abyss" banner, and the run carries the Abyss modifier as a Standard run ([USER], 2026-10-12: "I'd prefer it have the normal screen where you select the character and ascension rather than the custom mode screen"). Co-op comes free, because the lobby already sends its modifier list to each player on joining and at the run's start.
- **The modifier.** `SpiralAbyss`, a run modifier saved with the run. It holds the Blessings and Shadows taken so far and applies them through combat hooks. It is registered by BaseLib's `CustomModifierModel`, or by one patch if BaseLib's version lacks it.
- **The choice screen.**
  - Before each act's Ancient (Neow in act 1), an event with three options. Each option shows its Blessing and the Shadow it brings if passed.
  - The enemies' Shadow is rolled from the two passed, on the run's seeded RNG, so a reload gives the same roll.
  - In co-op it is a shared event, so the party agrees on one option the way the game's shared events already work.
- **Art:** the Blessing and Shadow icons reuse official Abyss and Ley Line icons, under the art ruling.
- **Tests:**
  - Each Blessing and Shadow once.
  - Stacking across three acts.
  - Save and reload mid-act.
  - Then a co-op launch on two lanes.
- **Seats:** one solo and one co-op seat on the mode once it is built. Their record says which entries changed decisions and which were never chosen.
