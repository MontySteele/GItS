# S12b — Boss and encounter integration in public StS2 mods

> Research only. Decides nothing. No design, mapping, or scope call is made or
> implied here. Every factual claim below carries a pinned source; anything I
> could not pin says UNVERIFIED in place.

## Overview (the short answer)

1. **Downfall does not do this at all** — zero encounters, zero encounter pools,
   zero enemies or bosses the player fights. It only *reads* the current room's
   type to size a reward.
2. **Downfall's premise is the other kind of boss.** A "boss you play as" is
   registered as an ordinary playable character; there is no boss machinery. The
   boss identity is art, cards, and a signature mechanic rebuilt player-side.
3. **So I widened the search once, and it paid off.** Two MIT-licensed primary
   sources answer the question properly: **BaseLib** (which we already depend on)
   ships `CustomEncounterModel` plus the patch that injects an encounter into an
   act's pool; **Act 4: Final Ascent** ships a four-phase boss the player fights —
   entry, phases, death, run-end, rewards — using raw Harmony and **no** BaseLib.
4. **Bosses are not an engine concept.** The engine has boss-flavoured *rooms*
   and a boss *slot* on an act. Phases are invented by the mod and hung off one
   hidden Power that tells the engine "combat is not over yet".
5. The encounter API already exists in the BaseLib version we pin (3.3.7),
   unchanged from the current 3.4.5 copy.

---

## Sources (pinned)

| Ref | Repository | Pin | License |
|---|---|---|---|
| `Downfall@32e6113` | [lamali292/Downfall](https://github.com/lamali292/Downfall/tree/32e61132052ae58e32cd33342d24136ffe18be12) | `32e61132052ae58e32cd33342d24136ffe18be12` (2026-08-26) | MIT (`LICENSE`, 2026 lamali) |
| `BaseLib@2275793` | [Alchyr/BaseLib-StS2](https://github.com/Alchyr/BaseLib-StS2/tree/22757933ba10adc4322a628519a233a567507d87) | `22757933ba10adc4322a628519a233a567507d87` = tag `v3.4.5` (2026-08-14) | UNVERIFIED — I did not open its LICENSE this pass |
| `BaseLib@v3.3.7` | same repo, tag `v3.3.7` | `f7db6b5158df441bd46e6fd807b704cd51cffffd` | same |
| `Act4@05c251a` | [kphxgames/Act4FinalAscent](https://github.com/kphxgames/Act4FinalAscent/tree/05c251a4186b323fc2a7fef5dab3cf586b856767) | `05c251a4186b323fc2a7fef5dab3cf586b856767` (2026-04-05) | MIT (`LICENSE`, 2026 Act 4: Final Ascent Contributors) |

Repo-relative paths with no `@ref` prefix are **our** checkout at
`C:\Users\Monty\Documents\GitHub\GItS`.

Reference-reading only (charter §3.7). Nothing above was copied into anything.

---

## Pattern table

### A. Encounter registration and pools

| Pattern | Purpose | Pinned source | Base type it hangs off |
|---|---|---|---|
| **Encounter = a model subclass, discovered by type** | An encounter is a class, not data. Subclass, and `ModelDb.Encounter<T>()` resolves it. Neither public mod calls an explicit "register encounter" method for ModelDb's sake. | `Act4@05c251a:src/Act4Placeholder/Architect/Act4ArchitectBossEncounter.cs:13`; resolved by type at `:23`, `:42` | `MegaCrit.Sts2.Core.Models.EncounterModel` |
| **Two required overrides** | `AllPossibleMonsters` (every monster that *can* appear) and `GenerateMonsters()` (the mutable instances that *will* appear, as `(MonsterModel, slotName?)` tuples). | `Act4@05c251a:…/Act4ArchitectBossEncounter.cs:21-44`; documented as required at `BaseLib@2275793:Abstracts/CustomEncounterModel.cs:44-49` | `EncounterModel` |
| **Room type carried on the encounter, not the room** | `EncounterModel.RoomType` is what makes a fight Monster / Elite / Boss. BaseLib warns on any other value. | `BaseLib@2275793:Abstracts/CustomEncounterModel.cs:13,16-22`; `Act4@05c251a:…/Act4ArchitectBossEncounter.cs:15` | `MegaCrit.Sts2.Core.Rooms.RoomType` |
| **Pool membership by predicate** | `CustomEncounterModel.IsValidForAct(ActModel)` decides which acts an encounter can appear in. The doc-comment's own advice is to test the act ("act is Glory"). | `BaseLib@2275793:Abstracts/CustomEncounterModel.cs:30-38` | `MegaCrit.Sts2.Core.Models.Acts.ActModel` |
| **Pool injection by postfix on every act type** | BaseLib reflects over every `ActModel` subtype (base game **and** mods), postfixes `GenerateAllEncounters`, and appends each custom encounter whose `IsValidForAct` passes. Dedupe is by `Id`. | `BaseLib@2275793:Patches/Content/ContentPatches.cs:352-362, 381-393` | `ActModel.GenerateAllEncounters()` |
| **The registration sink** | `CustomEncounterModel`'s constructor calls `CustomContentDictionary.AddEncounter(this)` unless `autoAdd:false`; the list is a sorted static. | `BaseLib@2275793:Abstracts/CustomEncounterModel.cs:24-27`; list at `Patches/Content/ContentPatches.cs:29, 70-74` | BaseLib static registry |
| **The boss slot of an act** | An act declares its boss encounters through `BossDiscoveryOrder`. Act 4 restricts it to exactly one. Non-boss pool is a separate override. | `Act4@05c251a:src/Act4Placeholder/Map/Act4PlaceholderMapTemplate.cs:26` (boss), `:52-55` (non-boss, delegated to the Glory act) | `ActModel.BossDiscoveryOrder`, `ActModel.GenerateAllEncounters()` |
| **Pacing dials on the act** | `NumberOfWeakEncounters`, `BaseNumberOfRooms`. BaseLib's comment defines "weak": first 3 encounters in act 1, first 2 in other acts. | `Act4@05c251a:…/Act4PlaceholderMapTemplate.cs:32-34`; semantics at `BaseLib@2275793:Abstracts/CustomEncounterModel.cs:55` | `ActModel` |
| **Anti-repeat dial on the encounter** | `Tags` — "the game will avoid generating two encounters that share a tag in a row." Neither mod overrides it; the comment is the evidence. | `BaseLib@2275793:Abstracts/CustomEncounterModel.cs:54` | `EncounterModel.Tags` |
| **Encounter identity is a ModelId string** | The live encounter is reachable as `room.Encounter` / `combatState.Encounter`, and its `Id.Entry` is the fight's name. Act 4 matches its own boss by literal id `"ACT4_ARCHITECT_BOSS_ENCOUNTER"`. | `Act4@05c251a:src/Act4Placeholder/Patches/NBossMapPointReadyPatch.cs:16,30`; our own reader `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs:805-812` | `EncounterModel.Id`, `CombatRoom.Encounter`, `ICombatState.Encounter` |
| **Encounter presentation slots** | `CustomScenePath` points at a 1920×1080 `Control` whose `Marker2D` children are the enemy slots, named and ordered; `Slots` is derived from them by default. | `BaseLib@2275793:Abstracts/CustomEncounterModel.cs:61-90, 96-97` | `EncounterModel.ScenePath`, `EncounterModel.Slots` |
| **Encounter background / music / map icon** | `CustomEncounterBackground(act, rng)` (with three Harmony shims to route it), `CustomBgm` (an fmod event path), `BossNodePath` and `CustomRunHistoryIconPath` for the boss's map and history icons. | `BaseLib@2275793:Abstracts/CustomEncounterModel.cs:104-132, 135-168`; `Act4@05c251a:…/Act4ArchitectBossEncounter.cs:17,19` | `EncounterModel.GetBackgroundAssets`, `EncounterModel.BossNodePath` |

### B. Boss-specific lifecycle — a boss the player FIGHTS

All of this is Act 4's Architect. It is the only public implementation I found.

| Pattern | Purpose | Pinned source | Base type it hangs off |
|---|---|---|---|
| **A boss is just a MonsterModel** | No boss base class, no boss interface. `Act4ArchitectBoss : MonsterModel`. Everything boss-shaped is the mod's own. | `Act4@05c251a:src/Act4Placeholder/Architect/Act4ArchitectBoss.cs:51` | `MegaCrit.Sts2.Core.Models.Monsters.MonsterModel` |
| **Entry hook** | `AfterAddedToRoom()` — the boss corrects its own HP, applies its opening powers, applies its phase-gate Power, repositions its intent/talk anchors, sets the opening move, plays its entrance line. | `Act4@05c251a:…/Act4ArchitectBoss.cs:330-397` | `MonsterModel.AfterAddedToRoom()` |
| **Exit hook** | `BeforeRemovedFromRoom()` — used to stop an ambient VFX loop. | `Act4@05c251a:…/Act4ArchitectBoss.cs:398-402` | `MonsterModel.BeforeRemovedFromRoom()` |
| **Death hooks** | `OnDieToDoom()` and `AfterDiedToDoom(ctx, creatures)`, plus the two presentation flags `ShouldDisappearFromDoom` and `ShouldFadeAfterDeath`. Death is *redirected* into a phase transition unless it is the last phase. | `Act4@05c251a:…/Act4ArchitectBoss.cs:132-137, 163-193` | `MonsterModel` |
| **Phases are a hidden Power** | One invisible `PowerModel` on the boss overrides `ShouldStopCombatFromEnding()`, `ShouldDie()`, `ShouldCreatureBeRemovedFromCombatAfterDeath()`, `ShouldPowerBeRemovedAfterOwnerDeath()` and `ShouldAllowHitting()`. **`ShouldStopCombatFromEnding` is the load-bearing one** — it is what keeps the fight alive between phases. `AfterDeath` then starts the next phase. | `Act4@05c251a:src/Act4Placeholder/Architect/Act4ArchitectRevivalPower.cs:15, 25-56, 58-78` | `MegaCrit.Sts2.Core.Models.PowerModel` |
| **Phase state is plain fields** | Phase number, per-phase "has triggered" flags, carried Strength, per-phase stun budget — ordinary mutable fields on the model instance, saved by the mod's own save patches. | `Act4@05c251a:…/Act4ArchitectBoss.cs:62-108, 124-161, 195-197`; save side at `src/Act4Placeholder/Patches/Act4SaveStatePatches.cs` (not read this pass — UNVERIFIED beyond its filename) | `MonsterModel` instance state |
| **Mid-fight summons must be pre-declared** | Every shadow and linked shadow the boss can summon in phases 3 and 4 is listed in `AllPossibleMonsters`, with the source comment saying why: names, animations and targeting break otherwise. | `Act4@05c251a:…/Act4ArchitectBossEncounter.cs:24-35` | `EncounterModel.AllPossibleMonsters` |
| **Finishing the run on the final kill** | `RunManager.OnEnded(true)` returns a `SerializableRun`, which is handed to `NRun.Instance.ShowGameOverScreen(...)`. Queued once, guarded by a bool. | `Act4@05c251a:src/Act4Placeholder/Core/ModSupport.cs:2886-2894`; queue at `src/Act4Placeholder/Architect/Act4ArchitectBossMechanics.cs:1349-1358` | `RunManager.OnEnded(bool)`, `NRun` |
| **Per-encounter enemy scaling** | `CombatManager.AddCreature` postfix, branching on `creature.IsEnemy`. | `Act4@05c251a:src/Act4Placeholder/Patches/CombatManagerAddCreaturePatch.cs:13-26` | `CombatManager.AddCreature` |

### C. Rewards attached to an encounter

| Pattern | Purpose | Pinned source | Base type it hangs off |
|---|---|---|---|
| **Inject an extra reward with no patch at all** | From a combat-end hook, call `room.AddExtraReward(player, reward)`. Downfall's Collector grants Essence sized by room type, plus one card per distinct enemy defeated. | `Downfall@32e6113:CollectorCode/Core/CollectorModel.cs:66-88` (rewards at `:82`, `:84`; room-type switch at `:73-79`) | `MegaCrit.Sts2.Core.Rooms.CombatRoom.AddExtraReward` |
| **Same seam from a relic** | A relic overrides `AfterCombatEnd(CombatRoom)`, filters on `room.RoomType`, and adds its own reward. | `Downfall@32e6113:GuardianCode/Relics/PickOfRhapsody.cs:12-17` | `RelicModel.AfterCombatEnd(CombatRoom)` |
| **Victory-only variant** | `AfterCombatVictory(CombatRoom)` exists separately from `AfterCombatEnd`. Exactly one use in Downfall (an `[Obsolete]` relic), and one in our own telemetry. | `Downfall@32e6113:HermitCode/Relics/BrokenTooth.cs:22-24`; ours at `klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs:1175` | `RelicModel.AfterCombatVictory(CombatRoom)` |
| **Patch the reward set instead** | `RewardsSet.WithRewardsFromRoom(AbstractRoom)` postfix — Act 4 appends gold to its non-boss act-4 combats and deliberately skips boss rooms. | `Act4@05c251a:src/Act4Placeholder/Patches/RewardsSetWithRewardsFromRoomPatch.cs:14-30` | `MegaCrit.Sts2.Core.Rewards.RewardsSet` |
| **A wholly new reward kind** | Subclass BaseLib's `CustomReward`, mint a `RewardType` with `[CustomEnum]`, supply `Populate()`, `OnSelect()`, `OnSkipped()`, `ToSerializable()` and a static deserializer registered through `Reward.FromSerializable`. | `BaseLib@2275793:Abstracts/CustomReward.cs:26,50,68`; registry + patch at `Patches/Content/CustomRewardPatches.cs:11-40`; two worked examples at `Downfall@32e6113:CollectorCode/Rewards/EssenceReward.cs:12-19,37-49` and `GuardianCode/Rewards/GemFinderReward.cs:22-24,54-92` | `MegaCrit.Sts2.Core.Rewards.Reward` / `RewardType` |
| **Co-op reward selection** | A reward whose selection opens a screen must run the screen on the owning client only and drive remotes through `PlayerChoiceSynchronizer` — one reserved choice id per pick, then a null terminator. Both sides must build an identical list because remotes dereference synced indices. | `Downfall@32e6113:GuardianCode/Rewards/GemFinderReward.cs:94-160` (protocol comment at `:118`) | `RunManager.PlayerChoiceSynchronizer` |

### D. Reading the encounter (what both mods actually do most)

| Pattern | Purpose | Pinned source | Base type it hangs off |
|---|---|---|---|
| **Room-type-conditional card/relic behaviour** | `CombatState.Encounter.RoomType == RoomType.Boss` for a card that behaves differently against a boss; `room.RoomType` switches for gold/essence sizing. | `Downfall@32e6113:ChampCode/Cards/Rare/CheapShot.cs:24-25`; `HermitCode/Cards/Rare/DeadOrAlive.cs:43-47`. We already do the same: `klee-mod/KleeCode/Cards/KleeCardTooltips.cs:51`, `klee-mod/KleeCode/Powers/ReactionEffects.cs:222` | `EncounterModel.RoomType` |
| **Run-level room lifecycle** | A singleton model declared `HookType.Run` receives `AfterRoomEntered(AbstractRoom)`; `HookType.Combat` receives `BeforeCombatStart` / `AfterCombatEnd` / `AfterDeath`. | `Downfall@32e6113:AutomatonCode/Core/AutomatonModel.cs:12-14`; `CollectorCode/Core/CollectorModel.cs:17-20, 57-63` | `BaseLib.Abstracts.CustomSingletonModel(HookType)` |
| **Encounter history and telemetry** | Per-room records live on `RunState.MapPointHistory`: each entry's `Rooms` carry `RoomType`, an encounter `ModelId`, and `TurnsTaken`. `RoomType.IsCombatRoom()` filters fights; the last combat room's `ModelId` is "what killed you". | `Downfall@32e6113:DownfallCode/Data/DownfallMetrics.cs:49-63, 112` | `MegaCrit.Sts2.Core.Runs.History.MapPointHistoryEntry` |
| **Hand-maintained census of base-game fights** | There is no public API that enumerates "act 1's bosses". Downfall's Collector hard-codes **100** base-game `MonsterModel` types as card classes, grouped by act/region/tier **in code comments only** — Act 1 (Underdocks, Overgrowth), Act 2 (Hive), Act 3 (Glory), each split Monster / Elite / Boss. | `Downfall@32e6113:CollectorCode/Cards/Token/MonsterCards.cs:8-12, 72, 85, 97, 209-213, 309-313, 392` (100 classes, 400 lines); wrapper at `CollectorCode/Cards/Token/Collectible.cs:12-26, 56-59` | `MegaCrit.Sts2.Core.Models.Monsters.*`, `ModelDb.Monster<T>()` |

### E. The other kind of boss — one the player PLAYS AS

| Pattern | Purpose | Pinned source | Base type it hangs off |
|---|---|---|---|
| **A playable boss is an ordinary character** | `SlimeBoss : DownfallCharacterModel : CustomCharacterModel`. Starting HP, gold, deck, relics, three pools, colours, animation delays — the same shape any character has. **No boss lifecycle, no phases, no encounter, no monster model for the player.** | `Downfall@32e6113:SlimeBossCode/Core/SlimeBoss.cs:14-62`; base at `DownfallCode/Abstract/DownfallCharacterModel.cs:7` | `BaseLib.Abstracts.CustomCharacterModel` |
| **The boss's signature move becomes player-owned creatures** | Slime Boss's Split makes *pets*: `CreateCreature(model, player.Creature.Side, null)` then `PlayerCmd.AddPet`. They sit on `PlayerCombatState.Pets`, on the **player's** side. | `Downfall@32e6113:SlimeBossCode/Core/SlimeQueue.cs:64-68, 22` | `CombatState.CreateCreature`, `PlayerCombatState.Pets` |
| **The nearest thing to a "phase" on the player side** | Gremlins: a death interceptor swaps the dying gremlin for the next one on the bench instead of ending the run. Registered through Downfall's own `DeathHooks` registry, which prefixes `CreatureCmd.KillWithoutCheckingWinCondition` — first taker wins, forced kills are never interceptable. | `Downfall@32e6113:GremlinsCode/Core/GremlinsModel.cs:20-40`; registry `DownfallCode/Utils/DeathHooks.cs:13-32`; patch `DownfallCode/Patches/DeathInterceptPatch.cs:8-21`; sole registration `GremlinsCode/GremlinsMainFile.cs:37` | `MegaCrit.Sts2.Core.Commands.CreatureCmd` |
| **Custom monster models exist, but never hostile** | All three `CustomMonsterModel` families in Downfall — `SlimeModel`, `GremlinsMonsterModel`, `TorchheadMonsterModel` — are player-side. Every `CreateCreature` call in the repo passes the player's side. | `Downfall@32e6113:SlimeBossCode/Slimes/SlimeModel.cs:19`, `GremlinsCode/Core/GremlinsMonsterModel.cs:16`, `CollectorCode/Core/TorchheadMonsterModel.cs:13`; side check across `GremlinsCode/Core/GremlinsCmd.cs:179`, `SlimeBossCode/Core/SlimeQueue.cs:64` | `BaseLib.Abstracts.CustomMonsterModel` |

---

## Gotchas

1. **`AllPossibleMonsters` is not documentation — it is a load-bearing list.**
   Anything that can appear mid-fight must be in it. Act 4 says so in its own
   comment: the phase-3 and phase-4 shadows are listed "so name/animations/
   targeting work" (`Act4@05c251a:…/Act4ArchitectBossEncounter.cs:24-35`). A boss
   that summons is therefore not self-contained; the encounter must know the
   summons.

2. **The engine scales monster HP before your entry hook runs, and it will
   double-scale you.** Act 4's comment: `CombatState.CreateCreature()` calls
   `ScaleMonsterHpForMultiplayer` (hp × player count × per-act factor) *before*
   `AfterAddedToRoom`, so a boss that does its own player-count scaling must
   reset HP in the entry hook (`Act4@05c251a:…/Act4ArchitectBoss.cs:335-347`).
   This matters to us specifically because we ship co-op.

3. **A phase transition is a death you caught.** Nothing in the engine knows what
   a phase is. The whole mechanism is one hidden Power answering
   `ShouldStopCombatFromEnding()` correctly
   (`Act4@05c251a:…/Act4ArchitectRevivalPower.cs:39-42`). Get that one predicate
   wrong and the fight ends in the middle of the boss.

4. **Presentation flags can crash on the fast-forward setting.** Act 4 guards
   `ShouldFadeAfterDeath` with a `FastMode != Instant` check because
   `NMonsterDeathVfx.Create` returns null in instant mode and `AnimDie`'s
   `MoveChild` crashes on it (`…/Act4ArchitectBoss.cs:134-137`). A found bug in a
   released mod, stated in its own source.

5. **BaseLib only patches acts that *declare* `GenerateAllEncounters`.** It uses
   `AccessTools.DeclaredMethod` per subtype
   (`BaseLib@2275793:Patches/Content/ContentPatches.cs:358-362`). An act that
   inherits the method rather than declaring it is not patched, so custom
   encounters would never reach its pool.

6. **Pool injection dedupes silently by `Id`.** If a custom encounter's id
   collides with one already in the act's list, it is skipped with no warning
   (`ContentPatches.cs:391`).

7. **Two entirely different integration routes exist, and the stronger example
   uses neither library.** `Act4FinalAscent.json` declares **no dependencies at
   all** — no BaseLib — and registers its act, encounter, boss and monsters by
   subclassing base types directly plus ~30 Harmony patches. Downfall declares
   `BaseLib >= 3.4.5` (`Downfall@32e6113:Downfall.json`). Whether a mod *needs*
   BaseLib for encounters is therefore a real choice, not a given.

8. **Act 4 casts enum values by ordinal** — `(RoomType)3` for Boss, `(PowerType)1`,
   `(CombatSide)2` (`…/Act4ArchitectBossEncounter.cs:15`,
   `…/Act4ArchitectRevivalPower.cs:19`). It also invokes `CreatureCmd.SetMaxHp`
   by reflection because its return type changed across game builds
   (`…/Act4ArchitectBoss.cs:53-60`). Both are deliberate anti-version-binding
   moves, and both are exactly the sort of thing that fails silently on a game
   update.

9. **`MapPointTypeCounts` has no public constructor.** Act 4 builds one with
   `FormatterServices.GetUninitializedObject` and reflected setters, with a
   backing-field fallback (`…/Act4PlaceholderMapTemplate.cs:75-99`). Anything
   downstream of act room counts inherits that fragility.

10. **Encounter identity vs. enemy list.** Our own telemetry already records the
    right thing and says why: two encounters can spawn the same bodies, so the
    encounter `Id.Entry` is the name of the fight, not the roster
    (`klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs:801-812`).

11. **Version pin is *not* a blocker for us.** `CustomEncounterModel.cs` at tag
    `v3.3.7` (`f7db6b5`) is byte-identical in its API surface to the `v3.4.5`
    copy — same constructor, same `IsValidForAct`, same registration call. We pin
    BaseLib 3.3.7.0 (`docs/current/STATE.md:160`), so the encounter API is already
    available to us at the pin we ship.

**Pointers to other S12 agents (found in passing, not pursued):**

- **S12a** — `BaseLib@2275793:Abstracts/CustomMonsterModel.cs`,
  `Monsters/MoveBuilder.cs`, `Utils/MonsterActions.cs`, and the base
  `MonsterMoveStateMachine` / `MoveState` pattern used at
  `Downfall@32e6113:GremlinsCode/Core/GremlinsMonsterModel.cs:30-35`. Also
  `Patches/UI/MonsterSourceLabel.cs`.
- **S12c** — `BaseLib@2275793:Abstracts/CustomActModel.cs`, and the
  `ActModel.GenerateRooms` / `RunManager.GenerateRooms` patches at
  `Patches/Content/ContentPatches.cs:171-200`; Act 4's whole `src/Act4Placeholder/Map/`
  directory and `HookModifyGeneratedMapPatch.cs` / `RunManagerEnterNextActPatch.cs`.
- **S12d** — `BaseLib@2275793:Abstracts/CustomEventModel.cs` and
  `CustomAncientModel.cs`, injected the same way through `ActModel.AllEvents`
  (`ContentPatches.cs:365-372, 396-408`); Downfall writes an event row into run
  history at `DownfallCode/Console/AncientVisitConsoleCmd.cs:37`. Act 4's Architect
  is *also* an event (`TheArchitectIsSharedPatch.cs`) plus three reward events
  under `src/Act4Placeholder/Rewards/`.
- **S12e** — `[Pool(typeof(...))]` attribute routing at
  `BaseLib@2275793:Patches/Content/ContentPatches.cs:55-67` and
  `Utils/PoolAttribute.cs`.
- **S12f** — `SerializableReward` has a **fixed field set** that custom rewards
  must squeeze into (`GoldAmount`, `OptionCount`, `SpecialCard` reused for
  unrelated meanings at `Downfall@32e6113:CollectorCode/Rewards/EssenceReward.cs:42-49`
  and `GuardianCode/Rewards/GemFinderReward.cs:184-192`); also
  `BaseLib/Patches/Saves/ExtendedSaveHandlers.cs` and `SavedSpireField`
  (`Downfall@32e6113:GremlinsCode/Core/GremlinsRunModel.cs:18-39`).
- **S12g** — Act 4 ships `has_dll` + `has_pck` with **no dependencies**;
  Downfall ships both with a BaseLib floor. Both `*.json` manifests are one file
  at repo root.

---

## Transfer questions

Questions only — each is something we would have to **learn or decide**, not a
proposal, and none of them is answered here.

1. **Does the encounter API reach our build unchanged?** `CustomEncounterModel`
   is present at our pinned BaseLib 3.3.7.0 (`docs/current/STATE.md:160`) with an
   identical surface to 3.4.5. What would we have to run against the actual
   installed `BaseLib.dll` (`klee-mod/local.props`) to confirm the *compiled*
   type matches the source at tag `v3.3.7`, given we build against a Workshop
   binary and not the repo?

2. **What would an encounter id have to be for our two engines to agree?** Our
   sim carries six frozen encounters (`content/encounters/battery.yaml`, and
   `RUN_ACTS` = `act1` / `act2` "the Hive" / `act3` "Glory",
   `docs/current/STATE.md:53-54`) while the mod side names fights by
   `EncounterModel.Id.Entry`. What would we need to learn to know whether those
   two id spaces can be made to line up, or whether they are deliberately
   separate?

3. **Which of our existing hooks already sits on the right seam?**
   `KleeMod`'s telemetry already overrides `AfterCombatEnd(CombatRoom)` and
   `AfterCombatVictory(CombatRoom)` and reads `room.Encounter`
   (`klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs:1165, 1175, 805-812`). What
   would change about that code if a fight we authored ever entered a pool —
   and is that a question for the telemetry's owner or for measurement law?

4. **Co-op HP scaling.** `ScaleMonsterHpForMultiplayer` runs inside
   `CombatState.CreateCreature` before any entry hook. Our co-op has only a
   partial automated backstop (`klee-mod/KleeTests/README.md`,
   `docs/current/STATE.md:194-197`). What would we have to learn about that
   scaling before any enemy-side work could be reasoned about for two and three
   seats?

5. **Testability.** `KleeTests` cannot construct a live `CombatState`. If an
   encounter or a boss lifecycle were ever in scope, what could actually be
   asserted headlessly — registration, id stability, pool predicate — versus
   what would necessarily be play-only or Understudy-only
   (`docs/current/atlas/understudy.md`)?

6. **Library or no library.** Act 4 proves an encounter and a multi-phase boss
   can be built with raw Harmony and zero library dependency. We already carry a
   BaseLib dependency for cards. What would we need to know about the trade
   (version exposure vs. patch maintenance) before that question could even be
   put to [USER]?

7. **Reward serialisation.** We ship no `CustomReward`. If we ever wanted one,
   what does the fixed `SerializableReward` field set imply for save
   compatibility, and what does the `PlayerChoiceSynchronizer` index-then-
   terminator protocol imply for a reward that opens a screen in co-op?

8. **Whose call is which.** Where an enemy or boss would *live* — a new
   `EncounterModel` inside an existing act's pool via `IsValidForAct`, versus a
   new act with its own `BossDiscoveryOrder` — reads to me as a design direction,
   i.e. [USER]'s. Is that the right read, and does it belong on QUEUE rather
   than here?

---

## NON-FINDINGS (explicit)

1. **Downfall implements no encounter of any kind.** No `EncounterModel`
   subclass, no `MonsterGroup`, no `EncounterPool`, no `CombatEncounter` — a
   repo-wide grep over 1,858 C# files returns zero hits for all four names at
   `Downfall@32e6113`. Its only encounter awareness is reading `RoomType` and
   reading run history.
2. **Downfall implements no boss the player fights, and no hostile creature at
   all.** Every `CreateCreature` call in the repo places the creature on the
   player's side. This is a NON-FINDING for S12b's second half at the charter's
   designated first source, exactly as §4 anticipated.
3. **"Boss" is not an engine lifecycle.** I found no boss base class, boss
   interface, phase system, boss-entry event, or boss-reward table anywhere in
   the three sources. What exists is: `RoomType.Boss` on an encounter,
   `ActModel.BossDiscoveryOrder`, `EncounterModel.BossNodePath` /
   `CustomRunHistoryIconPath` for icons, and `NBossMapPoint` for the map node.
   Everything else in Act 4's Architect — four phases, revival, per-phase
   summons, per-phase stun budget — is the mod's own invention.
4. **No data-driven encounter definition found.** In all three sources an
   encounter is a compiled class. I found no JSON/YAML/resource format for
   encounters or pools.
5. **No weighting or difficulty-curve API found for encounter pools** beyond
   `Tags` (avoid two sharing a tag in a row), `IsWeak` (first 3 / first 2 of an
   act) and `NumberOfWeakEncounters`. I did not find where the engine consumes
   `Tags`; that lives in the base decompile, so it is **S13's** to confirm.
6. **Unread by choice, and named so no one assumes otherwise:** Act 4's
   `Act4ArchitectBossStateMachine.cs` (72 KB), `Act4ArchitectBossMechanics.cs`
   (83 KB, grepped only), `Act4ArchitectBossPresentation.cs` (45 KB),
   `Act4SaveStatePatches.cs`, and `ModSupport.cs` beyond one function. Claims
   about intent scripting, boss VFX/audio and boss save-restore are **not made**
   here.
7. **BaseLib's LICENSE was not opened this pass.** Its reuse terms are
   UNVERIFIED. Downfall's and Act 4's are both MIT, read directly.

---

## Search boundary

- **Date:** 2026-08-26. All pins and page reads are from that date.
- **Primary source, per charter:** `lamali292/Downfall@32e6113`, read from the
  read-only local fetch. README opened first; then repo-wide greps for
  `Encounter`, `EncounterModel`, `MonsterGroup`, `EncounterPool`,
  `CombatEncounter`, `RoomType`, `Rooms.`, `Reward`, `AddExtraReward`,
  `CombatRoom`, `\bboss\b`, `CreateCreature`, `CombatSide`, `ModelDb.*`,
  `CustomMonsterModel`, and an enumeration of every `Before*/After*/On*`
  lifecycle override in the repo. ~25 files read in full.
- **Widen, used ONCE (charter §7):** two WebSearch queries —
  `Slay the Spire 2 mod BaseLib github source custom monster encounter` and
  `"Slay the Spire 2" mod github custom boss encounter pool add enemy`.
- **Repositories opened as primary sources from that widen:**
  `Alchyr/BaseLib-StS2` (tree + 4 files at `2275793`, 1 file at tag `v3.3.7`,
  tag list) and `kphxgames/Act4FinalAscent` (tree + 12 files at `05c251a`).
  Both read as raw source pinned to a commit SHA, never as a summary.
- **Listed by the search but NOT opened**, so nothing here rests on them:
  `BAKAOLC/STS2-RitsuLib`, `Alchyr/ModTemplate-StS2`, `spencerqfox/sts2-custom-mods`,
  `JaydenLiang/slay-the-spire-2-mods`, `bwbear0412/slay_the_spire_2`,
  `jiegec/STS2RouteSuggest`, and the Nexus/Steam Workshop listings. In
  particular, the search summary claimed the mod template "shows folder structure
  for custom monsters and custom encounters" — **that is a filename claim about a
  repo I did not open, and it is not evidence.** It is recorded here only as a
  lead for whoever picks this up next.
- **Not consulted:** the base-game decompile and `game_ref/` (that is S13's
  authority), and any forum, wiki or video.

---

## What this does NOT establish

- **Not that the encounter API works.** I read source. Nothing was compiled, run,
  loaded, or observed in the game. No mod was installed, no PCK built, no
  playtest touched.
- **Not that our own build could use any of it.** The BaseLib source at a tag is
  not the Workshop `BaseLib.dll` we link against, and I did not inspect that
  binary.
- **Not a recommendation of a route.** BaseLib-based and raw-Harmony-based
  integrations both exist in released mods. Choosing between them, or choosing
  to do neither, is not mine.
- **Not a design, scope, mapping, or feasibility verdict.** In particular this
  file says nothing about whether Teyvat Spire should have custom encounters,
  custom bosses, an act 4, or an enemy pipeline. Those live in QUEUE and are
  [USER]'s.
- **Not a completeness claim about Act 4's boss.** Roughly 200 KB of its boss
  implementation was not read (see NON-FINDING 6). The lifecycle *seams* named
  above are cited; the behaviour hanging off them is not characterised.
- **Not an engine-truth claim.** Where I say "the engine does X", the evidence is
  a mod's source comment or its observable workaround, not the decompile. Every
  such claim is S13's to confirm or overturn, and S13 wins.
- **Not a rights or reuse claim.** MIT licensing is recorded as a fact about two
  repositories. Whether anything may be borrowed, and in what form, is a [USER]
  call, and LAW's reference-reading rule (charter §3.7) applied throughout: no
  code, scene, art, audio or text was copied.
