Status: RECORD (spike build half; feasibility only, nothing measured)

# Spike 4, build half: the four items, behind `-p:TeyvatFrame=true`

Branch `teyvat-spike`, three commits. Nothing deployed, launched or measured; no seat, no lane, no game. Against `sts2.dll` 0.111.0 and BaseLib 3.4.7. The decompile read `review/records/teyvat-spike-zone-read-2026-09-14.md` §7 is the design; it survives contact with two corrections, named below.

**Build and test.** `dotnet build klee-mod/KleeCode` compiles with the arm off, with `-p:TeyvatFrame=true`, and with `-p:PrototypeCards=true -p:TeyvatFrame=true` — 0 errors, no new warnings. `klee-mod\build\deploy_bridge.ps1 -BuildOnly` succeeds; it builds `vendor/STS2_MCP` and takes no `-p:` arm, so the arm's two directions are shown by the `dotnet build` line, which is what `operations/prototype.md` uses. `dotnet test klee-mod/KleeTests` 338/338; `-p:PrototypeCards=true` 1524/1524; `-p:TeyvatFrame=true` 337/337 (the arm-ships-off pin is `#if`-skipped there, per `operations/prototype.md`). `python tools/run_lints.py --lane ci`: 37/37.

**What the pins can and cannot say.** `ModelDb` is outside the headless boundary, so no test can call `ModelDb.Acts`, construct an `ActModel`, or compare two encounter lists by reference. The act-list decision is therefore extracted as a pure function over *types* that the shipped postfix and the pin share, and the delegation is pinned structurally through `Harness/Il` — `Mondstadt.GenerateAllEncounters` reaches the base act's cached `AllEncounters` and constructs nothing. Reference equality itself is a deploy question.

## Item 1 — a zone dressed two ways: WORKS WITH A COST

`Mondstadt` and `Liyue` are `ActModel` subclasses at Overgrowth's and Underdocks' `Index` (both 0). `GenerateAllEncounters` returns `ModelDb.Act<Overgrowth>().AllEncounters` — the base act's *cached* sequence, so the table is the same object, not an equal one. `AllEvents`, `AllAncients`, `GetUnlockedAncients`, `BossDiscoveryOrder`, `GetMapPointTypes` and the chest and music members delegate the same way.

**The roll keeps its shape by REPLACEMENT.** With the arm on, the `get_Acts` postfix takes `Overgrowth` and `Underdocks` *out* and puts `Mondstadt` and `Liyue` in their places, in order. Act 1 is still exactly two candidates, so `GetRandomList` still makes one `rng.NextItem` draw against a two-element list at index 0, off the same rng, consuming the same amount of it. Appending would have made act 1 a four-way roll in which a zone and its own dressing were separate faces. Both dressings are `IsDefault => true` and `IsUnlocked => true` deliberately: `ActModel.cs:563` *forces* a non-default undiscovered act past the roll on a single-player run, which would make a dressing's first appearance a certainty rather than a coin.

**Cost, and a fourth patch the read did not price.** `FilePathIdentifier` and the five asset-path properties over it (`RestSiteBackgroundPath`, the three `Map*BgPath`s, `BackgroundScenePath`) are **non-virtual**; a subclass cannot override one. Aliasing a dressing's assets to the base zone's — which this spike does, commissioning no art — needs a postfix on `get_FilePathIdentifier`. `Id.Entry` is deliberately not aliased, so the act is **named** Mondstadt and **drawn** as Overgrowth. A real dressing deletes that patch and ships `scenes/backgrounds/mondstadt/layers`, a rest-site scene and three map PNGs; `BackgroundAssets`'s ctor throws rather than falls back.

Second cost: `ApplyActDiscoveryOrderModifications` is `protected abstract` and writes into *this* instance's `_rooms`, so Overgrowth's eleven-line first-run ordering is **replicated** in `Mondstadt`, not delegated. It is the arm's one copied body and a real drift risk against a future game patch; it fires only on a save with zero completed runs.

**A deploy must prove:** the `get_Acts` postfix lands before `ModelDb._acts` and `_actsByIndex` are first read (check `ActsByIndex[0]` after a full boot); that `get_FilePathIdentifier`, a one-expression getter and a JIT inline candidate, actually takes the patch (symptom if not: `InvalidOperationException` out of `BackgroundAssets` on the first combat of a Mondstadt run); coin fairness over ≥20 runs; a save/load round-trip; and `NBestiary`, run history and the epoch screens with a dressing active.

**Patched:** `MegaCrit.Sts2.Core.Models.ModelDb.get_Acts`, `MegaCrit.Sts2.Core.Models.ActModel.get_FilePathIdentifier`.

## Item 2 — one gallery event on the act-1 map: WORKS WITH A COST

`SpringvaleCheeseCellar` mirrors `RoomFullOfCheese` clause for clause: the same `DamageVar(14m, Unblockable | Unpowered)`, the same eight Commons at uniform odds with `NoRarityModification`, the same take-two selector, the same `CreatureCmd.Damage` then `RelicCmd.Obtain<ChosenCheese>`, the same `CurrentActIndex < 2` gate. Text is gallery variant 1, verbatim; a pin compares the two `IsAllowed` bodies' call sets and both option bodies' commands.

**The read's route does not work, and that is the item's finding.** Room Full of Cheese is **not an act event** — it is one of `ModelDb.AllSharedEvents`'s eighteen, so an act's `AllEvents` cannot remove it, and swapping it inside the dressing's pool would have *added* a fourteenth act event beside the shared thirteenth. Pool length is a hard rule: `GenerateRooms` shuffles `AllEvents.Concat(AllSharedEvents)` on the run's `UpFront` rng at run start, so one extra element moves every later roll on it — bosses, Ancients, encounter order, and the Klee calibration seed's whole map. So the substitution happens **downstream of the shuffle**, in a postfix on `ActModel.PullNextEvent`: one-for-one, only in Mondstadt, costing no rng draw, leaving the two zones' room sets byte-identical on a fixed seed.

**Cost.** `PullNextEvent` calls `runState.AddVisitedEvent` *before* the postfix runs, so a run's visited-event history records the base event, not the conversion; `Hook.ModifyNextEvent`, called on the line below, is the seam that fixes it and is the right long-term home. And the relic keeps its base name — the gallery calls it The Anointed Wheel, `RelicCmd.Obtain<ChosenCheese>` grants The Chosen Cheese, and relics have no `L10NMonsterLookup`-shaped choke point, so renaming one needs its own seam.

**A deploy must prove:** that the event is reachable and completes both options, and that the substitute's `IsAllowed` never contradicts the base event's at the head of the pre-shuffled list.

**Patched:** `MegaCrit.Sts2.Core.Models.ActModel.PullNextEvent`.

## Item 3 — one enemy renamed, re-worded and drawn as a still: WORKS

*Name*: one table row. `MonsterModel.L10NMonsterLookup` is the only constructor of monster loc strings in the game, so one postfix rewriting `NIBBIT.name` to `NIBBIT.name@MONDSTADT` covers the display name, every banter line and the bestiary move names. `TeyvatLoc` merges the dressed rows; a monster with no dressed row takes the base key unchanged.

*Intent words*: **cheap, and the patch is armed and empty.** `AbstractIntent` builds `new LocString("intents", IntentPrefix + ".title")` with no monster in scope, so a generic verb is per-*zone* or nothing. Two postfixes, ~30 lines, one loc row per dressed verb; `TeyvatFrame.IntentWords` ships empty because the frame packet §7.1's design view is that per-monster *move* titles carry the nation and the generic verbs do not. Turning it on costs one row.

*Portrait*: `pck-src/teyvat/creature_visuals/hilichurl_guard.tscn` — a `Node2D` with a `Sprite2D` under `%Visuals` plus the three other markers `_Ready` fetches with `GetNode`. The texture is Tier F and **is not committed**; `tools/build_pck.ps1` gains one `Note-Skip`'d copy block for `ImageGen\images\teyvat\creature_visuals`, and `pck-src/teyvat/README.md` carries the 240x280 placeholder's recipe.

**Every SpineSprite-gated door, and which this still trips.** `NCreatureVisuals._Ready` sets `SpineBody` only when `%Visuals`'s `GetClass()` is `"SpineSprite"`, so a `Sprite2D` leaves `HasSpineAnimation` false. Gated and therefore safe: `NCreature.cs:509` (the whole animator build — which is why `MonsterModel.GenerateAnimator(MegaSprite)` and `SetupSkins(MegaSprite, MegaSkeleton)` are never reached, and must not be overridden), `NCreature.SetAnimationTrigger` (`?.`), `NCombatUi.cs:387`, `NMonsterDeathVfx.cs:149`, `NFormVfx.cs:77`, `NCreatureVisuals.UpdatePhobiaMode` and `.SetUpSkin`, `DoomPower.cs:159` (via `SpineAnimation.IsValid`). **Ungated, and the doors this body would trip:** `NCreature.GetCurrentAnimationLength` and `.GetCurrentAnimationTimeRemaining`, which reach `SpineAnimation` with no `HasSpineAnimation` check at the call site. **Ungated but unreachable for this body:** the per-monster `?.SpineAnimation.SetAnimation` calls in `WaterfallGiant`, `Vantom`, `SoulNexus`, `Queen`, `LagavulinMatriarch` and `TheArchitect` — none is Nibbit's, but they are the cost line for any later body copied from one of them. Out of combat, the merchant's unconditional `MegaSprite` is already handled by the shipped `MerchantSpineBindingPatch`.

**A deploy must prove:** whether those two ungated `NCreature` timing methods bite in a real fight, and whether `get_VisualsPath`, a trivial getter, takes the patch at all (fallback: patch `get_AssetPaths` and `CreateVisuals` instead).

**Patched:** `MegaCrit.Sts2.Core.Models.MonsterModel.L10NMonsterLookup`, `...MonsterModel.get_VisualsPath`, `MegaCrit.Sts2.Core.MonsterMoves.Intents.AbstractIntent.get_IntentTitle`, `...AbstractIntent.GetIntentDescription`.

## Item 4 — packaged music with the original ducked: WORKS WITH A COST

**There is no FMOD bus duck call, and there is no FMOD bus.** The managed audio surface is three files: `Core.Audio/FmodSfx.cs` (a bag of `const string` event paths), `Core.Audio/DamageSfxType.cs`, and `Core.Nodes.Audio/NAudioManager.cs`. No `Bus`, `Snapshot`, `Duck` or `setVolume` type exists anywhere in the decompile; every FMOD call goes out as `Node.Call("update_music", ...)` on a Godot node — a GDExtension surface Harmony cannot reach. The only volume levers are `NAudioManager.SetMasterVol` / `SetSfxVol` / `SetAmbienceVol` / `SetBgmVol`, which are the **options-screen sliders**: global, persistent, no paired fade-and-restore. Writing one from a patch would leave a player's music slider down after the arm was turned off.

So **the duck is `NRunMusicController.StopMusic()`** — total, not partial — and the track plays through a Godot `AudioStreamPlayer` parented to the run's music controller, so it dies with the run. Ambience is deliberately untouched. The `UpdateMusic` postfix is idempotent (a room change does not restart the track) and a re-entrancy guard keeps the arm's own stop from tearing down the player it just built. **With no file in the pack both postfixes fall straight through**; no audio file is added by this commit. The pck path is `res://teyvat/music/<act>/` — a namespace of the frame's own, answering `operations/media.md` §7's open question — and the track name is enumerated from the directory rather than guessed, because the ledger owns it.

**Cost.** A partial duck needs an FMOD bank of our own or a GDScript helper in the pck, neither of which a spike should build. And `UpdateMusic` is one of five public music entry points: `PlayCustomMusic`, `ToggleMerchantTrack`, `TriggerEliteSecondPhase` and `TriggerCampfireGoingOut` are separate methods and would each need a row if a surface routes through them.

**A deploy must prove:** that a Godot `AudioStreamPlayer` is audible at all while FMOD holds the device; that `StopMusic` from inside the `UpdateMusic` postfix does not re-enter it on the GDExtension side; and which of the four named surfaces (combat start, rest site, map screen, boss intro) actually route through `UpdateMusic`.

**Patched:** `MegaCrit.Sts2.Core.Nodes.Audio.NRunMusicController.UpdateMusic`, `...NRunMusicController.StopMusic`.

## What the arm costs when it is off

Six Harmony postfix classes whose first line is the flag; two `ActModel` subclasses and one `EventModel` subclass that `ModelDb`'s reflection walk constructs at boot and nothing can reach (`ModelDb.Acts` is a hardcoded list the postfix declines to touch, and `ModelDb.AllEvents` derives from `Acts`); zero loc rows merged; zero pck files, since the portrait's texture is not committed and no track exists. The arm stays off on every calibration deploy.
