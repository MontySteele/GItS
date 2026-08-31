# Regent's Stars — what the decompile actually says

> **Research note, not a ruling.** Everything below is read off the shipped
> assembly and the shipped localisation blob for the pinned build. Where the
> decompile does not answer a question, the gap is stated as a gap.

## 0. Provenance, and one correction to our own records

**Source A — the assembly.** `ilspycmd -p -o <scratch> "…\Slay the Spire 2\
data_sts2_windows_x86_64\sts2.dll"`, ilspycmd `8.2.0.7535` (the pinned
version, `STATE.md` "Mod build environment"). Game **v0.111.0**, commit
`41cef1ea`, `main_assembly_hash` `222455745` — `release_info.json` in the game
directory, matching the pin exactly. 3538 `.cs` files, decompiled into the
session scratchpad; **nothing from that decompile is committed** and paths
below are given as `<namespace>/<File>.cs` relative to the decompile root.

**Source B — the card text.** The localisation payload is a plain JSON blob
embedded in `SlayTheSpire2.pck` (`LocManager.cs:128` `LocalizationAssetDir =>
"res://localization"`). Sixteen language blocks; English quoted throughout.

**The correction, and it has since been ACTED ON (EB-192 / R231).**
`tools/canon_role_tempo.py` used to mint a marker called `ForgeStars`:

```python
(re.compile(r"ForgeCmd\.|GainStars|\bStars\b"), "ForgeStars"),
```

**`ForgeStars` is our word, not the game's.** No type, method, field or
localisation key named `ForgeStars` exists anywhere in the assembly (grep over
all 3538 files: zero hits). The marker is a regex alternation that fuses **two
unrelated Regent mechanics** into one 19-card "package":

- **Stars** — a numeric resource on `PlayerCombatState`, spent as a card cost.
- **Forge** — `ForgeCmd.Forge` (`MegaCrit.Sts2.Core.Commands/ForgeCmd.cs`),
  which has nothing to do with Stars. Its own doc comment: *"Applies Forge to
  the player. Adds Sovereign Blade to their hand if they haven't forged this
  combat, and adds the amount of damage to it."* Forge is a growing 0-cost
  attack card, closer to Ironclad's Strength than to a spendable bank.

Of the 19 members of that `regent_forge` package, ten were Forge-only cards
that never touch a Star, and `klee/spark` was anchored to it: **the anchor's
cell percentages were computed over a population that was roughly half a
different mechanic.**

**R231 rebuilt the anchor from Star-touching cards only.** The package is now
`regent_stars`, and its membership is **this note's census** — §2 (every
generator), §3.5 (every spender), §3.6 (the readers) — held as an explicit
list in `tools/canon_role_tempo.py::REGENT_STARS`, because a Star price is a
cost FIELD rather than a call in a card body (§3.1) and so no body regex can
ever draw this package. `tier0/tests/test_role_tempo_coverage.py` fails if
that list drifts from the three sections below, which makes those sections
load-bearing: **edit them only from the assembly.**

Everything from §1 down is about **Stars only**, re-derived from the assembly.

**A second, smaller correction.** `game_ref/regent.json`'s `vars` field never
carries a Star amount (Venerate shows `"vars": {}`). That is an extractor
artifact, not a fact about the game: `tools/extract_base_game_pool.py:106`
reads `new (\w+)Var\(\s*(-?[\d.]+)m` — a **decimal** literal — and `StarsVar`
takes an `int` (`Localization.DynamicVars/StarsVar.cs`: `public StarsVar(int
stars)`). So every Star amount in this document was read from the C# source,
never from our JSON extract. The same regex gap also hid `Genesis` from the
`\bStars\b` marker, because its var is spelled `"StarsPerTurn"` and the word
boundary fails.

---

## 1. Generation in the base kit

### 1.1 The starting deck

`Models.Characters/Regent.cs` — `StartingHp => 75`, `StartingGold => 99`,
`MaxEnergy` not overridden so it is the `CharacterModel.cs:97` default of
**3**, and:

```csharp
public override IEnumerable<CardModel> StartingDeck => new CardModel[10]
{
    StrikeRegent ×4, DefendRegent ×4, FallingStar, Venerate
};
public override IReadOnlyList<RelicModel> StartingRelics => { DivineRight };
public override bool ShouldAlwaysShowStarCounter => true;
```

| card | energy | ★ cost | type | what it does |
|---|---|---|---|---|
| `StrikeRegent` ×4 | 1 | — | Attack | `DamageVar(6m)` |
| `DefendRegent` ×4 | 1 | — | Skill | `BlockVar(5m)` |
| `FallingStar` | **0** | **2** | Attack, Basic | 8 damage, 1 Weak, 1 Vulnerable |
| `Venerate` | 1 | — | Skill, Basic | **gain 2 Stars** |

**Venerate is confirmed as the Basic generator**, and its amount is 2, not 1
(`Models.Cards/Venerate.cs`):

```csharp
protected override IEnumerable<DynamicVar> CanonicalVars => new StarsVar(2);
public Venerate() : base(1, CardType.Skill, CardRarity.Basic, TargetType.Self) { }
protected override async Task OnPlay(...)
{
    await CreatureCmd.TriggerAnim(...);
    await PlayerCmd.GainStars(base.DynamicVars.Stars.BaseValue, base.Owner);
}
protected override void OnUpgrade() { base.DynamicVars.Stars.UpgradeValueBy(1m); }
```

Text: `"VENERATE.description": "Gain {Stars:starIcons()}."` — upgrade takes it
to 3.

The starter deck therefore ships **one generator and one spender**, and the
spender is the Basic Attack. `FallingStar` costs **0 energy and 2 Stars**
(`Models.Cards/FallingStar.cs:16` `public override int CanonicalStarCost =>
2;`). That is the whole idea in the opening hand: the character's cheapest
real attack is bought with Stars rather than energy.

### 1.2 The starting relic — Divine Right

`Models.Relics/DivineRight.cs`, complete:

```csharp
public sealed class DivineRight : RelicModel
{
    public override RelicRarity Rarity => RelicRarity.Starter;
    protected override IEnumerable<DynamicVar> CanonicalVars => new StarsVar(3);

    public override async Task AfterRoomEntered(AbstractRoom room)
    {
        if (room is CombatRoom)
        {
            await PlayerCmd.GainStars(base.DynamicVars.Stars.BaseValue, base.Owner);
        }
    }
}
```

**Answering the question directly: it is per COMBAT, not per room and not
run-persistent.** The hook is `AfterRoomEntered`, but the body gates on `room
is CombatRoom`, so a shop, a rest, a treasure or an event grants nothing. And
because Stars live on the per-combat state (§4), the 3 it grants is
functionally *"start every fight at 3 Stars"* — which is exactly how the card
text words it:

```
"DIVINE_RIGHT.description": "At the start of each combat, gain {Stars:starIcons()}."
```

Our own `game_ref/regent_char_facts.yaml` records the relic as unmodelled and
says the counter is "exercised on room entry"; the combat gate is the part
that note does not carry.

### 1.3 Anything else in the base kit

Nothing. The other seven Regent relics (`Models.RelicPools/RegentRelicPool.cs`)
are not starters and only two touch Stars at all:

- `LunarPastry` (**Rare**) — `StarsVar(1)`, `AfterSideTurnEnd` → +1 Star per
  turn. This is the only relic that generates Stars on a schedule.
- `GalacticDust` — counts Stars **spent** (`_starsSpent`, `ShowCounter`), a
  payoff rather than a source.
- `MiniRegent` (Rare) — `AfterStarsSpent` → +1 Strength, once per turn. Payoff.
- `FencingManual`, `OrangeDough`, `Regalite`, `VitruvianMinion` — Forge, card
  generation, block, minion damage. No Stars.

There is one Common potion: `Models.Potions/StarPotion.cs`, `StarsVar(3)`,
`"STAR_POTION.description": "Gain {Stars:starIcons()}."`

---

## 2. Full generator census

Population: the 91 cards enumerated by `Models.CardPools/RegentCardPool.cs`
(`ModelDb.Card<…>()` calls, de-duplicated). Rarity mix of that pool: **Basic
4, Common 20, Uncommon 38, Rare 27, Ancient 2**.

A card counts as a generator if its source contains `PlayerCmd.GainStars`,
applies `StarNextTurnPower`, or applies `GenesisPower`.

| card | rarity | energy | type | Stars | upgrade | conditions |
|---|---|---|---|---|---|---|
| `Venerate` | Basic | 1 | Skill | **2** | Stars +1 | none |
| `GatherLight` | Common | 1 | Skill | **1** | Block +3 (Stars unchanged) | none — also 8 Block |
| `Glow` | Common | 1 | Skill | **1** | Stars +1 | none — also draw 1, draw 1 next turn |
| `HiddenCache` | Common | 1 | Skill | **1 now + 3 next turn** | next-turn +1 | none |
| `SolarStrike` | Common | 1 | Attack | **1** | Damage +1 **and Stars +1** | none — 9 damage |
| `Convergence` | Uncommon | 1 | Skill | **1 next turn** | Stars +1 | none — also 1 energy next turn, Retain hand |
| `KnockoutBlow` | Uncommon | 3 | Attack | **5** | Damage +8 (Stars unchanged) | **only if the attack kills** |
| `RoyalGamble` | Uncommon | 0 | Skill | **9** | gains Retain | **costs 5 Stars to play**; Exhaust |
| `ShiningStrike` | Uncommon | 1 | Attack | **2** | Damage +3 | none — 8 damage, returns to top of draw |
| `BigBang` | Rare | 0 | Skill | **1** | gains Innate | Exhaust; also draw 1, +1 energy, Forge 5 |
| `Genesis` | Rare | 2 | Power | **2 per turn** | +1 per turn | permanent for the combat |

Eleven generators. The two next-turn ones ride
`Models.Powers/StarNextTurnPower.cs`, which fires on `AfterEnergyReset` and
then removes itself; `GenesisPower` fires on the same hook and does not.

**Count by rarity, and the ratio to spenders** (spender = has a Star cost,
§3):

| rarity | pool | generators | spenders | generators : spenders |
|---|---|---|---|---|
| Basic | 4 | 1 (`Venerate`) | 1 (`FallingStar`) | 1 : 1 |
| Common | 20 | 4 | 4 | 1 : 1 |
| Uncommon | 38 | 4 | 10 | 1 : 2.5 |
| Rare | 27 | 2 | 6 | 1 : 3 |
| Ancient | 2 | 0 | 2 | 0 : 2 |
| **total** | **91** | **11 (12.1%)** | **23 (25.3%)** | **1 : 2.1** |

`RoyalGamble` is in both columns (pay 5, gain 9). The shape is the stinginess
[USER] described from memory, and it is sharper than "a bit stingy": **the
pool is twice as full of things to spend Stars on as things that make them,
and the imbalance grows with rarity.** At Basic and Common the economy is
exactly break-even one-for-one; every rarity above that sells you sinks.

---

## 3. Spending

### 3.1 `ForgeStars` is not a spend verb — the spend is a second cost field

There is no "ForgeStars" effect. A Star price is a **card property**, declared
next to the energy cost and paid at the same moment:

`Models/CardModel.cs:410`
```csharp
public virtual int CanonicalStarCost => -1;      // -1 = "no star cost"
public int BaseStarCost { … }                     // mutable copy
public bool HasStarCostX { … }                    // X-cost in Stars
public TemporaryCardCost? TemporaryStarCost => _temporaryStarCosts.LastOrDefault();
public event Action? StarCostChanged;
```

### 3.2 Alternative, additional, or effect-time? — **ADDITIONAL**

Unambiguous, from `Entities.Players/PlayerCombatState.cs:197`:

```csharp
public bool HasEnoughResourcesFor(CardModel card, out UnplayableReason reason)
{
    int num  = Math.Max(0, card.EnergyCost.GetWithModifiers(CostModifiers.All));
    int num2 = Math.Max(0, card.GetStarCostWithModifiers());
    if (num > Energy && card.CombatState != null
        && Hook.ShouldPayExcessEnergyCostWithStars(card.CombatState, _player))
    {
        num2 += (num - Energy) * 2;
        num = Energy;
    }
    reason = UnplayableReason.None;
    if (num  > Energy) reason |= UnplayableReason.EnergyCostTooHigh;
    if (num2 > Stars ) reason |= UnplayableReason.StarCostTooHigh;
    return reason == UnplayableReason.None;
}
```

Both are checked, and both must pass. A card with `cost 1, ★3` needs 1 energy
**and** 3 Stars. Regent's designers get the *feel* of an alternative cost by
printing **energy 0** on most Star cards — 13 of the 23 spenders cost 0
energy, including the Basic `FallingStar` — but the engine has one shape:
**energy cost and Star cost are two independent additive prices.**

The payment mirror is `Models/CardModel.cs:1806` `SpendResources()`, which
returns `(energySpent, starsSpent)`, calls `SpendEnergy` then `SpendStars`,
and fires `Hook.AfterStarsSpent`. Both prices are paid **before** the card's
effects resolve, at the top of the card play.

### 3.3 How playability is gated

Not a per-card `IsPlayable` override — it is a first-class unplayable reason.
`Entities.Cards/UnplayableReason.cs:29` `StarCostTooHigh = 0x20`, produced by
`HasEnoughResourcesFor` above and consumed by `CardModel.CanPlay`. The card
sits in hand, greyed, exactly like an unaffordable energy cost.

There is also a **cost-modifier hook**, so a Star price can be changed by
anything on the board: `Models/AbstractModel.cs:2078`

```csharp
public virtual bool TryModifyStarCost(CardModel card, decimal originalCost,
                                      out decimal modifiedCost)
```

fanned out by `Hooks/Hook.cs:2168 ModifyStarCost` and read for display by
`Helpers.Models/CardCostHelper.cs:118 TryModifyStarCostWithHooks`. **No
shipped model overrides it**; the only implementor in the assembly is
`Models.Powers.Mocks/MockModifyStarCostPower`. The extension point exists and
is unused.

### 3.4 The one either/or mechanism, and it is not shipped

`Hook.ShouldPayExcessEnergyCostWithStars` (default `false`,
`AbstractModel.cs:2336`) converts a **shortfall** in energy into Stars at
**2 Stars per missing energy**, automatically, with no prompt. Its card text
survives in the loc blob:

```
"RESERVES.description": "If you don't have enough {energyPrefix:energyIcons(1)}
 for a card, 2{singleStarIcon} are used per {energyPrefix:energyIcons(1)} instead."
```

**But `Reserves` does not exist in v0.111.0.** No class, no `ModelDb`
registration, no pool membership — a grep for the string `Reserves` across the
whole decompile hits exactly one unrelated file
(`GameActions.Multiplayer/PlayerChoiceSynchronizer.cs`). The same is true of
`VISIONS_OF_GRANDEUR` ("If you have N★, draw N cards") and `PITY` ("Gain ★ for
every N HP healed"): loc rows with no implementation. They are cut or
unreleased content.

So the answer to *"does STS2 have an either/or cost UI?"* is: **no.** It has
one automatic fallback conversion at a fixed 2:1 rate, which nothing in the
shipped game turns on, and which asks the player nothing.

### 3.5 Every spender

23 cards. `★` is `CanonicalStarCost`.

| card | rarity | energy | ★ | type | effect |
|---|---|---|---|---|---|
| `FallingStar` | Basic | 0 | 2 | Attack | 8 damage, 1 Weak, 1 Vulnerable |
| `AstralPulse` | Common | 0 | 3 | Attack | damage to ALL enemies, twice |
| `CloakOfStars` | Common | 0 | 1 | Skill | 7 Block |
| `CrescentSpear` | Common | 1 | 1 | Attack | 8 + 2 damage per Star-costed card you own |
| `GuidingStar` | Common | 1 | 1 | Attack | 12 damage, draw 1 next turn |
| `Alignment` | Uncommon | 0 | 2 | Skill | gain energy |
| `Constellation` | Uncommon | 0 | 2 | Skill | **co-op only** — ally draws 1, +1 energy, 9 Block |
| `Devastate` | Uncommon | 1 | 4 | Attack | large single-target damage |
| `GammaBlast` | Uncommon | 0 | 3 | Attack | damage + Weak + Vulnerable |
| `ParticleWall` | Uncommon | 0 | 2 | Skill | Block, returns to hand |
| `Quasar` | Uncommon | 0 | 2 | Skill | choose 1 of 3 Colorless into hand |
| `Reflect` | Uncommon | 1 | 3 | Skill | Block; blocked damage reflected this turn |
| `Resonance` | Uncommon | 1 | 2 | Skill | +Strength; all enemies −1 Strength |
| `RoyalGamble` | Uncommon | 0 | 5 | Skill | **gain 9 Stars**; Exhaust |
| `Stardust` | Uncommon | 0 | **X** | Attack | 5 damage to a random enemy, X times |
| `Comet` | Rare | 0 | 5 | Attack | big damage + Weak + Vulnerable |
| `DecisionsDecisions` | Rare | 0 | 6 | Skill | draw; play a Skill from hand N times |
| `DyingStar` | Rare | 1 | 3 | Attack | 9 to ALL; all enemies lose Strength this turn |
| `NeutronAegis` | Rare | 1 | 5 | Power | Plating |
| `SevenStars` | Rare | 2 | 7 | Attack | 7 damage to ALL enemies, N times |
| `TheSmith` | Rare | 1 | 4 | Skill | Forge 10 |
| `MeteorShower` | Ancient | 0 | 2 | Attack | AoE damage + Weak + Vulnerable to all |
| `TheSealedThrone` | Ancient | 1 | 3 | Power | gain ★ whenever you play a card |

**Cheapest sinks are 1★** (`CloakOfStars`, `CrescentSpear`, `GuidingStar`);
the Basic sink is 2★; the median printed price across all 23 is **3★**.

`Stardust` is the X case (`HasStarCostX => true`), resolved by
`CardModel.ResolveStarXValue()` — it spends the whole bank and hits that many
times.

### 3.6 Cards that read Stars without spending them

- **`Radiate`** (Uncommon, 0 energy, no Star cost) — the `StarsModifiedEntry`
  reader named in the brief. Its `CalculatedHits` var sums every positive
  `StarsModifiedEntry` this turn by this creature:
  ```csharp
  new CalculatedVar("CalculatedHits").WithMultiplier((card, _) =>
      CombatManager.Instance.History.Entries.OfType<StarsModifiedEntry>()
        .Where(e => e.HappenedThisTurn(card.CombatState) && e.Amount > 0
                    && e.Actor == card.Owner.Creature)
        .Sum(e => e.Amount));
  ```
  Text: *"Deal N damage to ALL enemies for each ★ gained this turn. (Hits N
  times)"* — it pays **nothing** and scales on **income**, not on bank size.
- **`CrescentSpear`** — scales on how many Star-costed cards are in your
  combat deck (`c.CanonicalStarCost >= 0 || c.HasStarCostX`), a *deckbuilding*
  read rather than a resource read.
- **`ChildOfTheStarsPower`** — `AfterStarsSpent` → Block per Star spent.
- **`BlackHolePower`** — damage all enemies on **spend or gain**, with an
  explicit note that it uses `AfterCardPlayed` rather than `AfterStarsSpent`
  because *"stars are spent at the beginning of the card play"*.
- **`GalacticDust`**, **`MiniRegent`** — relic payoffs on `AfterStarsSpent`.

---

## 4. Persistence and cap

**Stars do not persist across combats.** The counter is a field on
`PlayerCombatState` (`Entities.Players/PlayerCombatState.cs:109`), and
`Entities.Players/Player.cs:800` throws the whole object away between fights:

```csharp
/// Resets the player's combat state to an empty state.
public void ResetCombatState() { PlayerCombatState = new PlayerCombatState(this); }
```

`_stars` has no initialiser, so a fresh combat starts at **0**; Divine Right
then puts it at 3. There is no run-level Star field, no save field, nothing in
`Player`'s serialisable state. **This makes Divine Right's grant per-fight
income, not a run bank**, and the card text agrees.

**There is no cap.** `GainStars` clamps only at the bottom:

```csharp
public void GainStars(decimal amount)
{
    if (amount < 0m) throw new ArgumentException("Must not be negative.", "amount");
    Stars = (int)Math.Max((decimal)Stars + amount, 0m);
}
public void LoseStars(decimal amount) { … Stars = (int)Math.Max(Stars - amount, 0m); }
```

Contrast `GainEnergy`, four lines up, which clamps to `999999999`. Stars have
**no ceiling and no overflow rule at all** — [USER]'s "Regent doesn't cap its
stars" is exactly right, and the game does not even carry a nominal maximum.
The setter emits a `StarsModifiedEntry` on every change
(`Combat.History.Entries/StarsModifiedEntry.cs`), which is what `Radiate`
reads.

---

## 5. Display

Three separate surfaces, and the important one is that **the price is never in
the rules text**.

### 5.1 A dedicated cost badge on the card face

`Nodes.Cards/NCard.cs:1044` — a `_starIcon` / `_starLabel` pair beside the
energy orb, with its own colour rules:

```csharp
private void UpdateStarCostVisuals(PileType pileType)
{
    …
    if (Model.HasStarCostX) { _starLabel.SetTextAutoSize("X"); _starIcon.Visible = true; }
    else {
        _starLabel.SetTextAutoSize(Model.GetStarCostWithModifiers().ToString());
        _starIcon.Visible = Model.GetStarCostWithModifiers() >= 0;
    }
    UpdateStarCostColor(pileType);
    …
}
```

The badge is what `-1` means: a card with no Star cost simply hides the icon,
and `NCard.cs:929` even shifts the enchantment tab up 45px when there is no
star badge to make room for. Colour comes from
`Helpers.Models/CardCostHelper.cs:52 GetStarCostColor`, which turns the number
red on `UnplayableReason.StarCostTooHigh` and recolours it when a hook or a
`TemporaryStarCost` has moved it — the same affordance energy costs get.
`StsColors.cs:81` `defaultStarCostOutline = #175561DC`.

### 5.2 The persistent counter

`Nodes.Combat/NStarCounter.cs`, subscribed to `PlayerCombatState.StarsChanged`.
Its visibility rule (line 303):

```csharp
base.Visible = base.Visible || _player.Character.ShouldAlwaysShowStarCounter || stars > 0;
```

`CharacterModel.ShouldAlwaysShowStarCounter` defaults to `false` and **Regent
overrides it to `true`** — so the bank is on screen from turn one of every
fight whether or not it holds anything.

### 5.3 Text, and what text never says

Gains are printed with a formatter that renders **N repeated star sprites**
rather than a numeral —
`Localization.Formatters/StarIconsFormatter.cs`, name `starIcons`, emitting
`[img]res://images/packed/sprite_fonts/star_icon.png[/img]` once per point.
`{singleStarIcon}` is the same glyph used as a noun.

```
"VENERATE.description":       "Gain {Stars:starIcons()}."
"GATHER_LIGHT.description":   "Gain {Block:diff()} [gold]Block[/gold].\nGain {Stars:starIcons()}."
"SOLAR_STRIKE.description":   "Deal {Damage:diff()} damage.\nGain {Stars:starIcons()}."
"HIDDEN_CACHE.description":   "Gain {Stars:starIcons()}.\nNext turn, gain {StarNextTurnPower:starIcons()}."
"KNOCKOUT_BLOW.description":  "Deal {Damage:diff()} damage.\nIf this kills an enemy, gain {Stars:starIcons()}."
"GENESIS.description":        "At the start of your turn, gain {StarsPerTurn:starIcons()}."
"ROYAL_GAMBLE.description":   "Gain {Stars:diff()} {singleStarIcon}."
"CONVERGENCE.description":    "Next turn,\ngain {Energy:energyIcons()} and {Stars:starIcons()}.\n[gold]Retain[/gold] your [gold]Hand[/gold] this turn."
"DIVINE_RIGHT.description":   "At the start of each combat, gain {Stars:starIcons()}."
"STAR_POTION.description":    "Gain {Stars:starIcons()}."
"CHILD_OF_THE_STARS.description": "Whenever you spend {singleStarIcon}, gain {BlockForStars:diff()} [gold]Block[/gold] for each {singleStarIcon} spent."
"CRESCENT_SPEAR.description": "Deal {CalculatedDamage:diff()} damage.\nDeals {ExtraDamage:diff()} additional damage for ALL your cards that have a {singleStarIcon} cost."
"RADIATE.description":        "Deal {Damage:diff()} damage to ALL enemies for each {Stars:starIcons()} gained this turn.{InCombat:\n(Hits {CalculatedHits:diff()} {CalculatedHits:plural:time|times})|}"
```

Now the spenders:

```
"FALLING_STAR.description":  "Deal {Damage:diff()} damage.\nApply {WeakPower:diff()} [gold]Weak[/gold].\nApply {VulnerablePower:diff()} [gold]Vulnerable[/gold]."
"CLOAK_OF_STARS.description":"Gain {Block:diff()} [gold]Block[/gold]."
"SEVEN_STARS.description":   "Deal {Damage:diff()} damage to ALL enemies {Repeat:diff()} {Repeat:plural:time|times}."
"THE_SMITH.description":     "[gold]Forge[/gold] {Forge:diff()}."
"STARDUST.description":      "Deal X times {Damage:diff()} damage to a random enemy."
```

**Not one spender's text mentions its Star price.** `FallingStar` reads as a
plain 0-cost attack; the 2★ is only on the badge. `SevenStars` says nothing
about the 7★ that gave it its name. The badge is the sole carrier of the
price, exactly as the energy orb is for energy — and `Stardust`'s "X" is
resolved by the badge too. That is a deliberate and quite strict UI
convention: **a resource cost lives in the cost corner, never in the rules
box; rules text only ever talks about gains and payoffs.**

---

## 6. Stinginess, quantified

The setup, all from §1: **3 energy per turn; 10-card deck; Divine Right = 3★
at the start of every fight; Venerate = 2★, one copy; FallingStar = 2★, one
copy.**

A 10-card deck with a 5-card draw cycles **every two turns**, so each single
copy is seen once per two turns. That gives, per turn averaged:

| flow | per turn | per 2-turn cycle |
|---|---|---|
| income from Venerate | **+1.0★** | +2★ |
| the only sink you own (FallingStar) | **−1.0★** | −2★ |
| net | **0** | **0** |

**The base kit is exactly break-even, with a 3★ opening buffer.** Over a
typical four-turn fight: 3 (relic) + 2 + 2 = **7★ generated**, and the deck's
own spender wants 2★ twice = **4★ spent**, leaving 3★ on the table at the
kill. Over a five-turn fight it is 9★ in and 6★ out.

Two more ways to say the same number, both useful as targets:

- **Per fight, the base kit makes 7★** (3 relic + 2 Venerate plays over four
  turns), of which the relic is **43%**. The relic is the largest single
  source in the starter kit and it is a flat, unsteerable, per-fight grant.
- **Income is 1★/turn from cards, plus a one-time 3.** The cheapest sink in
  the whole pool is **1★** and the average printed price is **3★**. So a
  base-kit Regent can afford *one* median-priced sink every three turns, or
  the pool's cheapest sink every turn — and cannot afford `SevenStars` (7★)
  before turn four without drafting generation.

**That ratio is what "matching the generation pattern" means:** income and
expenditure balanced at 1:1 in the starter kit, a fixed 3-point buffer from
the relic so turn one is never dead, a cheapest sink priced at one turn of
income, and a *median* sink priced at three turns of income — so leaning into
the plan means drafting generation, and not leaning into it still leaves your
Basic star-Attack playable every cycle.

Per **run-room**, the relic pays 3★ at each of the 16 floors' combat rooms
only — roughly 10–11 fights on the pinned map (`MAP_FLOORS = 16`, room odds
`N 0.53 / E 0.08 / B`), so ~30–33★ of relic income across a run — but the
number is not cumulative in any sense that matters: it resets to 0 every
fight, so the only meaningful unit is **per fight**.

---

## 7. What the decompile does not answer

- **The intended draft rate.** Nothing in the assembly says how many
  generators a Regent player is *expected* to pick up; the 1:2.1 pool ratio is
  a supply fact, not a play fact.
- **Whether `Reserves` was cut or is unreleased.** Its loc row exists, its
  hook exists and defaults off, its class does not. We can say it does not
  ship in v0.111.0. We cannot say why.
- **`GalacticDust`'s full body** was read only as far as its counter fields
  for this note; its trigger threshold is `DynamicVars.Stars.IntValue` but the
  reward it grants was not transcribed. Not needed for any question here.
- **Any balance intent behind the numbers.** No comments in the shipped
  assembly discuss Star tuning.
