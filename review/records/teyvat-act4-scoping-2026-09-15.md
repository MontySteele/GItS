Status: RECORD (EB-756 act-4 scoping read; decompile only, nothing built)

# EB-756: can the mod add a fourth act after Glory?

A decompile read of `sts2.dll` 0.111.0 answering BACKLOG EB-756. Nothing was
built, deployed or launched, and no git command was run. The decompile lives
outside the repo at `C:\Users\Monty\AppData\Local\Temp\claude\teyvat-decomp\`
(`ilspycmd -p`); every path below is relative to that directory. It extends
`review/records/teyvat-spike-zone-read-2026-09-14.md`, which flagged
`NRestSiteCharacter`'s throw as "the wall any future fourth act hits". That
wall is real, and it is one of exactly three.

## 1. Verdict: WORKS WITH A COST

A mod can add a fourth act at index 3 and reach it, at a cost of **three
Harmony patches** (two if the mod ships single-player only), one `ActModel`
subclass, and a complete asset set. It is this cheap because the engine almost
never asks "is this act 3?" — it asks "is this the last act?", against
`runState.Acts.Count - 1`. `RunManager.EnterNextAct` (`Runs/RunManager.cs:1316`)
is the whole act-transition decision and reads
`State.CurrentActIndex >= State.Acts.Count - 1`; so do
`Combat/CombatManager.cs:1339` (win time), `Rewards/RewardsSet.cs:91` (no
rewards after the final boss), `Models.Relics/AmethystAubergine.cs:39`,
`AutoSlay/AutoSlayer.cs:236`, `DevConsole.ConsoleCommands/ActConsoleCmd.cs:32`
and `Nodes.Debug/NSceneBootstrapper.cs:126`. Add a fourth `ActModel` to the
run's act list and all of those follow automatically — including the ending,
which simply moves one act later.

**Nothing is a fixed-size array.** `ModelDb.Acts` (`Models/ModelDb.cs:299`)
builds a `List<ActModel>` with capacity `4` via `CollectionsMarshal.SetCount`,
but it is a list behind a cached `IEnumerable` getter and the capacity binds
nothing. `ModelDb.ActsByIndex` (`Models/ModelDb.cs:323`) grows its bucket list
to fit whatever `Index` it sees — `for (int i = _actsByIndex.Count; i <=
act.Index; i++) _actsByIndex.Add(new List<ActModel>())` — so `Index => 3` mints
bucket 3 for free, and `ActModel.GetRandomList` (`Models/ActModel.cs:551`) and
`GetDefaultList` (line 587) both loop `actsByIndex.Count`.
`RunState._mapPointHistory` (`Runs/RunState.cs:295`) grows on demand in
`AppendToMapPointHistory` (line 777); `StandardActMap`'s `Grid = new
MapPoint[7, _mapLength]` (`Map/StandardActMap.cs:92`) is sized from the act's
own `GetNumberOfRooms`; `ActChangeSynchronizer._readyPlayers` is by players.

The three things that do break are: `ModelDb.Acts` does not see mod subtypes;
`MultiplayerScalingModel.GetMultiplayerScaling` throws on index 3; and
`NRestSiteCharacter._Ready` throws on index 3.

## 2. The site table

| Reader | Type.method (decompile path) | Behaviour at index 3 | Patchable? | Cost |
|---|---|---|---|---|
| Act registry | `ModelDb.get_Acts` (`Models/ModelDb.cs:299`) | Mod act invisible: hand-written 4-element list, does **not** consult `AllAbstractModelSubtypes` | Postfix, must land before the `_acts` / `_actsByIndex` lazy caches are first read | **Patch 1** |
| Index bucketing | `ModelDb.get_ActsByIndex` (`Models/ModelDb.cs:323`) | Grows to fit `Index`; creates bucket 3 | No patch | Zero |
| Act roll | `ActModel.GetRandomList` (`Models/ActModel.cs:551`), sole caller `Multiplayer.Game.Lobby/StartRunLobby.cs:469` | Loops `actsByIndex.Count`; picks one act per bucket, so a 4-act run list appears | No patch | Zero |
| Run construction | `RunState.CreateForNewRun` / `CreateShared` (`Runs/RunState.cs:539, 609`) | Stores `Acts` as given; `Act => Acts[CurrentActIndex]` (line 361) | No patch | Zero |
| Room generation | `RunManager.GenerateRooms` (`Runs/RunManager.cs:751`) | Loops `State.Acts`; shared Ancients split across `Acts.Skip(1)`; double-boss applied at `i == Acts.Count - 1` | No patch | Zero |
| Act transition | `RunManager.EnterNextAct` (`Runs/RunManager.cs:1316`), then `EnterAct` / `SetActInternal` (lines 1352, 1385) | `CurrentActIndex >= Acts.Count - 1` is now false at act 3, so it calls `EnterAct(3)` instead of the Architect; entry itself is index-agnostic | No patch — this is the whole feature | Zero |
| Map generator, floor plan | `StandardActMap..ctor` / `CreateFor` (`Map/StandardActMap.cs:87, 111`); `ActModel.GetNumberOfFloors` = `BaseNumberOfRooms` (−1 in MP) + 2; Ancient is the act's starting point (`StandardActMap.cs:301`, pulled at `RunManager.cs:966`), boss is the last row | Act declares its own room count (Glory: 13) and `GetMapPointTypes`; rng key becomes `act_4_map` | No patch | Needs ≥1 Ancient declared |
| Boss / event / Ancient pools | `ActModel.GenerateAllEncounters` → `AllBossEncounters`; `ActModel.AllEvents` + `ModelDb.AllSharedEvents` via `PullNextEvent`; `AllAncients` / `GetUnlockedAncients` | All abstract per act; the new act declares its own | No patch | Content only |
| Victory trigger | `AbstractRoom.IsVictoryRoom` (`Rooms/AbstractRoom.cs:37`) — true iff the `EventRoom`'s canonical event is `TheArchitect` | Unchanged; the Architect is now reached after act 4's boss | No patch | Zero |
| Run end | `RunManager.WinRun` / `OnEnded` (`Runs/RunManager.cs:1341, 1631`) | Index-agnostic | No patch | Zero |
| Co-op act sync | `ActChangeSynchronizer.OnPlayerReady` / `MoveToNextAct` (`Multiplayer.Game/ActChangeSynchronizer.cs:62, 79`), `GameActions/VoteToMoveToNextActAction.cs` | Purely relative (`actIndex < CurrentActIndex`); ships the index over the wire as an int | No patch | Zero |
| Save of act index | `RunManager.cs:697` writes `CurrentActIndex`; `ActModel.ToSave` / `FromSave` (`Models/ActModel.cs:513, 523`) round-trip by `ModelId` | A fourth `SerializableActModel` entry saves and loads | No patch | Zero |
| Map screen title | `NMapScreen.cs:1305, 1520` → `NActBanner.Create(act, index)`; `Nodes/NActBanner.cs:98` formats `gameplay_ui/ACT_NUMBER` with `_actIndex + 1` | Prints "Act 4" and the act's `Title` loc row | No patch | One loc row `acts/<ID>.title` |
| Music + ambience | `NRunMusicController.UpdateMusic` / `UpdateAmbience` (`Nodes.Audio/NRunMusicController.cs:273, 325`) read `_runState.Act.BgMusicOptions` / `MusicBankPaths` / `AmbientSfx` | Fully act-derived; `ResolveMusic` returns null on an empty options array | No patch | Placeholder FMOD event names |
| Chest rig | `ActModel.ChestSpineResourcePath` / `ChestSpineSkinName*` / `ChestOpenSfx` | Act-derived; point at Glory's rig | No patch | Zero |
| Backgrounds | `ActModel.GenerateBackgroundAssets` → `Rooms/BackgroundAssets..ctor` | Act-derived by `FilePathIdentifier`; **throws** `InvalidOperationException` if `res://scenes/backgrounds/<id>/layers` is missing | No patch | Full asset tree, all-or-nothing |
| **Rest-site idle** | `Nodes.RestSite/NRestSiteCharacter._Ready` (`:364`) — `switch { 0 => "overgrowth_loop", 1 => "hive_loop", 2 => "glory_loop", _ => throw new InvalidOperationException("Unexpected act") }` | **Hard crash** at the first rest site of act 4 | Transpiler on `_Ready`, or a prefix/postfix pair that swaps `RunState.CurrentActIndex` (it is a settable property, `Runs/RunState.cs:334`) around the call | **Patch 2** |
| **MP HP/block scaling** | `Models.Singleton/MultiplayerScalingModel.GetMultiplayerScaling(EncounterModel?, int)` (`:70`) — `switch` on actIndex with `default: throw new ArgumentOutOfRangeException` | **Throws** in co-op. Single-player is safe: `Creature.ScaleHpForMultiplayer` (`Entities.Creatures/Creature.cs:754`) returns early at `playerCount <= 1` and `ModifyBlockMultiplicative` returns early at `count <= 2` — but `Creature.ScaleMonsterHpForMultiplayer` (`:386`) calls it for any `playerCount != 1` | Prefix returning `false` with a 4th value, or postfix on a guarded prefix | **Patch 3** (co-op only) |
| Balance extrapolations | `Factories/CardFactory.RollForUpgrade` (`:298`) adds `actIndex * UpgradedCardOddScaling`; `Models/RelicModel.IsBeforeAct3TreasureChest` (`:453`) gates ~18 relics on a hardcoded `TotalFloor < 41` | No throw: upgrade odds peak in act 4, and those relics stay suppressed through it | Optional prefix | Balance note, see §5.4 |
| Achievement | `ActModel.DefeatedAllEnemiesAchievement` (`Models/ActModel.cs:~171`) does `Enum.Parse<Achievement>("Defeat" + Id.Entry.Capitalize() + "Enemies")` — the enum has only the four shipped names (`Achievements/Achievement.cs:10-13`) | Would throw, but **dormant**: `AchievementsHelper.CheckForDefeatedAllEnemiesAchievement`, `AfterRunEnded` and `AfterBossDefeated` are all **empty method bodies** in 0.111.0 | Latent | Zero today |
| Progress save | `Saves.Managers/ProgressSaveManager.UpdateProgressWithRunData` (`:215`) loops `MapPointHistory` against `Acts.Count`, calls `Progress.MarkActAsSeen(id)` | Marks the mod act discovered; warns only on a length mismatch | No patch | Zero |
| Continue-run card | `Nodes.Screens.MainMenu/NContinueRunInfo.cs:223, 229` uses `ModelDb.GetById<ActModel>` and sums `GetNumberOfFloors` over prior acts | Correct with the mod on; **throws** with the mod off — this path does not use `SaveUtil.ActOrDeprecated` | Not worth patching | See §5 |
| Collection / history / telemetry | `NBestiary.AddAct` (`Nodes.Screens.Bestiary/NBestiary.cs:878`, gated on `Progress.DiscoveredActs`), `NRelicCollectionCategory.cs:178` (Ancients over `ModelDb.Acts`), `NMapPointHistory.cs:96` (`SaveUtil.ActOrDeprecated`), `RunManager.UpdateRichPresence`, `Debug/SentryService.cs:489` | All enumerate or format; none compare against 2 or 3. Run history degrades to `DeprecatedAct` if the mod is gone | No patch | Untested surfaces |

## 3. The run-end path, in prose

The act-3 boss dies; `CombatManager` line 1339 sees
`RoomType.Boss && CurrentActIndex == Acts.Count - 1` and stamps
`RunManager.WinTime`. `RewardsSet.WithRewardsFromRoom` (`Rewards/RewardsSet.cs:91`)
sees the same condition and returns an empty reward set, which is why the final
boss drops nothing. The player leaves;
`ActChangeSynchronizer.MoveToNextAct` (`Multiplayer.Game/ActChangeSynchronizer.cs:79`)
calls `RunManager.EnterNextAct` (`Runs/RunManager.cs:1316`), which asks
`State.CurrentActIndex >= State.Acts.Count - 1`. Because that is true it does
**not** call `EnterAct(index + 1)`; it enters
`new EventRoom(ModelDb.Event<TheArchitect>())`. `AbstractRoom.IsVictoryRoom`
(`Rooms/AbstractRoom.cs:37`) is defined as "an `EventRoom` whose
`CanonicalEvent` is `TheArchitect`", so that room is now the victory room.
Inside it, `Models.Events/TheArchitect.cs:330` offers a `PROCEED` option bound
to a private `WinRun` (line 349) awaiting `RunManager.WinRun`
(`Runs/RunManager.cs:1341`), which calls `OnEnded(isVictory: true)` (line 1631)
— serialising the run into `SaveManager.UpdateProgressWithRunData`,
`AchievementsHelper.AfterRunEnded`, `RunHistoryUtilities.CreateRunHistoryEntry`,
`MetricUtilities.UploadRunMetrics` and `ScoreUtility.CalculateScore` (which
reads only `MapPointHistory` and gold, never an act index) — then kills the
players to unwind the run.

Add a fourth act and **none of that changes** — it just happens one act later.
At the act-3 boss, `Acts.Count - 1` is now 3, so `EnterNextAct` takes the
`EnterAct(3)` branch instead, the act-3 boss starts dropping rewards again
(because `RewardsSet`'s guard no longer fires), `WinTime` is no longer stamped
there, and the Architect waits behind the act-4 boss. There is no separate
"ending trigger" to patch: the ending is defined by the act list's length.

## 4. The cheapest design

One class and three patches.

```csharp
public sealed class TheAbyss : ActModel {              // KleeMod/Teyvat/TheAbyss.cs
    public override int  Index     => 3;               // mints ActsByIndex bucket 3
    public override bool IsDefault => true;            // GetDefaultList needs a default per bucket
    public override bool IsUnlocked(UnlockState s) => true;
    protected override int BaseNumberOfRooms => 13;    // + 2 => 15 floors, Glory's shape
    public override IEnumerable<EncounterModel> GenerateAllEncounters() => /* ≥1 Boss, elites, normals */;
    // Also: BossDiscoveryOrder, AllAncients (≥1), AllEvents, GetMapPointTypes (copy Glory's).
    // BgMusicOptions / MusicBankPaths / AmbientSfx / Chest* / Map*Color: act-derived, placeholders fine.
}
```

1. `MegaCrit.Sts2.Core.Models.ModelDb.get_Acts` — postfix appending the act.
   `_acts` and `_actsByIndex` are lazy statics, so this must be installed
   before the first read of either.
2. `MegaCrit.Sts2.Core.Nodes.RestSite.NRestSiteCharacter._Ready` — transpiler
   replacing the act-index switch, or (cheaper, uglier) a prefix setting
   `Player.RunState.CurrentActIndex = 2` and a postfix restoring it
   (`RunState.CurrentActIndex` has a public setter).
3. `MegaCrit.Sts2.Core.Models.Singleton.MultiplayerScalingModel.GetMultiplayerScaling`
   — prefix supplying a value for index 3. **Co-op only**; single-player never
   reaches the throw.

Reaching it needs nothing else: `GetRandomList` already rolls one act per
bucket, `StartRunLobby.BeginRunLocally` (`:469`) already takes the whole list,
`RunManager.GenerateRooms` already loops it, `EnterNextAct` already walks to it,
and `ActModel.ToSave` / `FromSave` already persist it by id. Assets are the real
bill: a complete `res://scenes/backgrounds/<id>/layers` tree, a rest-site scene,
three map PNGs, and one `acts/<ID>.title` loc row.

**Patch count: 3** (2 for a single-player-only build).

## 5. Risks

1. **MegaCrit shipping their own act 4 is the big one.** Their act would land
   in `ActsByIndex[3]` alongside the mod's, so `GetRandomList`
   (`Models/ActModel.cs:551`) would treat the mod act as an *alternate dressing
   of act 4*, not a fifth act — and the undiscovered-alt branch at line 563
   would **force** it on the first single-player run. `GetDefaultList`
   (line 587) would find two `IsDefault` acts in bucket 3 and silently take the
   first. The mod would have to move to `Index => 4` and re-audit. Their act
   would also add a `case 3` to `MultiplayerScalingModel.GetMultiplayerScaling`
   and a `3 =>` arm to `NRestSiteCharacter._Ready`'s switch, so patches 2 and 3
   would collide: a transpiler written against a three-arm switch will not
   match a four-arm one. Version-pin all three patches to 0.111.0.
2. **Save one-way door.** `ActModel.FromSave` (`Models/ActModel.cs:525`) and
   `NContinueRunInfo.cs:223` both use `ModelDb.GetById<ActModel>`, which throws
   rather than falling back — unlike `SaveUtil.ActOrDeprecated`, wired only into
   the run-history screen. A save taken with the mod on hard-fails the continue
   card once the mod is removed.
3. **ModelDb cache ordering.** `_acts` and `_actsByIndex` are cached on first
   read; a late patch silently yields a three-act run with no error. Prove by
   asserting `ModelDb.ActsByIndex.Count == 4` after a full boot.
4. **Run length and curve.** Nothing rebalances: ~15 more floors on top of ~45,
   `CardFactory.RollForUpgrade` (`:298`) peaking its upgrade odds there, and
   `RelicModel.IsBeforeAct3TreasureChest` (`:453`) suppressing ~18 relics for the
   whole act off a hardcoded floor 41. Nothing scales HP or ascension by act
   index, so act 4 is act 3's difficulty with a longer tail.
5. **The dormant achievement throw.** `ActModel.DefeatedAllEnemiesAchievement`
   `Enum.Parse`s a name that cannot exist for a mod act; every caller is an empty
   body in 0.111.0. If MegaCrit fills those stubs it crashes on every boss kill.
6. **Asset completeness is all-or-nothing.** `Rooms/BackgroundAssets`'s ctor
   throws on a missing `layers` directory *and* on a layer file matching neither
   the `_bg_NN` nor `_fg_` prefix; map PNGs and the rest-site scene have no
   fallback. Boot a placeholder-but-complete set before commissioning art.
7. **Rng displacement.** `RunManager.GenerateRooms` (`:751`) draws from
   `State.Rng.UpFront` once per act (the shared-Ancient split over
   `Acts.Skip(1)`, plus one `GenerateRooms` each). A fourth act consumes extra
   draws, so **every existing seed's later rolls move**: re-baseline any
   calibration seed and keep the act-4 arm off calibration deploys, for the
   same reason §5 of the run-frame packet gives for `TeyvatFrame`.
8. **Untested surfaces.** `NBestiary.AddAct` (`:878`), `NRelicCollectionCategory.cs:178`
   and the co-op `VoteToMoveToNextActAction` path were read, not exercised.
