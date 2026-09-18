Status: RESEARCH (decompile read; nothing deployed, the game was never launched)

# Every piece of music Slay the Spire 2 plays, and which Teyvat slot answers it

Read 2026-09-17 off `sts2.dll` v0.111.0 (`ilspycmd` 8.2, whole-assembly
decompile, 3,538 files) for the Teyvat run frame's music layer (R272 §1.4).
The job is to stop guessing at the seam: `docs/current/operations/media.md` §7
and `EB-814` both say the room scenes have no resolver, and the reason is that
**the thing the arm already patches does not know what room you are in.**

## 1. How `UpdateMusic` actually decides — and what it does not read

`NRunMusicController.UpdateMusic()` reads exactly three things:

```csharp
MusicSelection? sel = ResolveMusic(_currentTrack,
                                   _runState.Act.BgMusicOptions,
                                   _runState.Act.MusicBankPaths,
                                   _runState.Rng.Seed);
```

`ResolveMusic` is `new Rng(seed, "bg_music").NextInt(0, options.Length)` — one
deterministic draw over the act's own option list — and returns null when the
draw equals `_currentTrack`, so a redundant call is a no-op instead of a
restart. On a hit it loads the FMOD bank, sets `_currentTrack`, calls
`_proxy.Call("update_music", track)`, sets the global parameter `Progress` to
0, and updates ambience.

**It never reads the room type, an elite flag or a boss flag.** The act is the
only input. That is the whole finding: the existing arm's postfix on
`UpdateMusic` can answer "which nation", and cannot answer anything else.

Room variation is not a second track. It is a **global FMOD parameter named
`Progress` on the same act event**, moved by the *other* public method:

```csharp
public void UpdateTrack()                       // the room-aware seam
    => UpdateTrack("Progress", (float)GetTrack(_runState.CurrentRoom.RoomType));
```

and `GetTrack` is the whole room table (private enum `MusicProgressTrack`):

| `Progress` | name | `GetTrack` condition |
|---|---|---|
| 0 | `Init` | default; also `RoomType.Event` whose `CanonicalEvent is AncientEventModel`; also what `StopMusic` leaves behind |
| 1 | `Enemy` | `RoomType.Monster` |
| 2 | `Merchant` | `RoomType.Shop` |
| 3 | `Rest` | `RoomType.RestSite` |
| 4 | `Unknown` | `RoomType.Event`, non-Ancient |
| 5 | `Treasure` | `RoomType.Treasure` |
| 6 | `Elite` | `RoomType.Elite` **and `RoomType.Boss`** — the same value for both |
| 7 | `CombatEnd` | any `IsCombatRoom()` once `CombatManager.Instance.IsInProgress` is false (this test runs *first*, ahead of the switch) |
| 8 | `Elite2` | not from `GetTrack`; `TriggerEliteSecondPhase()` writes 8 directly |
| 9 | `MerchantEnd` | not from `GetTrack`; `ToggleMerchantTrack()` writes 9 when `NMapScreen.Instance.IsVisible()` |

**Corrected 2026-09-17 under `EB-821`:** `UpdateTrack()` has **four** managed
callers, not two. `CombatManager` has two — `StartCombatInternal` (right after
`CombatBegan`) and the combat-won path — and `RunManager` has two more:
immediately after `await room.Enter(...)` on every room entry, and again in
`ResumePreviousRoom`. So the seam fires at **combat start, combat end and every
room entry**, and all four are reachable. The missing pair is also the crash
path: `UpdateTrack()`'s body ends with
`if (_runState.CurrentRoom is RestSiteRoom) _proxy.Call("update_campfire_ambience", 0)`,
which lands on a released FMOD event instance once the arm has called
`StopMusic` — [USER]'s 2026-09-17 rest-site crash.
`klee-mod/KleeCode/Teyvat/Patches/RunMusicPatch.cs` carries the mechanism, the
proxy's measured method surface and the route taken.

`RoomType` itself is `Unassigned, Monster, Elite, Boss, Treasure, Shop, Event,
RestSite, Map`, and `IsCombatRoom()` is `(uint)(room - 1) <= 2u` — Monster,
Elite, Boss and nothing else.

## 2. The event list

`event:/` strings were grepped out of the whole decompile (748 hits, 20 of them
music or ambience). Every music event the game can play, with its trigger:

| game event | trigger | act-scoped? | our slot | counterpart pick | confidence |
|---|---|---|---|---|---|
| `event:/music/menu_update` | `NMainMenu._Ready` → `NAudioManager.PlayMusic`; `menu_progress` param goes `"main"` / `"timeline"` | no — global, outside any run | `menu` | `music_login_common` (95.0 s) | high |
| `event:/music/act1_a1_v1`, `act1_a2_v2` | Overgrowth's `BgMusicOptions`, one drawn by run seed in `UpdateMusic` | **yes** (act 1 / Overgrowth) | `act1_mondstadt/*` | see §3 | high |
| `event:/music/act1_b1_v1` | Underdocks' single option | **yes** (act 1 / Underdocks) | `act1_liyue/*` | see §3 | high |
| `event:/music/act2_a1_v2`, `act2_a2_v2` | the Hive's `BgMusicOptions` | **yes** (act 2) | `act2_natlan/*`, `act2_inazuma/*` | see §3 | high |
| `event:/music/act3_a1_v1`, `act3_a2_v1` | Glory's `BgMusicOptions` | **yes** (act 3) | `act3_fontaine/*`, `act3_sumeru/*` | see §3 | high |
| `Progress` 1 `Enemy` on the act event | `UpdateTrack()` at combat start, Monster room | yes (a parameter, not a track) | `<face>/combat` | the face's combat loop | high |
| `Progress` 6 `Elite` on the act event | same, Elite **or Boss** room | yes | `<face>/elite` (Elite) | the face's elite loop | high |
| `Progress` 8 `Elite2` | `TriggerEliteSecondPhase()` — `BygoneEffigy`, `InfestedPower` | yes | none; stays on `<face>/elite` | — | high |
| `Progress` 7 `CombatEnd` | `UpdateTrack()` on the combat-won path | yes | none; we hold the room's slot (§4) | — | high |
| `Progress` 2 / 9 `Merchant` / `MerchantEnd` | Shop room; `ToggleMerchantTrack()` from `NMerchantRoom` and `NFakeMerchant` | yes | `shop` (global by our choice) | `music_city_mengde_day_03` | high |
| `Progress` 3 `Rest` | RestSite room | yes | `rest` (global by our choice) | `music_scene_mengde_saloon` | high |
| `Progress` 5 `Treasure`, 4 `Unknown`, 0 `Init` | Treasure room, Event room, Ancient event | yes | `<face>/map` | the face's exploration loop | medium — these are one act track in the game and three slots' worth of room in ours; we give them the out-of-combat loop |
| `event:/music/act1_boss_ceremonial_beast`, `act1_boss_the_kin`, `act1_boss_vantom`, `act1_b_boss_soul_fysh`, `act1_b_boss_waterfall_giant`, `act2_boss_kaiser_crab`, `act2_boss_knowledge_demon`, `act2_boss_the_insatiable`, `act3_boss_queen`, `act3_boss_test_subject` | `EncounterModel.CustomBgm`; `CombatManager.StartCombatInternal` calls `PlayCustomMusic` when `HasBgm`. This one **stops** the act event and plays its own; `StopCustomMusic` brings the act event back at `Progress` 7 | per **encounter**, so act-scoped in effect (`act3_boss_queen` serves both Queen and Aeonglass) | `<face>/boss` | see §3 | high |
| `UpdateMusicParameter("<boss>_progress", n)` — `queen`, `kaiser_crab`, `the_kin`, `knowledge_demon`, `soulfysh`, `test_subject`, `vantom`, `waterfall_giant`, `the_insatiable`, plus `beckon` and `kaiser_crab_direction` | boss scripts at phase changes | n/a | none | — | high |
| `event:/temp/sfx/game_over` | `CreatureCmd`, all players dead: `RunMusicController.StopMusic()` then `NAudioManager.PlayMusic` | no — global stinger | **none; the game's own stands** | — | high |
| `event:/sfx/ambience/act1_ambience`, `act2_ambience`, `act3_ambience`, `act1_neow`, `act2_ambience_the_insatiable` | `UpdateAmbience`, from `ActModel.AmbientSfx` overridden by `EncounterModel.AmbientSfx` | yes | **none; deliberately left alone** | — | high |
| `update_campfire_ambience` 0 / 1 | entering a rest site; `TriggerCampfireGoingOut()` from `NRestSiteRoom` | yes | none | — | high |

**Three things the game does not have.** There is no victory music and no
credits music in the managed assembly: `PlayMusic` has exactly two call sites
outside `NAudioManager` itself, the main menu and the game-over stinger.
`UpdateCustomTrack(track, label)` is public and has no managed caller at all.
And there is no FMOD bus, snapshot or duck anywhere in managed code — the
finding `TeyvatMusic`'s header already carries — so the only lever remains
`StopMusic()`, and the arm's "duck" is still total.

**Amended 2026-09-17 under `EB-821`, having read the GDScript side.** Buses do
exist, one level below managed code: `res://src/gdscript/audio_manager_proxy.gd`
names four — `bus:/master`, `/sfx`, `/ambience`, `/music` — and sets each with
`FmodServer.get_bus(...).set_volume(v)` behind `set_bgm_volume` and its three
siblings, which are the options screen's own sliders. The **music controller's**
proxy, `res://src/gdscript/music_controller_proxy.gd`, has no bus, no pause and
no volume at all: its nine methods are `update_music`, `stop_music`,
`update_music_parameter`, `update_global_parameter`, `update_ambience`,
`stop_ambience`, `update_campfire_ambience`, `load_act_bank`,
`unload_act_banks`. So the conclusion stands and is now measured rather than
inferred — with the sharper reason that no getter for a bus volume exists
anywhere, so a borrowed slider could never be handed back.

## 3. The counterpart picks

All from [USER]'s own install via the 2026-09-17 extraction
(`research/teyvat-music-sources-2026-09-16.md` §6; internal names, never OST
titles; `licence = PLACEHOLDER-COPYRIGHTED` on every row). E defaults under the
R212 ladder, disclosed and vetoed by ear. The full table with durations and
source packages is `media/MUSIC.tsv`; the boss picks are matched to the boss
the nation mapping puts on that face
(`review/ruled/teyvat-nation-mapping-{,act1-,act2-,act3-}2026-09-14.md`):

| face | boss the mapping puts here | boss track |
|---|---|---|
| act1_mondstadt | Vantom ↔ **Andrius, Lupus Boreas** (act1 §44) | `music_combat_LupiBoreasS02` |
| act1_liyue | Lagavulin Matriarch ↔ Primo Geovishap (act1 §86) — no Geovishap theme exists, so Liyue's own weekly boss stands | `music_combat_Tartaglia_S02` (Childe) |
| act2_natlan | no Natlan boss reading on the Hive (act2 §110-115); the nation's strongest boss theme stands | `Music_Combat_TheAbyssXiuhcoatl_ZhouBen_N306` (Xiuhcoatl) |
| act2_inazuma | Kaiser Crab ↔ La Signora is Snezhnaya-scored (act2 §61); the face's own archon is the nation-correct read | `Music_Combat_Shougun_Mita_S01` (Raiden Shogun) |
| act3_fontaine | Test Subject ↔ Iniquitous Baptist (act3 §70) — no Baptist theme; Fontaine's weekly boss stands | `music_combat_Devourer_S01_F210_02` (All-Devouring Narwhal) |
| act3_sumeru | Aeonglass ↔ **Shouki no Kami**, literal (act3 §71) | `music_combat_Scaramouche_S03_loop` |

Elites: Sumeru and Inazuma have real `elite_` names in the dump
(`music_combat_elite_XuMi_X51`, `music_combat_YXG_Elite_loop_02`); the other
four take the face's second combat variant, which is what the nation's own
suite offers. Fontaine's combat pick is **`music_combat_FengDan_F012`**, [USER]'s
2026-09-17 ruling over the `F011` default; `F013` takes the elite slot.

One track was not in the 419-file extraction and was pulled from the census for
this: **`music_explore_BW_F128`** (152.45 s, `Music27.pck`), Fontaine's
overworld day loop. Fontaine's exploration family is named `music_explore_BW_F<nnn>`
with no nation token, so `classify.py`'s `explore`-needs-a-nation rule dropped
all 39 of them. Same pipeline, same tools, no re-encode.

## 4. What the resolvers key on, and why there

Because `UpdateMusic` cannot see the room (§1), the arm keys on four postfixes
rather than one:

- **`UpdateMusic`** — the act/room-change re-assert the arm already had.
- **`UpdateTrack()`** — combat start and combat end, the only room-aware seam.
- **`PlayCustomMusic(string)`** — a boss encounter's own event starting.
- **`StopCustomMusic()`** — it ending.
- **`StopMusic`** — teardown, unchanged.

All five ask one function, `TeyvatMusic.SlotFor(roomType)`:

| room | slot |
|---|---|
| `Boss` | `<face>/boss` |
| `Elite` | `<face>/elite` |
| `Monster` | `<face>/combat` |
| `Shop` | `shop` (global) |
| `RestSite` | `rest` (global) |
| `Treasure`, `Event`, `Map`, `Unassigned`, no room | `<face>/map` |

**A combat room keeps its combat slot after the fight is won**, unlike the
game, which moves `Progress` to 7. A parameter change is a crossfade inside one
event; ours would be a file swap and a restart, and swapping the track under a
player reading their card rewards is worse than holding the loop until the room
changes. That is the one place this table deliberately differs from `GetTrack`.

Fallback, in order, and it is the rule that matters: **face slot → face
combat → silence-with-FMOD.** An elite or boss slot with nothing filed drops to
that face's combat loop, which is the same nation. Nothing ever falls across to
another nation. A global slot (`menu`, `shop`, `rest`) has **no** fallback —
with nothing filed, `Play` returns false, the arm never calls `StopMusic`, and
the game's own merchant or campfire progress plays exactly as it does today.

`menu` is not on the run controller at all — there is no run, so
`NRunMusicController` does not exist. It hangs off `NAudioManager`, keyed on the
literal `event:/music/menu_update`, so the game-over stinger through the same
method is untouched.

## 5. The nested scene, measured

A slot is a directory below the face, which neither the packer nor the reader
had ever been asked to do. Both halves were measured before any of the above was
written (MegaDot 4.5.1 headless, `tools/build_pck.ps1`'s own `project.godot` and
export preset; then a second scratch project that mounts the resulting pack).

**Packing.** Three real files went in —
`teyvat/music/act1_mondstadt/combat/music_combat_A.ogg`,
`.../act1_mondstadt/boss/music_combat_LupiBoreasS02.ogg` and
`teyvat/music/menu/music_login_common.ogg`. Import exit 0, export exit 0, nine
pack entries: three `.godot/imported/<name>.ogg-<hash>.oggvorbisstr`, three
`<path>.ogg.import` at their full nested paths, and three project files.
Exactly the two-entries-per-track shape the flat case already had.

**Reading.** With that pack mounted:

```
dir_exists res://teyvat/music/act1_mondstadt/combat -> true
  files ["music_combat_A.ogg.import"]
dir_exists res://teyvat/music/act1_mondstadt/boss   -> true
  files ["music_combat_LupiBoreasS02.ogg.import"]
dir_exists res://teyvat/music/menu                  -> true
  files ["music_login_common.ogg.import"]
dir_exists res://teyvat/music/act1_mondstadt        -> true
  files []   dirs ["boss", "combat"]
dir_exists res://teyvat/music/act1_liyue/combat     -> false   (and silent)
exists .../combat/music_combat_A.ogg        -> true
exists .../combat/music_combat_A.ogg.import -> false
loaded class = AudioStreamOggVorbis
```

So `TeyvatMusic.TrackFor` needed no change beyond the path it asks for: the
`.import` strip, the `ResourceLoader.Exists` question and `EB-758`'s silent
`DirExistsAbsolute` guard all behave identically one level down. The fourth line
is the one worth keeping: the old flat scene directory still exists in a pack
that has nested ones under it, and lists **no files** — so a reader left on the
old path goes quiet rather than playing something wrong.

## 6. What is not proved here

The running game. Every claim above is off the decompile, off a headless
MegaDot, or off the extraction inventory; nothing was deployed and the game was
never launched. What a deploy still owes, and `EB-814`'s acceptance line asks
for: that a boss track plays in a boss fight and `godot.log` names the slot
(`TeyvatMusic.Play` logs `slot '<name>' -> playing packaged track <path>`), that
the four postfixes do not fight each other across a room change, and that the
menu patch does not swallow the game-over stinger.
