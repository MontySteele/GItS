# S12f — Save and version compatibility in public StS2 sources

> Research only. Decides nothing. Every claim below carries a pinned source; anything
> unpinned is marked UNVERIFIED. Retrieval date for all sources: **2026-08-26**.

## Overview

Saves are well evidenced, but mostly not in Downfall — the answers are in BaseLib
and in MegaCrit's own patch notes. Four things are proven. **One:** the base game
keeps modded and unmodded saves in *separate directories*, copies the unmodded ones
over once on first modded launch, and never merges them back. **Two:** since v0.107.1
it "no longer deletes progress from mods that are removed or errored", and a run save
holding a modded *character* loaded without its mod errors loudly rather than
black-screening. **Three:** mod content is identified in saves by a `ModelId` that
BaseLib prefixes from the mod's root namespace and derives from the C# class name —
a class rename is an ID change, and no public source declares an explicit stable ID
string. **Four:** extra mod data reaches the save via two BaseLib mechanisms
(`SavedSpireField`, `ExtendedSaveHandlers`) keyed on a plain string you pick,
ordinally sorted for a deterministic encoding, and silently skipped when absent on
load. Listed as NON-FINDINGS below, because nothing public proves them: a save-schema
version number, any migration path for a mod's own data, and the fate of modded
*cards or relics* (not characters) when their mod goes away mid-run.

## Pinned sources

| Tag used below | Source | Pin | License |
|---|---|---|---|
| `Downfall@32e6113` | `lamali292/Downfall` | `32e61132052ae58e32cd33342d24136ffe18be12` | MIT (`LICENSE`) |
| `BaseLib@2275793` | `Alchyr/BaseLib-StS2` (= release `v3.4.5`) | `22757933ba10adc4322a628519a233a567507d87` | MIT |
| `BaseLibWiki@5558d89` | `Alchyr/BaseLib-Wiki` (source of alchyr.github.io/BaseLib-Wiki) | `5558d8982dc7c28300f8c5de8fbc97620da009cf` | — |
| `Jayden@b2cae7b` | `JaydenLiang/slay-the-spire-2-mods` (`modded-save-sync`) | `b2cae7b13157dbaf9eee09b8734883507402f146` | MIT |
| `luojiesi@3de9d08` | `luojiesi/SLS2Mods` (`UnifiedSavePath`) | `3de9d089bced96b697458f13b6c33846032bdb1c` | — (no LICENSE file) |
| `nyaoouo@2c58c2f` | `nyaoouo/sts-2-saves` (`STS2Saves`) | `2c58c2f1e71b1963e12129714082e15e30acebc5` | — (no LICENSE file) |
| `uploader@d7b7e6b` | `megacrit/sts2-mod-uploader` (MegaCrit's own) | `d7b7e6b16c413d5a124f474f9e5104ef01f76ab1` | — |
| `PN-<ver>` | Slay the Spire 2 patch notes, published by MegaCrit | retrieved via Valve's official `ISteamNews` API for appid `2868840`, 2026-08-26 | — |

Patch-note pins (title, date, Steam announcement `gid`):

- `PN-0.111.0` — "Beta Patch Notes - v0.111.0", 2026-08-14, gid `1840944183778277`
- `PN-0.109.0` — "Beta Patch Notes - v0.109.0", 2026-07-17, gid `1838407329258348`
- `PN-0.108.0` — "Beta Patch Notes - v0.108.0", 2026-07-03, gid `1836506165569491`
- `PN-0.107.1` — "Major Update #2 - v0.107.1", 2026-06-19, gid `1835871199305790`
- `PN-0.106.0` — "Beta Patch Notes - v0.106.0", 2026-05-22, gid `1833334318570400`
- `PN-0.105.0` — "Beta Patch Notes - v0.105.0", 2026-05-08, gid `1832065502813730`

(Announcement URL form: `https://steamcommunity.com/games/2868840/announcements/detail/<gid>`.
The API returned `steamstore-a.akamaihd.net/news/externalpost/steam_community_announcements/<gid>`
for the same items. Patch notes are the developer's own publication, which is why
they are treated as primary here; no forum, wiki, or guide was used as evidence.)

## Pattern table

| Pattern | Purpose | Pinned source | Base type / interface it hangs off |
|---|---|---|---|
| **Modded/vanilla save-path split** | The game routes saves to a different profile directory when any mod is loaded, so modded play cannot damage vanilla progress | `PN-0.108.0`; `Jayden@b2cae7b:docs/designs/modded-save-sync.md:9-17`; `luojiesi@3de9d08:UnifiedSavePath/UnifiedSavePathMod.cs:21-54` | `MegaCrit.Sts2.Core.Saves.UserDataPathProvider` — `IsRunningModded` (property), `GetProfileDir(int profileId)` |
| **One-way copy on first modded launch** | Unmodded saves are copied into the modded directory the first time you launch modded, with an explaining popup; they stay separate afterwards | `PN-0.108.0` ("Unmodded saves are now copied to the modded save directory if you are launching modded for the first time"); refined by `PN-0.111.0` (no copy if the player declined mod loading) | base-game save bootstrap (type not named in the notes) |
| **Removed-mod progress is retained** | Progress belonging to a mod that is removed or failed to load is no longer deleted | `PN-0.107.1` MODDING section: "The base game no longer deletes progress from mods that are removed or errored" | base-game progress save (type not named) |
| **Loud failure for a missing modded character** | Loading a run save whose character's mod is absent raises an explicit error instead of a black screen | `PN-0.107.1`; earlier form in `PN-0.105.0` | `current_run.save` (run save file) |
| **Run save file naming** | The active run save is a named file under a profile-scoped saves directory; multiplayer has its own | `nyaoouo@2c58c2f:Src/Infrastructure/Persistence/SaveArchivePathResolver.cs:163-164` | `MegaCrit.Sts2.Core.Saves.Managers.RunSaveManager.runSaveFileName` / `.multiplayerRunSaveFileName`; `UserDataPathProvider.SavesDir`; `SaveManager.Instance.GetProfileScopedPath(...)` |
| **Mod data written beside the save** | Mods put their own files under the *profile-scoped* path, so mod data follows the modded/vanilla split automatically | `nyaoouo@2c58c2f:Src/Infrastructure/Persistence/SaveArchivePathResolver.cs:12-43` | `SaveManager.GetProfileScopedPath(string)`; Godot `user://` (globalized at `:173-178`) |
| **Automatic ID prefixing** | Every custom model's save-facing ID is prefixed with the mod's root namespace, so two mods rarely collide | `BaseLibWiki@5558d89:docs/models/index.md:11`; `BaseLibWiki@5558d89:docs/Features.md:10` | `ICustomModel` (or any `CustomModel` class); `ModelId` (category + entry) |
| **ID derived from the class, never declared** | Not one Downfall model declares an explicit ID string; the entry is generated from the type name plus prefix | `Downfall@32e6113` — zero matches for `override ModelId Id` across the tree; corroborated by `Downfall@32e6113:DownfallCode/Abstract/CustomIntent.cs:12` (`GetType().Name.ToSnakeCase().ToUpperInvariant()`) and `DownfallCode/Artists/Artist.cs:13`; loc keys such as `AUTOMATON-DEPRECATE.title` (`Downfall@32e6113:Automaton/localization/eng/cards.json:61`) for class `Deprecate` (`AutomatonCode/Cards/Common/Deprecate.cs:12`) | `ModelId`, `ModelDb` |
| **Retired content kept registered** | Cut cards/relics stay in the tree marked `[Obsolete]` but still carry their pool attribute, so the ID keeps resolving | `Downfall@32e6113:AutomatonCode/Cards/Removed/Batch.cs:7-9`; `GremlinsCode/Relics/FragmentationGrenade.cs:10-13`; `GuardianCode/Relics/WanderBots.cs:12`; `HermitCode/Cards/Rare/ScopeOut.cs:9` | `[Pool(typeof(...))]` on a `CardModel` / `RelicModel` |
| **`SavedSpireField` — extra persistent field on a base type** | Attach a saved value to a model or the player without owning the class | `BaseLibWiki@5558d89:docs/utilities/spirefield.md:43-60`; used at `Downfall@32e6113:CollectorCode/Core/EssenceModel.cs:9`, `CollectorCode/Core/CollectiblesModel.cs:17-38`, `GremlinsCode/Core/GremlinsRunModel.cs:18-37` | `SavedSpireField<TKey,TVal>`; holders: `CardModel`, `RelicModel`, `PotionModel`, `EnchantmentModel`, `Player`, `Reward`, `IRunState` (`BaseLib@2275793:Patches/Saves/ExtendedSaveTypes.cs:46-54`) |
| **Save-key string chosen by the mod author** | The `SavedSpireField` constructor takes the save-data name; uniqueness is convention, not enforcement | `BaseLibWiki@5558d89:docs/utilities/spirefield.md:47` ("Try to ensure that the name will be something unique to your mod to avoid conflicts") | `SavedSpireField` ctor arg |
| **Built-in save types vs. registered types** | A short list saves without ceremony; everything else needs an explicit registration in the mod initializer | `BaseLibWiki@5558d89:docs/utilities/spirefield.md:49-60`; `BaseLib@2275793:Utils/SavePatchUtils.cs:13-29` | `int, bool, string, int[], ModelId, SerializableCard, SerializableCard[], List<SerializableCard>`, plus any enum |
| **`ExtendedSaveTypes` registration** | Teach the base-game JSON serializer about a mod's own save type | `Downfall@32e6113:GremlinsCode/GremlinsMainFile.cs:30-35` (object + list); `DownfallCode/DownfallMainFile.cs:41`; `GuardianCode/GuardianMainFile.cs:63` | `BaseLib.Patches.Saves.ExtendedSaveTypes` — `RegisterObjectSaveType<T>`, `RegisterListSaveType<T>`, `PropertyFunc<T,P>` |
| **`ExtendedSaveHandlers` — extra data hung off a serializable** | Attach mod data to a *specific* saved card/relic/player/reward and have it survive save and network copy | `Downfall@32e6113:GuardianCode/GuardianMainFile.cs:65-108` (gems on a card); mechanism at `BaseLib@2275793:Patches/Saves/ExtendedSaveHandlers.cs:78-190` | `ExtendedSaveHandlers<CardModel, SerializableCard>.RegisterSave(id, getter, setter, writer, reader)` |
| **On-disk shape is JSON, keyed by your string ID** | Extended data lands in a JSON property `save_dict_<TypeName>` holding a `Dictionary<string,T>` whose keys are the registered IDs | `BaseLib@2275793:Patches/Saves/ExtendedSaveHandlers.cs:136-147` and `:194-207`; JSON context patched at `Patches/Saves/ExtendedSaveTypes.cs:15-27` | `MegaCritSerializerContext` (System.Text.Json source-generated), `JsonPropertyInfo` |
| **Deterministic ordering of save keys** | Registered fields and extended saves are sorted by ordinal string comparison so the encoding does not depend on mod load order | `BaseLib@2275793:Patches/Utils/SavedSpireFieldPatch.cs:44-47`; `BaseLib@2275793:Utils/SavePatchUtils.cs:244-248` | `ISavedSpireField.Name`; `ExtendedSaveInfo.Id` |
| **Base game sorts its own ID map too** | MegaCrit moved the serialization cache to sort by `ModelId` rather than typename, and to push non-gameplay mods to the end | `PN-0.108.0`: "Sort content by ModelId instead of typename"; "Content from mods with affectsGameplay set to false are now sorted to end of ID maps"; "Exclude non-gameplay-affecting models from the `ModelIdSerializationCache` hash" | `ModelIdSerializationCache` |
| **`[SavedProperty]` on a model's own property** | Per-instance run state that lives on the card/relic itself (a card that grows, a relic that remembers a character) | `Downfall@32e6113:AutomatonCode/Cards/Rare/CultistStrike.cs:27,39`; `HermitCode/Cards/Uncommon/CursedWeapon.cs:59,72`; `HermitCode/Cards/Uncommon/GoldenBullet.cs:25`; `SneckoCode/Relics/SneckoChoice.cs:32-34`; registration noted at `BaseLibWiki@5558d89:docs/Features.md:26` | base-game `[SavedProperty]` + `SavedPropertiesTypeCache`; setters call `AssertMutable()` |
| **Canonical model vs. mutable run copy** | The registered model is immutable; saved state only exists on the per-run mutable clone | `Downfall@32e6113:SneckoCode/Relics/SneckoChoice.cs:50` (`AssertMutable()`); `GuardianCode/Core/GemModel.cs:56,132`; `HexaghostCode/Core/GhostflameModel.cs:139,198`; `ToMutable()` used at `GuardianCode/GuardianMainFile.cs:83` | `AbstractModel.ToMutable()`, `CanonicalInstance` |
| **Unresolvable ID skipped, not fatal** | On load, a saved gem ID that no longer resolves to the expected type is skipped and the rest of the list still loads | `Downfall@32e6113:GuardianCode/GuardianMainFile.cs:81-82` | `ModelDb.GetById<CardModifier>` + type pattern-match |
| **Defensive `?? ModelId.none`** | Every ID read out of a `Serializable*` is treated as possibly null | `Downfall@32e6113:DownfallCode/Data/DownfallMetrics.cs:103,112-114` | `SerializableRun`, `SerializablePlayer`, `SerializableCard`, `SerializableRelic` (`MegaCrit.Sts2.Core.Saves.Runs`) |
| **"Is this content still resolvable and mine?"** | A guard that resolves each saved ID and checks the owning assembly before acting on a finished run | `Downfall@32e6113:DownfallCode/Data/RunMetricsUploader.cs:208-228` | `ModelDb.GetByIdOrNull<T>(ModelId)`, `AbstractModel` |
| **Piggyback on an existing save field** | `SerializableReward` has no room for custom fields, so a custom reward stores its quantity in the existing `GoldAmount` slot | `Downfall@32e6113:CollectorCode/Rewards/EssenceReward.cs:42-49`; card-shaped variant at `CollectorCode/Rewards/CollectibleReward.cs:77-84` | `SerializableReward`; `CustomReward.DeserializeMethod` → `CreateRewardFromSave<CustomReward>` |
| **Custom enum value written into the save** | A reward's `RewardType` is a runtime-assigned `[CustomEnum]` value that is then persisted and used to route deserialization | `Downfall@32e6113:CollectorCode/Rewards/CollectibleReward.cs:19,22,49,81`; `EssenceReward.cs:14,16,17,46`; assignment semantics at `BaseLibWiki@5558d89:docs/utilities/enums.md:6` | `[CustomEnum]` on `public static RewardType` |
| **Reflection shim across a game-version rename** | BaseLib finds the property-name cache under either the old or the new type/property name, so one build works across the rename | `BaseLib@2275793:Patches/Utils/SavedSpireFieldPatch.cs:65-95` (`SavedPropertiesTypeCache` else `ModelIdSerializationCache`; `NetIdBitSize` else `PropertyIdBitSize`) — matching `PN-0.109.0` "Merged SavedPropertySerializationCache into ModelIdSerializationCache" | `AccessTools.TypeByName`, `AccessTools.StaticFieldRefAccess` |
| **Reflection shim across a game-API shape change** | Downfall reads `Mod.assemblies` (new) or `Mod.assembly` (old, V107) and throws a named error if neither exists | `Downfall@32e6113:DownfallCode/Compatibility/CompatibilityMod.cs:15-38`; matching note `PN-0.108.0` "Mods can now register multiple assemblies" | `MegaCrit.Sts2.Core.Modding.Mod` |
| **One DLL per game version, chosen at load** | A thin entry DLL picks a version-specific implementation DLL; `#if` capability flags handle renamed/asyncified APIs | `nyaoouo@2c58c2f:EntryProj/Entry.cs:10-14`; `Src/Infrastructure/Compat/RunManagerCompat.cs:7-28`; build wiring at `STS2Saves.csproj:16-23,32,63-64` | `[ModInitializer]`; `RunManager.SetUpSavedSinglePlayer` → `SetUpSavedSingleplayer` (renamed at v0.107.0 per the shim's own comment) |
| **Compile-time game-version constant** | Downfall defines `V107` in the project and branches comments/code on it | `Downfall@32e6113:Downfall.csproj` `<DefineConstants>$(DefineConstants);V107</DefineConstants>`; used at `DownfallCode/Compatibility/CompatibilityHook.cs:38` | MSBuild `DefineConstants` |
| **Manifest declares the compatibility floor** | `min_game_version` plus a dependency floor for BaseLib; `affects_gameplay` now has save/ID-map meaning | `Downfall@32e6113:Downfall.json:9-16` (`0.107.1`, BaseLib `3.4.5`, `affects_gameplay: true`); contrast `nyaoouo@2c58c2f:STS2Saves.json` (`affects_gameplay: false`, no deps); semantics from `PN-0.108.0` | mod manifest JSON |
| **Base game retires its own content and copes on load** | A save referencing a deprecated boss loads; the game just stops it rolling twice in a double-boss fight | `PN-0.107.1`; `PN-0.106.0` (2026-05-22) | run save / boss roll |
| **Save write is a patchable seam** | Mods hook the save write to archive snapshots | `nyaoouo@2c58c2f:Src/Features/SaveArchive/Integration/ClientSaveHooks.cs:10-29` | `MegaCrit.Sts2.Core.Saves.SaveManager.SaveRun` (Harmony postfix) |
| **Profile-level progress is a separate surface** | Lifetime stats and a per-install unique ID live outside the run save and are read, not written, by mods | `Downfall@32e6113:DownfallCode/Data/DownfallMetrics.cs:93,97-102` (`TotalPlaytime`, `Wins`, `NumberOfRuns`, `UniqueId`, and `run.NumReloads` at `:99`) | `SaveManager.Instance.Progress`; `Player.UnlockState` (`Downfall@32e6113:ChampCode/Powers/StrikeOfGeniusPower.cs:24`) |

## Gotchas

1. **A class rename is an ID change, and therefore a save break.** No public source
   declares an explicit stable ID string; the entry is generated from the type and
   prefixed from the root namespace (`BaseLibWiki@5558d89:docs/models/index.md:11`;
   zero `override ModelId Id` in `Downfall@32e6113`). Renaming a card class, or
   moving it so the root namespace changes, silently orphans every save that holds
   it. Downfall's own answer is to never rename: cut content stays in-tree as
   `[Obsolete]` with its pool attribute intact
   (`Downfall@32e6113:AutomatonCode/Cards/Removed/Batch.cs:7-9`).

2. **Save keys are unprefixed strings, and the advice is not followed.** The wiki
   says to make the name unique to your mod
   (`BaseLibWiki@5558d89:docs/utilities/spirefield.md:47`). Downfall's live keys are
   `"CollectorEssence"`, `"CollectorDeck"`, `"GremlinStats"`, `"GuardianGems"`
   (`Downfall@32e6113:CollectorCode/Core/EssenceModel.cs:9`,
   `CollectorCode/Core/CollectiblesModel.cs:17`,
   `GremlinsCode/Core/GremlinsRunModel.cs:19`,
   `GuardianCode/GuardianMainFile.cs:66`) — none carries a mod prefix. A duplicate
   name is caught at registration and logged as an error, and the second field is
   then **not saved at all**
   (`BaseLib@2275793:Patches/Utils/SavedSpireFieldPatch.cs:97-100`).

3. **A missing key on load is silent.** The extended-save load path does a
   `TryGetValue` and simply does nothing when the key is absent
   (`BaseLib@2275793:Patches/Saves/ExtendedSaveHandlers.cs:161-167`). Good for
   forward compatibility; bad for diagnosis, because a renamed key looks exactly
   like a fresh run.

4. **The packet path is positional; the JSON path is name-keyed.** On disk the data
   is a `Dictionary<string,T>` keyed by your ID
   (`ExtendedSaveHandlers.cs:136-147`). Over `PacketWriter`/`PacketReader` each
   registered save writes a presence bool then its payload, **in sorted-ID order**
   (`ExtendedSaveHandlers.cs:168-190`). Two peers whose *set* of registered save IDs
   differs will read that stream misaligned. That is the mechanism behind the
   "version mismatch" family MegaCrit spent v0.108.0 fixing (`PN-0.108.0`).

5. **The JSON property name embeds the C# type's full name.**
   `save_dict_<TypeFullName>` is built from `t.FullName`
   (`BaseLib@2275793:Patches/Saves/ExtendedSaveHandlers.cs:139,194-207`). Renaming
   or re-namespacing a *save data* class changes the JSON property, orphaning
   existing data, even if the string ID is untouched.

6. **`[CustomEnum]` values are runtime-assigned and some of them get persisted.**
   The wiki says a new value "will be assigned to it at runtime"
   (`BaseLibWiki@5558d89:docs/utilities/enums.md:6`) and says nothing about
   stability. Downfall then writes such a value into a saved reward
   (`Downfall@32e6113:CollectorCode/Rewards/CollectibleReward.cs:81`). Whether
   BaseLib stabilises the numeric value across differing mod sets is **UNVERIFIED**
   — I did not read the `CustomEnum` implementation.

7. **Modded progress does not flow back to vanilla.** The copy is one-way and
   one-time (`PN-0.108.0`). Two community mods exist purely to defeat the split by
   forcing `UserDataPathProvider.IsRunningModded` to `false`
   (`luojiesi@3de9d08:UnifiedSavePath/UnifiedSavePathMod.cs:21-42`;
   `Jayden@b2cae7b:mods/modded-save-sync/modded_save_syncCode/Patches/UnifiedSavePathPatch.cs:6-26`), and both also patch
   `GetProfileDir` as a guard against JIT inlining
   (`Jayden@b2cae7b:docs/designs/modded-save-sync.md:39`). Anyone testing our mod
   with such a mod installed is testing a different save topology than a normal player.

8. **The behaviour we are pinned to is 0.107.1, and this area moved twice since.**
   Our `min_game_version` is `0.107.1`
   (`GItS:klee-mod/Klee/manifest.json`), but the first-modded-launch copy arrived in
   0.108.0, the cache merge in 0.109.0 (which is exactly the branch BaseLib's
   reflection shim covers), and the decline-mod-loading refinement in 0.111.0. Any
   save statement we make should name the game version it was observed on.

9. **`affects_gameplay` is not cosmetic bookkeeping any more.** Since v0.108.0 it
   decides whether your models are excluded from the `ModelIdSerializationCache`
   hash and sorted to the end of ID maps (`PN-0.108.0`). Ours is `true`, like
   Downfall's; STS2Saves sets it `false`.

10. **The game exposes no obvious stable run identifier.** A save-manager mod
    synthesises one by SHA-256 over `(mode, StartTime, PlatformType, GameMode,
    daily, sorted CharacterIds, PlayerCount)`
    (`nyaoouo@2c58c2f:Src/Features/SaveArchive/Logic/RunIdentityService.cs:11-23`).
    That is consistent with there being no exposed run ID, but does not prove it.

11. *(Belongs to S12g, one-line pointer only.)* MegaCrit's own uploader defines the
    Workshop-side config with `minBranch` / `maxBranch`
    (`uploader@d7b7e6b:src/ModConfig.cs:12-13`), and Downfall's release/localization
    pipeline lives in `Downfall@32e6113:.github/workflows/`.

12. *(Belongs to S12a/S12e, one-line pointer only.)* `GremlinsRunModel` persists a
    party of monsters across combats through a `SavedSpireField` on `Player`
    (`Downfall@32e6113:GremlinsCode/Core/GremlinsRunModel.cs:18-121`) — the only
    public example I found of enemy-shaped state surviving a save.

## Transfer questions (questions, not proposals)

Against `GItS:klee-mod/KleeCode` (root namespace `KleeMod`, so our prefix is
`KLEEMOD-`), BaseLib as a pre-loaded dependency, and our Harmony patch set:

1. **We currently persist nothing of our own.** A grep of `klee-mod/KleeCode` finds
   `SpireField` only (`Powers/BombPower.cs:152`, a `SpireField<Creature,bool>`) and
   **no** `SavedSpireField`, `[SavedProperty]`, or `ExtendedSaveTypes` registration.
   Which of our per-run quantities — Spark, Charge, Burst meter, Fanfare cap, Salon
   membership, Companion slots, Artifact/Aura/Bomb state — are supposed to survive a
   save-and-reload, and which are combat-scoped by design? That list has to exist
   before any of this matters.

2. **What is our answer to a card rename?** Our IDs are `KLEEMOD-` +
   UPPER_SNAKE_CASE of the class name (`klee-mod/KleeCode/KleeMod.cs:81-82`), and
   our sheets carry the id list. Do we adopt Downfall's rule (never rename; retire
   in place as `[Obsolete]`), and if so does that become a lint against the YAML
   sheets rather than a convention?

3. **If we ever register a `SavedSpireField`, what is our key convention?** The
   framework does not enforce a prefix and Downfall does not use one. Do we mandate
   `KLEEMOD-`-prefixed save keys from the first one, and can `tools/` lint it?

4. **What do we owe a player who removes our mod mid-run?** `PN-0.107.1` says
   progress from removed mods is no longer deleted, and a missing modded *character*
   errors loudly. We ship three characters plus off-pool cards, relics, and
   companion cards that can enter a base character's deck. Nothing public says what
   happens to *those*. Is that a case we want to reproduce and observe, and under
   which lane?

5. **Do we have a game-version compatibility posture at all?** `nyaoouo` ships one
   DLL per game version behind a thin loader; Downfall carries reflection shims and
   a `V107` constant; we carry `min_game_version: 0.107.1` and a hand-written
   canary (`ProgressSaveManager_EpochCheck_Patch`, `KleeMod.cs:487-520`) that logs
   when a BaseLib guard stops applying. Is the canary pattern the whole posture, or
   do we want a `KleePatchBootstrap`-style resolve-or-report pass over every
   base-game member we name?

6. **We already patch a save-adjacent base type.** `ProgressSaveManager`'s epoch
   checks are ours to suppress (`KleeMod.cs:487-520`). Is `SaveManager.SaveRun` a
   seam we would ever want (for capture, for the understudy harness), and does
   touching it collide with a player's save-manager mod?

7. **Does our co-op story inherit the packet-ordering hazard?** Extended saves are
   written in sorted-ID order over the packet path
   (`ExtendedSaveHandlers.cs:168-190`). If we ever register one, two seats running
   different builds of our mod would misread the stream. Does that argue for
   registering the full set from day one rather than growing it per window?

8. **Which of our save-facing numbers are `[SavedProperty]`-shaped?** Downfall uses
   it for a card that grows (`CultistStrike`, `CursedWeapon`) and a relic that
   remembers a character (`SneckoChoice`). Do any of our cards have per-instance
   state that must persist — and does `AssertMutable()` interact with how the
   codegen builds canonical instances?

9. **Playtest hygiene:** should the playtest protocol record whether a
   save-unifying mod (`UnifiedSavePath`, `modded-save-sync`, `BetterSaves`) is
   installed, given it changes which directory the run came from?

## NON-FINDINGS (explicit)

- **No save-schema version number.** Nothing in Downfall, BaseLib, the BaseLib wiki,
  or the three save-manager mods reads or writes a version stamp on a mod's saved
  data. There is no `saveVersion`, no schema field, no `if (version < n)` branch.
- **No migration mechanism, anywhere.** Neither BaseLib nor any mod examined
  contains an upgrade path from an older shape of its own saved data. Grepping
  `Downfall@32e6113` for `migrat|backward|legacy|schemaversion|save_version` returns
  only unrelated matches (a card named `Deprecate`, `[Obsolete]` attributes, and a
  `FindListenerLoadBackwards` IL helper).
- **No documented custom-enum stability guarantee.**
  `BaseLibWiki@5558d89:docs/utilities/enums.md` does not say whether a
  `[CustomEnum]` value is stable across launches or mod sets, and does not warn
  about persisting one — despite Downfall persisting `RewardType` values.
- **No statement about removed-mod cards/relics.** `PN-0.107.1` covers a modded
  *character*; nothing public covers a modded card sitting in an otherwise vanilla
  deck when its mod goes away.
- **No public evidence of a stable per-run identifier** in the save (see gotcha 10).
- **Downfall has no save-related tests, docs, or CI check.** No `.md` in the repo
  mentions saves; `contribution-guidelines.md` says nothing about ID stability.
- **Downfall's history was not available.** The reference clone is depth-1
  (`git log --oneline | wc -l` = 1), so no commit message could be used as evidence
  about how or why a save decision was made.

## Search boundary

- **Date:** 2026-08-26. All web retrievals that day.
- **Primary reading:** the pinned Downfall tree, read exhaustively for
  `save|serializ|persist`, `SavedProperty`, `SpireField`, `ExtendedSave`,
  `ModelId`, `CustomEnum`, `GameMode`, `affects_gameplay`, `migrat|legacy|version`,
  `user://`, `SaveManager|UnlockState|Progress`, and `override ModelId Id`.
- **Widened once** (charter §7), because Downfall alone does not answer migrations,
  removal, or save separation. Queries run: *"Slay the Spire 2 BaseLib mod alchyr
  github SavedSpireField ExtendedSaveTypes"*; *"Slay the Spire 2 mod save
  compatibility save file mod removed run save github"*; *"Slay the Spire 2 official
  modding documentation save directory modded save separate megacrit"*; *"alchyr
  BaseLib wiki custom enums …"*.
- **Repositories opened and pinned:** `Alchyr/BaseLib-StS2`, `Alchyr/BaseLib-Wiki`,
  `JaydenLiang/slay-the-spire-2-mods`, `luojiesi/SLS2Mods`, `nyaoouo/sts-2-saves`,
  `megacrit/sts2-mod-uploader`. Files were fetched from `raw.githubusercontent.com`
  at the pinned SHA, and SHAs/licences confirmed through the GitHub REST API.
- **Patch notes** were retrieved through Valve's official `ISteamNews` API for appid
  `2868840` (40 items) and searched for save/mod/ID terms; only MegaCrit's own
  announcement text is quoted.
- **Deliberately not used as evidence:** Steam Community discussion threads, the
  `sts2.gg` guide, `xmodhub`, Nexus mod pages (nexusmods.com returned HTTP 403 to
  fetch in any case), and any wiki or summary. Two Nexus-listed mods —
  *BetterSaves* (`nexusmods/slaythespire2/mods/372`) and *More Saves*
  (`.../225`) — were therefore **not** examined; if their descriptions matter, they
  need a primary repository or a manual read.
- **Not read:** BaseLib's `CustomEnum` implementation, the base game decompile, and
  our own `game_ref/` tree. The decompile is S13's job and is where gotcha 6 and the
  removed-mod card question should be settled.

## What this does NOT establish

- It does not establish that our mod would behave any of these ways. Every
  base-game behaviour above is quoted from patch notes or inferred from what a
  third-party mod patches; none of it was run or observed on this machine, and no
  game was launched (charter §3, playtest in progress).
- It does not establish the on-disk layout of a run save beyond the file *names*
  and the fact that BaseLib's extension path is JSON. The overall save format,
  whether it is compressed, and what a `.save` file actually contains are unread.
- It does not establish that `[CustomEnum]` values are safe or unsafe to persist —
  only that Downfall persists them and no documentation addresses it.
- It does not establish that BaseLib 3.4.5's behaviour matches the BaseLib actually
  loaded on this machine. Downfall pins `3.4.5`; our manifest asks for `≥ 3.3.6`;
  `STATE.md` records `3.3.7.0` as the pinned build environment. Those are three
  different numbers and the difference has not been reconciled here.
- It does not establish any recommendation. There is no proposal in this file: the
  transfer section is questions, and every "what should we do" is [USER]'s.
- It does not touch `SKIP-10.9` or any other dormant row, mint any ID, or propose
  any code or design.
