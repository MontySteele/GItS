# S16 corpus — base / complex player character: **Regent**

> **This file decides nothing.** It is a research artifact from surplus-dispatch-3
> (charter §4/S16). Every recommendation is a **technical** note labelled
> `PROPOSED`; taste, lore, art direction, rights, spend, scope and ship calls
> remain [USER]'s. Nothing here opens a balance window, moves a stamp, mints an
> id, or interprets a playtest. No game was launched and no frame was captured.

**Follows** `s16-00-schema.md` sections A–L in order. Facts established there
(the scene contract, the code-built state machine, where tells fire, fallback
behaviour, and what our mod does instead) are cited, not re-derived — **except
in three places where this body contradicts or sharpens the schema, which are
flagged `SCHEMA CORRECTION` and stated loudly** (§D.0, §H.1, §F.4).

*Filename note for the integrator:* the schema's §4 ownership map calls this
file `s16-02-player-complex.md`; the dispatch assigned the name
`s16-body-base-complex-player-character.md`, matching the sibling
`s16-body-normal-enemy.md`. Same file, same owner, one body.

---

## A. Identity and provenance

| Field | Content |
|---|---|
| `body_id` | `regent` |
| `role` | `player-complex` |
| `class` | `MegaCrit.Sts2.Core.Models.Characters.Regent` (`sealed`, extends `CharacterModel`) — `sts2src/MegaCrit.Sts2.Core.Models.Characters/Regent.cs:18` |
| `scene` | `res://scenes/creature_visuals/regent.tscn` — **75,694 B**, 406 lines (pck directory row `scenes/creature_visuals/regent.tscn`) |
| `reachability` | A **base-roster player character**, chosen at character select — no act, encounter or map pin involved. It is gated behind an unlock: `UnlocksAfterRunAs => ModelDb.Character<Silent>()` (`Regent.cs:30`), and the chain across the whole roster is Ironclad / Silent free → **Regent after Silent** → Necrobinder after Regent → Defect after Necrobinder (`Ironclad.cs:29`, `Silent.cs:32`, `Necrobinder.cs:31`, `Defect.cs:26`). The exact grant condition (finishing a run vs. starting one) is **UNVERIFIED** — only the unlock-hint plumbing was read (`CharacterModel.cs:267-274`). For capture planning: an already-unlocked profile reaches this body in one screen, with no run RNG at all, which makes it the **cheapest of the four corpus bodies to capture**. |
| `read_on` | 2026-08-26; StS2 **v0.107.1**, commit `59260271`, Steam buildid `23811903` (`docs/current/STATE.md:158-160`); `pck:res://scenes/creature_visuals/regent.tscn` out of `C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\SlayTheSpire2.pck` (read-only, extracted to scratch) |

Two run-shape constants for orientation only, not analysed here: `StartingHp`
75, `StartingGold` 99, starting relic `DivineRight`, ten-card starting deck
(`Regent.cs:32-58`).

---

## B. Scene / resource topology

**One row per node, in tree order.** `regent.tscn` line numbers are the
extracted copy's; the node block runs 239–406.

| path | type | unique name | purpose | depends_on |
|---|---|---|---|---|
| `Regent` | `Node2D` | — (owner) | body root; carries the `NCreatureVisuals` script (`:239-241`) | `1_3dwrg` → `res://src/Core/Nodes/Combat/NCreatureVisuals.cs` |
| `Visuals` | **`SpineSprite`** | **`%Visuals`** | the body skeleton. `preview_animation = "idle_loop"`, `preview_time = 2.5`, `position (2, −20)`, `scale (0.29, 0.29)`, `multiply_material = CanvasItemMaterial_53uu0`, `metadata/_edit_lock_` (`:243-253`) | `3_jb1vq` → `regent_skel_data.tres` |
| `Visuals/Weapons` | **`SpineSlotNode`** | no | follows Spine **slot `shadow`**; `show_behind_parent = true`; sole purpose is to be a parent that inherits a slot's transform and draw order (`:255-259`) | — |
| `Visuals/Weapons/WeaponAnim1` | **`SpineSprite`** | no | first weapon skeleton, nested *inside* the body skeleton's slot. `preview_animation = "-- Empty --"` (`:261-269`) | `7_howi0` → `regent_weapon_skel_data.tres` |
| `Visuals/Weapons/WeaponAnim2` | **`SpineSprite`** | no | second weapon skeleton, **same resource**, ~0.0005 rad apart in rotation (`:271-279`) | `7_howi0` (shared) |
| `Visuals/Explosion` | `GPUParticles2D` | no | death explosion. `amount = 800`, `lifetime 2.5`, `explosiveness 1.0`, `emitting = false`, `show_behind_parent`, `visibility_rect 2000×2000` (`:281-291`) | `shared_additive_mat`, `4_2hmwe`, `ParticleProcessMaterial_siu7b` |
| `Visuals/SpineArmBone` | **`SpineBoneNode`** | no | follows bone **`arm_particle_attach`** (`:293-297`) | — |
| `Visuals/SpineArmBone/Particles` | `GPUParticles2D` | no | death particles, arm. `amount 80`, `lifetime 2.0`, `randomness 0.35`, `fixed_fps 60` (`:299-311`) | `shared_additive_mat`, `4_2hmwe`, `PPM_t61rr` |
| `Visuals/SpineChestBone` | **`SpineBoneNode`** | no | follows bone **`chest_particle_attach`** (`:313-317`) | — |
| `Visuals/SpineChestBone/Particles` | `GPUParticles2D` | no | death particles, chest front. `amount 200`, `lifetime 2.0` (`:319-332`) | `shared_additive_mat`, `4_2hmwe`, `PPM_m5irg` |
| `Visuals/SpineChestBone/ParticlesBack` | `GPUParticles2D` | no | death particles, chest back. `z_index = −1`, `amount 140`, `lifetime 1.5` (`:334-348`) | `shared_additive_mat`, `4_2hmwe`, `PPM_f830s` |
| `Visuals/SpineLegBoneL` | **`SpineBoneNode`** | no | follows bone **`leg_particle_attach_l`** (`:350-354`) | — |
| `Visuals/SpineLegBoneL/Particles` | `GPUParticles2D` | no | death particles, left leg. `amount 30`, `lifetime 1.25` (`:356-366`) | `shared_additive_mat`, `4_2hmwe`, `PPM_7ixmg` |
| `Visuals/SpineLegBone` | **`SpineBoneNode`** | no | follows bone **`leg_particle_attach`** (`:368-372`) | — |
| `Visuals/SpineLegBone/Particles` | `GPUParticles2D` | no | death particles, leg. `amount 80`, `lifetime 2.0` (`:374-383`) | `shared_additive_mat`, `4_2hmwe`, `PPM_4wq27` |
| `Visuals/NRegentVfx` | `Node` | no | the body's driver script (`:385-387`) | `4_sn882` → `res://src/Core/Nodes/Vfx/NRegentVfx.cs` |
| `Bounds` | `Control` | **`%Bounds`** | hitbox + selection-reticle rect. `offset_left −115`, `offset_top −335`, `offset_right 115`; **no `offset_bottom` line**, so it defaults to 0 → a 230 × 335 rect. `mouse_filter = 2` (`:389-396`) | — |
| `IntentPos` | `Marker2D` | **`%IntentPos`** | intent anchor, `(24, −414)` (`:398-400`) | — |
| `CenterPos` | `Marker2D` | **`%CenterPos`** | this is `VfxSpawnPosition`, `(0, −178)` (`:402-406`) | — |

### `ext_resource` list (6, at `:3-8`)

| id | type | path | shared? |
|---|---|---|---|
| `1_3dwrg` | `Script` | `res://src/Core/Nodes/Combat/NCreatureVisuals.cs` | **shared** — every creature body, player and monster alike (schema §1.1) |
| `3_jb1vq` | `SpineSkeletonDataResource` | `res://animations/characters/regent/regent_skel_data.tres` | private |
| `4_2hmwe` | `Texture2D` | `res://images/vfx/characters/regent_sparkle.png` | private — the only pck rows are its own `.import` and `.ctex` |
| `4_sn882` | `Script` | `res://src/Core/Nodes/Vfx/NRegentVfx.cs` | private (one body) |
| `7_howi0` | `SpineSkeletonDataResource` | `res://animations/characters/regent/regent_weapon_skel_data.tres` | private, **but used twice inside this one scene** |
| `shared_additive_mat` | `Material` | `res://themes/canvas_item_material_additive_shared.tres` | **shared** — 102 B packed; also referenced by `ceremonial_beast.tscn`, `kin_follower.tscn`, `kin_priest.tscn`, `test_subject.tscn` among the 18 bodies extracted tonight |

Note the hand-written `id="shared_additive_mat"`: every other ext_resource id in
the file is a generated token. Somebody typed that one, which is a small but
real signal that the shared additive material is treated as a house asset.

### Sub-resources (29, `load_steps = 36`)

`1 CanvasItemMaterial`, `1 Image`, `1 ImageTexture`, `10 Curve`,
`10 CurveTexture`, `6 ParticleProcessMaterial`. Three of the six process
materials **share** one `scale_curve` (`CurveTexture_pjfog`, referenced at
`:98`, `:231` and, via `Curve_5w7lj`/`Curve_32u4y`, duplicated with identical
15-point data at `:144` and `:181` — i.e. the same curve was pasted three times
and shared once). Two curves carry `resource_local_to_scene = true` (`:171`,
`:209`, `:215`).

### Nodes the §1.1 contract does **not** require, and what breaks without them

The contract requires only `%Visuals`, `%Bounds`, `%IntentPos`, `%CenterPos`.
**Twelve of the nineteen nodes are optional to the engine and mandatory to this
body's own driver.** `NRegentVfx._Ready` resolves eight of them with
`GetNode<T>` — which throws, not returns null — at
`sts2src/MegaCrit.Sts2.Core.Nodes.Vfx/NRegentVfx.cs:172-179`:
`SpineArmBone/Particles`, `SpineChestBone/Particles`,
`SpineChestBone/ParticlesBack`, `SpineLegBone/Particles`,
`SpineLegBoneL/Particles`, `Explosion`, `Weapons/WeaponAnim1`,
`Weapons/WeaponAnim2`. Delete any one and the body throws during scene ready.
The four `SpineBoneNode`s and the `SpineSlotNode` are not fetched by the script
but are the *parents* of five of those eight paths, so they are load-bearing by
position.

Optional contract nodes that are **absent**: `%PhobiaModeVisuals` (no alternate
body), `%OrbPos` (silently falls back to `%IntentPos`,
`NCreatureVisuals.cs:224`), `%TalkPos` (stays null, `:225`).

---

## C. Node / layer / bone counts

| count | value | how obtained |
|---|---|---|
| `nodes_total` | **19** | `[node ` blocks in `regent.tscn` |
| `spine_sprites` | **3** | 1 body + 2 weapons |
| `particle_emitters` | **6 GPU, 0 CPU** | all `GPUParticles2D` |
| `bone_nodes` (scene `SpineBoneNode`) | **4** | `arm_particle_attach`, `chest_particle_attach`, `leg_particle_attach`, `leg_particle_attach_l` |
| `slot_nodes` (scene `SpineSlotNode`) | **1** | slot `shadow` |
| `markers` | **2** | `IntentPos`, `CenterPos` |
| `sprite_layers` (`Sprite2D`) | **0** | none — nothing in this body is a flat sprite |
| `driver_scripts` | **2** | `NCreatureVisuals` (contract-mandated, on the root) + `NRegentVfx` (body-specific) |
| `ext_resources` / `sub_resources` / `load_steps` | 6 / 29 / 36 | header + blocks |

**Honesty rule (schema §C).** The four bone names and the one slot name above
are *scene-side* facts and are verified. The skeleton's **internal** bone and
slot counts are **UNVERIFIED**: no `.skel` parser was written. What was done is
a length-prefixed byte-string scan of `regent.skel`, which finds all five names
present (`shadow` at byte offsets 989 / 5860 / 7063; the four `*_particle_attach`
bones at 6030, 6100, 6170, 6345) — enough to say the scene's references are not
dangling, not enough to say how many bones the rig has.

**Scene-size rank.** Of the 127 `res://scenes/creature_visuals/*.tscn` entries
in the pack, `regent.tscn` is **third-largest** overall (behind
`test_subject.tscn` 139,319 B and `knowledge_demon.tscn` 83,838 B) and **the
largest player body by a wide margin**: 3.9× `necrobinder.tscn` (19,435 B),
28× `ironclad.tscn` (2,701 B), 66× `silent.tscn` (1,141 B), 66× `defect.tscn`
(1,149 B). Necrobinder is the intermediate rung between Ironclad and Regent;
it is **named here and deliberately not profiled** (schema §5.2).

But see §J before reading anything into the byte size: **79.3 % of this file is
one baked lookup texture**, not rig structure.

---

## D. Animation / state names

### D.0 `SCHEMA CORRECTION` — the player default is not the seven-trigger shape

Schema §1.2 lists seven canonical `CreatureAnimator` triggers: `Idle`,
`Attack`, `PowerUp`, `Cast`, `Dead`, `Hit`, `Revive`. Those seven **are** the
`const` names on the class (`CreatureAnimator.cs:11-23`). But the **player
default animator** registers six of them and one that is not on that list:

`CharacterModel.GenerateAnimator` (`sts2src/MegaCrit.Sts2.Core.Models/CharacterModel.cs:222-243`)
builds six states and registers seven anyState triggers — `Idle`, `Dead`,
`Hit`, `Attack`, `Cast`, `PowerUp`, **`Relaxed`** — and registers **no
`Revive`**. `Relaxed` has its own protected const,
`CharacterModel.cs:23: protected const string _relaxedTrigger = "Relaxed";`.
All five shipped player classes register it (`Defect.cs:118`,
`Ironclad.cs:116`, `Necrobinder.cs:119`, `Regent.cs:118`, `Silent.cs:116`).

So the player grammar's floor is **`idle_loop` / `cast` / `attack` / `hurt` /
`die` / `relaxed_loop`, seven triggers, no `Revive`** — and Regent's override
adds exactly **one state and one trigger** on top of that floor. This is the
sharpest version of the point the schema wanted from this body: *on the player
side, complexity lives in the scene, not in the state machine.* Regent's scene
is 28× Ironclad's; Regent's animator is Ironclad's plus one row.

### D.1 Referenced states — complete and verified

Every `AnimState` constructed in `Regent.GenerateAnimator`
(`sts2src/MegaCrit.Sts2.Core.Models.Characters/Regent.cs:97-121`):

| `AnimState` id | looping | reached by trigger | branch condition | `NextState` |
|---|---|---|---|---|
| `idle_loop` | **yes** | anyState `Idle` (`:112`) | none | — |
| `cast` | no | anyState `Cast` (`:116`) **and** anyState `PowerUp` (`:119`) | none | `idle_loop` (`:106`) |
| `attack` | no | anyState `Attack` (`:115`) | none | `idle_loop` (`:107`) |
| `hurt` | no | anyState `Hit` (`:114`) | none | `idle_loop` (`:108`) |
| `die` | no | anyState `Dead` (`:113`) | none | — |
| `attack_sovereign` | no | anyState **`sovereignBladeTrigger`** (`:117`) | none | `idle_loop` (`:109`) |
| `relaxed_loop` | **yes** | anyState `Relaxed` (`:118`) | none | — |

Seven states, eight anyState registrations (because `cast` is registered
twice), **zero conditional branches**, **zero `BoundsContainer` settings**.
The initial state passed to the `CreatureAnimator` constructor is `idle_loop`
(`:111`).

**One dead branch.** `Regent.cs:110` calls
`animState6.AddBranch("Idle", animState)` — a per-state branch on
`relaxed_loop`. It is **unreachable**: `CreatureAnimator.SetTrigger` consults
`_anyState.CallTrigger(trigger)` first and only falls through to
`_currentState.CallTrigger(trigger)` when the anyState returns null
(`CreatureAnimator.cs:67-78`), and the unconditional
`AddAnyState("Idle", idle_loop)` at `:112` always returns non-null.
`AnimState.CallTrigger` has exactly two call sites, both inside `SetTrigger`
(`CreatureAnimator.cs:69`, `:72`), so there is no other route in. The same dead
branch is present in the base player animator (`CharacterModel.cs:233`) and is
therefore a **house pattern, not a Regent bug** — every player body carries it.
Cosmetic today; it matters only as evidence that per-state branching is unused
on the player side.

### D.2 Skeleton-resident animations

**Verified without a parser**, per schema §D:

| source | names |
|---|---|
| `preview_animation` in `regent.tscn:247` | `idle_loop` |
| `preview_animation` on both weapon sprites (`:264`, `:274`) | `"-- Empty --"` — i.e. none |
| every `from`/`to` in `regent_skel_data.tres:6-21` | `cast`, `hurt`, `idle_loop`, `die` |
| `regent_weapon_skel_data.tres` mix table | **none — the resource has no `animation_mixes` at all** (`:6-8`) |
| animation names set in code on the weapon skeletons (`NRegentVfx.cs:257`, `:262`) | `attack`, `attack2` |
| `MonsterModel::GetBestiaryMoves` probes | **N/A** — bestiary probing is monster-only; a player body has no such source |

**`UNVERIFIED` raw scan of `regent.skel`** (277,959 B, extracted read-only;
length-prefixed byte-string scan, not a parse): exactly **seven** names in the
animation region —

`attack` (offset 69509), `attack_sovereign` (83537), `cast` (102112),
`die` (116197), `hurt` (147047), `idle_loop` (161563), `relaxed_loop` (237804)

— in alphabetical order, each with a correct Spine length-prefix byte.

**`UNVERIFIED` raw scan of `regent_weapon.skel`** (9,737 B): exactly **two**
animation names — `attack` (2094) and `attack2` (5915).

### D.3 Orphans, both directions

**Animation layer: none, in either direction.** The seven scanned skeleton
names and the seven registered `AnimState` ids are the same seven strings.
This is worth stating plainly because it is *not* the norm — the schema's
worked example is Ironclad's `weak_loop`, a skeleton string no code plays. On
Regent the body skeleton and the animator agree exactly. Likewise the weapon
skeleton's two animations are exactly the two `NRegentVfx.Attack()` sets.

**Trigger layer: one orphan, and it is a big one.**
`relaxed_loop` is registered by every player class and present in Regent's
skeleton, but the string `"Relaxed"` **is never passed to `SetTrigger` or
`SetAnimationTrigger` anywhere in the decompile**. Its own const,
`CharacterModel.cs:23`, has **no reader**. Search boundary: `grep` for
`"Relaxed"`, `_relaxedTrigger`, and `SetAnimationTrigger` across all 3,425
decompiled `.cs` files under `sts2src/` — the only hits are the five
`AddAnyState` registrations and the const declaration itself. So there is a
shipped, authored, packed idle-variant animation on all five player bodies that
nothing in this assembly plays. Whether something outside `SlayTheSpire2.dll`
(a scene script in the pack, a Godot signal, an editor tool) fires it is
**UNKNOWN — not searched**.

**Event layer: three declared-but-unhandled names.** Both skeletons carry an
identical nine-entry event-name table (body offsets 69316–69489; weapon offsets
1901–2074): `attack1`, `attack2`, `attack_end`, `attack_test`,
`death_particles_end`, `death_particles_start`, `death_particles_start2`,
`explode_dead`, `explode_end`. `NRegentVfx.OnAnimationEvent` handles **six** of
them (`NRegentVfx.cs:198-218`). Unhandled by Regent's driver: **`attack2`,
`attack_end`, `attack_test`**. `attack_end` is a real, live event name
elsewhere in the game (`NLivingGasVfx.cs:208`, `NQueenVfx.cs:88`);
`attack_test` is handled nowhere in the assembly. Whether any of the three is
actually *keyed on a Regent timeline* — as opposed to merely present in the
export's shared name table — is **UNVERIFIED**: the string table lists names,
not placements, and no timeline was parsed. The identical table in both
skeletons is consistent with one Spine project exporting both, but that is an
inference, not a fact.

---

## E. Durations and transitions

### E.1 From `regent_skel_data.tres` (1,059 B packed)

`default_mix = 0.05` (`:26`), the house default. Four explicit
`SpineAnimationMix` rows:

| from → to | `mix` | reading |
|---|---|---|
| `cast` → `hurt` | *(no `mix =` line)* = **0** | instant cut — getting hit mid-cast snaps |
| `hurt` → `hurt` | *(none)* = **0** | instant cut — re-hits re-snap, no blend smear |
| `idle_loop` → `hurt` | **0.02** | the only blended entry, and it is 2.5× tighter than the default |
| `hurt` → `die` | *(none)* = **0** | instant cut into death |

The authoring signal is legible and matches Mawler's (schema §5.3): **every
path *into* `hurt` or `die` is tuned tighter than the default, and three of the
four are hard cuts.** Everything else in the body — `idle_loop → attack`,
`attack → idle_loop`, `idle_loop → attack_sovereign`, `→ relaxed_loop`, and so
on — silently takes the 0.05 default.

### E.2 From `regent_weapon_skel_data.tres` (474 B packed)

`[resource]` sets only `atlas_res` and `skeleton_file_res` (`:6-8`). There is
**no `default_mix` line and no `animation_mixes` array**. The effective default
mix for the weapon skeletons is therefore whatever
`SpineSkeletonDataResource` initialises the property to, which the `.tres` does
not record — **UNKNOWN**; it would be settled by reading the property's default
in the spine-godot extension, which was not done. Practically this may not
matter: the weapon skeletons only ever play a single non-looping clip
(`attack` or `attack2`) triggered from an event, with nothing to blend from.

### E.3 From code

**`NextState` chains** (all one hop, all to `idle_loop`): `cast → idle_loop`,
`attack → idle_loop`, `hurt → idle_loop`, `attack_sovereign → idle_loop`
(`Regent.cs:106-109`). `die` and `relaxed_loop` terminate. Queued follow-ons
are added on track 0 via `CreatureAnimator.AddNextState`
(`CreatureAnimator.cs:114-132`), which recurses — irrelevant here, since no
chain is longer than one.

**`AddBranch`:** one, and it is dead (§D.1).

**Idle desync applies in full.** `idle_loop` is looping, so it gets a random
time-scale in [0.9, 1.1] and a phase offset of ±0.1 s
(`CreatureAnimator.cs:169-174`); and because Regent's *initial* state id is
literally `"idle_loop"`, the constructor's extra random-start branch fires too
(`CreatureAnimator.cs:44-59`) — the track time is seeded anywhere in the loop
and the skeleton is applied once immediately. Two Regents on screen (co-op)
never breathe in lockstep.

**Clip durations are UNKNOWN tonight** and are not estimated. They live in the
binary `.skel`; the runtime reads them through
`MegaTrackEntry::GetAnimationEnd` (used at `CreatureAnimator.cs:52`, `:172`)
and `GetCurrentAnimationDuration` (`NCreature.cs:873-876`).

**Code-side delays, which are NOT clip durations** and must not be confused with
them:

| constant | value | source |
|---|---|---|
| `AttackAnimDelay` | 0.15 s | `Regent.cs:60` |
| `CastAnimDelay` | 0.25 s | `Regent.cs:62` |
| `PowerUpAnimDelay` | = `CastAnimDelay` = 0.25 s | `CharacterModel.cs:196` |
| `sovereignBladeAnimDelay` | 0.25 s | `Regent.cs:22` (const; the card inlines the same literal, `SovereignBlade.cs:126`) |

These are what `CreatureCmd.TriggerAnim` waits on:
`await Cmd.CustomScaledWait(Mathf.Min(waitTime * 0.5f, 0.25f), waitTime)`
(`sts2src/MegaCrit.Sts2.Core.Commands/CreatureCmd.cs:947`). The game therefore
paces combat on **authored constants, not on animation length** — the only
place a real clip length is read back is death (§F).

---

## F. Intent / attack / hit / death tells

| tell | trigger name | state played | who fires it | blocking? | co-op visible? |
|---|---|---|---|---|---|
| idle | `Idle` | `idle_loop` | initial state (`Regent.cs:111` → `CreatureAnimator.cs:43`); also `NCreature.ImmediatelySetIdle` (`NCreature.cs:983-991`) | no | yes |
| attack | `Attack` | `attack` | `CreatureCmd.TriggerAnim` → `SetAnimationTrigger` (`CreatureCmd.cs:946`), reached from attack commands' `.WithAttackerAnim` | **yes** — caller awaits `:947` for `AttackAnimDelay` 0.15 s | yes |
| cast | `Cast` | `cast` | same | **yes** — 0.25 s | yes |
| power-up | `PowerUp` | `cast` *(shared state)* | same | **yes** — 0.25 s | yes |
| **sovereign blade** | **`sovereignBladeTrigger`** | `attack_sovereign` | `SovereignBlade.OnPlay` → `.WithAttackerAnim(animName, delay)` (`sts2src/MegaCrit.Sts2.Core.Models.Cards/SovereignBlade.cs:125-128`) | **yes** — 0.25 s | yes |
| weapon swing | *(Spine event `attack1`)* | weapon skeleton `attack` **or** `attack2`, alternating | `NRegentVfx.OnAnimationEvent` `:215-217` → `Attack()` `:253-265` | no | yes |
| hit | `Hit` | `hurt` | `NCreature.SetAnimationTrigger` (`NCreature.cs:868-870`) — `_spineAnimator?.SetTrigger(...)`, a guaranteed no-op without Spine; also fired directly by `DoomPower.cs:125` | no | yes |
| death | `Dead` | `die` | `NCreature.StartDeathAnim` `:944` (and `:517` for a body spawned already dead) | **yes** — the method's return value is the death length the caller waits on | yes |
| death VFX | *(Spine events `death_particles_start` / `…start2` / `…end`, `explode_dead`, `explode_end`)* | — | `NRegentVfx.cs:200-214` | no | yes |
| **revive** | `Revive` | **none — not registered** | `NCreature.StartReviveAnim` `:957-967` | no | yes |
| relaxed idle | `Relaxed` | `relaxed_loop` | **no firing site found** (§D.3) | — | — |
| bounds swap | — | **none** — no `AnimState` on this body sets `BoundsContainer` | — | — | — |

**Intents are not animation states.** They are `NIntent` nodes positioned from
`%IntentPos` via `NCreature.UpdateBounds` (`NCreature.cs:590-603`), and they are
frozen at the top of `StartDeathAnim` (`:923-926`). Regent's `%IntentPos` sits
at `(24, −414)`, 79 px above the top of its own `Bounds` rect.

### F.1 Death length — where the number comes from

`NCreature.StartDeathAnim` (`NCreature.cs:916-955`):

- Everything interesting is inside `if (_spineAnimator != null)` (`:933`).
- Player death SFX: `SfxCmd.PlayDeath(Entity.Player)` at **`:942`**, i.e. inside
  that guard, resolving to `player.Character.DeathSfx` (`SfxCmd.cs:94-100`) =
  `event:/sfx/characters/regent/regent_die` (`CharacterModel.cs:206`).
- `SetAnimationTrigger("Dead")` `:944`, then `a = GetCurrentAnimationLength()`
  `:945` — **the length comes from the animation**, via
  `SpineAnimation.GetCurrentAnimationDuration()` (`:873-876`).
- Return is `Mathf.Min(a, 30f)` `:954`.
- `DeathAnimLengthOverride` is checked at `:949-953` **on `Entity.Monster`
  only**.

So for this body: **death length is read from the clip, capped at 30 s, and
there is no override.** `AnimDie` then waits
`Math.Min(GetCurrentAnimationTimeRemaining() + 0.5f, 20f)` (`:1006-1009`) before
any removal.

### F.2 Revive — the one genuinely graceful fallback in the whole body

Regent registers no `Revive` anyState, so `_spineAnimator.HasTrigger("Revive")`
is false (`CreatureAnimator.cs:80-83` → `AnimState.HasTrigger`), and
`StartReviveAnim` takes its `else if (Entity.IsPlayer)` branch to
`AnimTempRevive()` (`NCreature.cs:957-967`). That method is
**pure Godot `Tween`, no Spine at all** (`:975-982`): fade `modulate:a` to 0 over
0.2 s, a `TweenCallback` that snaps the animator to `Idle` and fast-forwards the
track to its end with mix duration 0, then fade back up over 0.2 s.

This is the base game using a tween as a first-class animation substitute on a
shipped player body, and it is directly relevant to the joined matrix's
"particles / tweens" column.

### F.3 Co-op

The same scene and the same animator are built for a remote player's creature
node — the `HasSpineAnimation` branch at `NCreature.cs:503-513` does not consult
`_isRemotePlayerOrPet`. What differs is presentation chrome:
`_isRemotePlayerOrPet` (computed `:491-493`) hides the state display
immediately (`:494-497`) and suppresses the revive UI re-enable (`:968-971`).
Whether the *trigger* itself is replicated over the wire is **UNKNOWN** — not
traced tonight.

### F.4 `SCHEMA CORRECTION` — a bespoke trigger buys the animation and loses the sound

Schema §1.3 says player attack/cast/power-up audio is not gated on Spine,
because `CreatureCmd.TriggerAnim` plays the SFX before calling
`SetAnimationTrigger`. True — but the `switch` matches **only the three literal
strings** `"Attack"`, `"Cast"`, `"PowerUp"` (`CreatureCmd.cs:933-944`).
`"sovereignBladeTrigger"` matches none of them, so Regent's signature tell
receives **no character-derived SFX from `TriggerAnim` at all**. The card
supplies its own, hardcoded:
`.WithAttackerFx(null, "event:/sfx/characters/regent/regent_sovereign_blade")`
(`SovereignBlade.cs:129`).

Sharpened rule for any body with a bespoke trigger, ours included: **the trigger
gets you the animation; the sound is now the card's problem.** And note the
consequence in the shipped code — that FMOD path is hardcoded to `regent`, so a
non-Regent wielder of the card plays a Regent sound over their own `Cast`
animation (`SovereignBlade.cs:125-129`). Whether that is intended is a design
question and is **not ruled here**.

---

## G. VFX and audio hooks

### G.1 Particle emitters (6 GPU, 0 CPU)

| node | amount | lifetime | one-shot? | texture | material | process material |
|---|---|---|---|---|---|---|
| `Visuals/Explosion` | **800** | 2.5 | one-shot (`explosiveness = 1.0`) | `regent_sparkle.png` | shared additive | `PPM_siu7b` — the one with a baked emission-point texture, `emission_shape = 4`, `emission_point_count = 977` |
| `SpineArmBone/Particles` | 80 | 2.0 | burst via `Restart()` | same | shared additive | `PPM_t61rr` |
| `SpineChestBone/Particles` | 200 | 2.0 | burst via `Restart()` | same | shared additive | `PPM_m5irg` |
| `SpineChestBone/ParticlesBack` | 140 | 1.5 | burst via `Restart()` | same | shared additive | `PPM_f830s` |
| `SpineLegBoneL/Particles` | 30 | 1.25 | burst via `Restart()` | same | shared additive | `PPM_7ixmg` |
| `SpineLegBone/Particles` | 80 | 2.0 | burst via `Restart()` | same | shared additive | `PPM_4wq27` |

All six ship `emitting = false` in the scene **and** are re-asserted false in
`NRegentVfx._Ready` (`:188-193`) — belt and braces, because a `.tscn` edit that
flipped one on would otherwise leak particles from frame one. All six carry
`visibility_rect = Rect2(-1000, -1000, 2000, 2000)`, i.e. a manual culling box
2000 px on a side; five of the six also pin `fixed_fps = 60` and
`randomness = 0.35`.

### G.2 Attachment points

| scene node | Spine name | kind | present in `regent.skel` string table? |
|---|---|---|---|
| `Visuals/Weapons` | `shadow` | **slot** | yes (offsets 989 / 5860 / 7063) — `UNVERIFIED` scan |
| `Visuals/SpineArmBone` | `arm_particle_attach` | bone | yes (6100) |
| `Visuals/SpineChestBone` | `chest_particle_attach` | bone | yes (6170) |
| `Visuals/SpineLegBone` | `leg_particle_attach` | bone | yes (6030) |
| `Visuals/SpineLegBoneL` | `leg_particle_attach_l` | bone | yes (6345) |

The four bone names are *purpose-named for this exact use* —
`*_particle_attach` bones exist in the rig for no reason except to carry
emitters. That is the authoring convention this body exists to demonstrate:
**the rig is co-designed with the scene**, not handed over and decorated
afterwards.

### G.3 The driver: `NRegentVfx`

`sts2src/MegaCrit.Sts2.Core.Nodes.Vfx/NRegentVfx.cs`. It attaches a
`MegaSprite` to its **parent** (`:168-171` — the parent is `%Visuals`, not the
scene root) and subscribes to two spine signals: `animation_event` and
`animation_started`.

| Spine event | handler | effect |
|---|---|---|
| `death_particles_start` | `TurnOnDying` `:221-226` | `Restart()` on arm + both legs |
| `death_particles_start2` | `TurnOnDying2` `:228-232` | `Restart()` on chest front + chest back |
| `death_particles_end` | `TurnOffDying` `:234-241` | all five death emitters `Emitting = false` |
| `explode_dead` | `Explode` `:243-246` | `Restart()` on `Explosion` |
| `explode_end` | `DisableExplode` `:248-251` | `Explosion.Emitting = false` |
| `attack1` | `Attack` `:253-265` | alternates: weapon 1 plays `attack`, next time weapon 2 plays `attack2` (`_curWeapon` toggles) |

Plus a **safety net worth copying in principle**: `OnAnimationStart`
(`:271-278`) — on *any* animation start whose current name is not `"die"`, call
`DisableExplode()` and `TurnOffDying()`. Its own comment says why: "We have to
do this if the animation that is supposed to turn off the vfx is interrupted
early." That is the base game admitting, in a shipped comment, that
event-driven VFX teardown is not reliable under interruption, and papering it
over with a per-animation-start reset.

**Three dead fields.** `_attackParticlesSmall`, `_attackParticlesSmall2`,
`_attackParticlesLarge` are declared as `GpuParticles2D` (`NRegentVfx.cs:150-154`),
are **never assigned** in `_Ready` (`:166-194`), and are **never read** by any
method. They survive only in the generated Godot property bridge
(`:450-464`, `:512-526`, `:555-557`, `:574-576`, `:610-621`). There are no
matching scene nodes. This is almost certainly a removed attack-VFX feature
whose fields were left behind — harmless, but it means "count the fields" is not
a way to count a body's emitters.

### G.4 Audio

| surface | value | source | notes |
|---|---|---|---|
| `AttackSfx` | `event:/sfx/characters/regent/regent_attack` | `CharacterModel.cs:200` | **non-virtual**, derived from the character id |
| `CastSfx` | `event:/sfx/characters/regent/regent_cast` | `:202` | non-virtual |
| `PowerUpSfx` | = `CastSfx` | `:204` | non-virtual |
| `DeathSfx` | `event:/sfx/characters/regent/regent_die` | `:206` | non-virtual; played only inside the Spine guard (§F.1) |
| `CharacterSelectSfx` | `…/regent_select` | `:198` | **virtual**, not overridden |
| `CharacterTransitionSfx` | **`event:/sfx/ui/wipe_ironclad`** | **`Regent.cs:76`** | **virtual, and Regent overrides it to reuse Ironclad's wipe.** A shipped, first-party example of cross-character audio reuse |
| sovereign blade | `event:/sfx/characters/regent/regent_sovereign_blade` | `SovereignBlade.cs:129` | supplied by the card, not the trigger switch (§F.4) |

Where each is played from: `Attack`/`Cast`/`PowerUp` in
`CreatureCmd.TriggerAnim`'s switch (`CreatureCmd.cs:933-944`), **before**
`SetAnimationTrigger`; death in `StartDeathAnim` (`NCreature.cs:940-943`) via
`SfxCmd.PlayDeath(Player)` (`SfxCmd.cs:94-100`), **inside** the
`_spineAnimator != null` guard. There is no `HurtSfx` / `TakeDamageSfx` on the
player side — those are `MonsterModel` surfaces (schema §G).

The audio runtime is FMOD: `fmod.dll`, `fmodstudio.dll` and
`libGodotFmod.windows.template_release.x86_64.dll` ship in the game directory.

**S19 join key = the trigger name**, not the animation name. For this body the
keys are: `Idle`, `Attack`, `Cast`, `PowerUp`, `Dead`, `Hit`, `Revive`
(unregistered but fired at the body), `Relaxed` (registered but never fired),
`sovereignBladeTrigger` — plus the six handled Spine event names.

---

## H. Fallback behaviour

### H.1 `SCHEMA CORRECTION` — the player side has no `fallback.tscn`

Schema §1.4 describes `MonsterModel::CreateVisuals` wrapping the scene load in
`try/catch` and instantiating `res://scenes/creature_visuals/fallback.tscn` on
any exception. Verified: `MonsterModel.cs:420-431` (try/catch, `Log.Error`,
`SentryService.CaptureException`) → `CreateFallbackVisuals` `:434-437` →
`_fallbackVisualsPath` `:171`.

**`CharacterModel::CreateVisuals` has neither.** It is three lines, no guard:

```
public NCreatureVisuals CreateVisuals()
{
    return PreloadManager.Cache.GetScene(VisualsPath).Instantiate<NCreatureVisuals>(PackedScene.GenEditState.Disabled);
}
```
— `sts2src/MegaCrit.Sts2.Core.Models/CharacterModel.cs:212-215`

A broken monster body becomes a placeholder. **A broken player body throws.**
That asymmetry is a real, cited surface for a visual-QA gate, and it lands
squarely on us: our three roster characters are player bodies. (Our own mod
does not go through this method — BaseLib routes `CreateCustomVisuals()`
instead, `klee-mod/KleeCode/Klee.cs:233-256` — which is itself a fact worth
carrying into Lane C, not a reassurance, because the BaseLib path's own failure
behaviour was not read tonight.)

### H.2 Failure table

| case | severity | what actually happens |
|---|---|---|
| missing scene / load throws | **HARD, unguarded** | `CharacterModel.cs:212-215` — exception propagates. No fallback scene on the player side (§H.1) |
| missing `%Visuals` / `%Bounds` / `%IntentPos` / `%CenterPos` | **HARD** | `GetNode<T>` throws in `NCreatureVisuals._Ready` (`:219-223`) |
| missing any of `NRegentVfx`'s eight node paths | **HARD** | `GetNode<T>` throws in `NRegentVfx._Ready` (`:172-179`). None is optional; none uses `GetNodeOrNull` |
| skeleton data missing or fails to load | **SOFT** | `NCreatureVisuals._Ready` `:229-233`: `GD.PushWarning("Spine skeleton data failed to load for {Name}, disabling spine animation.")` and `SpineBody = null`. Then `HasSpineAnimation` is false (`:191`), `NCreature` never builds the animator (`:503`), every `SetAnimationTrigger` is a no-op (`:868-870`), **no death SFX and death length 0f** (§F.1), and the body stands frozen in its `preview` pose |
| missing **animation name** | **SOFT / SILENT** | `CreatureAnimator.SetNextState` `:88-92` logs `could not find '<id>' animation on '<node>'` and returns; queued variant `:116-120`. The guard is `MegaSprite.HasAnimation` → `GetSkeleton()?.GetData().HasAnimation(id) ?? false` (`MegaSprite.cs:128-131`). **The body simply stops where it was.** This is the single most important failure for a QA gate to catch, and this body has seven names to get wrong (plus two on the weapon skeletons) |
| missing `.skel` / atlas | **UNKNOWN as a distinct case** | Not tested. It plausibly lands in the "skeleton data failed to load" soft path above via the `.tres`, but that was not verified |
| phobia mode with no `%PhobiaModeVisuals` | **SOFT, and inert** | `_phobiaModeBody` is null (`:220`); `UpdatePhobiaMode` `:249-264` skips the body swap; `GetCurrentBody()` `:207-215` always returns `_body`. `OnPhobiaModeToggled` takes a `MonsterModel?` and is called with `Entity.Monster` (`NCreature.cs:583`), which is null for a player — **so a player body is never told about phobia mode at all** |
| skin not found | **N/A on this body** | `SetUpSkin(MonsterModel)` (`NCreatureVisuals.cs:266-276`) is monster-only and is called only in the monster branch (`NCreature.cs:512`). **Players get no skin setup.** NON-FINDING for a player skin path |
| missing FMOD event | **UNKNOWN** | Not read tonight |

---

## I. Authoring dependency

### I.1 What a human needs to make this body as shipped

| layer | artefact | consumed by |
|---|---|---|
| skeleton (body) | `regent.skel` (binary Spine) | importer **`spine.skel`** → `SpineSkeletonFileResource` |
| atlas (body) | `regent.atlas` + `regent.png` | importer **`spine.atlas`** → `SpineAtlasResource`; importer `texture` → `CompressedTexture2D` |
| skeleton (weapons) | `regent_weapon.skel` + `regent_weapon.atlas` + `regent_weapon.png` | same two importers |
| binding | `regent_skel_data.tres`, `regent_weapon_skel_data.tres` (`SpineSkeletonDataResource`) | the scene's `skeleton_data_res` |
| runtime | `libspine_godot.windows.template_release.x86_64.dll` | ships in the game directory (verified present) |
| scene | `regent.tscn` with `SpineSprite` / `SpineSlotNode` / `SpineBoneNode` node types | MegaDot 4.5.1 |

Importer names are read directly off the `.import` remaps extracted from the
pack (`animations/characters/regent/regent.skel.import` →
`importer="spine.skel"`, `type="SpineSkeletonFileResource"`; likewise
`regent.atlas.import` → `importer="spine.atlas"`).

Beyond a plain Spine body, **this one additionally requires**: a second Spine
project/export for the weapons; four bones authored purely as particle anchors;
a slot (`shadow`) used as a nesting parent for two whole sub-skeletons; and
**nine named timeline events** whose firing times are part of the art, not the
code.

### I.2 The licence question, stated and not answered

Spine is commercial software from Esoteric Software. **Per charter §4/S16, no
Spine purchase or other proprietary authoring dependency may be `PROPOSED` as
the answer**, and none is proposed here. Base Spine assets were inspected
read-only to understand the runtime contract, which is what this section
records.

Stated plainly, and as **description not proposal**, a no-paid-tools path would
have to reproduce five capabilities to match this body:

1. a **named bone hierarchy** a scene node can follow by name at runtime
   (`SpineBoneNode.bone_name`);
2. **named slots that accept nested children** and inherit their draw order
   (`SpineSlotNode` with two `SpineSprite`s under it, `show_behind_parent`);
3. **named timeline events with sub-clip timing**, delivered as a signal
   (`animation_event` → `NRegentVfx.OnAnimationEvent`);
4. **per-pair blend times between clips**, including an explicit zero
   (`SpineAnimationMix`);
5. **per-instance random loop phase and time-scale** (which the engine already
   does for us in `CreatureAnimator`, *provided* `HasSpineAnimation` — see the
   transfer questions).

Godot-native machinery that maps onto (1)–(4) exists — `Skeleton2D`/`Bone2D`
with `RemoteTransform2D`, `AnimationPlayer` method-call and signal tracks,
`AnimationNodeStateMachine` transition times — but **this file does not claim
those are sufficient**; establishing that is Lane A's bake-off, not S16's.

### I.3 Our own pipeline's cost baseline

The real comparison is not "Regent vs. a hypothetical" but "Regent vs. what
`klee-mod` already pays":

- text `.tscn` under `klee-mod/pck-src/`, copied verbatim into the pack
  (`klee-mod/pck-src/README.md:3-7`);
- **no scripts in scenes**, by standing rule — behaviour attaches from C# via
  BaseLib scene conversion plus Harmony routing
  (`klee-mod/pck-src/README.md:14-19`);
- every shipped scene needs a `resource=` line in the contract list at the
  bottom of `tools/build_pck.ps1`, and `validate.ps1 S6c` fails a deploy whose
  staged contract omits a source-referenced resource
  (`klee-mod/pck-src/README.md:20-23`);
- one scene path = one conversion target (`README.md:24-27`);
- the script-less root is converted to a real `NCreatureVisuals` by
  `NodeFactory<NCreatureVisuals>.CreateFromScene` inside `CreateCustomVisuals()`
  (`klee-mod/KleeCode/Klee.cs:233-243`), with two logged fallbacks — a bare
  texture, then null (`:245-256`);
- Klee's combat rig is five `Sprite2D` layers under `Visuals/Facing/Rig`, plus
  `Bounds` / `CenterPos` / `IntentPos`, an `AnimationPlayer` and an
  `AnimationTree` (`klee-mod/pck-src/klee/model/combat.tscn:393-449`), 14,109 B;
  Furina's equivalent is 15,359 B;
- triggers reach that tree through `CreatureAnimationRouter`
  (`klee-mod/KleeCode/Vfx/CreatureAnimationRouter.cs:45-54`, Harmony postfixes
  at `:84-103`), because `SetAnimationTrigger` is a no-op for spine-less bodies.

So the honest size comparison is **75,694 B of Spine-backed scene (plus 288 KB
of skeleton and 334 KB of texture) against 14,109 B of layered scene** — but
see §J: most of Regent's scene bytes are not structure.

---

## J. Runtime / performance observables

### J.1 Static, verified tonight

| artefact | packed bytes | note |
|---|---|---|
| `scenes/creature_visuals/regent.tscn` | **75,694** | 406 lines; 3rd largest of 127 creature scenes |
| `.godot/imported/regent.skel-*.spskel` | **277,959** | body skeleton |
| `.godot/imported/regent.png-*.ctex` | **323,430** | body atlas page |
| `.godot/imported/regent.atlas-*.spatlas` | 3,057 | **1 page, 952 × 523, scale 0.385, 53 regions** |
| `.godot/imported/regent_weapon.skel-*.spskel` | 9,737 | weapon skeleton |
| `.godot/imported/regent_weapon.png-*.ctex` | 10,572 | weapon atlas page |
| `.godot/imported/regent_weapon.atlas-*.spatlas` | 401 | **1 page, 231 × 134, scale 0.4, 3 regions** (`medium weapon`, `small big weapon`, `small weapon`) |
| `.godot/imported/regent_sparkle.png-*.ctex` | 2,088 | the only VFX texture; private |
| `themes/canvas_item_material_additive_shared.tres` | 102 | **shared** across bodies |
| `animations/characters/regent/regent_skel_data.tres` | 1,059 | |
| `animations/characters/regent/regent_weapon_skel_data.tres` | 474 | |
| **body total (scene + both skeletons + both atlas pages + sparkle)** | **≈ 703,000** | excludes card art, portraits, rest-site / merchant / character-select rigs |

**The headline number is not what it looks like.** Of the scene's 75,694 bytes,
**60,020 (79.3 %) are a single line** — line 14, the `PackedByteArray` of
`SubResource("Image_xptcu")`, a **2048 × 1 `RGFloat` image** that is wrapped as
`ImageTexture_mpn02` and used as `emission_point_texture` on **one** emitter,
`Explosion`, with `emission_point_count = 977` (`:40-46`, `:281-291`). It is a
baked list of 977 emission points — a *pre-computed silhouette* for the death
explosion. Strip it and the scene is ~15.7 kB, i.e. **roughly the same order as
our own Klee combat scene (14,109 B)**. The structural complexity of this body —
three skeletons, one slot nest, four bone anchors, six emitters — costs about
16 kB of text. The other 60 kB is one artist's baked point cloud.

Other static observables:

- **Max simultaneous particles if every emitter runs:** 800 + 200 + 140 + 80 +
  80 + 30 = **1,330**. In practice the five death emitters and the explosion are
  sequenced by events and are mutually exclusive with normal play.
- **Draw-affecting materials:** 2 distinct — the shared additive
  `CanvasItemMaterial` on all six emitters, and an empty
  `CanvasItemMaterial_53uu0` set as the `SpineSprite`'s `multiply_material`.
- **Textures:** 2 private atlas pages + 1 private VFX texture; 0 shared
  textures. The *material* is shared, the pixels are not.
- **Skeleton instances at runtime: 3** (one body + two weapons, the two weapons
  sharing one `SpineSkeletonDataResource` but each needing its own skeleton
  instance and animation state — `NRegentVfx.cs:178-187` builds a `MegaSprite`
  and waits for a `MegaAnimationState` per weapon).
- **The pack ships 1-byte stubs** at `src/Core/Nodes/Vfx/NRegentVfx.cs`,
  `src/Core/Models/Characters/Regent.cs`, etc. The code lives in
  `SlayTheSpire2.dll`; the `.cs` entries exist only so `ScriptPath` uids resolve.

### J.2 Dynamic — **UNKNOWN, capture pending**

Draw calls, per-frame cost with all six emitters live, skeleton update cost for
three skeletons, scene instantiation time, and the memory footprint of the
977-point emission texture are **not measured and not estimated**. The game was
not launched ([USER] is playtesting on `0.2-1155`; PREFLIGHT forbids it). See §K.

---

## K. Three annotated capture slots — **CAPTURE PENDING**

| field | `cap-1` |
|---|---|
| moment | idle, two Regents on screen where possible (co-op, or one Regent beside any other body) |
| status | **capture pending** |
| blocked_by | [USER] playtest — no game launch (PREFLIGHT) |
| how_to_capture | Attended session on an unlocked profile: character select → Regent → first combat. Still frame plus a 3 s clip of `idle_loop`. For the two-copy shot, a co-op seat with two Regents; failing that, two runs side by side is not equivalent and should be recorded as a substitute. |
| what_it_would_settle | Whether the `%Bounds` rect (230 × 335, `:389-396`) actually matches the silhouette; where `%IntentPos` `(24, −414)` sits relative to the head; whether the `CreatureAnimator` loop desync (§E.3) is visible at all on this body's idle; and whether any of the six emitters is visibly live during idle (the scene and `_Ready` both say no). |
| what_it_would_record when filled | `file:` + 3 annotation bullets |

| field | `cap-2` |
|---|---|
| moment | the signature tell — **Sovereign Blade** (`sovereignBladeTrigger` → `attack_sovereign`), with a plain `Attack` on the same enemy as the control |
| status | **capture pending** |
| blocked_by | [USER] playtest — no game launch (PREFLIGHT) |
| how_to_capture | Attended run as Regent. Sovereign Blades are generated by Forge (`ForgeCmd.cs:36-53`); the starting relic `DivineRight` (`Regent.cs:58`) is the likely first source — confirm in play, do not assume. Record trigger → return-to-idle, then repeat to see the weapon alternation. |
| what_it_would_settle | Whether the weapon skeletons visibly alternate (`attack` then `attack2`, `NRegentVfx.cs:253-265`) or read as one motion; whether `attack_sovereign` is longer than the 0.25 s the code waits (`SovereignBlade.cs:126`), i.e. whether combat resumes over a still-playing animation; whether `regent_sovereign_blade` is the **only** sound (§F.4 predicts no `AttackSfx`); and whether `attack1` fires once or twice per swing. |
| what_it_would_record when filled | `file:` + frame at contact + SFX cue time relative to the contact frame |

| field | `cap-3` |
|---|---|
| moment | hit → death: take a hit (`Hit` → `hurt`), then die (`Dead` → `die`) |
| status | **capture pending** |
| blocked_by | [USER] playtest — no game launch (PREFLIGHT) |
| how_to_capture | Attended run as Regent, deliberate loss in an early fight. Record continuously from the last hit through corpse removal / game-over. |
| what_it_would_settle | The **five-stage death VFX sequence** and its timing — `death_particles_start` (arm + both legs) → `death_particles_start2` (chest front + back) → `explode_dead` (the 800-particle, 977-point burst) → `explode_end` → `death_particles_end` (`NRegentVfx.cs:200-214`); whether the `die` clip length matches the wait computed at `NCreature.cs:945`/`:1006-1009`; whether the `hurt → die` instant cut (§E.1) reads as a snap; and whether `regent_die` plays. |
| what_it_would_record when filled | `file:` + 3 annotation bullets, incl. measured clip length to close the §E `UNKNOWN` |

**A capture-pending slot is a complete answer for tonight.** No frame was
described that was not seen.

---

## L. Closing sections

### L.1 UNKNOWN

| question | what would answer it |
|---|---|
| Clip durations for all seven body animations and both weapon animations | A `.skel` parser, or `cap-2` / `cap-3` timed against frame counts |
| The skeleton's internal bone and slot counts | A `.skel` parser. Tonight's byte-string scan proves the five referenced names exist, nothing more |
| Whether `attack2`, `attack_end`, `attack_test` are keyed on any Regent timeline, or are only names in a shared export table | A `.skel` parser reading event timelines, not the string table |
| The default mix the weapon skeletons actually use (`regent_weapon_skel_data.tres` writes none) | Reading `SpineSkeletonDataResource`'s property default in the spine-godot extension |
| Whether anything outside `SlayTheSpire2.dll` fires the `Relaxed` trigger | A scan of pack scene scripts / GDScript, and of BaseLib |
| Whether animation triggers replicate to remote seats in co-op, or each client derives them | Tracing the multiplayer command path; `_isRemotePlayerOrPet` (`NCreature.cs:491-493`) only gates chrome |
| What happens on a missing `.skel`/atlas as distinct from a failed `SpineSkeletonDataResource` | A deliberate breakage test in a scratch build — not tonight |
| What happens when an FMOD event path does not exist | S19 territory; not read |
| Every dynamic performance number | Attended capture (§K) plus a profiler run |
| The exact Regent unlock grant condition | Tracing `PendingCharacterUnlock` (`NCharacterSelectScreen.cs:592`) back to its writer |

### L.2 NON-FINDINGS

1. **No conditional branches on this body.** Searched every `AddBranch` /
   `AddAnyState` call in `Regent.cs:97-121`: zero `Func<bool>` conditions. The
   machinery exists (`AnimState.cs:54-82`) and Ceremonial Beast uses it
   (schema §5.4); the most complex *player* body does not.
2. **No `BoundsContainer` on this body.** No `AnimState` sets it, so
   `CreatureAnimator.BoundsUpdated` never fires for Regent and
   `UpdateBounds(string)` (`NCreature.cs:576-579`) is unreachable here. The
   silhouette never changes. Searched: all seven `AnimState` constructions.
3. **No `Revive` state.** Not registered (§D.1). Confirmed by the fallback it
   forces at `NCreature.cs:957-967`.
4. **No `stun`, `stun_loop`, `wake_up`, `revive` or `weak_loop` strings** in
   `regent.skel`. Searched by byte substring across the whole 277,959 B file.
5. **No CPU particles.** Zero `CPUParticles2D`. Searched: all 19 nodes.
6. **No `Sprite2D` layers.** Zero. Every visible pixel comes from a Spine
   skeleton or a particle system.
7. **No player skin or phobia path.** Both `SetupSkins` and
   `OnPhobiaModeToggled` are `MonsterModel` surfaces and are invoked only in the
   monster branch (`NCreature.cs:512`, `:583`). Searched: both call sites.
8. **No firing site for `Relaxed`.** Boundary: `grep` over all 3,425 `.cs`
   files under `sts2src/` for `"Relaxed"`, `_relaxedTrigger`, and
   `SetAnimationTrigger`. Only registrations and the const.
9. **No caller for `Regent.GetSovereignBladeAnimIfApplicable` /
   `GetSovereignBladeDelayIfApplicable`** (`Regent.cs:123-139`). The card
   inlines the same two ternaries instead (`SovereignBlade.cs:125-126`).
   Contrast: the equivalent `Ironclad.GetHeavyAnimIfApplicable` and
   `Necrobinder.GetSummonAnimIfApplicable` helpers **are** called, from a dozen
   cards each. Boundary: `grep` for `IfApplicable` across `sts2src/`. Dead code
   in the shipped game; noted because it is the pattern our own portable cards
   would want and it is worth knowing it exists in two flavours.

### L.3 Transfer questions

Numbered, against our BaseLib / Harmony path (schema §1.5). **Questions only.**

1. `CreatureAnimationRouter.TriggerToState` maps seven known triggers and
   **returns silently on any unknown one**
   (`klee-mod/KleeCode/Vfx/CreatureAnimationRouter.cs:70-73`). Regent's
   bespoke trigger is how the base game gives one card its own animation. If a
   Teyvat character ever wants a per-card tell, does that arrive as a new row in
   `TriggerToState`, as a scene-side convention, or not at all?
2. Our router folds `Cast` and `PowerUp` into `attack` and `Revive` into `idle`
   (`CreatureAnimationRouter.cs:45-54`). The base player floor keeps `cast`
   separate from `attack` and has **no** `Revive` at all, relying on the tween
   fallback `AnimTempRevive` instead (`NCreature.cs:975-982`). Is our `Revive →
   idle` mapping better or worse than the base game's tween, and is that a
   question anyone needs answered before a public release?
3. `relaxed_loop` is a shipped, authored second idle on all five base player
   bodies that nothing fires (§D.3). Is a second idle a thing our characters
   should have a slot for, given that nothing in the engine will ask for it?
4. Death is the sharpest asymmetry. For a spine-less player body,
   `StartDeathAnim` returns `0f` and plays **no death sound** (§F.1), and
   `DeathAnimLengthOverride` is monster-only so there is no escape hatch. Our
   mod patches the trigger side (`NCreature_StartDeathAnim_AnimationTreeRoute`,
   `CreatureAnimationRouter.cs:97-103`) but the returned **length** and the
   **SFX** are still inside the base guard. Is the missing player death sound a
   defect we already carry in play, and does the returned `0f` shorten anything
   visible?
5. `CharacterModel::CreateVisuals` has no try/catch and no fallback scene, where
   `MonsterModel` has both (§H.1). Our path goes through BaseLib's
   `CreateCustomVisuals()` instead. What does *that* path do on a bad scene, and
   should a visual-QA gate assert a fallback exists for player bodies?
6. Regent anchors emitters to rig bones by name and nests whole sub-skeletons in
   a named slot. Our layered rig has `Visuals/Facing/Rig` with five `Sprite2D`s
   and no bone concept at all. If a Teyvat character wants a weapon or companion
   that follows a moving hand, what is the seam — a `RemoteTransform2D` chain, a
   `Skeleton2D`, or an `AnimationPlayer` track per layer?
7. The base game's own driver admits event-driven VFX teardown is unreliable
   under interruption and adds a per-animation-start reset
   (`NRegentVfx.cs:267-278`). If our rigs ever drive VFX from
   `AnimationPlayer` method tracks, do we want the same reset by convention?
8. Loop desync (random time-scale and phase, `CreatureAnimator.cs:169-174`) is
   free for Spine bodies and **does not exist for ours**, because the whole
   `CreatureAnimator` is skipped when `HasSpineAnimation` is false. Two of our
   companions on screen would breathe in lockstep. Is that visible enough to
   care about, and is it the router's job or the scene's?
9. Regent's mix table tunes only the paths *into* `hurt` and `die`, and makes
   three of four instant (§E.1). Our `AnimationTree` transitions carry their own
   times. Is "hard-cut into hurt and death, blend everything else" a convention
   worth writing down, or a Regent-specific taste call?
10. 79 % of Regent's scene is a baked emission-point texture for one death
    burst (§J.1). If a Teyvat body ever wants a comparable death effect, does
    that data live in the scene, in a separate resource, or is a baked point
    cloud simply not something our pipeline should carry in a `.tscn`?

### L.4 What this does NOT establish

This file describes one shipped body as it exists in the pack and the
decompile. It does not say that Regent should be reskinned, remapped or copied,
does not recommend an animation approach for our characters, and does not rank
Spine against anything — the capability comparison is `s16-05`'s joined matrix
and the practical evidence is Lane A's bake-off. No animation was timed, no
frame was captured, no runtime cost was measured, and the game was not launched;
clip durations, skeleton bone counts and every dynamic number remain UNKNOWN and
are marked as such rather than estimated. Several statements about the skeleton
files rest on byte-string scans rather than a parser and are labelled
`UNVERIFIED` where they appear — a name present in a file is not proof of a
timeline that uses it. The three schema corrections (§D.0, §F.4, §H.1) are
readings of the decompiled code, not observed behaviour, and the two that
describe defect surfaces — the missing player-side fallback scene and the silent
player death — are reported as **candidates for triage**, not as confirmed
defects, because neither was reproduced in a running game.
