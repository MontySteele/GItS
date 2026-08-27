# S13 — StS2 engine socket probe (LOCAL READ-ONLY)

> **Decides nothing.** This is a description of the base game's own code, read
> off a local decompile. Every technical suggestion below is `PROPOSED`. No
> mapping, mechanic, taste, rights, spend, scope, or ship call is made or
> implied. Nothing here was built, deployed, or run — the game was never
> launched.

---

## 0. Provenance, method, and how to read the citations

**Gate (charter §4/S13): PASSED.** The local runner could read both ignored
sources. No deferral.

| Source | Pin |
|---|---|
| Base game | Slay the Spire 2 `v0.107.1`, commit `59260271`, dated `2026-06-18` (`release_info.json` in the game dir) |
| Base assembly | `…\Slay the Spire 2\data_sts2_windows_x86_64\sts2.dll`, 9 364 480 bytes, MD5 `694db3dce059fc496908235086cb2c94` |
| BaseLib | Workshop `2868840/3737335127`, manifest `BaseLib.json`: `"version": "v3.4.5"`, `"author": "Alchyr"`, `"min_game_version": "0.107.1"`, `has_pck` + `has_dll` both true |
| BaseLib assembly | `BaseLib.dll`, 1 090 560 bytes, MD5 `4380fd038fda7ca92708fd09a8aebf39` |
| Decompiler | `ilspycmd` 8.2.0.7535, `--project --nested-directories`, with `-r` pointed at the game's assembly dir (the workflow `tools/extract_base_game_pool.py:218-260` documents) |
| Output | 3 425 `.cs` files (sts2) + 507 `.cs` files (BaseLib), written **only** into the scratchpad |

**Citation shorthand used throughout.** Line numbers are *ILSpy 8.2 render*
line numbers in my scratch tree, not MegaCrit source lines. A different ILSpy
version will renumber them; the type/member name is the durable half of every
citation and is always given.

- `[STS2]` = `…\scratchpad\S13\sts2\MegaCrit\Sts2\Core\`
- `[BL]`  = `…\scratchpad\S13\baselib\Baselib\`

so `MegaCrit.Sts2.Core.Models.MonsterModel::VisualsPath` →
`[STS2]Models\MonsterModel.cs:216`.

**Nothing decompiled left the scratchpad.** No game source, no game data, and
no decompiled text is reproduced in this file beyond short signature-level
quotes needed to make a claim checkable (repo rule, `.gitignore:28` /
`tools/extract_base_game_pool.py:20-31`).

**Hostile enemy vs. player hook — stated once, up front.** Throughout this
document:

- a **hostile monster** is a `MonsterModel` instantiated onto
  `CombatSide.Enemy` by `CombatState::CreateCreature`
  (`[STS2]Combat\CombatState.cs:490`);
- a **player-owned summon / pet** is the *same* `MonsterModel` type
  instantiated onto `player.Creature.Side` by
  `PlayerCmd::SpawnPet` (`[STS2]Commands\PlayerCmd.cs:239`);
- a **world event** is an `EventModel` reached through an `EventRoom`
  (`[STS2]Rooms\EventRoom.cs:16`), i.e. a map node the player walks onto —
  *not* the `MegaCrit.Sts2.Core.Hooks` namespace, which is the combat/run
  callback bus and contains no player-facing content.

The side argument, not the type, is what makes a monster hostile. Any claim
of the form "X proves hostile enemies are moddable" that rests on a summon or
a pet is therefore **not** proof, and I have flagged every place that
distinction bites.

---

## 1. Type inventory

### 1.1 Hostile monsters

| Type | Where | What it is |
|---|---|---|
| `MonsterModel` (abstract) | `[STS2]Models\MonsterModel.cs:30` | The monster. Declaration-time abstracts: `MinInitialHp` / `MaxInitialHp` (`:197`,`:199`), `GenerateMoveStateMachine()` (`:549`). Everything presentational is `virtual`. |
| 122 concrete monsters | `[STS2]Models\Monsters\` | One `sealed class … : MonsterModel` per enemy. Act-1 plain example: `Nibbit` (`Models\Monsters\Nibbit.cs:18`). |
| `Creature` | `[STS2]Entities\Creatures\Creature.cs` | The combat entity wrapping a monster **or** a player. `IsDead => !IsAlive` (`:208`). |
| `MonsterMoveStateMachine`, `MoveState`, `ConditionalBranchState` | `[STS2]MonsterMoves\MonsterMoveStateMachine\` | The AI. A monster's whole behaviour is the state machine it returns. |
| `AbstractIntent`, `SingleAttackIntent`, `DefendIntent`, `BuffIntent`, `IntentType` | `[STS2]MonsterMoves\Intents\`, `[STS2]Entities\Intents\` | Telegraphs. `MonsterModel::IntendsToAttack` reads `IntentType.Attack`/`DeathBlow` (`Models\MonsterModel.cs:384-390`). Intents carry their own `AssetPaths`, folded into the monster's (`:218-230`). |
| `NCreature`, `NCreatureVisuals`, `CreatureAnimator`, `AnimState` | `[STS2]Nodes\Combat\`, `[STS2]Animation\` | The Godot presentation layer. See §4. |
| `BestiaryMonsterMove` | `[STS2]Models\BestiaryMonsterMove.cs` | Compendium rows, generated from the state machine + the Spine skeleton's animation list (`Models\MonsterModel.cs:468-509`). |
| `DeprecatedMonster` | `[STS2]Models\Monsters\DeprecatedMonster.cs` | The tombstone a save falls back to when a monster id no longer resolves (`Saves\SaveUtil.cs:93-96`). |

Mutability is a hard invariant: `ModelDb` holds one **canonical** instance per
type; combat gets a `MutableClone` via `MonsterModel::ToMutable`
(`Models\MonsterModel.cs:541`), and every setter calls `AssertMutable()`.

### 1.2 Encounters and bosses

| Type | Where | Notes |
|---|---|---|
| `EncounterModel` (abstract) | `[STS2]Models\EncounterModel.cs:25` | Abstract: `RoomType` (`:51`), `GenerateMonsters()`. Virtual: `IsWeak` (`:56`), `ShouldGiveRewards` (`:62`), `Min/MaxGoldReward` (`:64`,`:83`), `Tags` (`:114`). |
| 89 concrete encounters | `[STS2]Models\Encounters\` | Suffix carries the tier: `…Weak`, `…Normal`, `…Elite`, `…Boss`, `…EventEncounter`. |
| `RoomType` | `[STS2]Rooms\RoomType.cs` | `Monster` / `Elite` / `Boss` / `Event` / `Treasure` / `Shop` / `RestSite` / `Map`. Gold rewards switch on it (`Models\EncounterModel.cs:68-74`). |
| `EncounterTag` | `[STS2]Entities\Encounters\` | Anti-repeat family key; `SharesTagsWith` (`Models\EncounterModel.cs:280`). |
| `CombatRoom` | `[STS2]Rooms\CombatRoom.cs` | Owns the `CombatState`; `StartCombat` at `:199-235`. |
| `CombatState` / `CombatManager` | `[STS2]Combat\` | `CreateCreature` (`CombatState.cs:490`), `AddCreature` (`:717`), `RemoveCreature` (`:535`); `CombatManager::AddCreature` (`:848`), `AfterCreatureAdded` (`:861`). |
| `DeprecatedEncounter` | `[STS2]Models\Encounters\DeprecatedEncounter.cs` | Save tombstone (`Saves\SaveUtil.cs:39-42`). |

There is **no separate `BossModel`.** A boss is an `EncounterModel` whose
`RoomType` is `RoomType.Boss`, listed in the act's `BossDiscoveryOrder`
(`Models\ActModel.cs`, e.g. `Models\Acts\Overgrowth.cs:19-24`).

### 1.3 Acts and maps

| Type | Where | Notes |
|---|---|---|
| `ActModel` (abstract) | `[STS2]Models\ActModel.cs:25` | Abstract: `Index` (`:72`), `IsDefault` (`:78`), map colours (`:84-92`), `BgMusicOptions`/`MusicBankPaths`/`AmbientSfx` (`:126-130`), `BaseNumberOfRooms` (`:138`). Content: `GenerateAllEncounters()`, `AllEvents`, `AllAncients`, `BossDiscoveryOrder`. |
| 4 live acts + 1 tombstone | `[STS2]Models\Acts\` | `Overgrowth` (Index 0, default), `Underdocks`, `Hive`, `Glory`, `DeprecatedAct`. |
| `RoomSet` | `[STS2]Rooms\RoomSet.cs` | The act's drawn pools; `SwapToOrCreateAtIndex` is how the first-run fixed order is imposed (`Models\Acts\Overgrowth.cs:110-120`). |
| `ActMap` + variants | `[STS2]Map\` | `StandardActMap`, `GoldenPathActMap`, `SpoilsActMap`, `NullActMap`, `MockCraftedActMap`, `MockSinglePointActMap`, `SavedActMap`. Plus `MapCoord`, `MapPoint`, `MapPointType`, `MapPointTypeCounts`, `MapPathPruning`, `MapPostProcessing`, `MapTravel`. |
| `RunManager::CreateRoom` | `[STS2]Runs\RunManager.cs:868-892` | The single switch that turns a `RoomType` into a room object. |

### 1.4 World events

| Type | Where | Notes |
|---|---|---|
| `EventModel` (abstract) | `[STS2]Models\EventModel.cs:28` | Abstract: `GenerateInitialOptions()` (`:302`). Virtual: `IsAllowed(IRunState)` (`:323`), `IsShared` (`:85`), `LayoutType` (`:168`), `LocTable` (`:64`), `OnRoomEnter()` (`:496`), `Resume()` (`:507`), `GetAssetPaths()` (`:453`). |
| 69 concrete events | `[STS2]Models\Events\` | Includes `DeprecatedEvent`, `DeprecatedAncientEvent`. |
| `AncientEventModel` | `[STS2]Models\AncientEventModel.cs` | Subclass of `EventModel`; only Ancients may be `isPreFinished` (`Models\EventModel.cs:260-266`). |
| `EventOption` | `[STS2]Events\EventOption.cs:12` | One choice: `TextKey`, `Title`, `Description`, `OnChosen : Func<Task>?`, `HoverTips`, `IsLocked` (a null `OnChosen` **is** locked, `:64`), `Chosen()` (`:162`). |
| `EventLayoutType` | `[STS2]Events\EventLayoutType.cs` | `Default` / `Combat` / `Ancient` / `Custom`. Drives which assets get preloaded (`Models\EventModel.cs:459-489`). |
| `EventRoom` | `[STS2]Rooms\EventRoom.cs:16` | `EnterInternal` (`:56`), `Exit` (`:85`), `Resume` (`:104`). |
| `EventSynchronizer` | `[STS2]Multiplayer\Game\EventSynchronizer.cs` | Per-seat mutable events; `BeginEvent` (`:76`), `GetLocalEvent` (`:300`), `AwaitPendingOptionTasks` (`:326`). Shared events resolve one option for everyone (`:232-248`). |
| `NEventRoom` | `[STS2]Nodes\Rooms\NEventRoom.cs:171` | The Godot node. |

### 1.5 Relics

| Type | Where | Notes |
|---|---|---|
| `RelicModel` (abstract) | `[STS2]Models\RelicModel.cs:22` | Abstract: `Rarity` (`:172`). Virtual: `IsAllowedInShops` (`:205`), `MerchantCost` by rarity (`:305`), `IsStackable` (`:251`), `SpawnsPets` (`:246`), `HasUponPickupEffect` (`:241`), `IsUsedUp` (`:236`), `IsAllowed(IRunState)` (`:435`), `IsAllowedAtNeow(Player)` (`:444`), `FlashSfx` (`:352`). |
| 298 concrete relics | `[STS2]Models\Relics\` | |
| `RelicPoolModel` | `[STS2]Models\RelicPoolModel.cs` + `[STS2]Models\RelicPools\` | `ModelDb::AllRelicPools = CharacterRelicPools ∪ AllSharedRelicPools` (`Models\ModelDb.cs:234-239`). |
| Art path derivation | `RelicModel::PackedIconPath` (`:130`), `PackedIconOutlinePath` (`:132`), `BigIconPath` (`:134`) | All three derive from `IconBaseName` = `Id.Entry.ToLowerInvariant()` (`:128`) and all three are `virtual`. |

### 1.6 Potions

| Type | Where | Notes |
|---|---|---|
| `PotionModel` (abstract) | `[STS2]Models\PotionModel.cs:30` | Abstract: `Rarity` (`:97`), `Usage` (`:99`), `TargetType` (`:101`). Virtual: `CanBeGeneratedInCombat` (`:153`), `PassesCustomUsabilityCheck` (`:164`), `OnUse` (`:349`). |
| 65 concrete potions | `[STS2]Models\Potions\` | Includes `DeprecatedPotion`. |
| `PotionPoolModel` | `[STS2]Models\PotionPoolModel.cs` + `[STS2]Models\PotionPools\` | Same character/shared split as relics (`Models\ModelDb.cs:195-200`). |
| Serialization | `ToSerializable(int slotIndex)` (`:354`), `FromSerializable` (`:364`) | Potions are saved by slot index + model id. |

### 1.7 Saves and IDs

| Type | Where | Notes |
|---|---|---|
| `ModelId` | `[STS2]Models\ModelId.cs:8` | `record { Category, Entry }`, serialized as `"CATEGORY.ENTRY"` (`ToString` `:38`, `Deserialize` `:28`, which throws on any string without exactly one dot). |
| Id derivation | `ModelDb::GetEntry` (`Models\ModelDb.cs:491`) = `StringHelper::Slugify(type.Name)` (`Helpers\StringHelper.cs:90`) — CamelCase → `UPPER_SNAKE`. Category = the direct subclass of `AbstractModel`, slugified with `_MODEL` stripped (`Models\ModelId.cs:58-68`). | **The C# type name IS the save id.** Renaming a class is a save-format change. |
| `ModelDb` | `[STS2]Models\ModelDb.cs:19` | `Init()` reflects every `AbstractModel` subtype and instantiates one canonical each (`:389`); `InitIds()` stamps ids afterwards (`:429`); `Inject(Type)` / `Remove(Type)` are documented "should only be used in tests **and mods**" (`:404`, `:418`); `Preload()` warms card/relic/power icon paths (`:440`). |
| `SaveUtil` | `[STS2]Saves\SaveUtil.cs` | Eleven `XOrDeprecated(ModelId)` helpers (`:21`–`:113`). **An unresolvable id degrades to a tombstone model; it does not crash the save.** This is the entire modded-content-removal story. |
| `ISaveSchema` + `MigrationManager`/`MigrationRegistry`/`MigrationAttribute` | `[STS2]Saves\ISaveSchema.cs`, `[STS2]Saves\Migrations\` | Versioned schemas (`schema_version`) with registered migration paths per save family (`PrefsSaves`, `ProfileSaves`, `ProgressSaves`, `RunHistories`, `SerializableRuns`, `SettingsSaves`, `Shared`). Gap/duplicate/invalid-path exceptions are first-class types. |
| `SerializableRun` | `[STS2]Saves\SerializableRun.cs:16` | Carries `List<ModelId> EventsSeen`, `SerializableRoom PreFinishedRoom`, per-player state, RNG set, map history. Also `IPacketSerializable` — the same object is the multiplayer wire format. |
| `EpochState`, `ProgressState`, `UnlockState` | `[STS2]Saves\`, `[STS2]Unlocks\` | Meta-progression gating; acts consult it (`Models\Acts\Overgrowth.cs:100-108`). |

### 1.8 Asset lifecycle

| Type | Where | Notes |
|---|---|---|
| `PreloadManager` | `[STS2]Assets\PreloadManager.cs:23` | Static. `LoadRunAssets` (`:79`), `LoadActAssets` (`:91`), `LoadRoomCombatAssets` (`:106`), `LoadRoomEventAssets` (`:101`), plus treasure/merchant/rest-site. Each builds a path set and hands it to a loading session. |
| `AssetCache` | `[STS2]Assets\AssetCache.cs:12` | Thread-safe `ConcurrentDictionary<string,Resource>`. Typed getters `GetScene` (`:140`), `GetTexture2D` (`:145`), `GetMaterial` (`:150`), `GetCompressedTexture2D` (`:155`). Also `SetAsset(path, resource)` (`:165`) — a *global* cache poke. |
| Cache miss behaviour | `AssetCache::LoadAsset` (`:45-55`) | A path not preloaded is **not** an error: it logs `"Asset not cached: <path>"`, loads it synchronously, and records it in `_missedCacheAssets` so it can be unloaded later (`:91-107`). |
| Hard failure | `AssetCache::MarkAssetFailed` (`:62`) + the throw at `:47-50` | Once a path is marked failed, later loads throw `AssetLoadException("… The game installation may be corrupted.")` rather than re-entering the Godot parser. Comment says this exists to avoid repeated native crashes. |
| Path helpers | `SceneHelper::GetScenePath` → `"res://scenes/" + inner + ".tscn"` (`[STS2]Helpers\SceneHelper.cs:12-20`); `ImageHelper::GetImagePath` (`[STS2]Helpers\ImageHelper.cs:14`) | Every content path in the game is derived, never enumerated. |
| Mod pack mounting | `ModManager` (`[STS2]Modding\ModManager.cs:874-880`): `Path.Combine(mod.path, modId + ".pck")` → `ProjectSettings.LoadResourcePack(...)` when `manifest.hasPck` | The mod's own `res://` tree is merged before its assembly initializer runs (corroborated in-repo at `klee-mod/KleeCode/KleePck.cs:7-24`). |
| Mod assembly + init | `ModManager.cs:861-921` | Loads the DLL into the game's `AssemblyLoadContext`; if a type carries `[ModInitializer]` it calls that method, **otherwise it calls `harmony.PatchAll(assembly)`**. `AssemblyResolve` is redirected so mods built against an older sts2/Harmony still bind (`:1035-1046`). |

---

## 2. Two call traces, `file:line` at every load-bearing step

### 2.1 Hostile enemy: **Nibbit** — instantiation to death

**Why Nibbit.** StS2 has no Jaw Worm. Nibbit is the closest equivalent: a
single-slot act-1 normal enemy with three moves and no gimmick, and it is
literally the game's first fight — `Overgrowth::ApplyActDiscoveryOrderModifications`
pins `NibbitsWeak` to normal-encounter index 0 when `unlockState.NumberOfRuns == 0`
(`[STS2]Models\Acts\Overgrowth.cs:110-115`). Its `ModelId` is `MONSTER.NIBBIT`
(§1.7 derivation), so its derived visuals path is
`res://scenes/creature_visuals/nibbit.tscn` — corroborated by the fact that
`Nibbit` hand-overrides `DeathSfx` to the same lowercase stem
(`Models\Monsters\Nibbit.cs:38`).

| # | Step | `file:line` |
|---|---|---|
| 1 | Act declares the encounter in its pool | `Models\Acts\Overgrowth.cs:71-98` (`GenerateAllEncounters`, `NibbitsWeak` at `:85`) |
| 2 | Map node → room type → room object | `Runs\RunManager.cs:868-892` (`CreateRoom`); `RoomType.Monster` → `new CombatRoom(State.Act.PullNextEncounter(roomType).ToMutable(), State)` at `:875` |
| 3 | Encounter rolls its monsters (mutable clones + slots) | `Rooms\CombatRoom.cs:201-204` → `Models\EncounterModel.cs:260-278` (`GenerateMonstersWithSlots`; seeds a per-encounter `Rng` from run seed + floor + id hash at `:268-270`) |
| 4 | This encounter's concrete roll | `Models\Encounters\NibbitsWeak.cs:18-23` — `ModelDb.Monster<Nibbit>().ToMutable()`, then `nibbit.IsAlone = true` |
| 5 | Combat assets preloaded **before** any creature exists | `Rooms\CombatRoom.cs:206-208` → `Assets\PreloadManager.cs:106-109` → `Models\EncounterModel.cs:329-344` (`GetAssetPaths` unions each monster's `AssetPaths`) |
| 6 | Monster's own asset list = its visuals scene + every intent's assets | `Models\MonsterModel.cs:218-230` (reads `VisualsPath` at `:227`) |
| 7 | Creature created on the **enemy** side | `Rooms\CombatRoom.cs:215` → `Combat\CombatState.cs:490-505` (`CreateCreature`: asserts mutable, assigns `RunRng`, HP uniquifier + multiplayer HP scale for `CombatSide.Enemy` at `:496-500`, attaches at `:501`, seeds the monster's own `Rng` at `:502`) |
| 8 | Creature added to combat (targetable, powers live) | `Rooms\CombatRoom.cs:216` → `Combat\CombatState.cs:717-729` |
| 9 | Move state machine built exactly once | `Combat\CombatManager.cs:849` (`creature.Monster?.SetUpForCombat()`) → `Models\MonsterModel.cs:551-555` → `Models\Monsters\Nibbit.cs:68-92` (`GenerateMoveStateMachine`) |
| 10 | Combat room node spawns the creature node | `Nodes\Rooms\NCombatRoom.cs:724` → `Nodes\Combat\NCreature.cs:446-455` (`NCreature.Create`) |
| 11 | **Presentation is resolved here** | `Nodes\Combat\NCreature.cs:454` → `Entities\Creatures\Creature.cs:394-409` → `Models\MonsterModel.cs:420-432` (`CreateVisuals`) → `Assets\AssetCache.cs:140` (`GetScene(VisualsPath)`) |
| 12 | Visuals node wires its required children | `Nodes\Combat\NCreatureVisuals.cs:217-235` (`_Ready`) — see §4 |
| 13 | Animator built **only if the body is a Spine node** | `Nodes\Combat\NCreature.cs:503-518`; monster branch at `:511` (`Entity.Monster.GenerateAnimator(Visuals.SpineBody)`) → `Models\Monsters\Nibbit.cs:117-133` |
| 14 | First intent rolled | `Combat\CombatManager.cs:861-869` (`AfterCreatureAdded` → `RollMove`) → `Models\MonsterModel.cs:557-560`; re-rolled per turn via `Entities\Creatures\Creature.cs:551` |
| 15 | Monster acts | `Entities\Creatures\Creature.cs:719` → `Models\MonsterModel.cs:576-596` (`PerformMove`: waits, sets `IsPerformingMove`, targets `combatState.PlayerCreatures`, logs, awaits `move.PerformMove`, records history, and **removes itself if it died mid-move** at `:590-593`) |
| 16 | The move body (mechanics) | `Models\Monsters\Nibbit.cs:94-115` — `DamageCmd.Attack(...).FromMonster(this).WithAttackerAnim("Attack", 0.15f).WithAttackerFx(null, AttackSfx).WithHitFx("vfx/vfx_attack_slash").Execute(null)` |
| 17 | Death: HP zeroed, hooks, die-vote | `Commands\CreatureCmd.cs:489-512` (`KillWithoutCheckingWinCondition`: `LoseHpInternal`, `Hook.BeforeDeath`, `Hook.ShouldDie`, `InvokeDiedEvent`) |
| 18 | Death animation starts, length returned to the caller | `Commands\CreatureCmd.cs:513` → `Nodes\Combat\NCreature.cs:916-953` (`StartDeathAnim`: drops focus, freezes intents, **and only inside `if (_spineAnimator != null)`** plays death SFX + the `"Dead"` trigger and measures the clip, `:933-945`) |
| 19 | Fade / cleanup | `Nodes\Combat\NCreature.cs:994-1053` (`AnimDie`) → `Nodes\Vfx\NMonsterDeathVfx.cs:76,130-199` (bounds from the Spine skeleton **or**, in the `else` branch, from the plain hitbox `Control` at `:167-176`) |
| 20 | Removal from state | `Commands\CreatureCmd.cs:514-517` (`RemoveCreatureNode`), `:524-532` (`CombatManager.RemoveCreature` + `CombatState.RemoveCreature`), powers stripped at `:535-539` → `Entities\Creatures\Creature.cs:673` |

**Reading of the trace.** Mechanics (steps 3–4, 9, 14–17, 20) and presentation
(steps 5–6, 10–13, 18–19) touch in exactly two places: `VisualsPath` (read at
step 6 for preloading and at step 11 for instantiation) and `GenerateAnimator`
(step 13). That is the seam §6 rests on.

### 2.2 World event: **Wood Carvings** — entry to exit

Picked because it is a `LayoutType.Default` act-1 event with three plain
options and no combat branch — the simplest possible shape
(`[STS2]Models\Events\WoodCarvings.cs:21`). It is listed in Overgrowth's
`AllEvents` (`Models\Acts\Overgrowth.cs:42`).

| # | Step | `file:line` |
|---|---|---|
| 1 | `?` node resolves to an event room | `Runs\RunManager.cs:885` — `new EventRoom((model as EventModel) ?? (mapPointType == MapPointType.Ancient ? State.Act.PullAncient() : State.Act.PullNextEvent(State)))` |
| 2 | Room construction asserts the model is **canonical** | `Rooms\EventRoom.cs:41-45` (per-player mutable copies come later) |
| 3 | Room entered | `Runs\RunManager.cs:1091` (`EnterRoomInternal`) → `Rooms\EventRoom.cs:56` (`EnterInternal`) |
| 4 | Assets preloaded | `Rooms\EventRoom.cs:58` → `Assets\PreloadManager.cs:101-104` → `Models\EventModel.cs:453-490` (`GetAssetPaths`: layout scene always; for `Default` also the portrait, the optional phobia portrait, and the optional vfx) |
| 5 | Per-seat mutable events created and begun | `Rooms\EventRoom.cs:59` → `Multiplayer\Game\EventSynchronizer.cs:76` → `Models\EventModel.cs:230-257` (`BeginEvent`: sets `Owner`, derives a deterministic `Rng` from run seed + seat index + `Id.Entry` hash at `:237`, `BeforeEventStarted`, `CalculateVars`, then `SetInitialEventState`; **any throw runs `EnsureCleanup()` and rethrows**, `:251-255`) |
| 6 | Initial page built | `Models\EventModel.cs:260-268` → `:275` (`GenerateInitialOptionsWrapper`) → `:302` (abstract) → `Models\Events\WoodCarvings.cs:41-51` |
| 7 | Gate that could have refused the room | `Models\EventModel.cs:323-326` (`IsAllowed`) overridden at `Models\Events\WoodCarvings.cs:36-39` — every player must hold a removable Basic card |
| 8 | Godot node built and bound | `Rooms\EventRoom.cs:75` → `Nodes\Rooms\NEventRoom.cs:171` (`Create`), `:195-196` (`_event.CreateScene().Instantiate<Control>(…)` then `_event.SetNode(control)`) → `Models\EventModel.cs:331-334`, `:336-347` |
| 9 | Room-entered hook, then the event's own start hook | `Rooms\EventRoom.cs:80`, `:82` (`Hook.AfterRoomEntered`, `AfterEventStarted`) |
| 10 | Player picks an option | `Multiplayer\Game\EventSynchronizer.cs:222` / `:250` (`ChooseOptionForEvent`; shared events fan one index to all seats at `:232-248`) → `Events\EventOption.cs:162-172` (`Chosen()` awaits `OnChosen()`) |
| 11 | Option body runs (mechanics) | `Models\Events\WoodCarvings.cs:53-86` — card select, then `CardCmd.TransformTo<…>` / `CardCmd.Enchant<Slither>` |
| 12 | Page terminates | `Models\EventModel.cs:516-521` (`SetEventFinished` → `SetEventState(desc, [])`, `IsFinished = true`, `EnsureCleanup()`); UI refresh rides the `StateChanged` event (`:216`) |
| 13 | Exit | `Runs\RunManager.cs:1079-1081` (`ExitCurrentRoom` → `currentRoom.Exit(State)`) → `Rooms\EventRoom.cs:85-102`: await pending option tasks, **checksum the run if the event `IsDeterministic`** (`:89-92`), reset any internal combat state, unsubscribe, `EnsureCleanup()` on every seat |
| 14 | Saved shape | `Rooms\EventRoom.cs:112-118` (`ToSerializable` writes `EventId` + `IsPreFinished`); reload path `Rooms\EventRoom.cs:47-54` uses `SaveUtil.EventOrDeprecated` (`Saves\SaveUtil.cs:21-24`) |

**Note the branch this trace deliberately avoids.** `EventLayoutType.Combat`
events (`Models\EventModel.cs:383-420`) build an *internal* `CombatState` and
call `CreateCreature` themselves (`:400`) — that is a second, distinct route by
which a hostile monster reaches the screen, and it preloads through
`NCombatRoom.AssetPaths` + the mutable encounter instead
(`Models\EventModel.cs:477-482`).

---

## 3. Socket table, keyed to S12a–g

S12 runs later tonight. Rows below use the charter's own S12 subsystem letters
so its integrator can join on the key. **Status vocabulary:** `OPEN` = an
override/patch point exists and BaseLib already exercises it; `OPEN (base)` =
the engine member is overridable/patchable but nothing in BaseLib exercises it
for *base-game* content; `NARROW` = reachable but only through a specific
choke point; `NOT FOUND` = I looked and found no seam (see §5).

| Key | Subsystem | Engine socket (member) | Evidence | Status | Notes / what it costs |
|---|---|---|---|---|---|
| **S13-a1** | S12a hostile enemy — lifecycle | `MonsterModel` subclass + `ModelDb::Inject` | `[STS2]Models\MonsterModel.cs:30`; `Models\ModelDb.cs:404-415` | OPEN | BaseLib wraps this as `CustomMonsterModel` (`[BL]Abstracts\CustomMonsterModel.cs:10`), which self-registers in its ctor (`:20-23`). |
| **S13-a2** | S12a — AI / moves | `MonsterModel::GenerateMoveStateMachine` (abstract) | `Models\MonsterModel.cs:549` | OPEN | Mechanics only. Untouched by any presentation work. BaseLib ships `MoveBuilder` (`[BL]Monsters\MoveBuilder.cs`) as sugar. |
| **S13-a3** | S12a — intents | `MoveState` ctor takes `AbstractIntent`s | `Models\Monsters\Nibbit.cs:71-73` | OPEN | Intents contribute their own preload paths (`Models\MonsterModel.cs:228-229`). |
| **S13-a4** | S12a — **presentation of an existing base enemy** | `MonsterModel::VisualsPath` getter (`protected virtual`) | `Models\MonsterModel.cs:216`; patched by `[BL]Abstracts\VisualsPath.cs:6-18` | **OPEN (base)** | **This is the Lane D socket. See §6.** BaseLib's prefix returns `true` (falls through) for anything that is not a `CustomMonsterModel`, so a second prefix can claim base instances without fighting it. |
| **S13-a5** | S12a — presentation, node-level | `MonsterModel::CreateVisuals` (public, non-virtual) | `Models\MonsterModel.cs:420`; patched by `[BL]Abstracts\CreateVisuals.cs:7-19` | OPEN (base) | Coarser than a4: returns a live `NCreatureVisuals`. Bypasses preload (see §4.4). |
| **S13-a6** | S12a — animation states | `MonsterModel::GenerateAnimator` (`public virtual`) | `Models\MonsterModel.cs:602`; patched by `[BL]Abstracts\GenerateAnimatorPatchMonster.cs:8-20` | OPEN (base) | Only reached when a Spine body exists (`Nodes\Combat\NCreature.cs:503`). |
| **S13-a7** | S12a — enemy audio | `AttackSfx` / `CastSfx` / `DeathSfx` getters | `Models\MonsterModel.cs:292,294,296`; patched by `[BL]Abstracts\{AttackSfxMonster,CastSfxMonster,DeathSfxMonster}.cs` | OPEN (base) | FMOD event strings, derived from `Id.Entry`. Replacing one needs an FMOD bank, not a file. |
| **S13-b1** | S12b encounter registration | `EncounterModel` subclass + act pool | `Models\EncounterModel.cs:25`; `Models\Acts\Overgrowth.cs:71-98` | OPEN | BaseLib: `CustomEncounterModel` (`[BL]Abstracts\CustomEncounterModel.cs:13`), `IsValidForAct` (`:120`). |
| **S13-b2** | S12b — injecting into a **base** act's pool | Postfix on each act's `GenerateAllEncounters` | `[BL]Patches\Content\AddActContent.cs:444-451` — BaseLib enumerates every `ActModel` subtype (base **and** modded) and postfixes `GenerateAllEncounters` and the `AllEvents` getter | OPEN | Proven mechanism for adding to base acts without editing them. |
| **S13-b3** | S12b — boss | Same as b1 with `RoomType.Boss` + act `BossDiscoveryOrder` | `Models\ActModel.cs`; `Models\Acts\Overgrowth.cs:19-24` | NARROW | `BossDiscoveryOrder` is a plain virtual getter on the act; changing a **base** act's boss order needs a patch on that act type, not a pool postfix. Not exercised by BaseLib as far as I read. |
| **S13-b4** | S12b — encounter scene / background | `EncounterModel::ScenePath` (`private`, `Models\EncounterModel.cs:186`), `HasScene` (`:174`), `Slots` (`:176`), `ExtraAssetPaths` (`:233`), `GetBackgroundAssets`, `CreateBackgroundAssetsForCustom` (`:311`) | `[BL]Abstracts\CustomEncounterModel.cs:15-56` (three nested Harmony patch classes) | OPEN | Slots are read off `Marker2D` children of the encounter scene (`:66-87`). |
| **S13-c1** | S12c act registration | `ActModel` subclass | `Models\ActModel.cs:25`; `[BL]Abstracts\CustomActModel.cs:24` | OPEN | |
| **S13-c2** | S12c — map generation | `ActModel::CreateMap` | `[BL]Abstracts\CustomActModel.cs:26-39` (prefix, falls through when `CustomCreateMap` returns null) | OPEN | |
| **S13-c3** | S12c — act art (map bgs, background scene) | `BackgroundScenePath`, `MapTopBgPath` (+ mid/bot) getters | `Models\ActModel.cs:53-65`; `[BL]Abstracts\CustomActModel.cs:41-60+` | OPEN | Note `CustomActBackgroundScenePath` returns `false` **unconditionally** (`:52`), unlike the monster patches — a custom act with a null path suppresses the base path rather than falling through. |
| **S13-c4** | S12c — node mutation inside a base act | `ActModel::GenerateRooms` | `[BL]Patches\Content\ActModelGenerateRoomsPatch.cs` (file present; **I did not read its body** — flagged in §5) | UNVERIFIED | |
| **S13-d1** | S12d world-event registration | `EventModel` subclass + act `AllEvents` / shared list | `Models\EventModel.cs:28`; `Models\ModelDb.cs:135-176` | OPEN | BaseLib: `CustomEventModel` (`[BL]Abstracts\CustomEventModel.cs`), `CustomContentDictionary.AddEvent` splits act-scoped from shared (`[BL]Patches\Content\CustomContentDictionary.cs:88`), shared list joined at `[BL]Patches\Content\CustomSharedEvents.cs`. |
| **S13-d2** | S12d — choice tree | `GenerateInitialOptions()` + `SetEventState` / `SetEventFinished` | `Models\EventModel.cs:302,563,516` | OPEN | A page is `(description, options)`; there is no declarative tree format — pages are code. |
| **S13-d3** | S12d — event → combat | `EnterCombatWithoutExitingEvent<T>` | `Models\EventModel.cs:593,608` | OPEN | The second hostile-monster spawn route (§2.2 note). |
| **S13-d4** | S12d — event art | `InitialPortraitPath` / `BackgroundScenePath` / `VfxPath` (all `private`, id-derived) | `Models\EventModel.cs:202,208,210` | NARROW | These are **private**, not virtual — unlike the monster/relic paths. BaseLib works around it with `[BL]Abstracts\EventBackgroundScenePath.cs` / `InitialPortraitPath.cs`. `HasVfx` / `HasPhobiaModePortrait` are `ResourceLoader.Exists` probes (`:206,212`), so absent optional art is a legal state, not a failure. |
| **S13-e1** | S12e relic registration | `RelicModel` subclass + a `RelicPoolModel` | `Models\RelicModel.cs:22`; `Models\ModelDb.cs:234-239` | OPEN | BaseLib: `CustomRelicModel`, `CustomRelicPoolModel` (`[BL]Abstracts\CustomRelicPoolModel.cs:9`), pool joined by postfix on `ModelDb::AllSharedRelicPools` (`[BL]Patches\Content\ModelDbSharedRelicPoolsPatch.cs:8-14`). |
| **S13-e2** | S12e relic gating | `IsAllowed(IRunState)`, `IsAllowedAtNeow(Player)`, `IsAllowedInShops`, `MerchantCost` | `Models\RelicModel.cs:435,444,205,305` | OPEN | All `virtual` on the model; no patch needed for **new** relics. |
| **S13-e3** | S12e potion registration | `PotionModel` subclass + `PotionPoolModel` | `Models\PotionModel.cs:30`; `ModelDbSharedPotionPoolsPatch.cs` | OPEN | |
| **S13-e4** | S12e reward/shop surfaces | `[BL]Patches\Content\CustomRewardPatches.cs`, `RewardSynchronizerPatches.cs`, `[BL]Abstracts\CustomReward.cs` | file-level only | UNVERIFIED | Named, not read. §5. |
| **S13-f1** | S12f stable ids | `ModelId` = `(slugified category, slugified type name)` | `Models\ModelId.cs:8`; `Models\ModelDb.cs:486-493`; `Helpers\StringHelper.cs:90` | OPEN, with a trap | **The class name is the save key.** Corroborates the repo's own R69 finding (`docs/current/atlas/klee-mod-runtime.md` §4: renaming a relic type moves its runtime id and desyncs co-op). |
| **S13-f2** | S12f mod id namespacing | `ModelDb::GetEntry` postfix | `[BL]Patches\Content\PrefixIdPatch.cs:12-40` — any `ICustomModel` gets `type.GetPrefix() + entry`; `[CustomID]` overrides it outright | OPEN | Consequence: a custom monster's derived `VisualsPath` includes the prefix, which is exactly why `CustomVisualPath` exists. |
| **S13-f3** | S12f removal / downgrade | `SaveUtil.XOrDeprecated` × 11 | `Saves\SaveUtil.cs:21-113` | OPEN | Removing a mod turns its content into `Deprecated*` tombstones rather than corrupting the save. **This is engine behaviour, not a mod feature.** |
| **S13-f4** | S12f schema versioning | `ISaveSchema.schema_version` + `Migrations\` registry | `Saves\ISaveSchema.cs:8-14`; `Saves\Migrations\` | OPEN (base only) | The migration registry is the *base game's*; I found no evidence a mod can register its own migration. Absence stays absence — §5. |
| **S13-f5** | S12f extra fields on saved models | Harmony on `ToSerializable`/`FromSerializable`/`Serialize`/`Deserialize` per model family | `[BL]Patches\Saves\ExtendedSavePatches.cs:33-123` (cards, relics, …) | OPEN | Note it also patches the **packet** path, i.e. multiplayer, not just disk. |
| **S13-g1** | S12g packaging | `<modid>.pck` beside a DLL, driven by a manifest with `has_pck` / `has_dll` | `Modding\ModManager.cs:861-880`; `BaseLib.json` shape quoted in §0 | OPEN | |
| **S13-g2** | S12g dependency + version pinning | `ModManifest`, `ModDependency`, `min_game_version` | `[STS2]Modding\ModManifest.cs`, `ModDependency.cs`; `BaseLib.json` | OPEN | |
| **S13-g3** | S12g init contract | `[ModInitializer]`, else `Harmony.PatchAll` | `Modding\ModManager.cs:896-921` | OPEN | Matches the repo's per-type-patch rule (`klee-mod-runtime.md` §3). |
| **S13-g4** | S12g resource-pack collisions | `ProjectSettings.LoadResourcePack` | `Modding\ModManager.cs:880` | **TRAP** | Godot's pack loader replaces colliding `res://` paths by default. A mod pck that contains `res://scenes/creature_visuals/nibbit.tscn` **would** globally overwrite the base scene for every enemy of that id. Namespacing (`res://klee/…`, as `klee-mod/KleeCode/KleePck.cs:33` does) is what keeps a replacement local. |
| **S13-g5** | S12g localization | `LocString(table, key)`; tables `monsters`, `encounters`, `events`, `relics`, `potions`, `acts` | `Models\MonsterModel.cs:195,536`; `Models\EncounterModel.cs:107`; `Models\EventModel.cs:64,66` | OPEN | Missing a move's loc line is a `Log.Warn` + a fallback row, not a failure (`Models\MonsterModel.cs:474-481`). |
| **S13-g6** | S12g scene → C# type binding | `NodeFactory` + a postfix on `PackedScene.Instantiate(GenEditState)` | `[BL]Patches\UI\SceneConversionPatch.cs:9-26`; `[BL]Utils\NodeFactories\NodeFactory.cs:111-142` | OPEN | Lets a mod-authored `.tscn` with no attached game script become a real `NCreatureVisuals`. See §4.5 — this is a major finding for art pipelines. |

---

## 4. Animation coupling: declaration-time vs. lazy, hard vs. soft failure

### 4.1 What is required at **declaration** time (compile time, C#)

Only two things, and neither is presentational:

- `MinInitialHp` / `MaxInitialHp` (`Models\MonsterModel.cs:197,199`)
- `GenerateMoveStateMachine()` (`:549`)

Every path, scene, skin, SFX event, animator, death-fade behaviour and padding
value is a `virtual` member with a working default derived from `Id.Entry`
(`:208,216,292,294,296,311,598,602`). **A monster can be declared with no art
declared at all.**

### 4.2 What is resolved **lazily**, and when

| Thing | Resolved at | Site |
|---|---|---|
| `VisualsPath` string | twice: at combat preload, and again at node creation | `Models\MonsterModel.cs:227` and `:424` |
| The visuals `PackedScene` | combat-room entry (preload) or first use (cache miss) | `Assets\PreloadManager.cs:106`; `Assets\AssetCache.cs:26-55` |
| The `NCreatureVisuals` node | when `NCreature.Create` runs | `Nodes\Combat\NCreature.cs:454` |
| Child node handles (`%Visuals`, `%Bounds`, …) | Godot `_Ready` | `Nodes\Combat\NCreatureVisuals.cs:217-235` |
| Whether Spine exists at all | same `_Ready`, by `_body.GetClass() == "SpineSprite"` | `Nodes\Combat\NCreatureVisuals.cs:179-188`, called at `:226` |
| `CreatureAnimator` | `NCreature._Ready`, **only if** `HasSpineAnimation` | `Nodes\Combat\NCreature.cs:503-518` |
| Skins | immediately after the animator | `:512` → `Models\MonsterModel.cs:598` |
| Bestiary move list | when the compendium is opened; probes `HasAnimation("revive"/"hurt"/"die")` | `Models\MonsterModel.cs:498-509` |

### 4.3 Which missing resource shapes **fail hard**

| Missing thing | Result | Site |
|---|---|---|
| `%Visuals` node in the visuals scene | **Hard.** `GetNode<Node2D>` throws in `_Ready`. | `Nodes\Combat\NCreatureVisuals.cs:219` |
| `%Bounds` (`Control`) | **Hard.** `GetNode<Control>`. | `:221` |
| `%IntentPos` (`Marker2D`) | **Hard.** | `:222` |
| `%CenterPos` (`Marker2D`) | **Hard.** | `:223` |
| A path that already failed once | **Hard.** `AssetLoadException("… game installation may be corrupted.")` | `Assets\AssetCache.cs:47-50` |
| `%Viewport`/`Visual` inside the death-vfx scene | **Hard** (`GetNode<SubViewport>`), but that scene is base-owned | `Nodes\Vfx\NMonsterDeathVfx.cs:141,183` |

### 4.4 Which missing resource shapes **fall back**

| Missing thing | Fallback | Site |
|---|---|---|
| The whole visuals scene (load throws) | Logged `Log.Error`, reported to Sentry, replaced with `res://scenes/creature_visuals/fallback.tscn` — a **visible error scene**, not a crash | `Models\MonsterModel.cs:420-437` (`_fallbackVisualsPath` at `:171`) |
| A path that was never preloaded | `Log.Warn("Asset not cached: <path>")`, then a synchronous load; tracked for later unload | `Assets\AssetCache.cs:45-55,91-107` |
| `%PhobiaModeVisuals` | `GetNodeOrNull` → null → phobia toggle is a no-op | `Nodes\Combat\NCreatureVisuals.cs:220`, `:250-254` |
| `%OrbPos` | falls back to `IntentPosition` | `:224` |
| `%TalkPos` | null, and every consumer is null-guarded | `:225` |
| Body is **not** a `SpineSprite` | `SpineBody` stays null → `HasSpineAnimation` false → **no `CreatureAnimator` is built at all** | `:179-188` (test), `:226` (call); `Nodes\Combat\NCreature.cs:503` |
| Spine skeleton data present but unloadable | `GD.PushWarning`, `SpineBody = null` — degrades to the no-Spine path above | `Nodes\Combat\NCreatureVisuals.cs:229-233` |
| No animator, at death | `StartDeathAnim` skips SFX, the `"Dead"` trigger and the clip-length measurement; returns `0f` (or `DeathAnimLengthOverride`); `AnimDie` skips the animation wait | `Nodes\Combat\NCreature.cs:933-953`, `:1002-1018` |
| No animator, at fade | `NMonsterDeathVfx` takes the `else` branch and sizes the fade viewport from the creature's **hitbox `Control`** instead of the skeleton bounds | `Nodes\Vfx\NMonsterDeathVfx.cs:149` vs `:167-176` |
| A move's loc key missing | `Log.Warn("No loc for move …")` + a raw-state bestiary row | `Models\MonsterModel.cs:486-490` |
| An animation name missing from the skeleton | `HasAnimation` probe simply omits the bestiary row | `:498-509` |

**The load-bearing consequence.** A monster whose body is an ordinary
`Node2D`/`Sprite2D` — no Spine, no skeleton, no `.skel`/atlas — is a **fully
supported state**. It loses: the animator, animation triggers
(`SetAnimationTrigger` no-ops through `_spineAnimator?.`,
`Nodes\Combat\NCreature.cs:868-871`), the death clip and its timing, and
skeleton-accurate fade bounds. It keeps: spawning, HP bar, intents, targeting,
hitbox, damage, powers, death, hitbox-based fade, removal, and rewards.

Cost of that trade, stated plainly and **not** recommended either way: a
non-Spine enemy has no attack/hurt/death motion and its death is instant, so it
reads as a static prop that vanishes. That is a taste call, not a technical
one, and it is [USER]'s.

### 4.5 The authoring escape hatch BaseLib already ships

`NodeFactory` postfixes **`PackedScene.Instantiate(GenEditState)` itself**
(`[BL]Patches\UI\SceneConversionPatch.cs:12-26`) and, for registered paths,
converts the instantiated tree into the game's C# node type. For creature
visuals specifically, `NCreatureVisualsFactory`
(`[BL]Utils\NodeFactories\NCreatureVisualsFactory.cs:8-88`) declares the node
contract as data —

`%Visuals`, `%PhobiaModeVisuals`, `Bounds`, `%CenterPos`, `%FormVfx`,
`IntentPos`, `%OrbPos`, `%TalkPos` (`:11-21`)

— **generates the missing ones with sane defaults** (`Bounds` 240×280 at
`(-120,-280)`, `IntentPos` above it, `CenterPos` at 60 % height, an empty
`FormVfx` control), and warns rather than throws for the one it cannot invent:
`"'Visuals' node must be provided for NCreatureVisuals"` (`:58-60`).

It will even build a complete `NCreatureVisuals` **from a bare `Texture2D`**
(`CreateBareFromResource`, `:25-44`): it makes the `Bounds` control from the
texture size × 1.1 and parents a `Sprite2D` as `Visuals`.

Two things follow, both technical:

1. The practical minimum presentation for a monster under BaseLib is **one
   image**, not a rig.
2. Because conversion is keyed to registered scene paths and applied at
   `Instantiate` time, a mod-authored `.tscn` needs no game-editor script
   binding — which is what makes `PROPOSED` non-Spine proof art buildable
   without the MegaDot editor round-trip that `tools/build_pck.ps1` normally
   requires for textures.

**Unverified caveat:** I read `NCreatureVisualsFactory`'s declaration and
generation logic, not the full `NodeFactory::ConvertScene` body
(`[BL]Utils\NodeFactories\NodeFactory.cs:333-455`). Whether conversion also
reparents/retypes arbitrary children correctly for a hand-built scene is
**untested here**.

---

## 5. NON-FINDINGS, unverified rows, and remaining questions

### 5.1 NON-FINDINGS (I looked; the thing is not there)

1. **No `BossModel`.** Bosses are `EncounterModel` + `RoomType.Boss` + act
   `BossDiscoveryOrder`. Any S12 row claiming a "boss lifecycle type" would be
   a filename match, not an implementation.
2. **No declarative monster/event data format.** No JSON/YAML/resource schema
   for enemies, encounters, acts or events exists in `sts2.dll`. Content is
   C# classes; loc strings are the only externalized part.
3. **No mod-registered save migration.** `Saves\Migrations\` is a base-game
   registry keyed to base schema families; I found nothing letting a mod add a
   migration path. BaseLib's answer is additive extra fields
   (`ExtendedSavePatches`), not migrations. **Absence stays absence** — I did
   not exhaustively read the registry.
4. **No public API to replace a base monster's art.** There is no
   "`ReplaceMonsterVisuals(id, path)`" in either assembly. The seam in §6 is a
   Harmony patch on an engine member, not a supported extension point.
5. **`MegaCrit.Sts2.Core.Hooks` is not a world-event system.** It is the
   combat/run callback bus (`Hook.BeforeDeath`, `Hook.AfterRoomEntered`,
   `Hook.ShouldDie`, …). Reading it as evidence of moddable world events would
   be exactly the error the charter §7 warns about.

### 5.2 Read at file level only — treat as UNVERIFIED

`[BL]Patches\Content\ActModelGenerateRoomsPatch.cs`,
`AddCustomAncientsToPool.cs`, `CustomAncientExistence.cs`,
`CustomRewardPatches.cs`, `RewardSynchronizerPatches.cs`,
`[BL]Patches\Compatibility\`, `[BL]Patches\Networking\`,
`[BL]Utils\NodeFactories\NodeFactory.cs:333-455`, and the whole of
`[STS2]Multiplayer\`. Filenames are named above only as pointers, never as
proof.

### 5.3 Line-number fragility

Every `file:line` here is an ILSpy 8.2.0.7535 render of
`sts2.dll` MD5 `694db3d…` / `BaseLib.dll` MD5 `4380fd0…`. A game patch or a
different decompiler version renumbers everything. Re-derive from the
type/member name, which is stable.

### 5.4 Remaining questions — for [USER], as numbered picks where a call is needed

These are questions, not proposals. Numbering is for citing them, not ranking.

1. **Harmony prefix coexistence with BaseLib on `MonsterModel.get_VisualsPath`.**
   Both prefixes would run; BaseLib's returns `true` for non-`CustomMonsterModel`
   instances (`[BL]Abstracts\VisualsPath.cs:12-15`), so they should compose.
   **This is reasoned from the decompiled source and has not been executed.**
   The cheap proof is the existing manual gate `klee-mod/build/bitecheck/`
   (`docs/current/atlas/klee-mod-runtime.md` §2), which patches `sts2.dll`
   outside Godot — it can confirm both patches arm without launching the game.
2. **Does `AssetCache` ever unload a mod-namespaced path mid-run?**
   `UnloadAssets` (`Assets\AssetCache.cs:72-85`) skips anything in
   `_missedCacheAssets`, so a preloaded mod path is eligible for unload while a
   cache-missed one is not. Whether that asymmetry matters for a replaced enemy
   across a long run is **untested**.
3. **Multiplayer.** `EncounterModel::GetAssetPaths` and HP scaling are
   player-count-aware (`Combat\CombatState.cs:498`), and every seat instantiates
   its own visuals. Whether a presentation replacement present on only one seat
   desyncs anything is **unknown** — the checksum path
   (`Rooms\EventRoom.cs:89-92`) covers events, and I did not trace the combat
   checksum. Co-op has no sim backstop in this project, so this is play-derived
   only.
4. **Phobia mode.** A replacement body with no `%PhobiaModeVisuals` silently
   ignores the accessibility toggle (`Nodes\Combat\NCreatureVisuals.cs:249-254`).
   Whether that is acceptable for a proof spike vs. production is a scope call.
5. **Which enemy, if any, is the right subject.** Nibbit is my pick *for the
   trace* because it is the simplest and earliest. Whether any base enemy should
   have its presentation replaced at all — and which one — is a
   mapping/taste/rights call and is entirely [USER]'s. Lane D's charter says
   "one ordinary enemy" without naming it; §6 establishes only that the seam
   exists.

---

## 6. Lane D go/no-go — credible socket, with evidence

**Answer: YES, a credible socket exists.**

The charter's test is three-part: (i) one ordinary enemy's presentation
(model/scene/animation) can be replaced, (ii) without overwriting global base
resources, (iii) without touching its mechanics.

**(i) Replaceable.** `MonsterModel::VisualsPath` is `protected virtual`
(`[STS2]Models\MonsterModel.cs:216`) and is the **sole** source of the scene
string, read at exactly two sites: preload
(`Models\MonsterModel.cs:227`) and instantiation (`:424`). It is
demonstrably Harmony-patchable, because BaseLib already patches it —
`[HarmonyPatch(typeof(MonsterModel), "VisualsPath", MethodType.Getter)]`
with a prefix that sets `__result` and returns `false` to suppress the original
(`[BL]Abstracts\VisualsPath.cs:6-18`). The same proven pattern exists for
`CreateVisuals` (`[BL]Abstracts\CreateVisuals.cs:7-19`) and `GenerateAnimator`
(`[BL]Abstracts\GenerateAnimatorPatchMonster.cs:8-20`). BaseLib's prefixes gate
on `__instance is CustomMonsterModel` and **return `true` (fall through) for
base monsters** — i.e. base instances are unclaimed, and a mod prefix filtering
on `__instance.Id.Entry` takes them without contest.

**(ii) No global overwrite.** The replacement is a *different string*, not a
different file at the same path: base `res://scenes/creature_visuals/nibbit.tscn`
stays untouched, and the mod serves e.g. `res://<modid>/creature_visuals/…`
out of its own pack, which `ModManager` merges into `res://` via
`ProjectSettings.LoadResourcePack` (`[STS2]Modding\ModManager.cs:874-880`;
in-repo precedent `klee-mod/KleeCode/KleePck.cs:7-24,31-45`). Because the getter
patch is per-instance, every *other* monster keeps resolving to the base path.
The failure mode to avoid is named explicitly as socket **S13-g4**: shipping the
base path *inside* the mod pck would overwrite globally, since Godot's pack
loader replaces colliding paths — so the namespaced-path discipline is not
cosmetic, it is the whole of requirement (ii).

**(iii) Mechanics untouched.** Nothing in the presentation path can reach the
move machine. HP is `MinInitialHp`/`MaxInitialHp`
(`Models\MonsterModel.cs:197,199`), behaviour is `GenerateMoveStateMachine()`
(`:549` → `Models\Monsters\Nibbit.cs:68-92`), damage flows through
`DamageCmd`/`CreatureCmd`. The visuals seam produces only an `NCreatureVisuals`
node and, conditionally, a `CreatureAnimator`. `Creature`, `CombatState`,
intents and rewards never read the visuals path.

**Why it is safe to attempt.** `CreateVisuals` wraps the load in `try/catch`
and degrades to `res://scenes/creature_visuals/fallback.tscn`
(`Models\MonsterModel.cs:420-437`), so a malformed replacement is a visible
error scene plus a `Log.Error`, not a crash. A non-Spine body is a supported
state end to end, including the death fade
(`Nodes\Vfx\NMonsterDeathVfx.cs:167-176`). And BaseLib's
`NCreatureVisualsFactory` will construct the required node contract — even from
a single texture — and warns rather than throws for what it cannot invent
(`[BL]Utils\NodeFactories\NCreatureVisualsFactory.cs:25-88`).

**Which socket key Lane D should take.** Prefer **S13-a4** (`VisualsPath`)
over **S13-a5** (`CreateVisuals`) — a4 is read by the preloader too
(`Models\MonsterModel.cs:227`), so the replacement scene is warmed with the rest
of the combat set; a5 alone leaves the mod scene as a cache miss
(`Log.Warn "Asset not cached"`, `Assets\AssetCache.cs:52`) while the *base*
scene is still preloaded and then discarded. Both work; a4 is the tidier one.
This is a technical preference, `PROPOSED`, not a decision.

**Standing blocker for Lane D, not lifted by this document.** Nothing above was
executed. The game was not launched, no pck was built, no DLL was compiled, and
[USER] is playtesting on `0.2-1155` tonight. Every claim here is source-reading.
The first runtime evidence should come from the offline Harmony bite-check, not
from a deploy.

---

## What this does NOT establish

It does not establish that any enemy *should* be re-presented, which one, or
what it should look like; it does not establish that the patch composes with
BaseLib at runtime (nothing was run); it does not establish multiplayer,
save-migration, or performance safety; it does not measure anything, move any
stamp, or interpret any playtest; and it grants Lane D a technical seam, not
permission — the mapping, art, rights, scope and ship calls remain [USER]'s.
