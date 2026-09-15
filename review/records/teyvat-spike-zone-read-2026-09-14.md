Status: RECORD (spike 4.1 decompile half; feasibility only, nothing measured)

# Spike 4.1, first half: can one zone be dressed two ways?

A decompile read of `sts2.dll` 0.111.0, answering §4.1 of `review/ruled/teyvat-run-frame-2026-09-14.md`. Nothing was built, deployed or launched. The decompile lives outside the repo at `C:\Users\Monty\AppData\Local\Temp\claude\teyvat-decomp\` (3,538 files, `ilspycmd -p`); every path below is relative to that directory. Nothing here is measured and nothing here is quotable.

## 1. Verdict: WORKS WITH A COST

A zone can be dressed two ways from a mod, and the cheapest route is not the one the packet assumed. The packet imagined a per-run flag read at four or five call sites. The engine offers something better: an act is a **first-class model object** (`MegaCrit.Sts2.Core.Models/ActModel.cs`), it is selected at run start by a roll the game already performs (`ActModel.GetRandomList`, line 551), it is persisted by id (`ActModel.ToSave` / `FromSave`, lines 424 and 434), and almost everything the packet wants to vary — background scene, rest-site scene, all three map background images, map colours, act title, music tracks, ambience, treasure-chest rig, event pool, Ancient pool — is derived from that one object. So a second dressing is a second `ActModel` subclass at the same `Index`, whose `GenerateAllEncounters()` returns **the identical list of `EncounterModel` objects** as the zone it dresses. Mechanics cannot drift, because they are literally the same model instances. The coin flip, its persistence, its multiplayer sync and its save/load are then all free: the base game already rolls one act per index and already saves the winner's id. The cost is that `ModelDb.Acts` is a hardcoded four-element list, so one Harmony postfix is needed to make the new act visible; that enemy **display names and enemy visuals are keyed off the monster, not the act**, so two further patches are needed for those; and that a dressing needs a complete parallel asset set on disk, because two constructors throw rather than fall back when their directory is missing. Call it three Harmony patches, one model class per dressing, and one full asset directory per dressing.

## 2. How zones are held and rolled

A zone is an `ActModel` (`MegaCrit.Sts2.Core.Models/ActModel.cs`), an `AbstractModel` with a `ModelId`. The four concrete ones live in `MegaCrit.Sts2.Core.Models.Acts/`: `Overgrowth.cs`, `Underdocks.cs`, `Hive.cs`, `Glory.cs`. Each declares `Index` (0, 0, 1, 2) and `IsDefault` (true, false, true, true). Act-exclusive event counts are 13 / 10 / 10 / 7; the repo's 16 / 14 / 21 / 14 figures are these plus `ModelDb.AllSharedEvents`.

`ActModel.FilePathIdentifier` (line 34) is `Id.Entry.ToLowerInvariant()`, and it is the root of nearly every asset path on the class: `RestSiteBackgroundPath`, `MapTopBgPath` / `MapMidBgPath` / `MapBotBgPath`, `BackgroundScenePath` (line 397), `GetFullLayerPath`, `GetAllBackgroundLayerPaths` and `ChestSpineResourcePath`. `Title` (line 32) is `new LocString("acts", Id.Entry + ".title")`. So the act's id *is* its dressing.

The roll happens in exactly one place. `ActModel.GetRandomList(Rng, UnlockState, bool)` at `ActModel.cs:551` walks `ModelDb.ActsByIndex`, keeps the unlocked acts at each index, and calls `rng.NextItem(list2)`. Its only caller is `MegaCrit.Sts2.Core.Multiplayer.Game.Lobby/StartRunLobby.cs:469`. The rng passed in is the run's `UpFront` rng (`MegaCrit.Sts2.Core.Runs/RunRngSet.cs:34`).

`ModelDb.ActsByIndex` (`MegaCrit.Sts2.Core.Models/ModelDb.cs:323`) buckets by `Index`, which is the reason two acts can share an index at all — Overgrowth and Underdocks already do. `ModelDb.Acts` (line 299), however, is a hand-written four-element list; unlike cards and relics it does **not** consult `ModelDb.AllAbstractModelSubtypes`, which is where `ReflectionHelper. GetSubtypesInMods<AbstractModel>()` brings mod content in (line 81). A mod act is therefore invisible until `ModelDb.get_Acts` is postfixed.

Persistence: `RunState.Acts` (`MegaCrit.Sts2.Core.Runs/RunState.cs:329`) and `CurrentActIndex` (line 334) round-trip through `SerializableActModel`, which carries only `Id` and the rolled `RoomSet`. `RunState.cs:562` rebuilds via `ActModel.FromSave`, which is `ModelDb.GetById<ActModel>(save.Id).ToMutable()`. A dressing chosen as an act id survives save/load with no mod-side work.

The `GetRandomList` branch at `ActModel.cs:563` is worth naming: a non-default, unlocked, *undiscovered* act (`SaveManager.Instance.Progress.DiscoveredActs`) is **forced**, bypassing the roll, on single-player runs with `TestMode.IsOff`. On the first run after a dressing ships it will always appear, then join the coin. That is a feature for the spike and a wrinkle for a calibration seed.

## 3. What reads the zone

| Reader | Type.method (decompile path) | Can a patch fork it? | Cost |
|---|---|---|---|
| Encounter pools | `ActModel.GenerateAllEncounters` / `AllWeakEncounters` / `AllRegularEncounters` / `AllEliteEncounters` / `AllBossEncounters` (`Models/ActModel.cs:142-166`), rolled once in `ActModel.GenerateRooms` (line 292) | No patch needed — the sibling act returns the same `EncounterModel` instances | Zero. This is what makes mechanics-freeze structural rather than a promise |
| Event pool | `ActModel.AllEvents` (abstract, per act class); consumed in `ActModel.GenerateRooms`, pulled by `ActModel.PullNextEvent` (line 480) | Yes, by declaring `AllEvents` on the sibling; see §6 | Low |
| Ancient | `ActModel.AllAncients` / `GetUnlockedAncients` | Yes, same route | Low |
| Combat background | `ActModel.BackgroundScenePath` and `ActModel.GenerateBackgroundAssets` → `Rooms/BackgroundAssets.cs` ctor | Yes, via the id | Needs a full `res://scenes/backgrounds/<id>/layers` tree; the ctor **throws** `InvalidOperationException` if the directory is missing |
| Rest site | `ActModel.CreateRestSiteBackground` (line 399) ← `RestSiteBackgroundPath` | Yes, via the id | One scene |
| Map art + colours | `ActModel.MapTopBg` / `MapMidBg` / `MapBotBg`, `MapTraveledColor`, `MapUntraveledColor`, `MapBgColor` | Yes, via the id and three abstract colour properties | Three PNGs per dressing |
| Map shape | `ActModel.GetMapPointTypes(Rng)`, `ActModel.CreateMap` → `StandardActMap.CreateFor` | Yes — but copy the source act's numbers verbatim, or the map changes | Zero if copied |
| Music + ambience | `ActModel.BgMusicOptions`, `MusicBankPaths`, `AmbientSfx`, read by `Nodes.Audio/NRunMusicController.UpdateMusic` (line 273) and `UpdateAmbience` (line 325) | Yes, via the sibling's properties | This is spike item 4.4's hinge; naming a non-existent FMOD event here is the cheapest possible duck |
| Treasure chest rig | `ActModel.ChestSpineResourcePath`, `ChestSpineSkinNameNormal/Stroke`, `ChestOpenSfx` | Yes | Point at the source act's rig; costs nothing |
| Act title | `ActModel.Title` → loc table `acts`, key `<Id.Entry>.title` | Yes, one loc row per dressing | Trivial |
| Preload set | `Assets/PreloadManager.LoadActAssets(ActModel)` (line 92) reads `act.AssetPaths` | No patch needed — it reads the act's own paths | Zero |
| Rest-site idle animation | `Nodes.RestSite/NRestSiteCharacter.cs:364` switches on `Player.RunState.CurrentActIndex` → `"overgrowth_loop"` etc., and **throws** `InvalidOperationException("Unexpected act")` on any other index | Not affected — it keys off *index*, not zone, so a sibling at index 0 gets `overgrowth_loop` free | Zero, but the throw is a hard ceiling on ever adding a fourth act index |
| Enemy display name | `MonsterModel.Title` → `MonsterModel.L10NMonsterLookup` (`Models/MonsterModel.cs:196, 537`) | **No** — keyed by monster id, not act. Needs its own patch (§4) | One patch |
| Enemy visual | `MonsterModel.VisualsPath` (`Models/MonsterModel.cs:217`) | **No** — same reason. Needs its own patch (§5) | One patch |
| Achievement | `ActModel.DefeatedAllEnemiesAchievement` (line 171) does `Enum.Parse<Achievement>("Defeat" + Id.Entry.Capitalize() + "Enemies")` and would throw on a new id | Dormant: its only caller, `Achievements/AchievementsHelper.CheckForDefeatedAllEnemiesAchievement`, is an **empty method body** in 0.111.0 | Zero today; a latent crash if MegaCrit fills the stub |
| Rich presence | `Runs/RunManager.UpdateRichPresence` sends `State.Act.Id.Entry` | Harmless | Zero |
| Bestiary | `Nodes.Screens.Bestiary/NBestiary.cs:878` gates on `Progress.DiscoveredActs.Contains(act.Id)` | Untested surface | Unknown; put it on the build list |

## 4. Names and intent text

Text is `Localization.LocString` (table + key), resolved through `LocManager.Instance.SmartFormat` / `LocTable.GetRawText` (`Localization/LocString.cs:88, 99`). Three facts matter.

First, mods already merge loc tables. `LocManager.LoadTablesFromPath` at `Localization/LocManager.cs:470-479` iterates `ModManager.GetModdedLocTables (language, file)` and calls `locTable.MergeWith(dictionary4)` for each. That is the supported route for *adding or overriding* keys, and it is what the Klee mod already rides. `LocTable.MergeWith(Dictionary<string,string>)` is public, so a mod can also merge at runtime.

Second, merging is global: it cannot by itself hold two values for one key. So per-dressing names need key rewriting, not merging.

Third, there is a single choke-point for that rewrite. `MonsterModel.L10NMonsterLookup(string entryName)` (`Models/MonsterModel.cs:537`) is a public static returning `new LocString("monsters", entryName)`, and a `grep` across the decompile shows it is the **only** constructor of monster loc strings: `MonsterModel.Title` (line 196) goes through it, every hand-written override goes through it (`BigDummy.cs:13`, `DecimillipedeSegment.cs:49`), and so does every banter and speak line (`BygoneEffigy.cs:60,77`, `Chomper.cs:78`, `KinPriest.cs:27,29`, `Queen.cs:173,228`). Per-monster move titles shown in the bestiary use the same table via `MonsterModel.GetBestiaryMoveName` (line 642). One Harmony postfix on `L10NMonsterLookup` that rewrites `X.name` to `X.name@<dressing>` when the key exists (`LocString.Exists`, line 71) and falls through when it does not covers every enemy name and every line of enemy speech in the game, in about fifteen lines.

Generic intent words are a different table and are **not** per-monster: `MonsterMoves.Intents/AbstractIntent.cs:45` builds `new LocString("intents", IntentPrefix + ".title")` and line 75 does the same for `.description`. Those are shared by every act, so "Attack" is "Attack" in both dressings unless `AbstractIntent.get_IntentTitle` and `AbstractIntent.GetIntentDescription` are patched the same way. They can be, at the same cost. The design view of §7.1 of the frame packet suggests the per-monster move titles carry the nation and the generic intent verbs do not; if so this patch is optional.

## 5. Visuals

`MonsterModel.VisualsPath` (`Models/MonsterModel.cs:217`) is `protected virtual`, `SceneHelper.GetScenePath("creature_visuals/" + Id.Entry.ToLowerInvariant())`, and it is overridden in only six places, all of them `BigDummy` and mocks (`Models.Monsters/BigDummy.cs:15`, four files under `Models.Monsters.Mocks/`). No shipped act monster overrides it. That is a clean patch target: a Harmony postfix that appends a dressing suffix when the scene exists.

Critically, `MonsterModel.AssetPaths` (line 219) is built *from* `VisualsPath`, and `PreloadManager.LoadActAssets` / `LoadRoomCombatAssets` consume `AssetPaths`. So patching the getter fixes preloading for free — there is no second registration to remember.

The still-portrait question belongs to spike item 4.3, not here, but the read confirms the shape: `MonsterModel.CreateVisuals` (line 425) instantiates the scene as `NCreatureVisuals` and falls back to `creature_visuals/fallback` on exception (line 437); `NCreatureVisuals` exposes `HasSpineAnimation` and `IsSpineNode` (`Nodes.Combat/NCreatureVisuals.cs:106,111`), which is the same gate the mod already documents out of combat in `klee-mod/KleeCode/Vfx/StaticPortraitIdle.cs` and works around in `klee-mod/KleeCode/Patches/MerchantSpineBindingPatch.cs`. `MonsterModel` line 608 sets an unconditional `new AnimState("idle_loop", isLooping: true)`, which is the first door a rig-less body will hit.

Act backgrounds, by contrast, are pure convention: `Rooms/BackgroundAssets.cs` scans `res://scenes/backgrounds/<title>/layers` with `DirAccess`, groups files by `_bg_NN` / `_fg_` prefix, and picks one per group with the rng. A pck can supply that tree. It **throws** if the directory does not exist, and throws again if a layer file matches neither prefix — so the asset set is all-or- nothing, not degrade-gracefully. `ActModel.GetAllBackgroundLayerPaths` (line 411) is the forgiving twin and returns an empty array instead.

## 6. Event pools

Per-act events are `ActModel.AllEvents`, abstract, implemented as a literal array of `ModelDb.Event<T>()` in each act class. `ActModel.GenerateRooms` (line 292) concatenates it with `ModelDb.AllSharedEvents`, strips events behind unrevealed epochs (`Event1Epoch` … `Event3Epoch`), shuffles with `UnstableShuffle(rng)` and stores the whole ordering in `_rooms.events` — once, at run start, for every act (`Runs/RunManager.cs:764` loops all acts calling `act.GenerateRooms(State.Rng.UpFront, ...)`).

So a sibling act declares its own `AllEvents` and gets its own pool with no patch at all. Two further levers exist if pools need to be forked without a sibling act:

- `EventModel.IsAllowed(IRunState)` (`Models/EventModel.cs:324`) is virtual and
is consulted at *pull* time by `Rooms/RoomSet.EnsureNextEventIsValid` (line 110), which skips forward through the pre-shuffled list. A postfix here filters a pool without disturbing the shuffle's rng draws.
- `Hook.ModifyNextEvent(IRunState, EventModel)` (`Hooks/Hook.cs:1983`), called
from `ActModel.PullNextEvent` (line 480), lets a hook listener substitute the event outright.

Mod-authored events themselves are ordinary `EventModel` subclasses and *are* reflected in, since `ModelDb.AllEvents` derives from the acts and shared pools rather than from a hardcoded list. That is spike item 4.2's business.

One number to protect: forking `AllEvents` between dressings with **different list lengths** changes how many draws `UnstableShuffle` consumes from the `UpFront` rng, which moves every later roll on that rng — bosses, Ancients, encounter order. Keep the two dressings' event counts equal, or accept that the seed's map changes. This is exactly the hazard §5 of the frame packet flags for the Klee calibration seed, and it is a second reason the `TeyvatFrame` arm must be off on calibration deploys.

## 7. The cheapest design, and its save/load story

One `ActModel` subclass per dressing, one postfix to publish it, two postfixes for the things acts do not own. There is **no mod-side coin and no mod-side persistence**: the coin is `ActModel.GetRandomList`'s existing `rng.NextItem`, and the result is saved by the base game as `SerializableActModel.Id`.

```csharp
// KleeMod/Teyvat/LiyueDocks.cs — dresses Underdocks as Liyue harbour.
public sealed class LiyueDocks : ActModel {
    public override int  Index     => 0;          // shares act 1 with Overgrowth/Underdocks
    public override bool IsDefault => false;
    public override bool IsUnlocked(UnlockState s) => true;
    // MECHANICS: the identical EncounterModel instances Underdocks returns.
    public override IEnumerable<EncounterModel> GenerateAllEncounters()
        => ModelDb.Act<Underdocks>().AllEncounters;
    public override IEnumerable<EventModel> AllEvents => /* Liyue conversions, same count */;
    // Everything else (backgrounds, map art, music, title) follows Id.Entry.
}

[HarmonyPatch(typeof(ModelDb), "get_Acts")]                  // publish it
static void Postfix(ref IEnumerable<ActModel> __result) { /* append if TeyvatFrame */ }

[HarmonyPatch(typeof(MonsterModel), nameof(MonsterModel.L10NMonsterLookup))]
static void Postfix(string entryName, ref LocString __result) { /* key@dressing if it exists */ }

[HarmonyPatch(typeof(MonsterModel), "get_VisualsPath")]
static void Postfix(MonsterModel __instance, ref string __result) { /* _<dressing> if it exists */ }
```

The three patched call sites, named: `MegaCrit.Sts2.Core.Models.ModelDb.get_Acts`, `MegaCrit.Sts2.Core.Models.MonsterModel.L10NMonsterLookup`, and `MegaCrit.Sts2.Core.Models.MonsterModel.get_VisualsPath`. Optionally a fourth and fifth, `MegaCrit.Sts2.Core.MonsterMoves.Intents.AbstractIntent.get_IntentTitle` and `.GetIntentDescription`, if generic intent verbs must change too.

Where the dressing is read: any patch that needs it asks `RunManager.Instance.State.Act.Id.Entry`. It is never stored, so it cannot desync, cannot need a save migration, and is identical on every peer in multiplayer because `StartRunLobby` rolls it once and ships the run state.

If a dressing ever *must* be decided independently of act identity, the fallback needs no new save field either: `RunRngSet.StringSeed` and `Seed` provably survive save/load — `RunRngSet.LoadFromSerializable` throws `NotImplementedException("RngSet seed should not change during the run!")` if they ever differ (`Runs/RunRngSet.cs:170`) — so `new Rng(State.Rng.Seed, "teyvat_dressing").NextBool()` is a stable per-run coin that consumes nothing from the run's own rngs. `ExtraRunFields` (`Runs/ExtraRunFields.cs`) is the game's own bag for this sort of thing but has three fixed fields and a hand-written `ToSerializable`, so a mod cannot extend it without patching serialization. Don't.

## 8. Risks, and what the build half must prove

1. **`ModelDb` caches.** `_acts`, `_actsByIndex`, `_allEvents`, `_allEncounters` are all lazily cached statics. The `get_Acts` postfix must land before the first read, and `ActsByIndex` must not have been built already. Prove it by checking a new act appears in `ActsByIndex[0]` after a full boot.
2. **Harmony vs. JIT inlining.** The design deliberately patches only methods with real bodies (`get_Acts`, `L10NMonsterLookup`) and one trivial getter (`get_VisualsPath`). Trivial expression-bodied getters are inline candidates; if `get_VisualsPath` does not take, the fallback is to patch `MonsterModel.get_AssetPaths` and `MonsterModel.CreateVisuals` instead. Prove which by logging from inside the postfix.
3. **The forced-undiscovered branch** (`ActModel.cs:563`) will show the new dressing on the first run and skew any coin-fairness reading. Prove the coin over ≥20 runs *after* the act is in `DiscoveredActs`, or patch that branch.
4. **Asset completeness is all-or-nothing.** `BackgroundAssets`'s ctor throws on a missing `layers` directory and on a badly-named layer file; the three map PNGs and the rest-site scene have no fallback either. Prove a dressing boots with a placeholder-but-complete set before any art is commissioned.
5. **Event-count parity.** Prove that two dressings with equal `AllEvents` counts produce byte-identical `SerializableRoomSet` encounter orderings on a fixed seed. If they do not, every later seed claim is unsafe.
6. **Save/load round-trip.** Save mid-act in a dressing, quit to desktop, reload: prove `State.Act.Id` is unchanged and the background, map art, music and enemy names all come back dressed.
7. **Untested surfaces** that key off act id and were not read in depth: `NBestiary` (line 878), run history / score, and the `Timeline.Epochs` unlock gating. Boot each screen once with a dressing active.
8. **`NRestSiteCharacter.cs:364` throws on an unexpected act index.** Nothing in this design adds an index, but it is the wall any future fourth act hits.

Nothing above changes an enemy number, an intent's mechanical effect, or a boss behaviour: the sibling act returns the source act's own `EncounterModel` instances, and every other patch touches a string or a scene path.
