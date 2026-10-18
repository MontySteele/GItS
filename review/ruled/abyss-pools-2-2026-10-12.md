# Spiral Abyss pools, round 2: "This act" next to "Whole run", 2026-10-12

**Ruled 2026-10-12: pick 1 (a) and pick 2 (a), with two changes. Built.**

[USER]: "Moonlit Spring sounds insanely strong even as a 1 act Blessing. I'd say bring it down to 8 to be safe (double the per-run amount) and don't retune the existing ones; nobody's done full runs on the spiral abyss yet, so there's nothing to tune against.
Frenzy sounds like +1 strength for an act which might be too low."

[USER], on Frenzy's wording: "Why the extra words? Just give enemies 2 Strength."

So Moonlit Spring heals 8, not 10. Frenzy gives enemies 2 Strength at the start of each combat. There are no retunes. The tables below are what was built.

[USER]: "I'm seeing some room here for 'Whole run' vs 'This floor' effects, and we should see if we can broaden the pool a little."

**Evidence.** The packet is `scratchpad/abyss-pools/packet.md` (gitignored). It covers:
- every shipped entry, with its code;
- the 4 Abyss runs played so far;
- the ARAM and run-frame censuses;
- 24 real Spiral Abyss effects with sources.

The play sample is small: about 7 Blessing picks.

## How Genshin splits it

The real Abyss has two layers:
- **The Blessing of the Abyssal Moon** lasts the whole cycle, on every floor. It is usually a "shockwave" on some action, such as reactions dealing extra True damage once every few seconds.
- **Ley Line Disorders** last one floor, or one half of a floor late on. They are big and narrow: "Overloaded DMG +200%", "Cryo DMG +75% and Frozen lasts much longer", "while above 50% HP, ATK +25%".

In none of the 24 examples does an effect last several floors without lasting the whole cycle. So two durations are enough, and our "floor" is an act: **"Whole run"** and **"This act"**.

## Where our pools stand

- **8 Blessings and 8 Shadows, every one "Whole run".** The card tag is a fixed string (`AbyssOverlayView.cs:298`).
- **Taken in play:**
  - Fateful Fortune (12 Max HP) in 3 of 4 runs;
  - The Ley Line twice;
  - First Strike and Moonlit Rest once each;
  - Abyssal Moon, Elemental Burst, Resonance and Jade Shield never.
- **Shadows applied:** Riptide, Fatui Skirmishers, Abyss Herald, Elemental Mark and Sheer Cold.
  - **Riptide** is the one that bit: a Kin Priest went from 1 to 8 Strength by turn 7. You'd called it "insanely dangerous for enemies that open with a single very high hit".
  - The Clock, Mage Shield and Rally were never applied.
- **The engine is ready.** Each pick already records its act, and the game has an act-change hook the mod doesn't use yet (`AfterActEntered`). Two things remain: "is this Blessing live" must check the act, and the strip must show the duration.

## The proposal

**The rule.** A "This act" entry is about twice as strong as a "Whole run" one and ends when the act ends. Each page shows at least one of each, so every pick is a real choice: a big push for this act, or a smaller edge for the rest of the run. A passed "This act" entry may come back in a later act.

**New Blessings, This act** (Genshin's Ley Line Disorders):

| Name | Text |
|---|---|
| **Overflow** | This act, Elemental Reactions deal double damage. |
| **Vigor of the Abyss** | This act, while you are above half HP, your Attacks deal 3 additional damage. |
| **Moonlit Spring** | This act, heal 8 HP at the end of each combat. |
| **Battle Rhythm** | This act, start each combat with 1 Strength and 1 Dexterity. |

Vigor of the Abyss and Battle Rhythm, 2026-10-18: numbers by act, see review/active/abyss-act-scaling-2026-10-18.md.

**New Blessings, Whole run** (Genshin's Abyssal Moon shockwaves):

| Name | Text |
|---|---|
| **Wavering Moon** | Whenever you trigger an Elemental Reaction, deal 3 damage to ALL enemies. |
| **Starfell Draft** | Card rewards show 1 additional card. |

Wavering Moon, 2026-10-18: numbers by act, see review/active/abyss-act-scaling-2026-10-18.md.

**No retunes.** [USER]: "don't retune the existing ones; nobody's done full runs on the spiral abyss yet, so there's nothing to tune against." Abyssal Moon stays at 4, Jade Shield at 8 Block, Moonlit Rest at 4 HP. Moonlit Spring is Moonlit Rest's This-act sibling at 8, "double the per-run amount", and the two stack.

**New Shadows, This act:**

| Name | Text |
|---|---|
| **Thorny Ground** | This act, enemies start each combat with 2 Thorns. |
| **Bulwark** | This act, at the start of your turn, each enemy gains 4 Block. |
| **Frenzy** | This act, enemies start each combat with 2 Strength. |

Thorny Ground, Bulwark and Frenzy, 2026-10-18: numbers by act, see review/active/abyss-act-scaling-2026-10-18.md.

Bulwark amended 2026-10-17 (was "enemies start each combat with 6 Block", which cleared at the enemies' first turn). The user: "Bulwark looks pretty weak"; "4 is fine for now, but we probably need to make per-act effects scale by act."

Frenzy was "enemy Attacks deal 1 additional damage". [USER]: "Frenzy sounds like +1 strength for an act which might be too low", then "Why the extra words? Just give enemies 2 Strength."

**Shadows moving to This act:**
- **Riptide** becomes "This act". It keeps its bite where it's most dangerous, early, and doesn't snowball for the rest of the run. Its text now says so:

| Name | Text |
|---|---|
| **Riptide** | This act, whenever an enemy attack deals you unblocked damage, that enemy gains 1 Strength. |

Riptide, 2026-10-18: numbers by act, see review/active/abyss-act-scaling-2026-10-18.md (it is now once per turn per enemy, up to 3 / 4 / 5 times per combat).

**New Shadow, Whole run:**

| Name | Text |
|---|---|
| **Withering** | You start each combat with 1 Weak. |

**Totals:**
- Blessings go from 8 to 14, 4 of them This act.
- Shadows go from 8 to 12, 4 of them This act.
- 14 Blessings is close to the earlier plan of about 16 each. Shadows stay smaller, since they are punishments.

**The screen:**
- Each card's tag reads "Whole run" or "This act".
- The top-right strip shows the duration. A This-act entry fades out when the act ends.
- The Shadow badges on enemies drop off with it.

**Not proposed:** Shadows that scale by act. You ruled flat Shadows earlier ("Let's go with a) and see how that plays"), and the This-act split gives the same early-or-late texture without scaling.

## How it was built

- **Durations.** Each entry's duration is fixed by its name (`AbyssDurations` in `klee-mod/KleeCode/Abyss/AbyssEntries.cs`). The run already saved the act of each pick, so nothing new is saved. A This act entry is in force only in the act it was taken in. A run continued mid-act keeps it; one continued after the act has ended has lost it.
- **The page.** Each page shows at least one Whole run and one This act Blessing while the pool still holds both (`AbyssDraft.MixedPage`). A passed entry may come back in a later act. A taken one never does.
- **The screen.** Each card's tag reads "Whole run" or "This act" (a blue chip for This act). The top-right strip lists only what is in force. A This act icon carries a "This act" caption, and every icon's hover names its duration.
- **At act end.** An expired Blessing's relic is removed, the Abyss Shadows relic's list is redrawn, and enemies stop wearing the expired Shadow's badge.
- **Co-op.** Unchanged: the party agrees on one Blessing, and the enemies take one of the two passed Shadows at random.
- **Icons.** The ten new entries wear stand-in icons borrowed from the first eight until their own are fetched (`BACKLOG.md`).

## For [USER]

Ruled 2026-10-12; see the top of this page.

1. **Durations.** **(a), ruled:** add This act, with each page mixing both durations and Riptide moving to This act.
2. **The new entries.** **(a), ruled, changed:** all ten new entries. Moonlit Spring heals 8. Frenzy gives enemies 2 Strength. There are no retunes.
