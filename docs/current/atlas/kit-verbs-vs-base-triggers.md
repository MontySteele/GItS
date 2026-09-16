# Kit verbs vs base-game triggers

> **Lifecycle: LIVING.** `EB-495`. The table nobody had: for each named kit
> effect, which base-game trigger sees it, and as WHAT. Answered per cell in
> BOTH engines, with the code site that decides it. This is a map, not a
> proposal — where the two engines disagree, or where a card face promises
> what the trigger does not deliver, the disagreement is recorded in §6 and
> the row is minted elsewhere. **Nothing here changed behaviour.**

Pinned by `tier0/tests/test_eb495_kit_verb_triggers.py` (the sim column and
the C# call sites, read off source) and
`klee-mod/KleeTests/KitVerbBaseTriggerPinTests.cs` +
`klee-mod/KleeTests/Prototype/KitVerbBaseTriggerProtoPinTests.cs` (the call
graph, read off the real `klee.dll` and the real `sts2.dll`). A cell that
moves fails a pin.

Decompiles cited below are from `sts2.dll` at the pinned build (v0.111.0,
`41cef1ea`); retrieve with
`ilspycmd -t <Full.Type.Name> "…/data_sts2_windows_x86_64/sts2.dll"`.

---

## 1. The one mechanism that decides every C# cell

The base game has **no** "is this an Attack" flag on a damage instance. It has
two separate things, and every trigger reads one of them:

* **`CardType.Attack`** (`MegaCrit.Sts2.Core.Entities.Cards.CardType`) — a
  property of the CARD. Read by the card-play triggers off `cardPlay.Card.Type`.
* **`ValueProp`** (`MegaCrit.Sts2.Core.ValueProps.ValueProp`) — a bitflag on the
  damage instance: `Move` (2^3) = "attack damage from an Attack card or an
  enemy move", `Unpowered` = "from a relic, potion or power", `Unblockable` =
  "HP loss". The test every damage trigger uses is
  `ValuePropExtensions.IsPoweredAttack()`:

  ```csharp
  public static bool IsPoweredAttack(this ValueProp props)
  {
      if (props.HasFlag(ValueProp.Move)) return !props.HasFlag(ValueProp.Unpowered);
      return false;
  }
  ```

Three further facts settle the rest:

1. **`Hook.BeforeAttack` / `Hook.AfterAttack` fire from exactly two places** —
   `AttackCommand.Execute` (`Commands.Builders/AttackCommand.cs:550`, `:673`)
   and `AttackContext` (`:47`, `:74`). Damage that does not go through an
   `AttackCommand` cannot reach them, whatever its props.
2. **`ValueProp.Move` is a property of the HIT, not of the card's `type:`.**
   Every damage clause the mod's generator emits is
   `DamageCmd.Attack(...).FromCard(card, cardPlay)`, whose `DamageProps`
   default is `ValueProp.Move` — so a **Skill** that deals damage is a powered
   attack to every damage trigger. This is `EB-521`'s finding, generalised.
3. **Every kit verb's damage leaves the mod through one door**,
   `ElementalHit.Deal` (`klee-mod/KleeCode/Powers/ElementalHit.cs:84`), whose
   terminal call is

   ```csharp
   await CreatureCmd.Damage(
       choiceContext, target, landed,
       ignoreBlock ? ValueProp.Unpowered | ValueProp.Unblockable : ValueProp.Unpowered,
       dealer: null, cardSource: null, cardPlay: null);      // ElementalHit.cs:120
   ```

   `Unpowered`, `dealer: null`, `cardSource: null`, no `AttackCommand`. That
   single line is why almost the whole matrix below reads `none`: the mod
   re-implements the damage pipeline itself (`Powers/SimDamagePipeline.cs`) and
   hands the game a finished number, so the base game's own attack-side
   machinery is bypassed by construction rather than by accident.

The one exception is `ProtoBombPower.DealCardDamage`
(`Powers/Prototype/ProtoBombPower.cs:1310`), the Set-off card's OWN printed
hit, which is a real `DamageCmd.Attack(...).FromCard(...)` and therefore a real
Attack.

## 2. The one mechanism that decides every sim cell

`tier0` has no hook broadcast and no `ValueProp`. It has:

* **`source`**, a string parameter on
  `effects.deal_damage_to_enemy(state, enemy, base, element, source, ignore_block, powered)`
  (`tier0/engine/effects.py:884`). `"attack"` is minted in exactly one place,
  `_op_damage` at `effects.py:1440`:
  `source = "attack" if card.type == "attack" else "card"`. **Every "does this
  count as an Attack" test in the sim is `source == "attack"`**, and it is
  therefore a fact about the card's declared `type:`, not about the hit.
* **`powered`**, a bool that drops the dealer's Strength and Weak
  (`powers.modify_damage_dealt`) and nothing else — the sim twin of
  `ElementalHit.Deal(..., powered: false)`.
* **`card.type == "attack"`**, read by the card-play mirrors in
  `refpowers.before_card_played` / `after_card_played`.

* **`refpowers.enemy_on_damage_received`**, the ENEMY's own
  `Hook.AfterDamageReceived`, driven from `deal_damage_to_enemy` and from
  nowhere else. It was built on 2026-09-16 (D5 and D6); before that the sim
  modelled no enemy-side "took damage" power except Skittish, and that one
  absence filled the whole T5 and T6 columns.
  `refpowers.on_damage_received` remains the PLAYER's funnel and reads
  `state.player.powers` only.

---

## 3. The trigger columns

| # | trigger, as a face says it | exact hook | the predicate that decides it | base-game readers |
|---|---|---|---|---|
| **T1** | "whenever you play a card" | `Hook.BeforeCardPlayed` (`Models/CardModel.cs:1926`), `Hook.AfterCardPlayed` (`:1965`) | none — every play | `Pocketwatch:35`, `BrilliantScarf:89`, `VelvetChoker:64`, `EchoFormPower:76`, enchantments `Glam:43` / `Goopy:30` |
| **T2** | "whenever you play an Attack" | the same hook | `cardPlay.Card.Type == CardType.Attack` | `ArtOfWar:65`, `RippleBasin:38`, `PenNib:138`; the mirror-image filters are `MummifiedHand:26` (Power) and `MasterPlannerPower:21` (Skill) |
| **T3** | "when you attack" | `Hook.BeforeAttack` (`AttackCommand.cs:550`), `Hook.AfterAttack` (`:673`) | an `AttackCommand` exists at all, then `command.DamageProps.IsPoweredAttack()` | `VigorPower:36`, `GigantificationPower:42`, `PainfulStabsPower:36`, `SuckPower:24`, `HellraiserPower:80`, `BoneFlute:19` (no props filter); **`SkittishPower:58` is the loose one** — `DamageProps.HasFlag(ValueProp.Move) && ModelSource is CardModel`, powered or not |
| **T4** | "whenever you deal damage" | `Hook.AfterDamageGiven` (`Commands/CreatureCmd.cs:412`) | `dealer == Owner && props.IsPoweredAttack() && result.UnblockedDamage > 0` | `EnvenomPower:22`, `PaperCutsPower:18`, `ReaperFormPower:59` |
| **T5** | "when it takes unblocked damage" | `Hook.AfterDamageReceived` (`CreatureCmd.cs:416`) | `result.UnblockedDamage > 0`, **no attack filter** | `EmotionChip:31`, `LavaLamp:52` (also excludes `ValueProp.Unblockable`), `HardenedShellPower:62`, `BeatingRemnant:71` |
| **T6** | "when hit by an attack, retaliate" | `Hook.BeforeDamageReceived` (`CreatureCmd.cs:285`) / `AfterDamageReceived` | `dealer != null && props.IsPoweredAttack()` | `ThornsPower:19`, `FlameBarrierPower:20`, `CurlUpPower:40` (also `cardSource != null`) |
| **T7** | Strength / Weak / Vulnerable / Slow on the number | `Hook.ModifyDamage(..., ModifyDamageHookType.All)` → `AbstractModel.ModifyDamageAdditive` / `…Multiplicative` / `…Cap` | `props.IsPoweredAttack()` | `VigorPower:64`, `GigantificationPower:65`, `SlowPower:46`, `PenNib:108`, enchantment `Vigorous:24` |
| **T8** | "when you apply a debuff" | `Hook.BeforePowerAmountChanged` (`Commands/PowerCmd.cs:124`), `Hook.AfterPowerAmountChanged` (`:160`) | `power.GetTypeForAmount(amount) == PowerType.Debuff` (`Models/PowerModel.cs:460`), plus `cardSource != null` and `applier == Owner` for `UnsettlingLamp:72-106`; `ArtifactPower:24` has no `cardSource` gate |

## 4. The verb rows

Every C# call site below is the *shared helper*, not a per-card copy.

| # | verb | C# call site | sim call site |
|---|---|---|---|
| V1 | Attack-card damage (baseline) | `DamageCmd.Attack(...).FromCard(...)`, ~160 card bodies | `effects._op_damage` → `deal_damage_to_enemy(source="attack")`, `effects.py:1589` |
| V2 | Non-Attack-card damage (17 Skills/Powers) | the same `DamageCmd.Attack(...).FromCard(...)` | the same op, `source="card"` |
| V3 | Card HP-loss / self damage | `CreatureCmd.Damage(..., Unblockable\|Unpowered, this, cardPlay)` | `_op_damage` `target: self`, direct `p.hp -=`, `effects.py:1443` |
| V4 | Bomb detonation (shipped) | `BombPower.ResolvePayload` → `ElementalHit.Deal`, `BombPower.cs:838` | `effects.detonate_bombs`, `source="bomb"`, `effects.py:1146` |
| V5 | Bomb explosion / Set off (overhaul) | `ProtoBombPower.Explode` → `ElementalHit.DealWithoutDealerMods`, `:1463` | `klee_overhaul._explode`, `source="set_off"`, `powered=False`, `klee_overhaul.py:562` |
| V6 | Mine trigger | `ProtoBombPower.BeforeDamageReceived:1684` → `Explode` | `klee_overhaul.mines_answer_attack:694` → `_explode`; fired from `combat.py:1516` |
| V7 | the Set-off card's OWN hit | `ProtoBombPower.DealCardDamage`, `:1315` | `_op_set_off` delegates back to `_op_damage`, `effects.py:5665` |
| V8 | Bomb echo (Sparks 'n' Splash) | `KleeOverhaulPowers.cs:259` → `ElementalHit.Deal` | `klee_overhaul.py:964`, `source="bomb_echo"` |
| V9 | Planned hit / Plan carry-out | `KokomiPlan.Hit` → `ElementalHit.Deal(..., powered: false)`, `KokomiPlan.cs:2477` | `kokomi_plan._hit`, `source="plan"`, `powered=False`, `kokomi_plan.py:1494` |
| V10 | Plan debuff | `KokomiPlan.Debuff<T>` → `PowerCmd.Apply(applier: kokomi, cardSource: null)`, `:2497` | `kokomi_plan._debuff` → `powers.apply_power(applier=player)`, `:1499` |
| V11 | Tamakushi Casket strike (relic) | `TamakushiCasket.Strike` → `ElementalHit.Deal`, `:190` | `kokomi_plan.casket_strike`, `source="casket"`, `powered=False`, `:1749` |
| V12 | Salon performance (tick / deploy-perform) | `SalonMemberPower.PerformMember` → `ElementalHit.Deal(..., powered: false)`, `SalonPowers.cs:979` | `effects.salon_member_act`, `source="salon"`, `powered=False`, `effects.py:7137` |
| V13 | Salon bow / Evoke | `SalonMemberPower.Bow` → `ElementalHit.Deal`, `SalonPowers.cs:540` | `effects._salon_bow`, `source="salon_final_bow"`, `effects.py:1941` |
| V14 | Stage act (performance) | `FurinaStage.Perform` → `ElementalHit.Deal(..., powered: false)`, `FurinaStage.cs:460`, `:474` | `furina_stage.perform`, `source="furina_stage/act"`, `furina_stage.py:669`, `:685` |
| V15 | Stage bow | `FurinaStage.Bow` → `ElementalHit.Deal(..., powered: false)`, `:541` | `furina_stage._bow`, `source="furina_stage/bow"`, `:334` |
| V16 | Stage Spend | `FurinaStage.Spend:360` — **no damage of its own**; the card's own `damage` clause carries it | `furina_stage.spend:510` — likewise |
| V17 | Companion / summon pulse (Evoke-class) | ~22 `*.FireVolley` → `ElementalHit.Deal` (§7 of the census) | `source="companion"` at 22 sites |
| V18 | Aura application only (no damage) | `ElementalHit.ApplyOnly:159` | `reactions.resolve_hit(..., 0, ...)`, ops `apply_aura` / `swirl` |
| V19 | Reaction-applied debuff (Superconduct / Frozen / Overload / ElectroCharged) | `ReactionEffects.cs:445`, `:483`, `:528`, `:538` — `PowerCmd.Apply(applier: dealer, cardSource: cardSource)` | `reactions._react`, `reactions.py:138` |
| V20 | Overload splash | `ReactionEffects.cs:519`, `Unblockable\|Unpowered`, `dealer: null` | `reactions._splash`, direct HP, `reactions.py:295` |
| V21 | Shatter | `FrozenPower.cs:132`, `Unblockable\|Unpowered` | `effects.py:1048` |
| V22 | Detonation splash | `DemolitionPowers.cs:192`, `Unblockable\|Unpowered`, `dealer: null` | `effects.py:1158`, `source="detonation_splash"` |
| V23 | Detonation Vulnerable | `DemolitionPowers.cs:239`, `PowerCmd.Apply(cardSource: null)` | `effects.py:1177`, `powers.apply_power` |
| V24 | Spark spend | `SparkPower.Spend:301` → `PowerCmd.ModifyAmount` — **no damage** | `effects._op_spend_spark:2506` — likewise |

There is **no mod-side potion**: all three characters return
`ModelDb.PotionPool<SilentPotionPool>()` (`Klee.cs:96`, `Furina.cs:57`,
`Kokomi.cs:73`), so "potion damage" is a base-game verb and not a kit one.

---

## 5. THE MATRIX

One word per cell. When the two engines agree the cell is one word; when they
do not it is written **`C# ≠ sim`** and carries a `D`-number from §6.

**Legend.** `Attack` — the trigger fires and the effect counts as an Attack
(`CardType.Attack` for T1/T2, an `AttackCommand` or `IsPoweredAttack()` for
T3–T7; `source == "attack"` in the sim). `damage-only` — the trigger fires but
the effect is not an Attack. `debuff` — the trigger fires as a debuff
application. `none` — the trigger does not fire. There is no `none*` left:
that mark meant "does not fire because the engine has no mirror of that
trigger at all", it carried the whole T5 and T6 columns, and D5 and D6 built
the two mirrors on 2026-09-16.

| verb | T1 card played | T2 played an Attack | T3 you attack | T4 you deal damage | T5 takes unblocked damage | T6 retaliation | T7 damage modifiers | T8 applied a debuff |
|---|---|---|---|---|---|---|---|---|
| V1 Attack-card damage | Attack | Attack | Attack | Attack | damage-only (**D5 repaired**) | Attack (**D6 repaired**) | Attack | none |
| V2 non-Attack-card damage | damage-only | none | Attack (**D1 repaired**) | Attack (**D2 repaired**) | damage-only (**D5 repaired**) | Attack (**D6 repaired**) | Attack | none |
| V3 card HP-loss (self) | none | none | none | none | damage-only (**D5 repaired**) | none | none | none |
| V4 Bomb detonation (shipped) | none | none | none | none | damage-only (**D5 repaired**) | none | none | none |
| V5 Bomb explosion / Set off | none | none | none | none | damage-only (**D5 repaired**) | none | none | none |
| V6 Mine trigger | none | none | none | none | damage-only (**D5 repaired**) | none | none | none |
| V7 Set-off card's own hit | Attack | Attack | Attack | Attack | damage-only (**D5 repaired**) | Attack (**D6 repaired**) | Attack | none |
| V8 Bomb echo | none | none | none | none | damage-only (**D5 repaired**) | none | none | none |
| V9 planned hit | none | none | none | none | damage-only (**D5 repaired**) | none | none | none |
| V10 Plan debuff | none | none | none | none | none | none | none | debuff |
| V11 Casket strike | none | none | none | none | damage-only (**D5 repaired**) | none | none | none |
| V12 Salon performance | none | none | none | none | damage-only (**D5 repaired**) | none | none | none |
| V13 Salon bow / Evoke | none | none | none | none | damage-only (**D5 repaired**) | none | none | none |
| V14 Stage act | none | none | none | none | damage-only (**D5 repaired**) | none | none (**D3 repaired**) | debuff (**D4 repaired**) |
| V15 Stage bow | none | none | none | none | damage-only (**D5 repaired**) | none | none (**D3 repaired**) | debuff (**D4 repaired**) |
| V16 Stage Spend | none | none | none | none | none | none | none | none |
| V17 companion pulse | none | none | none | none | damage-only (**D5 repaired**) | none | none | none |
| V18 aura application only | none | none | none | none | none | none | none | none |
| V19 reaction-applied debuff | none | none | none | none | none | none | none | debuff (**D7**) |
| V20 Overload splash | none | none | none | none | none | none | none | none |
| V21 Shatter | none | none | none | none | none | none | none | none |
| V22 detonation splash | none | none | none | none | none | none | none | none |
| V23 detonation Vulnerable | none | none | none | none | none | none | none | debuff |
| V24 Spark spend | none | none | none | none | none | none | none | none |

**24 verbs × 8 triggers = 192 cells per engine, 384 in total.** No cell is
unknown.

### How to read the wall of `none`

That column of `none` under T3/T4/T7 is not a gap in the map — it is the
design, and it is the same design in both engines for the same reason. A kit
verb is a hit the CHARACTER's own rules compute, so it must not be re-scaled
by the game's Strength or doubled by a relic that pays for attacking. C# says
that with `ValueProp.Unpowered` + `dealer: null`; the sim says it with
`source != "attack"`. Both refusals are deliberate, documented at their call
sites, and ruled — `EB-343`/R248 for the Bomb, `EB-334`/R246 for the Plan,
`EB-588` for the Salon.

What the two engines say DIFFERENTLY is §6.

---

## 6. Disagreements

Seven. Four were engine-vs-engine and were repaired on 2026-09-16 (D1–D4);
three were structural absences on the sim side, of which D5 and D6 were built
on 2026-09-16 and D7 stands. Every repair is sim-side only — no C# moved, no
rule moved, and no published sim number moved.

### D1 — a Skill's damage is an Attack to `SkittishPower` — REPAIRED in the sim

`SkittishPower.AfterAttack` gates on
`command.DamageProps.HasFlag(ValueProp.Move) && command.ModelSource is CardModel`
(`Models/Powers/SkittishPower.cs:58`) — the card's `type:` is never read. The
mod's generator emits every damage clause as
`DamageCmd.Attack(...).FromCard(...)`, so the 17 non-Attack cards that deal
damage (`FloodOfEmotion`, `MatineePerformance`, `TakeItFromTheTop`,
`SecretStash`, `StudyOfExplosions`, `ProtoKkAmbush`, … ) **do** wake Skittish
in the game.

The sim's Skittish was inline in `deal_damage_to_enemy` and gated
`source == "attack"`, which is `card.type == "attack"`, and did not fire.
Evidence: `EB-521` already ruled the same asymmetry for Thorns and found the
ENGINE right and the words wrong.

**Repaired 2026-09-16, sim side only.** The gate is now
`source in effects.CARD_DAMAGE_SOURCES` — the two `source` literals
`_op_damage` mints off a card, which is this engine's spelling of
`ModelSource is CardModel`. The negative half is unchanged and is the reason
the repair is narrow: a kit verb mints its own literal and, in the game,
leaves through `ElementalHit.Deal`, which carries no `ModelSource`, so no
Bomb, Plan, Mine or performance wakes Skittish in either engine. Pinned end to
end by `tier0/tests/test_eb495_d1_skittish_wakes_on_a_skill.py`. No published
sim number moved: the whole suite, batteries included, was unchanged by it.

### D2 — likewise for `EnvenomPower` — REPAIRED in the sim

`EnvenomPower.AfterDamageGiven` gates on
`dealer == Owner && props.IsPoweredAttack() && result.UnblockedDamage > 0`
(`Models/Powers/EnvenomPower.cs:22`). A Skill's `DamageCmd.Attack` is
`ValueProp.Move` and powered, so it poisons. The sim's
`refpowers.envenom_on_hit` returned early on `source != "attack"`. Same shape
as D1, different power.

**Repaired 2026-09-16, sim side only.** `envenom_on_hit` now takes the hit's
`powered` flag alongside its `source` and asks for both halves of
`IsPoweredAttack()`: `source in effects.CARD_DAMAGE_SOURCES` for `Move` /
`ModelSource`, and `powered` for the absence of `Unpowered`. The second is
redundant against the first today — every card-sourced call site in tier0 is
powered — and is written anyway, because the C# predicate is the flag and a
future Unpowered card clause must not quietly start poisoning. `UnblockedDamage
> 0` is untouched and pinned beside the repair. Pinned by
`tier0/tests/test_eb495_d2_envenom_takes_a_powered_attack.py`. No published sim
number moved.

### D3 — Furina's Stage act and bow took her Strength in the sim — REPAIRED

`FurinaStage.Perform` and `FurinaStage.Bow` both pass `powered: false`
(`Powers/Prototype/FurinaStage.cs:463`, `:477`, `:544`), the same refusal the
Salon's `PerformMember` makes at `SalonPowers.cs:981`. The sim's
`furina_stage.perform` and `_bow` call `deal_damage_to_enemy` with **no
`powered=` argument at all** (`furina_stage.py:669`, `:685`, `:334`), so the
default `True` applies and `powers.modify_damage_dealt` scales Chevalmarin's
and Crabaletta's numbers by Furina's Strength and Weak. The sim's own Salon
twin one file over does pass `powered=False` (`effects.py:7139`), so this
reads as an omission rather than a decision. The brief's own sentence is the
Salon's — "a performance is not an Attack and not a hit".

**Repaired 2026-09-16, sim side only.** All three sim call sites now pass
`powered=False`. THE BRIEF WAS CHECKED FIRST and it is with the game, so this
is a model catching up and not a rule moving: sec.3 rule 10 calls an act "a
flat act that does not read its bar" and ends "scaling on Fanfare lives in
payoff cards (§5.2), never in the performer". Pinned printed-equals-dealt with
Strength up, with Weak on, and with both, by
`tier0/tests/test_eb495_d3_a_performance_carries_no_strength.py` — Weak
beside Strength because `powered` drops both at one site
(`powers.modify_damage_dealt`), so a Strength-only pin would pass a half
repair. Furina's own cards are untouched and that control is pinned in the
same file. No published sim number moved: the Stage is a prototype arm, no
battery runs it, and the whole suite was unchanged apart from these pins.

### D4 — Crabaletta's act and bow apply Hydro — REPAIRED in the sim

`FurinaStage.cs:461` and `:542` pass `Elements.Element.Hydro`;
`furina_stage.py:685` and `:334` pass no `element=` at all, so the default
`None` applies and the hit neither sets an aura nor consumes one. That is a
reaction difference, so it changes T8: a Crabaletta hit into a standing Electro
aura applies Superconduct's Vulnerable in the game and nothing in the sim. The
Chevalmarin leg of the same two methods DOES pass `"hydro"`, which is what
makes this look like a miss rather than a rule.

**Repaired 2026-09-16, sim side only.** Both Crabaletta legs now pass
`element="hydro"`. THE BRIEF WAS CHECKED and it is SILENT: it names
Chevalmarin's Hydro twice in as many words (rule 10 "deals 2 to every enemy
and applies Hydro", rule 9 "Chevalmarin: Hydro on every enemy") and says only
"Crabaletta deals 5 to a random enemy" and "Crabaletta: deal 8 to a random
enemy". It never says a Crabaletta hit is elementless, so there is no rule for
the C# to contradict and the game is the answer — recorded here because the
reading is the load-bearing part, and writing the brief the other way would
make this a rule change rather than a parity repair.

No second `resolve_hit` pass was added. Chevalmarin's leg has one because rule
10's clause has to hold against a body the hit loop skips; Crabaletta aims at
one living enemy and the element travels with the hit ahead of Block in both
engines. **One correction to this row's own text:** it said a Crabaletta hit
into an Electro aura applies Superconduct's Vulnerable. It does not, in either
engine — Superconduct is Electro + Cryo, and Hydro into Electro is
Electro-Charged, whose rider is a DoT. The observable is the same (a reaction
the game had and the sim did not) and the DoT is what is pinned, by
`tier0/tests/test_eb495_d4_crabaletta_hits_hydro.py`. No published sim number
moved.

### D5 — the sim had no mirror of the enemy-side "took unblocked damage" triggers — REPAIRED in the sim

`Hook.AfterDamageReceived` fires in the game for EVERY damage instance,
including every `ElementalHit.Deal`, with no attack filter; `EmotionChip:31`,
`LavaLamp:52`, `HardenedShellPower:62` and `BeatingRemnant:71` read it.
`refpowers.on_damage_received` was called from one site (`combat.py`) for
damage the PLAYER received and read `state.player`'s powers only, so no tier0
verb could wake an enemy's `HardenedShell`. Every `none*` in the T5 column was
this one absence. It is a comparability gap, not a shipped-behaviour
difference, but it meant no sim number was a forecast of a fight against a
Hardened-Shell body.

**Repaired 2026-09-16, sim side only.** `refpowers.enemy_on_damage_received`
is the enemy's own funnel, driven from `effects.deal_damage_to_enemy` — the
one kit-verb door §2 names — and `refpowers.enemy_hardened_shell_cap` is its
HP-loss half.

THE CENSUS CORRECTS THIS ROW'S OWN LIST. Three of the four powers named above
are PLAYER-side relics: `EmotionChip`, `LavaLamp` and `BeatingRemnant` all
live in `Models/Relics/` and read the hook for the creature that owns them,
which is never a monster. The enemy-side T5 population in the whole shipped
assembly is `HardenedShellPower` alone, granted by `SkulkingColony:56` at 20,
so that is what was built. The assembly holds eleven other enemy-side
`AfterDamageReceived` overrides — `AsleepPower`, `FlutterPower`,
`PersonalHivePower`, `PlowPower`, `ReflectPower`, `ShriekPower`,
`SlipperyPower`, `SlumberPower`, `TheGambitPower`, `LagavulinMatriarch`'s own,
and `CurlUpPower` under D6 — none of which is a "took unblocked damage"
reaction; each is its own unmodelled mechanic, and where the sim carries the
body at all it is already flagged `UNIMPLEMENTED` on its enemy in
`tier05/content/act*_pool.yaml`.

The predicates, read off the decompile rather than off the card:
`CreatureCmd.Damage` skips the broadcast entirely for a creature the hit
killed (`:410`); `HardenedShellPower.AfterDamageReceived` (`:52`) returns on
`WasFullyBlocked` and otherwise adds `result.UnblockedDamage` — the
overkill-free number — to the turn's spent allowance;
`ModifyHpLostBeforeOstyLate` (`:38`) caps the post-Block loss at the unspent
remainder; and `BeforeSideTurnStart` (`:66`) restores the allowance with **no
side filter**, so it resets at the top of BOTH sides, twice a round.

**WHAT NO SIM FIGHT REACHES.** No encounter the sim owns carries the power:
`tier0/content/encounters/` is the frozen synthetic battery, and
`tier05/content/act1_pool.yaml`–`act3_pool.yaml` hold no Skulking Colony (the
game's is `SkulkingColonyElite`, in `Underdocks`). The `powers:` key those
pools already own is the door, so nothing new was allowlisted — but authoring
the power onto a body would move that encounter's difficulty, which is a
content pick and not a parity repair, so none was. Pinned by
`tier0/tests/test_eb495_d5_an_enemy_can_read_the_hit_it_took.py`, which stands
the power up by hand. No published sim number moved.

**One named limit.** The funnel hangs off `deal_damage_to_enemy` only. In the
game the hook is broadcast from `CreatureCmd.Damage`, which
`refpowers.unpowered_damage` (a power's own tick) and the direct-HP paths
(`reactions._splash`, Shatter, Overload) also mirror. Those are not wired, and
the door count is pinned in `test_eb495_kit_verb_triggers.py`, so widening it
is a deliberate act.

### D6 — the sim modelled no enemy-side retaliation power — REPAIRED in the sim

Same shape, T6 column. `ThornsPower`, `FlameBarrierPower` and `CurlUpPower`
existed on the player's side of `refpowers.py` and nowhere on the enemy's. An
Attack into an enemy carrying Thorns cost HP in the game and nothing in the
sim.

**Repaired 2026-09-16, sim side only.** All three are built, and the reading
that matters is that they are THREE DIFFERENT HOOKS, not one:

| power | hook | predicate, as decompiled | fires on a fully blocked hit? | on a killing blow? |
|---|---|---|---|---|
| `ThornsPower` (`:19`) | `BeforeDamageReceived` | `dealer != null && (IsPoweredAttack() \|\| cardSource is Omnislice)` | **yes** | **yes** |
| `FlameBarrierPower` (`:20`) | `AfterDamageReceived` | `dealer != null && IsPoweredAttack()`, `DamageResult` taken as `_` | **yes** | no |
| `CurlUpPower` (`:31`) | `AfterDamageReceived` | `IsPoweredAttack() && cardSource != null` | **yes** | no |

Thorns fires above Block and above the HP loss (`CreatureCmd.cs:285`, one line
above `blockedDamage`), so it has its own sim entry point,
`refpowers.enemy_retaliates_before_the_hit`; the other two ride
`enemy_on_damage_received` and are therefore denied by the broadcast's own
kill gate (`:410`). None of the three asks for `unblocked > 0`. Curl Up does
not retaliate at all: it remembers the card and pays `Amount` Block when that
card's play FINISHES (`AfterCardPlayed`, `:49`), so the hit that woke it is
never mitigated by the Block it bought — `state.card_in_flight` is the sim's
`cardSource`, pushed and restored at the two card-play hooks so a nested play
hands the outer card back. The `Omnislice` disjunct in Thorns is not
transcribed: it is one base-game card the sim's pool does not hold.

**THE NEGATIVE HALF IS THE POINT.** All three ask `IsPoweredAttack()`, which
every kit verb fails by construction — `ElementalHit.Deal` passes
`ValueProp.Unpowered` with `dealer: null`. So a Bomb, a Plan, a Mine, a
performance and a Stage act are never thorned, never burned and never curl a
Louse, in either engine, and every `none` in the T6 column below stayed
`none`. That is swept over the whole `source` population in
`test_eb495_kit_verb_triggers.py` and pinned end to end in
`tier0/tests/test_eb495_d6_an_enemy_can_retaliate.py`.

**WHAT THE SIM'S FIGHTS REACH.** `ThornsPower` is granted by `SpinyToad:76`
and `Toadpole:110`, both `Underdocks` bodies and neither present in
`tier05/content/act1_pool.yaml`. `FlameBarrierPower` is granted by no monster
in the assembly at all — it is the player's card, and the enemy-side leg is
built for symmetry and for the day one is authored. `CurlUpPower` is granted
by `LouseProgenitor:70`, and **`louse_progenitor` IS in
`act2_pool.yaml`**, where the comment already reads "UNIMPLEMENTED: Curl Up 14
(folded into the block beat)". Wiring it there is now a one-line `powers:`
entry — and it was NOT made, because it moves that encounter's difficulty and
every tier0.5 number measured through it: a content pick, not a parity repair.
No encounter file moved and no published sim number moved.

An enemy-owned `flame_barrier` expires at the PLAYER's side turn end
(`refpowers.on_fighter_turn_end`), the mirror image of the player's, which
`after_enemy_side_turn_end` removes at the enemy side's end — two hook
firings, written apart. One named limit, the twin of D5's: the retaliation
hit on the player goes through Block and the Intangible cap but not through
Furina's stage absorb, Kokomi's ward or Encore, which sit on the enemy-intent
path only. The branch is unreachable in every shipped fight, and the function
that owes that chain is named in its own docstring.

### D7 — a kit verb's reaction debuff carries no `cardSource`, and the sim cannot tell

`ElementalHit.Deal` passes `cardSource: null` into `ReactionEffects.Resolve`,
which passes it on to `PowerCmd.Apply` (`ReactionEffects.cs:445`, `:483`).
`UnsettlingLamp.BeforePowerAmountChanged` returns early on `cardSource == null`
(`Models/Relics/UnsettlingLamp.cs:82`), so it doubles a Superconduct off a card
hit and never doubles one off a Bomb, a Plan or a performance. The sim's
`powers.apply_power` / `refpowers.on_power_applied` carry no `cardSource`
notion at all (`refpowers.py:1093`), so the sim cannot represent either half.
Nothing on a face promises it, so this is a modelling note rather than a
player-visible defect.

---

## 7. What a face promises that the trigger does not deliver

Checked, and the answer is one item, already ruled:

* **Thorns' printed line** ("when hit by an attack") vs its trigger (any
  powered hit, a Skill's included) — `EB-521`, closed; the mod carries a
  corrected `THORNS_POWER.description` row and
  `tier0/tests/test_eb521_thorns_prints_its_trigger.py` pins it.

No kit face claims an interaction with a base-game relic or power. The Klee
brief's "an explosion is not an Attack", the Kokomi brief's "a planned clause
is not a card being played" and the Salon's "a performance is not an Attack and
not a hit" are all delivered exactly as printed, in both engines, at every cell
above.
