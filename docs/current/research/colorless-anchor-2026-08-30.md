# The native colorless pool — a census read off the assembly

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.
> Re-run the tool (§1) against a new build rather than editing the numbers.

**Produced under:** the companion slate of 2026-08-30, **`R234` pick P8** — the
anchor was ruled owed before any Universal Companion Uncommon or Rare is added
or repriced.
**Date:** 2026-08-30. **Static analysis only:** the game was never launched,
nothing was deployed, and no file under the install was written.

**What this replaces.** `docs/current/research/companion-value-vs-colorless-study.md`
had to build its base-colorless reference band out of **Slay the Spire 1** wiki
material. Its own §2 says so in a warning box — *"No base-game colorless card
data exists in this repo… I cannot verify from here."* Every companion pricing
argument since has rested on that borrowed band. This note is the StS2 one,
read off the shipped assembly. **Where the two disagree, this note wins**, and
§8 lists the disagreements.

---

## 0. Provenance

**The assembly.** `ilspycmd` **8.2.0.7535** (the pinned version, `STATE.md`
"Mod build environment"), project mode, against
`…\Slay the Spire 2\data_sts2_windows_x86_64\sts2.dll` — the path read from
`klee-mod/local.props`, not guessed. Game **v0.111.0**, commit `41cef1ea`,
`main_assembly_hash` `222455745` (`release_info.json` in the game directory),
**matching the repo pin exactly**. 3,538 `.cs` files, decompiled into a session
scratchpad; **nothing from that decompile is committed**, and file citations
below are `<namespace path>/<File>.cs:<line>` relative to the decompile root
(`MegaCrit/sts2/Core/` unless the path says otherwise).

**One source only.** No wiki, no StS1 memory, no inference from card names.
Every number below is a literal in the assembly or an arithmetic over
literals in the assembly. Section §9 lists what could not be obtained that way
instead of approximating it.

---

## 1. Method, and how to re-run it

`tools/colorless_census.py` (new, this branch). It reads the ctor line
(`: base(COST, CardType.X, CardRarity.Y, …)`), the keyword list, the printed
`DamageVar`/`BlockVar` magnitudes and the `*Cmd.Method(` effect vocabulary of
every member of `ColorlessCardPool`, and prints a census.

```
python -m tools.colorless_census --cards --compare
python -m tools.colorless_census --json game_ref/colorless.json   # gitignored
```

It follows the same IP rule as its sibling `tools/extract_base_game_pool.py`:
the **file** holds no game data and is committed; the **output** is game data
and defaults to stdout, with `--json` pointed at gitignored `game_ref/` only.
It needs `ilspycmd` and a local install; `GITS_ILSPY_TREE` reuses a decompile
between runs. `tier0/tests/test_colorless_census.py` pins the plumbing against
synthetic sources and needs neither.

Three things it deliberately refuses to do, because each would manufacture the
very premium the anchor exists to measure:

- a pool that **parses short** of its own declared `new CardModel[N]` is a hard
  error, not a smaller census;
- a card that prints **no** damage/block magnitude stays **out** of the mean —
  a utility card is not a zero-damage card, and every band below reports its
  own coverage beside it;
- a **0-cost** body has no per-energy rate and is excluded from that column
  (counted, and the exclusion reported), rather than divided by one.

The acquisition sections (§6) are hand-read from the assembly, not tool
output; every claim there carries its own `file:line`.

---

## 2. Pool size, rarity split, and the headline

`Models/CardPools/ColorlessCardPool.cs:24-94` — `GenerateAllCards()` returns
`new CardModel[65]`, and 65 members parse.

| | count |
|---|---|
| **Pool size** | **65** |
| Uncommon | 40 |
| Rare | 25 |
| **Common** | **0** |
| Basic | 0 |
| Ancient | 0 |

**The base game's colorless pool has no common tier at all.** That is the
single most load-bearing fact in this note, it is structural rather than
incidental, and it is confirmed twice over: by the census of the 65 ctor lines,
and by the game's own `GetNextAllowedRarity` fall-forward (§6.3), which exists
precisely because a pool can lack a tier.

**Held against the character pools** (`--compare`, same regex on both sides so
a shape change breaks loudly rather than comparing a full pool to a partial
one):

| pool | size | Basic | Common | Uncommon | Rare | Ancient | mean cost | Exhaust share |
|---|---|---|---|---|---|---|---|---|
| **Colorless** | **65** | 0 | **0** | **40** | **25** | 0 | **1.00** | **27.7%** |
| Ironclad | 90 | 3 | 20 | 38 | 27 | 2 | 1.34 | 27.8% |
| Silent | 91 | 4 | 20 | 38 | 27 | 2 | 1.22 | 12.1% |
| Defect | 91 | 4 | 20 | 38 | 27 | 2 | 1.16 | 20.9% |
| Regent | 91 | 4 | 20 | 38 | 27 | 2 | 1.01 | 8.8% |
| Necrobinder | 91 | 4 | 20 | 38 | 27 | 2 | 1.33 | 15.4% |

Read the Uncommon and Rare columns: **40/25 against a character pool's 38/27.**
The colorless pool is not a small pool. It is a **character-sized pool with the
common tier deleted** — the same order of uncommons and rares, offered through
entirely different channels (§6).

**Multiplayer.** Twelve of the 65 declare
`MultiplayerConstraint => CardMultiplayerConstraint.MultiplayerOnly`:
BeaconOfHope, BelieveInYou, Coordinate, GangUp, HuddleUp, Intercept, Knockdown,
Lift, Mimic, Rally, TagTeam, TheBall. **A single-player run sees 53 cards, 32
Uncommon / 21 Rare.** Both populations are reported below where they differ.

---

## 3. Cost distribution and Exhaust share

| cost | all 65 | Uncommon | Rare | single-player 53 |
|---|---|---|---|---|
| 0 | 21 (32.3%) | 16 | 5 | 20 |
| 1 | 29 (44.6%) | 19 | 10 | 22 |
| 2 | 9 (13.8%) | 5 | 4 | 6 |
| 3 | 6 (9.2%) | 0 | 6 | 5 |
| **mean** | **1.00** | 0.85 | 1.24 | 1.11 |

Two shapes worth naming. **Nearly a third of the pool is free** (21 of 65),
and the free cards are concentrated in the *uncommon* tier (16 of 21) — the
colorless uncommon is characteristically a 0-cost splash, not a costed body.
**Cost 3 exists only at Rare** (6 cards, zero uncommons), so the pool's top end
is a small number of expensive, deliberate plays.

**Card types:** Skill 33, Attack 19, Power 13. Single-player: Skill 26, Attack
15, Power 12. The pool is skill-led, and **20% of it is Powers** against a
character pool's more attack-weighted mix.

**Keywords** (whole pool):

| keyword | count | share |
|---|---|---|
| Exhaust | 18 | 27.7% |
| Retain | 7 | 10.8% |
| Innate | 4 | 6.2% |
| Unplayable | 3 | 4.6% |

**Exhaust share is 27.7%** (30.2% among the 53 single-player cards) — level
with Ironclad's 27.8% and roughly double the roster median (Silent 12.1%,
Necrobinder 15.4%, Defect 20.9%, Regent 8.8%). **Colorless pays for its
premium partly in one-shot-ness**, and that is the pool's signature cost
mechanism, not a per-card accident.

Three cards are flagged `CanBeGeneratedInCombat => false` — Alchemize,
HandOfGreed, HiddenGem — so they are excluded from every in-combat generation
channel (§6.7) while remaining purchasable and rewardable.

---

## 4. What colorless cards actually DO

Effect vocabulary, counted structurally from `*Cmd.Method(` calls (no name
table involved):

| | Uncommon (40) | Rare (25) |
|---|---|---|
| type mix | Skill 21 / Attack 13 / Power 6 | Skill 12 / Power 7 / Attack 6 |
| `PowerCmd.Apply` | 16 | 9 |
| `DamageCmd.Attack` | 12 | 6 |
| `CreatureCmd.GainBlock` | 7 | 3 |
| `CardPileCmd.Draw` | 5 | 2 |
| `PlayerCmd.GainEnergy` | 3 | 0 |
| card-pile manipulation (`Add`, `AddGeneratedCardToCombat`, `CardSelectCmd.*`) | 8 | 10 |

The conventions this exposes:

**There is no common tier, so there is no vanilla tier either — except where
the pool prints one on purpose.** `UltimateStrike` (`Models/Cards/UltimateStrike.cs`)
is a 1-cost Attack with a single `DamageVar(14m)`, a `CardTag.Strike`, no
keyword and no rider. `UltimateDefend` is a 1-cost Skill with `BlockVar(11m)`
and a `CardTag.Defend`. These are the pool's *stated* rate: a colorless card
that does nothing but the basic thing does **14 damage or 11 block for one
energy**, against the roster's universal `StrikeIronclad`/`StrikeSilent`/… **6
damage** and `DefendIronclad`/… **5 block** at the same cost
(`Models/Cards/StrikeIronclad.cs:19,25`, `DefendIronclad.cs:17,20`, identical
across all five characters). **That is the colorless premium, printed: ×2.33
on damage, ×2.20 on block, for the plainest possible body.**

**Rares are one-off engines, not bigger bodies.** Seven of the 25 rares are
`Power` type, and the nine distinct `*Power` classes they apply
(`BeaconOfHopePower`, `CalamityPower`, `EntropyPower`, `PlatingPower`,
`KnockdownPower`, `MayhemPower`, `NostalgiaPower`, `RollingBoulderPower`,
`TheGambitPower`) are **one bespoke power class per card**. A colorless rare is
characteristically a rules-changing engine with its own implementation, which
is why the rare tier resists a per-energy reading almost entirely.

**The uncommon tier's premium is bought with a drawback, a condition, or
one-shot-ness — rarely for free.** The pattern, card by card:

| card | cost | body | what pays for it |
|---|---|---|---|
| `PanicButton` | 0 | **30 block** | applies `NoBlockPower` for 2 turns; Exhaust |
| `DramaticEntrance` | 0 | 11 damage | Exhaust + Innate (one card, once, turn one) |
| `Volley` | 0 | 10 damage per hit | `HasEnergyCostX` — the hit count *is* your whole energy |
| `Omnislice` | 0 | 8 damage | splash carries the *dealt* total to the rest of the enemy team |
| `Salvo` | 1 | 12 damage | applies `RetainHandPower` — a hand-size/tempo tax, not a discount |
| `ThrummingHatchet` | 1 | 11 damage | returns itself to hand next turn (upside, not cost) |
| `UltimateStrike` | 1 | 14 damage | **nothing** — this is the naked rate |
| `UltimateDefend` | 1 | 11 block | **nothing** |
| `Equilibrium` | 2 | 13 block | Retain |
| `TheGambit` (Rare) | 0 | **50 block** | applies `TheGambitPower` |
| `HandOfGreed` (Rare) | 2 | 20 damage + 20 gold | Fatal-gated; cannot be generated in combat |

Three cards are `Unplayable` (HiddenGem, BeatDown, Catastrophe) — the pool
contains cards whose value is entirely in *being held or being converted*, a
shape our companion sheet has no analogue for.

---

## 5. The power-level read against same-rarity character cards

This is the section the companion slate needs, and it is also the section where
the honest answer is partly "the metric does not reach."

**Coverage first.** Only 15 of the 40 colorless uncommons and 6 of the 25 rares
print a `DamageVar` or `BlockVar` at all. The rest are draw, energy, pile
manipulation, gold, upgrades and bespoke powers, and **no arithmetic over
damage numbers will ever see them.** Every mean below is over its printing
subset and states that subset.

### 5.1 Body magnitude, per rarity, per pool

`mean` is the flat printed magnitude; `/E` is the per-energy rate over the
costed cards only (0-cost cards counted but excluded from the rate).

| pool | rarity | n | dmg printing | dmg mean | dmg /E | blk printing | blk mean | blk /E |
|---|---|---|---|---|---|---|---|---|
| **Colorless** | **Uncommon** | 40 | 11 | 9.82 | **9.79** | 6 | 13.0 | **9.38** |
| **Colorless** | **Rare** | 25 | 4 | 14.5 | 7.22 | 2 | 31.0 | 6.00 |
| Ironclad | Uncommon | 38 | 13 | 11.69 | 7.57 | 4 | 7.25 | 5.75 |
| Silent | Uncommon | 38 | 9 | 9.67 | 6.57 | 5 | 7.20 | 5.62 |
| Defect | Uncommon | 38 | 8 | 11.00 | 6.25 | 6 | 8.50 | 6.50 |
| Regent | Uncommon | 38 | 10 | 14.80 | 12.54 | 6 | 9.00 | 7.50 |
| Necrobinder | Uncommon | 38 | 6 | 15.50 | 7.92 | 5 | 8.40 | 5.57 |
| Ironclad | Rare | 27 | 8 | 15.75 | 4.81 | 1 | 30.0 | 15.00 |
| Silent | Rare | 27 | 3 | 26.67 | 10.00 | 0 | — | — |
| Defect | Rare | 27 | 8 | 14.12 | 6.88 | 0 | — | — |
| Regent | Rare | 27 | 9 | 14.11 | 9.08 | 1 | 10.0 | 10.00 |
| Necrobinder | Rare | 27 | 5 | 25.40 | 15.56 | 1 | 7.00 | — |
| *(reference)* | Basic | — | Strike **6** dmg @1 | | **6.00** | Defend **5** blk @1 | | **5.00** |

**At Uncommon the premium is real and it is roughly a third.** Colorless
damage rate **9.79/E** sits above four of the five character uncommon tiers
(6.25–7.92; median **7.57**) — **+29% over the roster median** — and below
Regent's 12.54. Colorless block rate **9.38/E** is above **all five**
(5.57–7.50; median 5.75) — **+63%**. Single-player-only, the colorless
uncommon damage rate rises to **10.60/E** (median 11.0 over 5 costed cards),
because several of the excluded co-op cards are the tier's cheaper bodies.

**At Rare the metric fails and should not be quoted.** Four colorless rares
print damage and two print block; the character rare rates span 4.81 to 15.56
with no ordering. The rare tier of every pool, colorless included, is made of
engines and one-off rules changes (§4), and a damage-per-energy over four cards
is noise. **The anchor supports no rare-tier power claim.** What it supports is
a *shape* claim, which §7 uses instead.

### 5.2 The claim the naked cards make, which the averages cannot

The averages are over subsets. The two cards that print nothing but the basic
effect are not: `UltimateStrike` **14 dmg @ 1** and `UltimateDefend` **11 blk
@ 1**, against `Strike` **6 @ 1** and `Defend` **5 @ 1**. Those four numbers
are the cleanest statement of the convention in the assembly, they need no
coverage caveat, and they are what "slightly better than native at rarity"
should be calibrated against — with the observation that **"slightly" is the
wrong word**: at the vanilla end the native premium is **×2.2 to ×2.3 over
Basic**, and roughly **+30% to +45% over character Uncommons** in rate.

---

## 6. How colorless cards are acquired

The channels are entirely separate from the character-card economy. Every
consumer calls `GetUnlockedCards(player.UnlockState, …)`, so epoch gating
(§6.8) applies to all of them.

### 6.1 NOT the ordinary card reward

`Rewards/RewardsSet.cs:220-247` — Monster, Elite and Boss rewards each build
`CardCreationOptions.ForRoom(player, room.RoomType)`, and `ForRoom`
(`Runs/CardCreationOptions.cs:81-109`) sets a **single-element pool list holding
only `player.Character.CardPool`** (`:101`). `GetPossibleCards` (`:134-140`)
enumerates only those pools. **Colorless cannot appear in a normal post-combat
reward.** The one exception is a relic mutating the options through
`Hook.ModifyCardRewardCreationOptions` (`Factories/CardFactory.cs:218`), which
in the shipped game is **Dingy Rug alone**.

### 6.2 The shop — the primary channel

`Entities/Merchant/MerchantInventory.cs`.

| fact | value | source |
|---|---|---|
| colorless cards stocked | **exactly 2** | `_colorlessCardRarities = { Uncommon, Rare }` `:24-28`; loop `:114-124` |
| their rarities | **one Uncommon, one Rare — fixed** | same |
| rarity roll | **none** | `CardFactory.CreateForMerchant(…, CardRarity rarity)` `Factories/CardFactory.cs:69-80` filters `c.Rarity == modifiedRarity` directly |
| character cards stocked | 5: Attack, Attack, Skill, Skill, Power | `_coloredCardTypes` `:15-22`, loop `:98-112` |
| duplicates | excluded across all 7 slots | `MerchantCardEntry.cs:71-83` |
| base price | Rare **150**, Uncommon **75**, else **50** | `MerchantCardEntry.cs:42-45` |
| colorless surcharge | **×1.15**, rounded | `MerchantCardEntry.cs:46-49` — 75→**86**, 150→**173** |
| price jitter | ×0.95–1.05 | `:124` — practical 82–91 and 164–182 |
| **on sale** | **never for colorless** | the sale roll lives only in `PopulateCharacterCardEntries` (`MerchantInventory.cs:100,107-110`) |
| relic discounts | still apply | `MerchantEntry.cs:19-30`; MembershipCard ×0.50, TheCourier ×0.80 |
| restock after purchase | only with TheCourier | `MerchantEntry.cs:84-91`, `TheCourier.cs:28-31`, `MerchantCardEntry.cs:156-160` |

The Fake Merchant event sells **no cards at all** — six relic entries only
(`Models/Events/FakeMerchant.cs:116-125`).

**This confirms the repo's own shop constants against the current build.**
`tier0/constants.py:1330-1345` records 50/75/150 and the ×1.15 colorless
surcharge as read from the assembly, and both still hold on v0.111.0.

### 6.3 Rarity odds, and what a pool with no commons does

Enum `Runs/CardRarityOddsType.cs:3-39`. Weights in `Odds/CardRarityOdds.cs`
(`GetBaseOdds`, `:136-177`); the *Scarcity* ascension variant in parentheses:

| odds type | Common | Uncommon | Rare |
|---|---|---|---|
| RegularEncounter | 0.60 (0.615) | 0.37 | **0.03** (0.0149) |
| EliteEncounter | 0.50 (0.549) | 0.40 | **0.10** (0.05) |
| BossEncounter | 0 | 0 | **1.00** |
| Shop | 0.54 (0.585) | 0.37 | **0.09** (0.045) |
| Uniform | short-circuits the roll entirely (`CardFactory.cs:223-226`) | | |

Common is the residual — the roll only compares against rare and
rare+uncommon (`:96-111`, `:120-134`). Rare pity: `Roll` (`:69-81`) adds a
running offset to the rare threshold, **reset to −0.05** on a rare, **+0.01**
per miss (0.005 Scarcity), **clamped at 0.4**; boss rolls pass offset 0.

**There is no renormalisation for a missing tier anywhere in the assembly.**
The mechanism is a **fall-forward**: `CardFactory.RollForRarity` (`:246-263`)
rolls normally, then `GetNextAllowedRarity` (`:265-283`) walks
`GetNextHighestRarityWithWrapping` (`Entities/Cards/CardRarityExtensions.cs:14-31`,
Basic→Common→Uncommon→Rare→Common) until it lands on a rarity the filtered
pool actually contains. So against a colorless-only pool, **a Common roll
silently becomes Uncommon** — not re-rolled, not renormalised.

**Effective colorless-only distribution under default (RegularEncounter) odds:
Rare 3%, Uncommon 97%** (Scarcity 1.49% / 98.51%). Under `Uniform`, rarity is
ignored and all unlocked cards are equally likely.

When the colorless pool is *unioned* with a character pool (Dingy Rug, Massive
Scroll), Common **is** present, so a Common roll stays Common and can only
yield a character card; colorless surfaces only on the Uncommon/Rare branches,
diluted by count within that rarity (`CardFactory.cs:235,238`).

### 6.4 Relics

| relic | rarity | what it does | numbers | source |
|---|---|---|---|---|
| **Dingy Rug** | Shop | unions colorless into **card rewards** — the only relic that does | — | `Models/Relics/DingyRug.cs:11,16-28` |
| **Lead Paperweight** | Ancient | on pickup, choose 1 of **2** colorless, skippable, **into the deck** | 2, RegularEncounter odds ⇒ 97/3 | `LeadPaperweight.cs:15,19-24,27` |
| **Massive Scroll** | Ancient, co-op only | choose 1 of **3** from character ∪ colorless, filtered to `MultiplayerOnly` | 3 | `MassiveScroll.cs:17-20,24-34` |
| **Prismatic Gem** | Ancient | +1 Energy and unions all *character* pools into rewards; **explicitly no-ops when every pool is already colorless** | — | `PrismaticGem.cs:13,16,29-48` |
| **Toolbox** | Shop | turn 1 only: 1 of **3** colorless **to hand, combat-only** | 3 | `Toolbox.cs:15,19,23-36` |
| **Orange Dough** | Rare | first turn: **2** random colorless **to hand, combat-only** | 2 | `OrangeDough.cs:16,18,22-31` |

An exhaustive grep for `ColorlessCardPool|IsColorless` under `Models/Relics/`
returns these six and nothing else.

### 6.5 Events — two, and only two

- **Brain Leech** (`Models/Events/BrainLeech.cs`): the "Rip" branch costs
  **5 unblockable damage** (`:29,55`) and gives **one card reward of 3
  colorless choices** (`:30,56-57`), colorless-only pool, flags
  `NoRarityModification | NoCardPoolModifications`. No gold. Acts 1–2 only
  (`:38-41`). The other branch is character cards, not colorless.
- **Endless Conveyor** (`Models/Events/EndlessConveyor.cs`): the FRIED_EEL dish
  grants **1 colorless card straight to the deck** (`:188-193`) for the
  generic **40 gold** per grab (`:97,135-138`); dish weight **3** in a variable
  table (`:227-248`), and you cannot choose the dish, only whether to grab.
  Event requires all players ≥120 gold (`:110-113`).

A grep of `Models/Events/` for `ColorlessCardPool` returns only these two.

### 6.6 Potions — neither is permanent

- **Colorless Potion** (Common, CombatOnly): shows **3**, take **1**, free that
  turn, into hand (`Models/Potions/ColorlessPotion.cs:14,16,27-35`).
- **Cosmic Concoction** (Rare, CombatOnly): generates **3** distinct colorless
  cards, **upgrades each**, all into hand (`CosmicConcoction.cs:16,18,22,29-36`).

Both use `AddGeneratedCardToCombat`, which throws outside a combat pile;
permanent acquisition uses the different call `CardPileCmd.Add(card,
PileType.Deck)`. **No potion ever grants a permanent colorless card.**

### 6.7 In-combat generation (not acquisition)

`BundleOfJoy` (3 to hand, +1 upgraded), `JackOfAllTrades` (1, +1 upgraded,
excluding itself), `Largesse` (1, for a *target ally*), `ManifestAuthority`
(1), `Quasar` (3 shown, choose 1), `SpectrumShiftPower` (`Amount` per hand
draw). `CardFactory.FilterForCombat` (`:160-163`) excludes
`!CanBeGeneratedInCombat`, Basic, Ancient and Event cards from all of them.

**One genuine deck acquisition hides in this group:** the Neow modifier
`Models/Modifiers/AllStar.cs:17-33` adds **5 colorless cards to the deck**, at
**Uniform** odds with `NoRarityModification | NoCardPoolModifications` — so
rarity is ignored entirely and Prismatic Gem/Dingy Rug cannot dilute it.

### 6.8 Unlock gating

`ColorlessCardPool.FilterThroughEpochs` (`:96-140`) removes the cards of any
of five epochs that is not revealed. **Three cards each, 15 total:**

| epoch | cards | score threshold |
|---|---|---|
| Colorless1 | Automation, Entropy, Catastrophe | 200 |
| Colorless2 | EternalArmor, Jackpot, PrepTime | 1250 |
| Colorless3 | Rend, BeatDown, Prowess | 1800 |
| Colorless4 | Alchemize, Nostalgia, Scrawl | 2100 |
| Colorless5 | Splash, Anointed, Calamity | 2400 |

Thresholds from `Timeline/EpochModel.cs:86,94,102,108,114` (cumulative
end-of-run score, `AgnosticUnlocks`). Being *obtained* is not enough:
`UnlockState` counts only `EpochState.Revealed`
(`Unlocks/UnlockState.cs:148-151,189-192`), which requires the player to click
the slot (`Nodes/Screens/Timeline/NEpochSlot.cs:377-383`).

**A fresh save sees 50 colorless cards; a fully unlocked save sees 65.** In
co-op the union of all players' revealed sets applies
(`UnlockState.cs:159-168`).

---

## 7. What this anchor rules in and out

The slate's convention is that Universal Companions should be *"slightly
better than native at rarity, as unlikely finds."* The census says which half
of that sentence the data can carry.

### 7.1 What it rules IN

**1. "As unlikely finds" is confirmed, and it is structural, not a tuning
knob.** Colorless is absent from the ordinary card reward entirely (§6.1). Its
channels are a 2-card shop shelf at a **15% surcharge that never goes on sale**
(§6.2), one Ancient relic, one shop relic, one event branch costing 5 HP, one
40-gold dish, and one Neow modifier. Every design that makes companions a
*rare, paid, off-ramp* acquisition is native-shaped; every design that puts
them in the routine post-combat reward is not.

**2. The premium at Uncommon is real and quantified.** Against the roster
median, native colorless uncommons run **+29% on damage rate** (9.79 vs 7.57
per energy) and **+63% on block rate** (9.38 vs 5.75). At the vanilla end the
statement is sharper and needs no caveat: **14 damage or 11 block for one
energy**, against Strike's 6 and Defend's 5 (§5.2).

**"Slightly better" is therefore the wrong calibration.** A Universal Companion
Uncommon priced to sit a few percent over a character uncommon is **under** the
native colorless bar, not on it. The defensible reading of the convention is
**+30% on rate at Uncommon**, with the vanilla ceiling at **×2.2–2.3 over
Basic** for a body that does nothing else.

**3. The premium is paid for, and the currency is named.** 27.7% of the pool
Exhausts — level with the most Exhaust-heavy character pool and about double
the roster median (§3). The pool's own uncommons buy their rate with Exhaust,
`NoBlockPower`, `RetainHandPower`, an X-cost, or Innate-once (§4). **A
companion uncommon may carry a colorless-grade body if it carries a
colorless-grade drawback**; the two travel together in the native pool and
should travel together in ours.

**4. The rarity SHAPE is the finding our companion pool most visibly diverges
from.** Native colorless: **0 common / 40 uncommon / 25 rare**. Our companion
pool (`docs/*-companions.yaml`, 51 cards): **24 common / 18 uncommon / 9
rare** — nearly half commons, in the slot the base game fills with a pool that
has no commons at all. And our commons are the *cheapest* bodies: companion
common damage runs **4.95/E** and block **4.20/E**, uncommon **4.83/E** and
**3.62/E** — i.e. **our uncommons are not even above our own commons on rate**,
and the whole distribution sits at roughly **half** the native colorless
uncommon rate (9.79/E and 9.38/E).

That gap is not automatically a defect: the standing companion argument
(`companion-value-vs-colorless-study.md` §1.3) is that companion bodies are
deliberately thin because value is routed through element application, and LAW
holds that companions route power *through* your character. **But the anchor
now prices that argument.** The concession is roughly **2× on body rate**, and
whether reaction credit is worth 2× is a measurement this note does not make.

**5. The shop constants we already ship are correct.** 50/75/150 and the ×1.15
colorless surcharge (`tier0/constants.py:1330-1345`) match the v0.111.0
assembly exactly.

### 7.2 What it rules OUT

**1. No rare-tier power claim.** Four colorless rares print damage and two
print block; character rare rates span 4.81–15.56 per energy with no ordering
(§5.1). Anyone pricing a Universal Companion **Rare** against "the native rare
bar" is quoting noise. The rare tier's real convention is a *shape*: **one
bespoke engine per card** (nine distinct one-use `*Power` classes across seven
Power-type rares), plus a small expensive tail (all six 3-cost cards in the
pool are rares). Price a companion rare against **that** — does it change a
rule — not against a damage number.

**2. No claim that colorless is uniformly stronger.** Regent's uncommon damage
rate (12.54/E) is **above** the colorless one. The premium is a median
statement, not a dominance statement.

**3. No value-per-energy claim about the pool as a whole.** Coverage is 15/40
at Uncommon and 6/25 at Rare (§5). Two thirds of the pool is draw, energy,
pile manipulation, gold, upgrades and rules changes, and **32% of it is free**
(21 cards at cost 0) where a per-energy rate is undefined. Any "the colorless
pool averages N per energy" sentence is quoting a third of a pool.

**4. It does not settle whether the base pool should remain reachable.** LAW's
recorded live tension — principles §4.7 says the base pool is removed, ship
reality is a shop-only override (R60 phase 1), full removal deferred — is
untouched by this note. What the note adds is the **audit surface**: the
consumers that would need covering are §6.2 shop, §6.4's six relics, §6.5's
two events, §6.6's two potions, §6.7's six generators plus the AllStar Neow
modifier, and `CardFactory.cs:173`, which makes `ColorlessCardPool` the
*fallback transform pool* for Event/Ancient/Token/Quest cards.

**5. One divergence it flags without ruling on.** LAW records both mod shop
colorless slots as rolling `SHOP_COMPANION_RARITY_ODDS` renormalised over the
≥Uncommon pool, differing only by nation filter. **Native does not roll at
all**: slot 1 is *always* Uncommon and slot 2 is *always* Rare (§6.2). The mod
also never renormalises the way the base game doesn't — the base game
fall-forwards (§6.3). Whether to match native's fixed slots is a design call
and goes to [USER], not into this note.

**6. A latent engine consequence, stated because the anchor exposes it.**
`tier05/rewards.py:218` walks a rarity ladder **downward** —
`_RARITY_FALLBACK = {"rare": "uncommon", "uncommon": "common"}` — because *our*
reference pools lack rares. A colorless-shaped pool lacks **commons**, and a
Common roll against one would walk off the end of that ladder. The base game
walks the ladder **upward with wrapping** (`CardRarityExtensions.cs:14-31`).
If the mod ever models a colorless-shaped pool, the ladder must gain the other
direction. **This is a real, named consequence, not a filed defect** — id space
is owned elsewhere tonight (§10).

---

## 8. Corrections to our own records

The StS1-anchored band in `companion-value-vs-colorless-study.md` §2/§7 is
superseded on three points:

| the study said | the assembly says |
|---|---|
| colorless commons ≈ 6–8 v/e, midpoint ~7 (StS1: Swift Strike, Good Instincts, Flash of Steel, Dramatic Entrance) | **there is no colorless common tier in StS2** — 0 of 65. Its §7 already suspected this; it is now proven from the pool and from the fall-forward code that exists for it |
| colorless uncommons ≈ 10–12 v/e, midpoint ~10 | 9.79/E damage, 9.38/E block over the printing subset — close on damage, and the study had no block band at all |
| colorless rares are a "payoff tier, not a v/e point" | **upheld**, and now with a mechanism: one bespoke `*Power` per card, six of the pool's 3-cost cards, coverage too thin to average |
| StS1 card names (Ritual Dagger, Apparition, Blind, Sadistic Nature) used as StS2 exemplars | **none of those four exists in the StS2 colorless pool.** The pool's 65 members are listed by the tool, not reproduced here |

The study's §1 methodology and its floor/expected/ceiling treatment of
conditional companion cards are untouched — only its base-colorless band is
replaced.

---

## 9. Not recoverable by static analysis

Stated as gaps rather than approximated:

1. **The end-of-run score formula** behind the 200/1250/1800/2100/2400 epoch
   thresholds. `NGameOverScreen.cs:869-874` reads
   `AgnosticUnlocks[i].ScoreThreshold` but the score computation was not
   traced; no run-length estimate is offered for when a player unlocks the 15
   gated cards.
2. **Card rules text.** Descriptions live in the localisation blob inside
   `SlayTheSpire2.pck`, not in the assembly. §4's effect reads are structural —
   ctor lines, `*Cmd` calls, `*Var` magnitudes — so a card whose entire meaning
   is in its text (several of the 0-cost utility uncommons) is under-described
   here. Extracting the blob is possible and was out of scope.
3. **How often each acquisition channel actually fires in a run.** Node
   frequencies, event pool weights per act, relic drop rates and shop visit
   counts are a run-generation question, not a colorless question, and answering
   it would need the map/encounter layer plus play data. §6 gives the per-visit
   structure only. **No "expected colorless cards per run" number is offered,
   and none should be inferred from this note.**
4. **`EndlessConveyor`'s absolute dish odds.** The FRIED_EEL weight is 3, but
   the denominator is state-dependent (`:227-248`: a potion slot, damage taken,
   the previous dish removed, a forced fifth grab), so no fixed probability
   exists to quote.
5. **Any play-derived power claim.** This is a static census. It contains no
   winrate, no simulation and no balance verdict — Guardrail-7 territory.

---

## 10. Owed follow-ups

Named here only; **no ids are minted in this note** (id space is owned
elsewhere tonight). Each needs an owner before it is work:

1. **Engineering:** `tier05/rewards.py`'s `_RARITY_FALLBACK` has only the
   downward direction (§7.2 item 6). A colorless-shaped pool needs the upward,
   wrapping ladder the base game uses.
2. **Design ([USER]):** the "slightly better than native at rarity" convention
   should be restated as a number now that one exists — this note proposes
   **+30% on rate at Uncommon** and **shape, not magnitude, at Rare** (§7.1).
3. **Design ([USER]):** the companion pool's rarity shape (24/18/9 with commons
   at the bottom) against a native colorless shape with no commons at all
   (§7.1 item 4) — a genuine design direction pick, not a defect.
4. **Design ([USER]):** whether the mod's two shop colorless slots should match
   native's fixed Uncommon+Rare rather than rolling (§7.2 item 5).
5. **Hygiene:** `companion-value-vs-colorless-study.md` §2/§7 should point at
   this note. Left undone here because that doc is a frozen REFERENCE record
   and editing it is a separate, deliberate act.
6. **Optional research:** extract the localisation blob so the pool's
   text-only cards can be described (§9 item 2).
