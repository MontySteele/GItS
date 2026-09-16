Status: OPEN (census for EB-494; curation is the main session's)

# Inherited Silent potions and relics — a census, not a curation

`EB-494`: all three kits (Klee, Kokomi, Furina Stage) resolve their
`RelicPool` to `ModelDb.RelicPool<SilentRelicPool>().AllRelics` plus their
own starter relic (`Klee.cs:94/96`, `Kokomi.cs:70/74`, `Furina.cs:54/58`,
`KleeRelicPool.cs`, `KokomiRelicPool.cs`, `FurinaRelicPool.cs`), and all
three resolve `PotionPool` to `ModelDb.PotionPool<SilentPotionPool>()`
unconditionally. This packet counts every item those two pools actually
contain in the shipped game and rules a one-word verdict per kit — useful,
misleading, or dead — against that kit's own verbs. **It does not propose
cuts, replacements, or names; that is the main session's call on `EB-494`'s
next action.**

## What was counted, and how

`SilentRelicPool.GenerateAllRelics()` and `SilentPotionPool` (via
`Silent4Epoch.Potions`) were read directly off the shipped game DLL
(`ilspycmd -t ... sts2.dll`, `C:\...\Slay the Spire 2\data_sts2_windows_x86_64\sts2.dll`),
not reconstructed from a doc. That is **8 relics and 3 potions** — smaller
than the 42-relic/9-potion set in
`docs/current/dossiers/content/potion-relic-conversion-gallery.md`, which is
a different, unrelated layer: a names/flavor conversion gallery built over
the **tier05 sim's own** `common`/`neow`/`ancient`/`event` relic pool and a
StS1-style 9-potion list (`tier05/content/relics.yaml`,
`tier05/content/potions.yaml`), never wired to the C# `SilentRelicPool` /
`SilentPotionPool` the three kits actually resolve. That gallery is not
this census's source; it is flagged here only so nobody double-counts it
against `EB-494`.

For each of the 8 relics and 3 potions, the class body was read off the DLL
(hook, trigger, amount) and checked against each kit's card sheet
(`docs/klee-cards.yaml`, `docs/kokomi-cards.yaml`, `docs/furina-cards.yaml`)
and brief (`docs/current/characters/furina-kickoff-v0.1.md`,
`docs/current/kokomi-brief-2026-09-01.md`) for the verb or keyword (Shiv,
Poison, Dexterity, discard) the item's trigger depends on. **Useful** = the
item's trigger can fire from the kit's own play and does what it says.
**Misleading** = it can fire (sometimes only via another item in this same
inherited set) but its trigger or payoff names a mechanic no card in that
kit's sheet produces. **Dead** = the trigger can never fire at all — no seat
in that kit ever meets the item. One relic (Ring of the Snake, `Starter`
rarity) is never offered as loot at all under any of the three pools' own
documented reward rule ("relic rewards roll Common/Uncommon/Rare/Shop/Boss,
never Starter" — `KleeRelicPool.cs:25`, `KokomiRelicPool.cs:57`), so it is
dead by construction for all three, independent of any kit verb.

## The table

### Potions (3 — `SilentPotionPool`, identical set for all three kits)

| id / class | rules text | Klee | Kokomi | Furina Stage |
|---|---|---|---|---|
| `PoisonPotion` (Common) | Apply 6 Poison to one enemy (`PoisonPotion.cs`). | useful — a plain single-target DoT burst, claims no kit interaction | useful — same | useful — same |
| `GhostInAJar` (Rare) | Apply 1 Intangible to a targeted ally (all non-attack and attack damage taken reduced to 1) (`GhostInAJar.cs`). | useful — generic emergency panic button, no kit dependency | useful — same | useful — same |
| `CunningPotion` (Uncommon) | Add 3 Upgraded Shivs (0-cost, 4 dmg, Exhaust attack) to hand (`CunningPotion.cs`, `Shiv.cs`). | useful — does exactly what it prints (3 free attacks); no card in `docs/klee-cards.yaml` tags `Shiv` so nothing in the sheet reads it, but the potion itself overpromises nothing | useful — same, 0 `shiv` hits in `docs/kokomi-cards.yaml` | useful — same, 0 `shiv` hits in `docs/furina-cards.yaml` |

### Relics (8 — `SilentRelicPool.GenerateAllRelics()`, identical membership for all three kits)

| id / class | rarity | rules text | Klee | Kokomi | Furina Stage |
|---|---|---|---|---|---|
| `RingOfTheSnake` | Starter | Turn 1 only: draw 2 extra cards (`RingOfTheSnake.cs`). | **dead** — Starter rarity is never rolled as a reward under this pool's own reward rule, and each kit's own `StartingRelics` (`Relics.PoundingSurprise`) replaces it as the actual opener, so no run ever holds it | **dead** — same rule; kit opener is `Relics.PearlOfWisdomRelic` (`Kokomi.cs:165`+) | **dead** — same rule; kit opener is `Relics.EtherealSpotlightRelic` / `Relics.SalonSolitaire` (`Furina.cs:134`+) |
| `HelicalDart` | Rare | After playing a card tagged `Shiv`, gain Dexterity equal to the relic's stack (`HelicalDart.cs`). | misleading — fires only if the run also picked up `CunningPotion`; no card in `docs/klee-cards.yaml` carries `Shiv`, so the trigger names a card type absent from Klee's own sheet | misleading — same; 0 `shiv` hits in `docs/kokomi-cards.yaml` | misleading — same; 0 `shiv` hits in `docs/furina-cards.yaml` |
| `NinjaScroll` | Shop | Turn 1 only: add 3 Shivs to hand (`NinjaScroll.cs`). | useful — unconditional free attacks, no kit interaction claimed | useful — same | useful — same |
| `PaperKrane` | Rare | Powered attacks the owner takes deal 15% less damage (`PaperKrane.cs`). | useful — generic mitigation, no kit dependency | useful — same | useful — same |
| `SneckoSkull` | Common | Poison the owner applies is increased by 1 (`SneckoSkull.cs`, `ModifyPowerAmountGivenAdditive`). | misleading — no card in `docs/klee-cards.yaml` applies Poison (0 `poison` hits); the only Poison the relic can amplify comes from this same inherited set (`PoisonPotion`, `TwistedFunnel`), so it advertises a Poison engine the kit's own sheet has none of | misleading — same, 0 `poison` hits in `docs/kokomi-cards.yaml` | misleading — same, 0 `poison` hits in `docs/furina-cards.yaml` |
| `Tingsha` | Uncommon | After discarding a card on your turn, deal 3 unpowered damage to a random enemy (`Tingsha.cs`, `AfterCardDiscarded`). | useful — `docs/klee-cards.yaml` has direct discard payoffs (`blast_radius` line 35, `crackle`/`discard_for_sparks` line 48, `bright_idea` line 153) | useful — Kokomi's `assist` archetype is built on discard ("Sly/discard", `docs/kokomi-cards.yaml:5`); 13 `discard` rows incl. `steady_the_line` (line 101, "rings the Sly bell") and `rearguard_action` (line 112) | misleading — `docs/furina-cards.yaml` has exactly one incidental `scry_discard` line (`curtain_up` / "In the Wings", archetype `fanfare`, line 175) and no discard-payoff archetype; the trigger can fire but nothing on the sheet is built toward it |
| `ToughBandages` | Rare | Same discard trigger as `Tingsha`, grants 3 Block instead of damage (`ToughBandages.cs`). | useful — same discard rows as `Tingsha` | useful — same | misleading — same single incidental line as `Tingsha` |
| `TwistedFunnel` | Uncommon | Turn 1 start: apply 4 Poison to all enemies (`TwistedFunnel.cs`). | useful — unconditional AoE DoT, claims no kit interaction | useful — same | useful — same |

## Dead items per kit (curation candidates)

- **Klee — 1 dead:** `RingOfTheSnake`.
- **Kokomi — 1 dead:** `RingOfTheSnake`.
- **Furina Stage — 1 dead:** `RingOfTheSnake`.

`RingOfTheSnake` is dead for all three kits by the same structural cause
(Starter rarity, never rolled, always replaced by the kit's own opener) —
one root cause, three rows. No potion is dead in any kit. Misleading counts,
for reference and not part of the "dead" acceptance line: Klee 2
(`HelicalDart`, `SneckoSkull`), Kokomi 2 (same two), Furina Stage 4
(`HelicalDart`, `SneckoSkull`, `Tingsha`, `ToughBandages`).
