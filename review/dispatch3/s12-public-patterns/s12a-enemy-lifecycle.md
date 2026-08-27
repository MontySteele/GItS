# S12a — Enemy registration, AI, intents, death

*Surplus-dispatch-3, research rail. Written 2026-08-26. Decides nothing (charter §3.1).
Every claim below carries a pinned source. Where I could not pin one, the line says
UNVERIFIED or NON-FINDING.*

## Overview (the short answer)

**Downfall ships no hostile enemy at all.** Its 24 `CustomMonsterModel` classes — Torchheads,
Gremlins, sixteen Slimes — are every one a **player-owned pet**: created on
`CombatSide.Player`, given a `PetOwner`, added to the player's own pet list. All three of its
move-machine overrides return the same three-line no-op (`NOTHING_MOVE` looping to itself),
so none of them ever takes a turn, picks a move, or shows an AI intent. Zero encounters, zero
acts, zero enemies. Filenames are worthless here: `SlimeModel`, `GremlinsMonsterModel` and
`TorchheadMonsterModel` all say "monster" and all fight on our side.

**The proof is one level down, in the library we already depend on.** BaseLib-StS2 (Alchyr,
MIT) implements the hostile lifecycle in readable public C#: `CustomEncounterModel` injects an
encounter into a real act's pool by patching `ActModel.GenerateAllEncounters`;
`CustomMonsterModel` extends the base `MonsterModel` with visuals/animation/SFX overrides;
`MoveBuilder` composes a `MoveState` of real actions **plus the matching intents**; and
`CustomPetModel` exists purely to stamp out the no-op AI Downfall hand-writes three times.

So: **the API is proven, a shipped user of it is not** — I could not open a released mod that
registers a hostile enemy. The search boundary that produced that gap is recorded at the end.

---

## Pattern table

Citation keys used below:

* `DF@32e6113` = `lamali292/Downfall` @ `32e61132052ae58e32cd33342d24136ffe18be12`
  (<https://github.com/lamali292/Downfall/tree/32e61132052ae58e32cd33342d24136ffe18be12>)
* `BL@2275793` = `Alchyr/BaseLib-StS2` @ `22757933ba10adc4322a628519a233a567507d87`
  (<https://github.com/Alchyr/BaseLib-StS2/tree/22757933ba10adc4322a628519a233a567507d87>) — MIT, release v3.4.5
* `WIKI@5558d89` = `Alchyr/BaseLib-Wiki` @ `5558d8982dc7c28300f8c5de8fbc97620da009cf` (the project's own docs site)

### A. What Downfall actually does (all player-side)

| pattern | purpose | pinned source | base type it hangs off |
|---|---|---|---|
| **Player-side creature spawn** — `combatState.CreateCreature(model.ToMutable(), CombatSide.Player, null)`, then `creature.PetOwner = player`, `player.PlayerCombatState.AddPetInternal(creature)`, `NCombatRoom.Instance.AddCreature(creature)` | Put a second body on the board that belongs to the player | `DF@32e6113:GremlinsCode/Core/GremlinsCmd.cs:171-191` | `ICombatState`, `Creature`, `CombatSide`, `NCombatRoom` |
| **Pet spawn via the supported door** — `PlayerCmd.AddPet<T>(summoner)`, looked up afterwards through `CombatState.Allies.FirstOrDefault(c => c.Monster is T && c.PetOwner == summoner)` | Summon/revive a pet, tween it in, mark it `DieForYouPower` | `DF@32e6113:DownfallCode/Commands/DownfallCmd.cs:97-146` | `PlayerCmd`, `PlayerCombatState`, `MonsterModel` |
| **Second spawn route** — `CreateCreature(..., player.Creature.Side, null)` then `PlayerCmd.AddPet(pet, player)` | Slime queue: spawn on whatever side the *player* is on, never a fixed enemy side | `DF@32e6113:SlimeBossCode/Core/SlimeQueue.cs:64-65` | `ICombatState`, `Creature.Side` |
| **The AI is deliberately switched off** — `GenerateMoveStateMachine()` returns one `MoveState("NOTHING_MOVE", _ => Task.CompletedTask)` whose `FollowUpState` is itself | These creatures must never act on their own | `DF@32e6113:CollectorCode/Core/TorchheadMonsterModel.cs:27-32`; `GremlinsCode/Core/GremlinsMonsterModel.cs:30-35`; `SlimeBossCode/Slimes/SlimeModel.cs:68-73` — **these three are the only overrides in the repo** | `MonsterMoveStateMachine`, `MoveState` |
| **"Monster moves" fired by a card, not a turn** — `SlimeModel.Command(ctx)` is abstract on the model and invoked from `SlimeBossCmd.CommandInternal` with a `CardModel? cardSource` | Player pays a card; the pet performs an attack | `DF@32e6113:SlimeBossCode/Core/SlimeBossCmd.cs:54-70`, `SlimeBossCode/Slimes/BronzeSlime.cs:28-41` | `PlayerChoiceContext`, `DamageCmd.Attack` |
| **Attack attributed to a pet** — `command.Attacker = slime.Creature; command._attackerAnimName = "Attack"; command._sourceType = AttackCommand.SourceType.None` | Make a pet's hit read as a hit without claiming monster provenance | `DF@32e6113:SlimeBossCode/Extensions/AttackCommandExtensions.cs:10-18` | `AttackCommand`, `AttackCommand.SourceType` |
| **A card that makes a *real* enemy swing at you** — `attack.Attacker = monster.Creature; attack._sourceType = AttackCommand.SourceType.Monster` on `cardPlay.Target` | Turn an already-present enemy into the attacker for one card | `DF@32e6113:DownfallCode/Commands/DownfallCmd.cs:52-71` | `AttackCommand.SourceType.Monster` |
| **Reading enemy intent (read-only)** — `HittableEnemies.Count(e => e.Monster?.IntendsToAttack ?? false)` | Card text keyed off what the enemies are about to do | `DF@32e6113:GremlinsCode/Cards/Uncommon/FeelTheAudience.cs:21`, `GremlinsCode/Cards/Token/Bellow.cs:25` | `MonsterModel.IntendsToAttack` |
| **Authoring an intent for a player-side mechanic** — `CustomIntent : AbstractIntent, ICustomModel`, then `CustomAttackIntent`/`BolsteringIntent`/`MultiStatusIntent<T>` overriding `IntentType`, `GetAnimation`, `GetIntentLabel` | Hexaghost's ghostflame wheel shows six intents *on the player* | `DF@32e6113:DownfallCode/Abstract/CustomIntent.cs:10-30`; `HexaghostCode/Ghostflames/Intents/CustomAttackIntent.cs:9-29` | `AbstractIntent`, `IntentType`, `IntentAnimData`, `LocString("intents", …)` |
| **Instantiating the intent widget by hand** — `NIntent.Create(delay)` into a private array, then `_intents[i].UpdateIntent(wheel[i].Intent, [], _player.Creature)` | Attach intent UI to a creature the engine would never give one | `DF@32e6113:HexaghostCode/Vfx/NGhostflames.cs:80,158,188,439,464` | `NIntent` |
| **Registering a custom intent sprite** — writes straight into a base-game static dictionary: `IntentAnimData._data[key] = new IntentAnimData.InternalData { frames = [IntentSpritePath] }`, lazily on first `GetAnimation` | No public registration API exists for intent art | `DF@32e6113:DownfallCode/Abstract/CustomIntent.cs:17-29` | `IntentAnimData` (private static field) |
| **Re-labelling the intent number** — Harmony postfix on `NIntent.UpdateVisuals` writes `__instance._valueLabel.Text` when `__instance._intent is CustomIntent` | The base label formatter doesn't know custom intents | `DF@32e6113:DownfallCode/Patches/CustomIntentLabelPatch.cs:7-17` | `NIntent.UpdateVisuals`, `NIntent._valueLabel` |
| **Observing an enemy's death** — `AfterDeath(ctx, creature, wasRemovalPrevented, deathAnimLength)` with `if (creature is { IsEnemy: true, Monster: not null })` | Collector banks every enemy it kills and pays out at combat end | `DF@32e6113:CollectorCode/Core/CollectorModel.cs:57-63` | `CustomSingletonModel(HookType.Combat)` (BaseLib), `Creature.IsEnemy` |
| **Taking over a death entirely** — Harmony prefix on `CreatureCmd.KillWithoutCheckingWinCondition(creature, force)`, returning `false` to substitute your own `Task`; `force` kills are never interceptable | Death-denial effects | `DF@32e6113:DownfallCode/Patches/DeathInterceptPatch.cs:8-21`, `DownfallCode/Utils/DeathHooks.cs:6-32` | `CreatureCmd.KillWithoutCheckingWinCondition` |
| **Death / revive / animation-trigger hooks** — postfixes on `NCreature.SetAnimationTrigger(string)`, `NCreature.StartDeathAnim()`, `NCreature.StartReviveAnim()` | Drive custom visuals off the engine's own animation events | `DF@32e6113:DownfallCode/Patches/NCreatureAnimationPatch.cs:11-39` | `NCreature` |
| **Skipping the death animation** — prefix on `StartDeathAnim` sets `shouldRemove = true` and calls `NCombatRoom.RemoveCreatureNode`; a paired prefix on `GetCurrentAnimationTimeRemaining` returns `0f` | Make a pet vanish instantly instead of playing a death | `DF@32e6113:SlimeBossCode/Patches/SlimeDeathPatches.cs:8-33` | `NCreature`, `NCombatRoom` |
| **Removing a creature outright** — `CreatureCmd.Kill(oldest)`, `player.PlayerCombatState._pets.Remove(...)`, `combatState.RemoveCreature(...)` | Evict a pet over the slot cap | `DF@32e6113:SlimeBossCode/Core/SlimeQueue.cs:73-84` | `CreatureCmd`, `ICombatState.RemoveCreature` |
| **Custom creature scene contract (as shipped)** — Node2D root carrying a `[GlobalClass] NCreatureVisuals` subclass, with unique-named children `FormVfx`, `Visuals`, `Bounds`, `CenterPos`, `IntentPos` | The visual half of a creature | `DF@32e6113:Collector/scenes/character/torchhead_combat.tscn:1-35`; script `CollectorCode/Vfx/NTorchheadCreatureVisuals.cs:6-24` | `NCreatureVisuals` |
| **Creature persistence across combats** — `SavedSpireField<Player, List<GremlinSaveData>>` storing `ModelId`+hp; re-instantiated each fight in `BeforeCombatStart` via `ModelDb.GetById<MonsterModel>(saved.ModelId)` | Gremlins keep their damage between fights | `DF@32e6113:GremlinsCode/Core/GremlinsRunModel.cs:18-39,78-110,129-148` | `CustomSingletonModel(HookType.Run)`, `ModelDb`, `ModelId` |
| **Monster names are localized in their own table** — `monsters.json` per language, keys `MODPREFIX-CLASS_NAME.name` / `.description` / `.banter` | Nameplate + hover text | `DF@32e6113:Gremlins/localization/eng/monsters.json`, `SlimeBoss/localization/eng/monsters.json` | base loc table `monsters` |
| **Base-game monster models referenced by type** — 100 cards of the form `Collectible<CorpseSlug>`, resolved with `ModelDb.Monster<T>()`; visuals built off-board with `monster.CreateVisuals()` + `monster.GenerateAnimator(visuals.SpineBody)` | Collector's card art *is* the real enemy | `DF@32e6113:CollectorCode/Cards/Token/MonsterCards.cs:4,12-15` (100 rows), `CollectorCode/Cards/Token/Collectible.cs:41-68` | `MegaCrit.Sts2.Core.Models.Monsters.*`, `MonsterModel.CreateVisuals/GenerateAnimator` |
| **Pets excluded from enemy targeting** — target predicate `target is { IsAlive: true, IsPet: false, IsEnemy: true }` | A registered multi-target type that means "me and the enemies" | `DF@32e6113:DownfallCode/DownfallMainFile.cs:116-118` | `CustomTargetType`, `Creature.IsPet`, `Creature.IsEnemy` |

### B. What BaseLib proves (the hostile half)

| pattern | purpose | pinned source | base type it hangs off |
|---|---|---|---|
| **A modded monster type** — `CustomMonsterModel : MonsterModel, ICustomModel, ISceneConversions`; ctor calls `CustomContentDictionary.RegisterType(GetType())` | The declaration point for any modded creature, hostile or not | `BL@2275793:Abstracts/CustomMonsterModel.cs:11-16` | `MonsterModel` |
| **Monster presentation overrides, delivered as Harmony prefixes** — `VisualsPath` getter → `CustomVisualPath`; `CreateVisuals` → `CreateCustomVisuals`; `GenerateAnimator` → `SetupCustomAnimationStates`; `AttackSfx`/`CastSfx`/`DeathSfx` getters → `CustomAttackSfx`/`CustomCastSfx`/`CustomDeathSfx` | Give a modded monster art, animation and sound without a base-game data file | `BL@2275793:Abstracts/CustomMonsterModel.cs:115-195` | `MonsterModel` (six patched members) |
| **Animation-state helper** — `SetupAnimationState(controller, idleName, deadName, hitName, attackName, castName, …)` builds a `CreatureAnimator` with any-states `Idle/Dead/Hit/Attack/Cast`, defaulting every missing one to idle | The five animation states a creature is expected to have | `BL@2275793:Abstracts/CustomMonsterModel.cs:74-107` | `CreatureAnimator`, `AnimState`, `MegaSprite` |
| **The explicit "no AI" pet** — `CustomPetModel(bool visibleHp) : CustomMonsterModel` whose `GenerateMoveStateMachine` is the same `NOTHING_MOVE` loop Downfall hand-writes three times | The library's own name for "a creature that never acts" | `BL@2275793:Abstracts/CustomPetModel.cs:5-15` | `CustomMonsterModel` |
| **A hostile encounter** — `CustomEncounterModel : EncounterModel`, ctor takes a `RoomType` (warns unless `Monster`/`Elite`/`Boss`) and auto-adds itself via `CustomContentDictionary.AddEncounter(this)` | Registration of a fight into the game | `BL@2275793:Abstracts/CustomEncounterModel.cs:11-28` | `EncounterModel`, `RoomType` |
| **Where the fight may appear** — abstract `IsValidForAct(ActModel act)` | Pool gating, per act | `BL@2275793:Abstracts/CustomEncounterModel.cs:38` | `ActModel` |
| **Which monsters are in the fight** — required overrides `AllPossibleMonsters` (every monster that *can* spawn) and `GenerateMonsters()` returning `(MonsterModel, string? slot)` pairs from `ToMutable()`, randomised through the encounter's own `Rng` | Roster + randomisation of one encounter | `BL@2275793:Abstracts/CustomEncounterModel.cs:43-59` (class comment); worked example `WIKI@5558d89:docs/models/custom-encounter.md:52-66` | `EncounterModel`, `Rng` |
| **Where the monsters stand** — encounter scene is a 1920×1080 Control, Full Rect, MouseFilter Ignore, with `Marker2D` children as enemy positions; `Slots` defaults to reading those marker names off the scene; marker names are the keys `CreatureCmd.Add` takes when spawning **additional** enemies mid-fight | Positioning, and the documented mid-combat spawn door | `BL@2275793:Abstracts/CustomEncounterModel.cs:61-90`; `WIKI@5558d89:docs/models/custom-encounter.md:12-18` | `PackedScene`, `Marker2D`, `CreatureCmd.Add` |
| **Encounter injected into the real act pool** — BaseLib walks every `ActModel` subtype (base game *and* mods), Harmony-patches each declared `GenerateAllEncounters`, and the postfix yields each `CustomEncounter` whose `IsValidForAct(act)` is true and whose `Id` is not already present | This is the actual registration-as-an-opponent step | `BL@2275793:Patches/Content/ContentPatches.cs:348-394`, list at `:29`, add at `:70-75` | `ActModel.GenerateAllEncounters`, `ModelDb.InitIds` |
| **Monster AI + intent authored together** — `MoveBuilder(monster, id)` accumulates actions and intents in lockstep: `.Attack(dmg, hitCount, …)` adds `SingleAttackIntent`/`MultiAttackIntent`; `.Block()` adds `DefendIntent`; `.ApplyToPlayers<T>(amount, isStrongDebuff)` adds `DebuffIntent(strong)`; `.ApplyToSelf<T>()` adds `BuffIntent`; `.HealSelf()` adds `HealIntent`; `.PlayAnim`, `.PlaySfx`, `.CustomAction`, `.AddIntent`, `.FollowingState(id)`; `Build()` → `new MoveState(Id, actions, intents) { FollowUpStateId }` | The whole move/intent grammar for a hostile monster | `BL@2275793:Monsters/MoveBuilder.cs:16-304` | `MoveState`, `MonsterMoveStateMachine`, `AbstractIntent`, `IntentType` |
| **A monster's attack** — `new AttackCommand(baseDmg).FromMonster(monster)`, optional `.WithHitCount`, `.WithAttackerFx/.WithHitFx/.WithAttackerAnim/.OnlyPlayAnimOnce` | The hostile attack path — contrast Downfall's pets, which set `SourceType.None` | `BL@2275793:Utils/MonsterActions.cs:10-17`; used at `Monsters/MoveBuilder.cs:84-100` | `AttackCommand`, `AttackCommand.FromMonster` (base game) |
| **A monster applying powers** — `MonsterActions.ApplySelf<T>` / `Apply<T>` with a `ThrowingPlayerChoiceContext` when no context is supplied | Buffs/debuffs from a creature that has no player choice context | `BL@2275793:Utils/MonsterActions.cs:22-35` | `PowerCmd`, `PlayerChoiceContext` |
| **Co-op scaling baked into the AI helper** — `HealSelf(amount, autoScaleWithPlayers = true)` multiplies by `Monster.Creature.CombatState.Players.Count` | Monster numbers are expected to scale with seat count | `BL@2275793:Monsters/MoveBuilder.cs:186-189` | `ICombatState.Players` |
| **Boss extras** — encounter must supply run-history icon paths or the boss room will try (and fail) to load a base-game image by encounter name; `CustomBgm`, `GetCameraScaling`, `GetCameraOffset`, `Tags`, `IsWeak`, `BossNodePath`, `MapNodeAssetPaths` | Boss-shaped encounters need more than monsters | `BL@2275793:Abstracts/CustomEncounterModel.cs:52-58,127-132`; `WIKI@5558d89:docs/models/custom-encounter.md:48-70` | `EncounterModel`, `RoomIconPathPatch` |
| **"This monster came from a mod" nameplate** — postfix on `NCreatureStateDisplay.RefreshValues` writes `"{creature.Name}\n{modName}"`, gated on a config flag; comment states monsters have no hover tip of their own | Provenance UI for modded enemies | `BL@2275793:Patches/UI/MonsterSourceLabel.cs:10-30` | `NCreatureStateDisplay` |
| **Creature-visuals scene contract (documented)** — Control root; required unique-named `Visuals` (Node2D), `Bounds` (Control), `IntentPosition` (Marker2D), `CenterPos` (Marker2D); optional `PhobiaModeVisuals`, `OrbPos`, `TalkPos`. Godot `AnimationPlayer`/`AnimationTree` animations auto-bind by name (`idle`, `attack`, `cast`, `hurt`, `die`) | What a creature scene must contain | `WIKI@5558d89:docs/scenes/creature-visuals.md:23-54` | `NCreatureVisuals`, `NodeFactory<NCreatureVisuals>` |

---

## Gotchas

1. **The word "Monster" in a class name means nothing.** `TorchheadMonsterModel`,
   `GremlinsMonsterModel`, all sixteen `SlimeModel`s — 24 subclasses of `CustomMonsterModel`
   in Downfall, 24 player pets. The side is decided at spawn (`CombatSide.Player` /
   `player.Creature.Side`) and by `PetOwner`, not by the type.
2. **A no-op move machine is the tell.** All three of Downfall's `GenerateMoveStateMachine`
   overrides are byte-for-byte the same `NOTHING_MOVE` self-loop, and BaseLib ships that
   same body as `CustomPetModel`. If you are auditing a mod for hostile content, read
   `GenerateMoveStateMachine` first — it is a three-line yes/no.
3. **`DownfallCmd.EnemyAttackPlayer` is not enemy AI.** It reads like one (it even sets
   `AttackCommand.SourceType.Monster`), but it is a *player card* borrowing an enemy that is
   already on the board as the attacker. `DF@32e6113:DownfallCode/Commands/DownfallCmd.cs:52-71`.
4. **`SourceType` is the honest discriminator.** BaseLib's monster path calls
   `FromMonster` (`BL@2275793:Utils/MonsterActions.cs:13`); Downfall's pet path sets
   `SourceType.None` (`DF@32e6113:SlimeBossCode/Extensions/AttackCommandExtensions.cs:16`).
   Any effect keyed on "was this a monster move" will split those two apart.
5. **The kill path has a win-condition check in its name.** Downfall patches
   `CreatureCmd.KillWithoutCheckingWinCondition`, which implies the ordinary kill path
   *does* check it. Adding a hostile creature therefore changes when combat ends — that
   coupling is unexamined here and is S13's to trace.
6. **The shipped creature scenes do not match the documented one.** The BaseLib wiki says a
   Control root with `IntentPosition` and `CenterPos`
   (`WIKI@5558d89:docs/scenes/creature-visuals.md:25-36`); both Downfall creature scenes I
   opened use a **Node2D** root with **`IntentPos`** plus an extra `FormVfx` node
   (`DF@32e6113:Collector/scenes/character/torchhead_combat.tscn:6-35`,
   `Gremlins/scenes/gremlins/angry/angry_combat.tscn:6-33`). Whether `NCreatureVisuals`
   tolerates both spellings, or one of the two is simply wrong, is **UNVERIFIED** — it needs
   the base decompile (S13).
7. **Custom intent art is registered by writing a private static dictionary.**
   `IntentAnimData._data[key] = …`, keyed on a lowercased prefix, done lazily inside
   `GetAnimation` (`DF@32e6113:DownfallCode/Abstract/CustomIntent.cs:17-29`). There is no
   public registration API in evidence. Fragile across game patches.
8. **Several seams are private fields, not API.** `slimeNode._stateDisplay._healthBar`
   (`DF@32e6113:SlimeBossCode/Core/SlimeQueue.cs:200-203`), `NIntent._valueLabel`,
   `player.PlayerCombatState._pets`, `CombatManager.Instance._state`. A mod that touches
   creatures touches private state.
9. **BaseLib dedupes encounters by `Id`.** Two mods that register the same encounter id
   silently collapse to one — the postfix skips any encounter whose id the act already
   yielded (`BL@2275793:Patches/Content/ContentPatches.cs:391`). Id-prefix hygiene matters
   before, not after.
10. **`AddModel` demands a `[Pool]` attribute — and monsters do not use it.**
    `CustomContentDictionary.AddModel` throws without one
    (`BL@2275793:Patches/Content/ContentPatches.cs:55-68`), yet no monster class in Downfall
    carries `[Pool]` and `CustomMonsterModel`'s ctor only calls `RegisterType`. How a
    `MonsterModel` subclass actually acquires its `ModelId` and lands in `ModelDb` is
    **not shown in either public source** — see NON-FINDINGS.
11. **Pointers out of my lane** (one line each, per the charter): BaseLib also ships
    `Abstracts/CustomActModel.cs` and `Abstracts/CustomEventModel.cs` and
    `Abstracts/CustomAncientModel.cs`, with act/event injection in the same
    `ContentPatches.cs` — that is S12b/S12c/S12d material, not mine. Downfall's
    `DownfallCode/Events/` is an internal C# hook bus (`CollectorHook.OnPyre`,
    `GremlinsHook.AfterGremlinSwap`), **not** a world-event model — S12d.

---

## Transfer questions (questions, not proposals)

Against our own abstractions: `klee-mod/KleeCode` (Harmony patches + BaseLib), the PCK
pipeline, and the atlas maps.

1. **Version floor.** Our manifest pins `BaseLib >= 3.3.6`
   (`klee-mod/Klee/manifest.json`); the encounter/monster API above is read at **3.4.5**
   (`BL@2275793`), and Downfall pins `>= 3.4.5` (`DF@32e6113:Downfall.json`). What is the
   minimum BaseLib version any enemy work would require, and who signs off on raising our
   floor?
2. **Act identity.** `IsValidForAct(ActModel act)` gates on the *game's* acts. Our sim's
   acts (`RUN_ACTS`: `act1`, `act2` "the Hive", `act3` "Glory") are a tier-0.5 model, not
   base-game `ActModel`s. Which act identity would a Teyvat encounter key from, and does
   anything have to reconcile the two?
3. **New monster or reskin?** Would a Teyvat enemy be a new `CustomMonsterModel` (new type,
   new `ModelId`, new save identity) or a presentation swap on an existing base monster?
   Those differ sharply in save/version consequences — hand-off to S12f.
4. **Our one existing read of the hostile side.** `PlayTelemetry` already inspects
   `creature.Monster?.NextMove is MoveState move` and walks `move.Intents`, matching
   `IntentType.ToString() == "Attack"` and regex-parsing the rendered label
   (`klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs:747-775`). If we ever authored a
   `MoveState` of our own, would our telemetry double-count it, or mis-parse a label we
   wrote? What does that code owe an enemy we control?
5. **Reactions and auras on the hostile side.** Our reaction layer applies powers to
   `Creature`s, and `AuraPower`/`BombPower` are `Buff`-typed so they coexist with Artifact
   (STATE §Systems). Does an enemy we author need to carry auras — and if a hostile creature
   can be aura-bearing, what does that do to the Swirl aura-aware bind (R211)?
6. **Intent localization.** BaseLib/Downfall intents pull from the base `intents` table
   (`LocString("intents", "FORMAT_DAMAGE_MULTI")`). Our loc rows are merged by
   `KleeMod.InjectLocStrings`, and monsters use a separate `monsters` table. Where would our
   intent and monster strings live, and does `InjectLocStrings` reach those tables today?
7. **PCK cost.** An encounter wants a 1920×1080 scene with `Marker2D` slots, optionally a
   layered background set, and (for a boss) two run-history icons. Our PCK contract is
   `roster-pck-v3` and `tools/build_pck.ps1` owns packing. What does that add to package
   size and build time, and does the contract version have to move?
8. **Is the cheap thing the right thing first?** `CustomPetModel` (proven, no AI, no
   encounter, no act) is a far smaller surface than a hostile enemy. If we ever want a Klee
   bomb, a Furina Salon member, or a Kokomi ally *on the board*, is that the pattern — and
   is that a different question from enemy remapping entirely?
9. **Co-op.** `MoveBuilder.HealSelf` scales by `CombatState.Players.Count` by default. Our
   co-op has only a partial automated backstop (`klee-mod/KleeTests/README.md`). Who owns
   the seat-count scaling rule for any enemy numbers, and can it be tested at all before
   play?
10. **Id policy.** BaseLib dedupes encounters by `Id` and BaseLib's `WhatMod`/`PrefixId`
    machinery derives ids from type names. Does our identifier registry already cover
    encounter and monster ids, or is that an unallocated namespace?

---

## NON-FINDINGS (all of these are valid results)

1. **Downfall proves no hostile enemy lifecycle.** Counted at `32e6113`, whole tree:
   * `0` subclasses of `EncounterModel` or `CustomEncounterModel`.
   * `0` direct `: MonsterModel` subclasses (all 24 go through `CustomMonsterModel`).
   * `3` of `3` `GenerateMoveStateMachine` overrides are the `NOTHING_MOVE` no-op.
   * `0` occurrences of `CombatSide.Enemy` as a *spawn* argument — the only
     `CombatSide.Enemy` uses are turn-phase comparisons and one mirror-flip of slime layout
     (`DF@32e6113:SlimeBossCode/Core/SlimeQueue.cs:163`).
   * `0` `[Pool(...)]` attributes on any monster class; all **1,054** `[Pool]` uses in the
     repo name a card, relic or potion pool.
   * The only `Encounter` references are reads (`CombatState.Encounter.RoomType`) and metrics.
2. **No public source proves a *shipped, released* mod that registers a hostile enemy.** I
   proved the API in BaseLib; I did not open a mod that uses `CustomEncounterModel`. That
   remains open.
3. **How a `MonsterModel` subclass gets its `ModelId` and enters `ModelDb` is not shown in
   either public source.** `CustomMonsterModel`'s ctor only calls `RegisterType`
   (`BL@2275793:Abstracts/CustomMonsterModel.cs:15`), and `AddModel`'s `[Pool]` path does
   not apply to monsters. Presumably the base game's own mod-assembly scan does it —
   **UNVERIFIED**. This is exactly S13's question.
4. **`AttackCommand.FromMonster`, `CreatureCmd.Add`, `MonsterModel.NextMove`,
   `MonsterModel.IntendsToAttack`, `IntentType`'s full member list, and `CombatSide`'s full
   member list are base-game surface** — used by these mods, not defined in them. Only
   `CombatSide.Player` and `CombatSide.Enemy` are *proven* to exist
   (`DF@32e6113:HermitCode/Powers/AdaptPower.cs:18`, `GremlinsCode/Powers/AgonyPower.cs:31`).
5. **`BAKAOLC/STS2-RitsuLib` has no enemy/monster/encounter/intent subsystem.** Its full
   recursive tree at `a7c809b6a8e2c396302fb44a04895143b0ee67db` contains combat
   targeting, attack-hit hooks, healing hooks, health-bar forecasts, hand size, player
   resources, rewards — and nothing under Monster/Encounter/Intent. NON-FINDING for S12a.
6. **`Alchyr/ModTemplate-StS2`'s README does not mention monsters, encounters or enemies**
   (11 lines, fetched raw at `master`, 2026-08-26). Its file tree was **not** read — the
   GitHub API rate limit stopped me there. Not evidence of absence.

## Search boundary (recorded per charter §7)

Date: **2026-08-26**. Runner: local Windows, read-only.

**Primary source, as assigned:** `lamali292/Downfall` @
`32e61132052ae58e32cd33342d24136ffe18be12`, the local depth-1 clone. Method: full-tree
`grep` over `*.cs` for `Monster|Intent|Enemy|Hostile|encounter|summon|spawn|minion`, then
identifier-frequency inventory, then targeted reads of every file that matched; plus
`.tscn` creature scenes, `monsters.json` loc tables, `Downfall.json`, `README.md`, `LICENSE`,
and `DownfallMainFile.cs`. Nothing was copied; reference-reading only (charter §3.7).

**Widen (used once, charter §7).** Two `WebSearch` queries:
`Slay the Spire 2 mod GitHub custom monster enemy encounter BaseLib` and
`github "CustomEncounterModel" OR "CustomMonsterModel" Slay the Spire 2 mod repository`.
Search results were used only to *find* candidate repositories; **no summary, forum post,
wiki aggregator or Nexus page was used as evidence**. Primary sources then opened:

| repository | pinned at | what I read | outcome |
|---|---|---|---|
| `Alchyr/BaseLib-StS2` (MIT, pushed 2026-08-19) | `22757933ba10adc4322a628519a233a567507d87` | repo metadata; full recursive tree; read in full: `Abstracts/CustomMonsterModel.cs`, `Abstracts/CustomEncounterModel.cs`, `Abstracts/CustomPetModel.cs`, `Monsters/MoveBuilder.cs`, `Utils/MonsterActions.cs`, `Patches/Content/ContentPatches.cs`, `Patches/UI/MonsterSourceLabel.cs`, `Extensions/AttackCommandExtensions.cs`, `README.md`, `Notes.txt` | **the finding** |
| `Alchyr/BaseLib-Wiki` (project's own docs) | `5558d8982dc7c28300f8c5de8fbc97620da009cf` | full tree; read `docs/models/custom-encounter.md`, `docs/scenes/creature-visuals.md` | corroborates + worked example |
| `BAKAOLC/STS2-RitsuLib` (MIT) | `a7c809b6a8e2c396302fb44a04895143b0ee67db` | repo metadata; full recursive tree, filtered | NON-FINDING for this subsystem |
| `Alchyr/ModTemplate-StS2` | `master` (README only, unpinned — API rate limit) | `README.md`, 11 lines | nothing on monsters |

**Not opened, and therefore not searched:** `spencerqfox/sts2-custom-mods`,
`jiegec/STS2FirstMod`, `lamali292/sts2_example_mod`, `lamali292/WatcherMod`, the
`github.com/topics/sts2` and `topics/sts2-mods` listings, and every Nexus mod page. The
GitHub REST API returned `API rate limit exceeded` partway through, which is where the
widen stopped. A second pass with an authenticated token could close item 2 of the
NON-FINDINGS.

## What this does NOT establish

* It does **not** establish that anyone has shipped a working custom hostile enemy in a
  released StS2 mod. It establishes that the library we already depend on has the API for it.
* It does **not** establish the base game's monster turn order, target selection, intent
  refresh timing, or win-condition rules. Every one of those is base-engine behaviour and
  belongs to **S13**.
* It does **not** establish what a hostile enemy would cost us in art, animation, audio,
  save compatibility, or build weight (S16 / S17 / S19 / S12f / S12g).
* It does **not** establish boss- or encounter-pool integration beyond the API surface —
  that is **S12b**'s file, and the two should be read together.
* It contains **no recommendation and no design call**. Whether Teyvat Spire ever ships a
  hostile enemy, and which one, is [USER]'s.
