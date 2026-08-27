# S12c — Act and map hooks in public StS2 sources

**Question (charter §4, S12c):** which public source proves act / map / node mutation
(new act, altered map generation, new node types) while retaining base flow?
**Decides nothing.** Research only — no design, no proposal, no ids minted.
Researched 2026-08-26. Every claim below carries a pinned source; anything I could
not read myself is marked UNVERIFIED.

## Overview (plain English)

The answer is **yes for acts, yes for map generation, yes for node behaviour — and
no for genuinely new node kinds.** Four public mods, all pinned below, do this today.

Downfall — the mod the charter names as the first source — **does not do any of it.**
It reads the map, hooks "a room was entered" and "an act was entered", swaps art
inside existing rooms, and intercepts one node to open a custom scene. That is its
whole act/map surface. The charter's caution was right.

The real evidence is elsewhere. The base game exposes a friendly set of seams: a
subclassable `ActModel` and `ActMap`, a per-act `CreateMap` call, and two first-party
hooks (`Hook.ModifyGeneratedMap`, `Hook.ModifyUnknownMapPointRoomTypes`) that seem to
exist precisely so a map can be replaced or re-rolled. Two mods add a full Act 4 on
top of the base three; two others rewrite what every node on the map is. All keep the
base flow: they hand control back when their condition doesn't apply.

The cost is not the hook. It is everything downstream that assumed three acts: the
music controller indexes 0–2, the map-selection synchroniser must be reset, the save
must survive a missing act, and co-op needs the same map on every client.

## Pattern table

| Pattern | Purpose | Pinned source | Base type / seam it hangs off |
|---|---|---|---|
| **Append a 4th act to the live run** | Intercept the act-3→end transition, build a new `ActModel`, push it onto `RunState.Acts`, let vanilla continue and enter it | [act-4-Template@13abfb2](https://github.com/leddele/act-4-Template/blob/13abfb25b2ee96894afd1488a85d7adf21305acf/Act4MapPatch.cs#L57-L83):`Act4MapPatch.cs:57-83` | `RunManager.EnterNextAct` (Harmony prefix), `RunState.Acts` (written by reflection), `ActModel.GenerateRooms(rng, unlockState, isMultiplayer)` |
| **Same, via the private backing field** | Clone `Glory`, re-point its boss encounter, append, then `GenerateRooms` | [Act4FinalAscent@05c251a](https://github.com/kphxgames/Act4FinalAscent/blob/05c251a4186b323fc2a7fef5dab3cf586b856767/src/Act4Placeholder/Core/ModSupport.cs#L2792-L2807):`src/Act4Placeholder/Core/ModSupport.cs:2792-2807` | `RunState.<Acts>k__BackingField`, `ActModel.ToMutable()`, `SetBossEncounter` / `SetSecondBossEncounter` |
| **Declare a whole new act as a model** | A `CustomActModel` base with map bg / music banks / ambience / chest spine / rest-site scene / ancients / room count / point-type counts, auto-registered | [BaseLib@2275793](https://github.com/Alchyr/BaseLib-StS2/blob/22757933ba10adc4322a628519a233a567507d87/Abstracts/CustomActModel.cs):`Abstracts/CustomActModel.cs:22-148` | `MegaCrit.Sts2.Core.Models.ActModel`; ctor takes `actNumber` (`-1` = never spawns naturally) |
| **Get a custom act into the act list** | Transpile the `ModelDb.Acts` getter to append registered custom acts, then sort by `Index`, `IsDefault`, `Id` | BaseLib@2275793:`Patches/Content/ContentPatches.cs:315-343` | `ModelDb.Acts` getter (transpiler), `CustomContentDictionary.CustomActs` |
| **Custom map for one act, base map for the rest** | Prefix `ActModel.CreateMap`; if the act is a `CustomActModel`, call its `CustomCreateMap` — returning `null` falls through to vanilla | BaseLib@2275793:`Abstracts/CustomActModel.cs:158-161, 193-203` | `ActModel.CreateMap(RunState, bool replaceTreasureWithElites)` → `ActMap?` |
| **First-party map-replacement hook** | Postfix `Hook.ModifyGeneratedMap(runState, actIndex)` and swap in a bespoke `ActMap` for act index 3 only | [Act4FinalAscent@05c251a](https://github.com/kphxgames/Act4FinalAscent/blob/05c251a4186b323fc2a7fef5dab3cf586b856767/src/Act4Placeholder/Patches/HookModifyGeneratedMapPatch.cs):`src/Act4Placeholder/Patches/HookModifyGeneratedMapPatch.cs:13-23` | `MegaCrit.Sts2.Core.Hooks.Hook.ModifyGeneratedMap` → `ActMap` |
| **Hand-authored map graph** | Subclass `ActMap`, build a 7×9 grid, wire `AddChildPoint` edges by hand, put the boss one row past the grid | Act4FinalAscent@05c251a:`src/Act4Placeholder/Map/ShortAct4Map.cs:17-100` | `ActMap` (`Grid`, `StartingMapPoint`, `BossMapPoint`, `startMapPoints`), `MapPoint(col,row)`, `MapPoint.AddChildPoint`, `MapPoint.CanBeModified` |
| **Rewrite the route topology, keep base pruning** | Prefix the private `StandardActMap.GenerateMap()`; walk custom paths with a concept-seeded RNG; return `false` to run vanilla on error | [sts2-concept-map@c0072b3](https://github.com/ing-gom/sts2-concept-map/blob/c0072b39b4b8403e7fae0ebcb6d0cfbd2f510471/Sts2ConceptMapCode/Patches/GenerateMapPatch.cs):`Sts2ConceptMapCode/Patches/GenerateMapPatch.cs:14-19` + `ConceptMapService.cs:596-655` | `StandardActMap.GenerateMap` (private), `GetColumnCount/GetRowCount/GetOrCreatePoint/GetPoint`, `HasInvalidCrossover`, `startMapPoints`, `_rng` |
| **Re-type every node after generation** | Postfix the `StandardActMap` 7-arg constructor — the last point after `GenerateMap` + `AssignPointTypes` + pruning + post-processing — so writes are not overwritten | [sts2-random-map@f9266eb](https://github.com/ing-gom/sts2-random-map/blob/f9266ebacc88b20e31dbf312f63fb6fd10a2f739/Sts2RandomMapCode/Patches/StandardActMapPatch.cs):`Sts2RandomMapCode/Patches/StandardActMapPatch.cs:19-29`; same shape at sts2-concept-map@c0072b3:`Sts2ConceptMapCode/Patches/StandardActMapPatch.cs:18-31` | `StandardActMap..ctor(Rng, ActModel, bool, bool, bool, MapPointTypeCounts?, bool)`; `ActMap.GetAllMapPoints()`; `MapPoint.PointType` |
| **The other map subclass** | The Spoils/treasure-map event builds `SpoilsActMap`, so the `StandardActMap` patch never fires; needs its own ctor postfix | sts2-concept-map@c0072b3:`Sts2ConceptMapCode/Patches/SpoilsActMapPatch.cs:15-25` | `SpoilsActMap : ActMap`; ctor resolved via `AccessTools.GetDeclaredConstructors` |
| **Replace the "?" room roll** | Prefix `UnknownMapPointOdds.Roll` with a weighted pity model, then re-apply the relic hook the vanilla `Roll` would have run | sts2-random-map@f9266eb:`Sts2RandomMapCode/Patches/UnknownOddsPatch.cs:20-29` + `RandomMapService.cs:209-284` | `MegaCrit.Sts2.Core.Odds.UnknownMapPointOdds.Roll(IEnumerable<RoomType>, IRunState)`; `Hook.ModifyUnknownMapPointRoomTypes` |
| **Node-entry substitution** | Prefix `RunManager.EnterMapCoord`; when the coord equals `Map.StartingMapPoint.coord` in act index 0 and a Snecko is present, open a custom `EventRoom` instead and return `false` | Downfall@32e6113:`SneckoCode/Patches/SneckoSpiritDialoguePatch.cs:55-77` | `RunManager.EnterMapCoord(MapCoord)`, `RunManager.EnterRoom(AbstractRoom)`, `RunState.CurrentActIndex`, `ActMap.StartingMapPoint` |
| **Per-run gate reset** | Postfix `RunManager.CleanUp` to clear a static per-run flag | Downfall@32e6113:`SneckoCode/Patches/SneckoSpiritDialoguePatch.cs:79-83` | `RunManager.CleanUp` |
| **"A room was entered" hook, no Harmony** | Override `AfterRoomEntered(AbstractRoom)` on a run-scoped model | Downfall@32e6113:`SneckoCode/Core/SneckoModel.cs:75-81`; `AutomatonCode/Core/AutomatonModel.cs:14-24` | `BaseLib.Abstracts.CustomSingletonModel(HookType.Run)`; reads `state.Act.ActNumber()`, `state.ActFloor` |
| **"An act was entered" hook, no Harmony** | Override `AfterActEntered()`; guard on `ActFloor == 1` to run once per act | Downfall@32e6113:`GremlinsCode/Core/GremlinsRunModel.cs:62-76` | `CustomSingletonModel(HookType.Run)`; `RunManager.Instance.State.ActFloor` |
| **Act-keyed node content** | An ancient/encounter/event declares which acts it may appear in; BaseLib injects the valid ones into that act's pools at `GenerateRooms` | BaseLib@2275793:`Patches/Content/ContentPatches.cs:189-215, 274-291, 348-410`; opt-out example Downfall@32e6113:`SneckoCode/Ancients/SneckoSpirit.cs:18` | `ActModel.GenerateRooms` (pre/postfix), `RoomSet` (`_rooms`, `HasAncient`, `Ancient`), `CustomAncientModel.IsValidForAct(ActModel)` / `.ShouldForceSpawn`, `ActModel.GenerateAllEncounters`, `ActModel.AllEvents` |
| **Custom map-node icon** | Prefix `ImageHelper.GetRoomIconPath` / `GetRoomIconOutlinePath` and return the model's own art; `null` result falls through to vanilla | BaseLib@2275793:`Patches/UI/RoomIconPathPatch.cs:12-60`; independent copy Act4FinalAscent@05c251a:`src/Act4Placeholder/Patches/ImageHelperRoomIconPatch.cs` | `ImageHelper.GetRoomIconPath(MapPointType, RoomType, ModelId?)`; `CustomAncientModel.CustomMapIconPath` / `CustomRunHistoryIconPath` (Downfall@32e6113:`SneckoCode/Ancients/SneckoSpirit.cs:23-27`) |
| **Add an option inside an existing node** | Add a rest-site option to the list the game just built — with BaseLib, or with raw Harmony | BaseLib route: Downfall@32e6113:`GuardianCode/Core/GuardianModel.cs:112-125` + `GuardianCode/RestSiteOptions/GemRestSiteOption.cs:17-31`. Raw route: [sts2-custom-mods@5a39417](https://github.com/spencerqfox/sts2-custom-mods/blob/5a39417f7c234d54bf0c622d7fa403fbf7dfd6c5/FriendTrading/Code/Patches/RestSiteTradeOptionPatches.cs):`FriendTrading/Code/Patches/RestSiteTradeOptionPatches.cs:12-35` | `CustomSingletonModel.TryModifyRestSiteOptions(Player, ICollection<RestSiteOption>)`; `RestSiteOption.Generate(Player)` postfix; `BaseLib.Abstracts.CustomRestSiteOption` |
| **Swap node presentation per character** | Per-character rest-site and merchant scenes; a merchant character node subclass per character | Downfall@32e6113:`DownfallCode/Abstract/DownfallCharacterModel.cs:84-85`; `DownfallCode/Vfx/NSpineMerchantCharacter.cs:7` | `CharacterModel.CustomRestSiteAnimPath` / `CustomMerchantAnimPath`; `NMerchantCharacter` |
| **Map-screen overlay** | Postfix `NMapScreen.Open` and attach your own Godot node as a child, so visibility follows the screen | sts2-concept-map@c0072b3:`Sts2ConceptMapCode/Patches/NMapScreenPatch.cs:11-28`; also `NMapScreen._Ready` at Act4FinalAscent@05c251a:`src/Act4Placeholder/Patches/NMapScreenReadyPatch.cs` | `MegaCrit.Sts2.Core.Nodes.Screens.Map.NMapScreen` |
| **Map-screen visibility rewrite (fog of war)** | Postfix `NMapPoint.RefreshState` / `NNormalMapPoint._Ready` / `NMapScreen.RecalculateTravelability`, gated on a run modifier | sts2-custom-mods@5a39417:`FogOfWar/Code/Patches/MapFogPatches.cs:41-120` | `NMapPoint` (`Point`, `State`, `_runState`), `MapPointState`, `NMapScreen._mapPointDictionary` (`MapCoord`-keyed) / `_paths` (`(MapCoord,MapCoord)`-keyed), `MapPoint.Children`, `Hook.ShouldAllowFreeTravel`, `IRunState.Modifiers` |
| **Read-only map history** | Walk `RunState.MapPointHistory` for metrics; append a synthetic entry when force-entering a room | Downfall@32e6113:`DownfallCode/Data/DownfallMetrics.cs:46-123`; `DownfallCode/Console/AncientVisitConsoleCmd.cs:37` | `RunState.MapPointHistory` / `CurrentMapPointHistoryEntry`, `MapPointHistoryEntry.MapPointType`/`.Rooms`, `RunState.AppendToMapPointHistory(MapPointType, RoomType, ModelId)` |

## Gotchas

These are the failure modes the sources themselves document. They are the expensive
part, not the hook.

1. **A 4th act breaks the music controller.** `NRunMusicController.UpdateMusic`
   indexes acts 0–2; entering act index 3 throws "index out of bounds", so the mod
   suppresses the vanilla refresh entirely while in act 4.
   (act-4-Template@13abfb2:`Act4MapPatch.cs:212-219`.)
2. **A 4th act breaks map clicking in the base synchroniser.** On entering act
   index 3 the mod reflects out the private `MapSelectionSynchronizer` and forces
   `BeforeMapGenerated()`, or clicks are judged illegal and nothing responds.
   (act-4-Template@13abfb2:`Act4MapPatch.cs:26-51`.)
3. **A 4th act breaks the save.** Both act-4 mods carry save defence:
   act-4-Template prefixes `RoomSet.FromSave` to null-guard and to drop encounter /
   event ids that no longer resolve in `ModelDb`
   (`SaveLoadPatch.cs:14-51`); Act4FinalAscent patches `RunManager.ToSave` and
   `RunState.FromSerializable` to carry its own act-4 flags
   (`src/Act4Placeholder/Patches/Act4SaveStatePatches.cs` header). Detail belongs to
   **S12f** — pointer only.
4. **Where you write the node type matters.** Both re-typing mods target the
   `StandardActMap` *constructor postfix* specifically, because it is the last point
   after `GenerateMap`, `AssignPointTypes`, pruning, and post-processing; write
   earlier and the game overwrites you.
   (sts2-random-map@f9266eb:`Sts2RandomMapCode/Patches/StandardActMapPatch.cs:9-13`.)
5. **`StandardActMap` is not the only map.** The Spoils/treasure-map event builds a
   `SpoilsActMap`, and Golden Path acts are declared out of scope by Random Map.
   A patch that only knows `StandardActMap` silently misses them.
   (sts2-concept-map@c0072b3:`SpoilsActMapPatch.cs:8-14`; sts2-random-map@f9266eb:
   `README.md`, "Special maps … are left as the game generates them".)
6. **Some nodes are engine-fixed.** `MapPoint.CanBeModified == false` marks nodes
   the game will not let you re-type (the Spoils map's central treasure). Every
   re-typing mod also hand-exempts the start node, the boss, the second boss, the
   rest that feeds into a boss, and fixed treasure.
   (sts2-concept-map@c0072b3:`ConceptMapService.cs:681-698`.)
7. **A hand-built map must not skip rows.** `ShortAct4Map`'s own comment: the Flight
   modifier uses `GetPointsInRow(currentRow+1)` rather than `Children`, so a skipped
   row leaves the next room un-highlighted and permanently unreachable; and the boss
   must sit one row *past* the grid so the vanilla `RecalculateTravelability`
   last-row check fires.
   (Act4FinalAscent@05c251a:`src/Act4Placeholder/Map/ShortAct4Map.cs:35-53`.)
8. **Replacing a roll silently drops the relic hooks inside it.** Random Map's
   prefix on `UnknownMapPointOdds.Roll` had to re-run
   `Hook.ModifyUnknownMapPointRoomTypes` by hand, or Juzu Bracelet / Lantern Key /
   Golden Path stop working. Same shape as any wholesale prefix.
   (sts2-random-map@f9266eb:`RandomMapService.cs:252-284`.)
9. **Map generation must be seeded, not random.** Every map mod here derives its RNG
   from the run seed (concept-map swaps `m._rng` for a seeded stream and restores it
   in a `finally`; `ShortAct4Map` hashes run seed + ascension + player count) so
   co-op clients build the same map without extra network sync.
   (sts2-concept-map@c0072b3:`ConceptMapService.cs:216-238`;
   Act4FinalAscent@05c251a:`ShortAct4Map.cs:102-139`.)
10. **BaseLib version skew.** Downfall builds against `Alchyr.Sts2.BaseLib` **3.4.5**
    (Downfall@32e6113:`build/mod.build.props:20`, `Downfall.json`); our shipped
    manifest asks for **3.3.6** (`klee-mod/Klee/manifest.json`) against a workshop
    dll. `CustomActModel` exists at BaseLib master `2275793`; whether it exists at
    3.3.6 is **UNVERIFIED**.
11. **Two of these sources reach private members**, via a publicizer
    (sts2-concept-map@c0072b3:`ConceptMapService.cs:591-594`) or plain reflection
    (act-4-Template@13abfb2:`Act4MapPatch.cs:99`). That is a compatibility surface,
    not a stable API.
12. *(Pointer, other subsystems — one line each, per the standing rules.)*
    `ActModel.GenerateAllEncounters` / `RoomSet.Boss` / `eliteEncounters` are the
    encounter-pool seam → **S12b**. `EventModel.Acts` and `NEventRoom` are the event
    seam → **S12d**. `RunState.AppendToMapPointHistory` and the save patches →
    **S12f**.

## Transfer questions (against our BaseLib / Harmony abstractions)

Questions only. Nothing here is a recommendation, and none of it is scoped.

1. Our C# mod's only run-level Harmony patch today is `RunState.CreateForNewRun`
   (`klee-mod/KleeCode/KleeStartingCompanions.cs:25`) — the same seam Downfall uses
   (Downfall@32e6113:`DownfallCode/Patches/NewRunPatch.cs:7`). We have **no** act,
   map, or node patch at all. If Teyvat ever wanted a map-side behaviour, would it
   go through BaseLib's `CustomActModel` / `CustomCreateMap`, through
   `Hook.ModifyGeneratedMap`, or through a `StandardActMap` ctor postfix — and who
   decides? (All three are proven; they are not interchangeable.)
2. Does the BaseLib version we actually load (workshop dll, manifest floor 3.3.6 —
   `klee-mod/local.props:4`, `klee-mod/Klee/manifest.json`) contain
   `CustomActModel`, `CustomRestSiteOption`, and `TryModifyRestSiteOptions`? If not,
   what does moving the floor cost us, and is that a [USER] call?
3. Our sim's run layer already declares three acts and a 16-floor map with fixed
   treasure / rest / boss floors and 6 paths (`docs/current/STATE.md`, "Live cell" →
   `RUN_ACTS`, `MAP_FLOORS`, `MAP_TREASURE_FLOOR`, `MAP_REST_FLOOR`,
   `MAP_BOSS_FLOOR`, `MAP_PATHS`). The C# side's `ShortAct4Map` uses a 7-column grid
   and its own row count. **Are those two models supposed to agree**, and if a map
   pattern ever landed in the mod, would `RUNTEMPLATE_VERSION` have to move? That is
   a stamp question, not an engineering one.
4. `Hook.ModifyGeneratedMap` and `Hook.ModifyUnknownMapPointRoomTypes` are
   *first-party* hook methods, yet both mods reach them by Harmony-patching the hook
   method itself rather than registering a listener. **Is there a supported listener
   registration for `MegaCrit.Sts2.Core.Hooks.Hook`, and does BaseLib wrap it?**
   This is exactly the kind of thing S13 can settle from the decompile; I could not.
5. Every map mod here is deterministic from the run seed for co-op reasons. Our
   co-op has only a partial automated backstop (`docs/current/STATE.md`, klee-mod
   bullet; `klee-mod/KleeTests/README.md`). **What would we need before we could
   claim a map-side change is co-op-safe** — is there any test seam short of two
   live seats?
6. Downfall's `AfterRoomEntered` / `AfterActEntered` overrides need no Harmony at
   all. **Do we already have a run-scoped `CustomSingletonModel(HookType.Run)`**, or
   would adopting one be a new dependency on BaseLib surface we don't currently use?
7. Act 4 mods each carry a save-compat patch. Our save/version story is S12f's, but
   the question lands here too: **would any act/map change of ours have to be
   save-compatible with a run in progress**, and is that a LAW-level answer?

## NON-FINDINGS

1. **New node *type* — NOT PROVEN.** No source in the boundary mints a new
   `MapPointType` or `RoomType` value. BaseLib *can* generate new values for an
   arbitrary enum (`Patches/Content/CustomEnums.cs:20-24, 168-198` — a generic
   `KeyGenerator` over any enum type), but its own doc comment says the extra
   functionality currently covers `CardKeyword` and `PileType`
   (`CustomEnums.cs:16-17`), and those two plus `RewardType` are the only enum
   types the file names at all. Nothing in it teaches map generation, the map
   screen, or room construction about a new value.
   Every mod here **re-uses the existing node types** and changes which one a node
   is. Treat "new node type" as unproven, not as impossible.
2. **`(MapPointType)7` / `(MapPointType)8` — UNVERIFIED, flagged for S13.**
   `ShortAct4Map` assigns its boss and start points by numeric cast
   (Act4FinalAscent@05c251a:`src/Act4Placeholder/Map/ShortAct4Map.cs:57,62`). I know
   `MapPointType` has at least Monster / Elite / RestSite / Shop / Treasure /
   Ancient / Boss / Unknown from the mods that name them, but **not the enum's
   ordering or member count**, so I cannot say whether 7 and 8 are existing members
   written numerically (most likely) or out-of-range values. S13 can read this
   directly from the decompile. Do not build on it either way.
3. **Downfall does not mutate acts or maps.** No `CustomActModel`, no `ActMap`
   subclass, no map-generation patch, no encounter-pool or act-pool change. Its
   entire act/map surface is the five rows attributed to it above. Its one custom
   ancient explicitly opts *out* of map placement — `IsValidForAct(ActModel) => false`
   (Downfall@32e6113:`SneckoCode/Ancients/SneckoSpirit.cs:18`) — and is force-entered
   by the `EnterMapCoord` prefix instead. The complete list of act/room/map lifecycle
   overrides in the whole Downfall repository is five: `AfterRoomEntered` ×2,
   `AfterActEntered`, `TryModifyRestSiteOptions`, `IsValidForAct`.
4. **No public source proves removing or reordering a base act.** Every act mod here
   *appends*. Nothing shrinks the run or swaps act 2 for something else. BaseLib's
   `CustomActModel(actNumber)` sets `Index = actNumber - 1` and `-1` means "never
   spawns naturally" (`Abstracts/CustomActModel.cs:32-42`) — how an act at a
   *contested* index is chosen over the base act at that index is not shown by any
   code I read. UNVERIFIED.
5. **No test coverage found for any of it.** None of the four map/act mods ships a
   test project or a headless check for map generation. Their verification method is
   playing the game.
6. **Licensing is mixed and is [USER]'s call, not mine.** sts2-random-map,
   sts2-concept-map, sts2-custom-mods, and BaseLib-StS2 are MIT. Act4FinalAscent is
   MIT (`LICENSE`, "Act 4: Final Ascent Contributors"). **act-4-Template ships no
   LICENSE file at all.** Downfall has a LICENSE I did not open for this stream.
   Under charter §3.7 all of it is reference-reading only regardless.

## Search boundary (charter §7 — widened once, recorded)

Date: **2026-08-26.** Primary sources only; every citation pinned to a commit SHA.

- **Started at** the charter's pinned Downfall,
  `lamali292/Downfall@32e61132052ae58e32cd33342d24136ffe18be12`, read from the local
  read-only fetch. Exhaustive greps over all `*.cs` for `MapNode|MapRoom|NMap|MapGen|
  MapData|Act[0-9]|ActData|NAct|RoomType|NodeType|MapPath|Floor`, `MapCoord|MapPoint|
  \.Map\b|GenerateMap|MapModel`, `CurrentActIndex|ActIndex|ActModel|Acts|RunActEntry`,
  `Sts2.Core.Map`, `Sts2.Core.Rooms`, `RunManager`, `EncounterPool|EncounterModel`,
  `RestSite`, `merchant|shop|treasure|chest`, and every `override … (Act|Room|Run|Map|
  Floor|Rest|Merchant|Shop|Boss|Encounter)…(`. Result: the five overrides and the
  `EnterMapCoord` prefix listed above; nothing else.
- **Widened once**, via WebSearch (`"Slay the Spire 2 mod custom act map node github
  BaseLib"`, `"Alchyr BaseLib StS2 github repository slay the spire 2 modding
  library"`) and the GitHub REST API (repo search `"slay the spire 2 mod act"`; user
  repo listing for `ing-gom`). Code search requires auth and returned 401; the core
  API rate-limited after ~60 calls, after which I read raw file content from
  `raw.githubusercontent.com` and two source tarballs from `codeload.github.com`
  (extracted to scratch, outside every repo).
- **Repositories opened and read:** `Alchyr/BaseLib-StS2@22757933ba10adc4322a628519a233a567507d87`;
  `ing-gom/sts2-random-map@f9266ebacc88b20e31dbf312f63fb6fd10a2f739`;
  `ing-gom/sts2-concept-map@c0072b39b4b8403e7fae0ebcb6d0cfbd2f510471`;
  `spencerqfox/sts2-custom-mods@5a39417f7c234d54bf0c622d7fa403fbf7dfd6c5`;
  `leddele/act-4-Template@13abfb25b2ee96894afd1488a85d7adf21305acf`;
  `kphxgames/Act4FinalAscent@05c251a4186b323fc2a7fef5dab3cf586b856767`.
- **Seen in listings, NOT opened** (time; named so the next pass doesn't re-search):
  `ing-gom/sts2-blind-map`, `ing-gom/sts2-map-legend-count`,
  `Alchyr/ModTemplate-StS2`, `1r1di0us/OuterSteppes`,
  `FullLifeGames/SlayTheSpire2RandomizerMapMod`,
  `Kziz3988/ActsFromThePastMultiplayerBalance`, `leddele/slay-the-spire-2-more-bosses`.
  The BaseLib wiki (`alchyr.github.io/BaseLib-Wiki`) was also not opened — the
  repository source was available and is the stronger evidence.
- **Not used as evidence anywhere:** wikis, forum posts, Nexus/Steam pages, search-result
  summaries, or any filename/folder/namespace read as proof of an implementation.

## What this does NOT establish

- **Not that any of it works on our pinned game build.** Our environment is StS2
  v0.107.1 / commit `59260271` (`docs/current/STATE.md`). Downfall targets 0.107.1;
  the other five sources' game pins were not checked. Nothing here was run.
- **Not that these seams are stable API.** Two of the six reach private members
  (a publicizer, reflection on `<Acts>k__BackingField` and private
  `MapSelectionSynchronizer`). A game patch can remove any of them.
- **Not a design, mapping, scope, or feasibility verdict.** Nothing here says Teyvat
  Spire should have a fourth act, a themed map, or a new node. It says only what
  public code has been shown to do and what it cost.
- **Not an estimate.** No effort figures, no ordering, no batch, no ids.
- **Not a rights or reuse finding.** Licences are recorded as facts; whether any of
  it may inform our work beyond reference-reading is [USER]'s, and copying is barred
  by charter §3.7 regardless.
- **Not the socket table.** Base-type names here are taken from *mod* call sites, not
  from the decompile. S13 is authoritative on `ActModel`, `ActMap`, `StandardActMap`,
  `MapPoint`, `MapPointType`, `RoomType`, `UnknownMapPointOdds`, and
  `MegaCrit.Sts2.Core.Hooks.Hook` — including the two open items above:
  `MapPointType`'s membership (NON-FINDING 2) and whether `Hook` has a supported
  listener registration rather than a method to patch (transfer question 4).
- **Not co-op-verified.** The sources *claim* determinism and co-op safety; I read
  the seeding code, I did not observe two clients agree.
