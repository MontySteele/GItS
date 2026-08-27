# S16 body — base / simple player character: **Ironclad**

> **This file decides nothing.** It is a research artifact from surplus-dispatch-3
> (charter §4/S16). Everything technical below is `PROPOSED` or plain description;
> taste, lore, art direction, rights, spend, scope and ship calls remain [USER]'s.
> No balance window was opened, no stamp moved, no id minted, no playtest
> interpreted, and **the game was never launched** — [USER] was playtesting mod
> `0.2-1155` throughout (PREFLIGHT).

**Filename note for the integrator.** The schema's §4 ownership map names this
file `s16-01-player-simple.md`. The dispatch assigned it as
`s16-body-base-simple-player-character.md`, which is the name used here. Same
body, same slot, one file — join it as the `player-simple` row.

**Written against** `s16-00-schema.md` sections A–L, in order.

---

## Corrections to the schema's shared grammar — read these first

The schema (§1) says a corpus file that **contradicts** the shared grammar has
found something and should say so loudly. Seven things. None of them changes the
choice of body; three of them change what a visual-QA gate would have to check.

| # | Schema says | Evidence says | Where |
|---|---|---|---|
| 1 | Ironclad is "the canonical **seven-state** player shape with exactly one bespoke trigger" | The **base** `CharacterModel.GenerateAnimator` builds **six** states and wires **seven** anyState triggers. Ironclad is base **+1 state** (`attack_heavy`) **+1 trigger** (`heavyAttack`) = **7 states / 8 triggers**. The "exactly one bespoke trigger" half is correct. | `sts2src/MegaCrit.Sts2.Core.Models/CharacterModel.cs:222-243`; `sts2src/MegaCrit.Sts2.Core.Models.Characters/Ironclad.cs:94-118` |
| 2 | "`CreatureAnimator` exposes seven canonical triggers … `Idle, Attack, PowerUp, Cast, Dead, Hit, Revive`" | True as a list of C# constants, but it is **not the player set**. **No player wires `Revive`** — the string does not appear anywhere in `Models.Characters/`. And **every player wires `Relaxed`**, which is a `CharacterModel` constant, not a `CreatureAnimator` one. The player-side seven are `Idle, Dead, Hit, Attack, Cast, PowerUp, Relaxed`. | `sts2src/MegaCrit.Sts2.Core.Animation/CreatureAnimator.cs:11-23`; `CharacterModel.cs:23`, `:241`; grep for `Revive` across `Models.Characters/` returns **zero** hits |
| 3 | — | **`Relaxed` is an orphan trigger.** It is wired by all five players and **fired by nobody**: the only `SetAnimationTrigger` call sites in the whole decompile pass `"Dead"`, `"Revive"`, `"Hit"`, or a caller-supplied name, and no caller ever supplies `"Relaxed"`. The `relaxed_loop` clip *is* used out of combat, but through a different door (`SetAnimation` / `PlayAnimation` directly), never through the combat animator. | Call sites: `CreatureCmd.cs:946`, `DoomPower.cs:125`, `NCreature.cs:517`, `:944`, `:962`. Out-of-combat users: `NMerchantCharacter.cs:49`, `NFakeMerchant.cs:303` |
| 4 | `silent.tscn` is "1,141 B, two `ext_resource`s, **four nodes**" | It is **five** `[node]` blocks (root + Visuals + Bounds + CenterPos + IntentPos). Bytes and ext_resources are right. | `pck:res://scenes/creature_visuals/silent.tscn`, 5 × `^\[node` |
| 5 | Silent is "the strict floor — Ironclad minus the slash slot and its driver" | True of the **scene**, false of the **animator**. Silent also adds one bespoke state + trigger (`shiv`), so its animator is base+1 exactly like Ironclad's. And Silent is not uniquely the floor: **Defect** (`defect.tscn`, 1,149 B, 5 nodes, 2 ext_resources) is the same shape. | `sts2src/MegaCrit.Sts2.Core.Models.Characters/Silent.cs:95-119`; `pck:res://scenes/creature_visuals/defect.tscn` |
| 6 | §1.1 node table lists what happens when a required node is missing | Add one row the table does not have: if the **Spine skeleton data itself fails to load**, `_Ready` pushes a warning and sets `SpineBody = null` — the body **silently downgrades to spine-less** rather than throwing. Everything gated on `HasSpineAnimation` then quietly stops. | `sts2src/MegaCrit.Sts2.Core.Nodes.Combat/NCreatureVisuals.cs:226-234` |
| 7 | §1.4 "`CreateVisuals` wraps the scene load in `try/catch` … instantiates `fallback.tscn`" | That is **`MonsterModel::CreateVisuals` only**. `CharacterModel::CreateVisuals` has **no try/catch and no fallback** — a player body that fails to load throws. `fallback.tscn` is an enemy safety net; players do not have one. | `MonsterModel.cs:420-437` vs `CharacterModel.cs:212-215` |

---

## A. Identity and provenance

| Field | Content |
|---|---|
| `body_id` | `ironclad` |
| `role` | `player-simple` |
| `class` | `MegaCrit.Sts2.Core.Models.Characters.Ironclad` (`sealed`, extends `CharacterModel`) — `sts2src/MegaCrit.Sts2.Core.Models.Characters/Ironclad.cs:18` |
| `scene` | `res://scenes/creature_visuals/ironclad.tscn` — **2,701 B** packed (pck directory row) |
| `reachability` | **Unlocked from a fresh install.** `UnlocksAfterRunAs => null`, with the decompiled remark "Ironclad starts out unlocked" (`Ironclad.cs:26-29`). Pick him on the character-select screen; the body is on screen for the whole of every combat. Starting HP 80, starting gold 99, 10-card starting deck, one starting relic (Burning Blood) (`Ironclad.cs:33`, `:35`, `:43-57`). **No capture requires a specific act, encounter, seed or unlock** — this is the most capturable body in the corpus. |
| `read_on` | 2026-08-26. StS2 **v0.107.1** (commit `59260271`, Steam buildid `23811903`, appid `2868840`, branch `public` — `docs/current/STATE.md:159-163`). PCK read read-only at `C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\SlayTheSpire2.pck`. Decompile: ILSpy 8.2 output at `…/scratchpad/sts2src/`. The game was **not** launched. |
| house relevance | This body is also the measurement anchor `ref_ironclad` / `real_ironclad` (`tier0/roster.py:194-195`), the `(ref_ironclad, starter)` scoring anchor normalized to exactly 3.0 on every axis (`docs/current/STATE.md:88-91`), and its 76-card pool is already extracted at `game_ref/ironclad_pool.yaml`. **The anchors have no art, no C# class and no visuals of their own** — the scene below is the *base game's* Ironclad, not something we ship. |

---

## B. Scene / resource topology

`res://scenes/creature_visuals/ironclad.tscn` — `format=3`, `load_steps=8`, 66 lines,
7 nodes, 6 `ext_resource`s, 1 `sub_resource`.

| # | path | type | unique name | purpose | depends_on |
|---|---|---|---|---|---|
| 1 | `.` (`Ironclad`) | `Node2D` | — (root) | Carries the `NCreatureVisuals` script; this is the object `CharacterModel::CreateVisuals` instantiates | `ext 1_v62mv` — `res://src/Core/Nodes/Combat/NCreatureVisuals.cs` |
| 2 | `Visuals` | **`SpineSprite`** | `%Visuals` | The body. `position = (5, -19)`, `scale = (0.28, 0.28)`, editor-locked | `ext 2_0jedi` — `ironclad_skel_data.tres` |
| 3 | `Visuals/SlashVfxSlot` | **`SpineSlotNode`** | — | Binds a Godot node to the Spine **slot `slash_mesh`**, so a shader material draws in that slot's z-order. `show_behind_parent = true`, `position = (1183.45, -1660.71)`, `scale = (9.459, 9.459)` — those are *skeleton-space* numbers, hence the large values against the 0.28 body scale | `sub ShaderMaterial_rq7c3` |
| 4 | `Visuals/NIroncladVfx` | `Node` | — | The driver script. Looked up by its **plain node name** by its sibling (see §G) | `ext 3_wdh0x` — `res://src/Core/Nodes/Vfx/NIroncladVfx.cs` |
| 5 | `Bounds` | `Control` | `%Bounds` | Hitbox / silhouette rect: `offset_left −121`, `offset_top −278`, `offset_right 121`, no `offset_bottom` (so 0) ⇒ **242 × 278 px** rising from the floor line. `mouse_filter = 2` (ignore) | — |
| 6 | `CenterPos` | `Marker2D` | `%CenterPos` | `VfxSpawnPosition` — where hit VFX spawn. `(4, −168)` | — |
| 7 | `IntentPos` | `Marker2D` | `%IntentPos` | Intent anchor, and the **`OrbPosition` fallback** because there is no `%OrbPos`. `(30, −310)` | — |

**`ext_resource` list**

| id | type | `res://` path | shared? |
|---|---|---|---|
| `1_v62mv` | Script | `src/Core/Nodes/Combat/NCreatureVisuals.cs` | **Shared by 123 of the 126 creature scenes** — the near-universal root script. The three that do not reference it are `battleworn_dummy.tscn`, `kaiser_crab_boss.tscn` and `kaiser_crab_boss_setup.tscn`, which is a boss-composition detail, not a player one |
| `2_0jedi` | `SpineSkeletonDataResource` | `animations/characters/ironclad/ironclad_skel_data.tres` | Private (1,979 B) |
| `3_rq7c3` | Shader | `images/vfx/slash_shader_flat.tres` | **Private to Ironclad.** Checked across all 126 `creature_visuals/*.tscn`: 1 user |
| `3_wdh0x` | Script | `src/Core/Nodes/Vfx/NIroncladVfx.cs` | **Private to Ironclad.** 1 user across all 126 |
| `4_x8wap` | `Texture2D` | `images/vfx/fire/basic_fire_noise.png` | **Shared — 7 creature scenes**: `ironclad`, `kin_priest`, `knowledge_demon`, `mecha_knight`, `necrobinder`, `osty`, `spectral_knight` |
| `6_g8ov4` | `Texture2D` | `images/vfx/characters/ironclad_slash_base.png` | Private |

**`sub_resource`:** one `ShaderMaterial` (lines 10-24) parameterising
`slash_shader_flat.tres` — a warm orange `Color(0.99, 0.343, 0.198, 1)`, a
`step` vector the driver animates, a shape mask (`ironclad_slash_base.png`) and
**two panning noise samplers that both point at the same shared texture**
(`basic_fire_noise.png`) at different scales and pan speeds. `opacity = 0.8`.

**Nodes the §1.1 contract does not require, and what breaks without them:**

- `SlashVfxSlot` — **not** contract, but it is a hard dependency of the driver.
  `NIroncladVfx._Ready` does `_parent.GetNode("SlashVfxSlot")` by **plain path,
  not unique name** (`NIroncladVfx.cs:92`). Rename or delete it and `_Ready`
  throws. The very next line dereferences the cast result without a null check
  (`_slashStepBase = (Vector2)_slashShaderMat.GetShaderParameter(_step)`,
  `:93`) even though the field is declared `ShaderMaterial?` — so swapping the
  slot's material for a non-shader material also throws. Both are `_Ready`-time,
  i.e. combat-entry-time, failures.
- `NIroncladVfx` — remove it and the slash trail simply never animates. No error;
  the shader sits at its authored `step`.
- **Absent by design:** `%PhobiaModeVisuals`, `%OrbPos`, `%TalkPos`. Phobia mode
  is a **total no-op** for any player (see §H); `%OrbPos` silently falls back to
  `%IntentPos` (`NCreatureVisuals.cs:224`); `%TalkPos` stays null (`:225`).

---

## C. Node / layer / bone counts

| metric | value | note |
|---|---|---|
| `nodes_total` | **7** | counted `^\[node` in the packed `.tscn` |
| `spine_sprites` | **1** | `%Visuals` |
| `particle_emitters` | **0 CPU / 0 GPU** | no `CPUParticles2D`, no `GPUParticles2D` anywhere in the file |
| `bone_nodes` (`SpineBoneNode`) | **0** | Ironclad anchors nothing to a bone |
| `slot_nodes` (`SpineSlotNode`) | **1** | `SlashVfxSlot` → Spine slot `slash_mesh` |
| `markers` | **2** | `CenterPos`, `IntentPos` |
| `sprite_layers` (`Sprite2D`) | **0** | this is the whole point of the contrast with our rig |
| `driver_scripts` | **1 private** (`NIroncladVfx`) **+ 1 shared** (`NCreatureVisuals` on the root) | |
| atlas pages | **4** — `ironclad.png`, `ironclad_2.png`, `ironclad_3.png`, `ironclad_4.png` | parsed from the packed `.spatlas` JSON |
| atlas regions (attachments) | **82** | same source |
| atlas page 1 size / scale | `1000 × 269`, `filter Linear,Linear`, `scale 0.32` | |

**Honesty rule (schema §C).** The numbers above are **scene- and atlas-level and
verified**. The skeleton's internal bone and slot counts are a *different* number
and are **`UNVERIFIED`** — I did not write a Spine binary parser. What the string
scan does show is that a `slash_mesh` slot and bones named `slash_root`,
`slash1`…`slash5` exist inside the skeleton at offsets 5742-7116, which is what
the `SpineSlotNode` binds to.

**Where Ironclad sits among the five shipped player bodies** (all packed sizes,
all five extracted and counted tonight):

| scene | bytes | nodes | ext | sub | `SpineSlotNode` |
|---|---|---|---|---|---|
| `silent.tscn` | 1,141 | 5 | 2 | 0 | 0 |
| `defect.tscn` | 1,149 | 5 | 2 | 0 | 0 |
| **`ironclad.tscn`** | **2,701** | **7** | **6** | **1** | **1** |
| `necrobinder.tscn` | 19,435 | 12 | 13 | 43 | 3 |
| `regent.tscn` | 75,694 | 19 | 6 | 29 | 1 |

Ironclad is the **third-smallest of five and the smallest that carries any VFX
affordance at all** — which is exactly the schema's stated reason for picking him.

---

## D. Animation / state names

### D.1 Referenced states — complete and verified

Built in `Ironclad::GenerateAnimator` (`Ironclad.cs:94-118`). Seven `AnimState`s,
eight `AddAnyState` triggers.

| `AnimState` id | looping | reached by trigger(s) | `NextState` | branch condition |
|---|---|---|---|---|
| `idle_loop` | **yes** | `Idle` (`:109`); also the initial state (`:108`) | — | none |
| `cast` | no | `Cast` (`:113`) **and** `PowerUp` (`:115`) — one clip serves both | → `idle_loop` (`:103`) | none |
| `attack` | no | `Attack` (`:112`) | → `idle_loop` (`:104`) | none |
| `hurt` | no | `Hit` (`:111`) | → `idle_loop` (`:105`) | none |
| `die` | no | `Dead` (`:110`) | — | none |
| `attack_heavy` | no | **`heavyAttack`** (`:114`) — bespoke | → `idle_loop` (`:106`) | none |
| `relaxed_loop` | **yes** | `Relaxed` (`:116`) — **never fired**, see correction 3 | — | carries its own `AddBranch("Idle", idle_loop)` (`:107`), also unreachable |

**No conditional branches anywhere.** Every `AddAnyState` / `AddBranch` on this
body passes `condition = null`. The `Func<bool>` machinery in `AnimState`
(`AnimState.cs:54-82`) — the thing that lets a boss pick between two death
animations — is **entirely unused by the simple player body**. That is the
cleanest single statement of what "simple" means here.

**Diff against the base default** (`CharacterModel.cs:222-243`): identical, plus
`attack_heavy` and its `heavyAttack` trigger. Nothing removed, nothing renamed.

### D.2 Skeleton-resident animations

Source: a raw-string scan of the packed
`res://.godot/imported/ironclad.skel-8e96930de153cfcb09ff2bbedd54ed5d.spskel`
(160,875 B), corroborated by the `.tscn`'s `preview_animation` and by every
`from`/`to` in the mix table.

Marked **`UNVERIFIED`** per schema §D because it is a scan, not a parse — but the
corroboration is unusually strong and worth stating: the eight names below appear
at **strictly ascending offsets**, in alphabetical order, immediately after the
skeleton's two event names, which is the exact shape of Spine's animation section.

| animation | scan offset | byte span to next | in the mix table? | played by code? |
|---|---|---|---|---|
| `attack` | 47,113 | 18,238 | yes | **yes** |
| `attack_heavy` | 65,351 | 27,712 | yes | **yes** — and it is `preview_animation` in the scene |
| `cast` | 93,063 | 11,162 | no (uses `default_mix`) | **yes** |
| `die` | 104,225 | 24,186 | yes | **yes** |
| `hurt` | 128,411 | 18,159 | yes | **yes** |
| `idle_loop` | 146,570 | 4,734 | yes | **yes** |
| `relaxed_loop` | 151,304 | 8,334 | no | wired but **never triggered** (correction 3) |
| `weak_loop` | 159,638 | 1,237 (to EOF) | no | **NO — orphan** |

Skeleton file header string: **`4.2.43`** at offset 9 (Spine 4.2 line).

**Byte span is size, not time.** It is a proxy for *timeline complexity*, nothing
else. Do not read it as duration. It is reported because it is the one thing that
distinguishes the two suspicious rows: `idle_loop` at 4,734 B is a short simple
loop, and **`weak_loop` at 1,237 B is by far the smallest animation in the file** —
consistent with an authored stub.

### D.3 Orphans, both directions

- **Skeleton → code:** `weak_loop` exists in the skeleton and the string
  `weak_loop` appears **nowhere** in the decompile (verified by grep over the full
  `sts2src` tree). The schema flagged this; it is confirmed, and the size datum
  above is new. There is a **Weak** power in the game, so the natural guess is an
  abandoned status-tell. That is a guess and is **not** a finding.
- **Code → skeleton:** **none.** All seven referenced `AnimState` ids appear in
  the scan. Ironclad has no state that would trip the §1.4 silent-freeze path.
  (Contrast §"Transfer questions" Q6, where a *public mod* does trip it.)

---

## E. Durations and transitions

`res://animations/characters/ironclad/ironclad_skel_data.tres` (1,979 B packed),
`default_mix = 0.05`, ten explicit `SpineAnimationMix` rows.

| # | from → to | mix (s) | reading |
|---|---|---|---|
| 1 | `idle_loop` → `attack` | **0.10** | slowest blend in the table — the wind-up is allowed to ease in |
| 2 | `attack` → `attack` | **0** (no `mix =` line) | **instant cut** — re-attacking snaps, no cross-fade mush |
| 3 | `hurt` → `hurt` | **0** | instant cut — multi-hit flinches read as separate hits |
| 4 | `hurt` → `die` | **0** | instant cut — the killing blow is not softened |
| 5 | `idle_loop` → `hurt` | **0.03** | almost instant, but not quite |
| 6 | `hurt` → `idle_loop` | **0.10** | slow recovery back to breathing |
| 7 | `idle_loop` → `attack_heavy` | **0.02** | heavy attacks start **5× faster** than normal attacks (row 1) |
| 8 | `attack_heavy` → `attack_heavy` | **0** | instant cut |
| 9 | `attack` → `attack_heavy` | **0** | instant cut |
| 10 | `attack_heavy` → `attack` | **0** | instant cut |

A row with no `mix =` line is **0**, i.e. a deliberate instant cut, not a missing
value (schema §E). **Six of ten rows are deliberate instant cuts, and all six are
attack-to-attack or damage-to-damage.** The three blends that exist are all
idle-adjacent. That is a legible authoring rule: *blend into and out of rest,
never between blows.*

**Everything not in the table takes `default_mix = 0.05`** — including every
transition involving `cast`, every `→ idle_loop` return except from `hurt`, and
`idle_loop → die`.

**Contrast with the floor.** `silent_skel_data.tres` has the same
`default_mix = 0.05` but only **four** rows (`hurt→hurt` 0, `hurt→die` 0,
`idle_loop→hurt` 0.02, `cast→idle_loop` 0.02). Ironclad's table is 2.5× richer,
and Silent's carries a `cast→idle_loop` row that Ironclad's does not. So "simple
player body" does **not** mean "fewer authored transitions than the floor" —
Ironclad has meaningfully more.

**`NextState` chains from code** (`Ironclad.cs:103-106`): `cast → idle_loop`,
`attack → idle_loop`, `hurt → idle_loop`, `attack_heavy → idle_loop`. Queued on
the same track by `CreatureAnimator::AddNextState`
(`CreatureAnimator.cs:114-132`). `die` has none — the body stays dead.

**Clip durations are `UNKNOWN` tonight.** They live in the binary `.skel`. The
runtime reads them via `MegaTrackEntry::GetAnimationEnd`
(`CreatureAnimator.cs:52`, `:172`; `NCreature.cs:519`, `:990`) and via
`SpineAnimation.GetCurrentAnimationDuration()` behind
`NCreature::GetCurrentAnimationLength` (`NCreature.cs:873-876`). Not estimated.
The byte spans in §D.2 are size, not time.

**Loop desync applies here.** `idle_loop` and `relaxed_loop` are the two looping
states, so both get a random time-scale in `[0.9, 1.1]` and a ±0.1 s phase offset
(`CreatureAnimator.cs:169-174`), and because the initial state **is** `idle_loop`,
the constructor also seeds a random start time inside the loop
(`CreatureAnimator.cs:44-59`). For a single-player body this is invisible; it
matters in co-op, where two Ironclads can share a screen.

---

## F. Intent / attack / hit / death tells

| tell | trigger | state played | who fires it (`file:line`) | blocking? | co-op visible? |
|---|---|---|---|---|---|
| Normal attack | `Attack` | `attack` | `AttackCommand.cs:572` → `CreatureCmd.TriggerAnim` (`CreatureCmd.cs:915-948`); default set at `AttackCommand.cs:220-221` | **yes** — awaits `Cmd.CustomScaledWait(min(delay·0.5, 0.25), delay)` with `delay = AttackAnimDelay = 0.15 s` (`Ironclad.cs:59`, `CreatureCmd.cs:947`) | yes |
| **Heavy attack** | **`heavyAttack`** | `attack_heavy` | same path, but the card asks for it via `Ironclad.GetHeavyAnimIfApplicable` / `GetHeavyAttackDelayIfApplicable` (`Ironclad.cs:120-136`). **Nine cards** do: Bludgeon, Break, Cinder, Mangle, Pact's End, Perfected Strike, Stomp, Unrelenting, Uppercut | **yes**, `delay = 0.2 s` | yes |
| Cast (Skill) | `Cast` | `cast` | `CreatureCmd.TriggerAnim(owner, "Cast", CastAnimDelay)` from **117 card files** | **yes**, `CastAnimDelay = 0.25 s` (`Ironclad.cs:61`) | yes |
| Power-up (Power) | `PowerUp` | **`cast`** (shared) | `CreatureCmd.TriggerAnim(owner, "PowerUp", PowerUpAnimDelay)` from **100 card files** | **yes**, `PowerUpAnimDelay => CastAnimDelay = 0.25 s` (`CharacterModel.cs:196`) | yes |
| Hit / flinch | `Hit` | `hurt` | `CreatureCmd.cs:325` with `waitTime = 0f`; also `DoomPower.cs:125` | **no** — gathered and awaited elsewhere | yes |
| Death | `Dead` | `die` | `NCreature::StartDeathAnim:944`; also on spawn if already dead (`:517`) | see below | yes |
| Revive | `Revive` | — | `NCreature::StartReviveAnim:957-963` — **but `HasTrigger("Revive")` is false for every player**, so this branch is never taken | — | yes |
| Revive **fallback** | *(none)* | *(none)* | `AnimTempRevive` (`NCreature.cs:975-981`): a 0.2 s fade-out → `ImmediatelySetIdle()` → 0.2 s fade-in | no | yes |
| Relaxed | `Relaxed` | `relaxed_loop` | **nobody** (correction 3) | — | — |
| `BoundsContainer` swap | — | — | **not used by this body.** No `AnimState` sets `BoundsContainer`, so `CreatureAnimator.BoundsUpdated` never fires for Ironclad and `%Bounds` is fixed for the whole combat | — | — |

**Death length — where the number comes from.** `StartDeathAnim`
(`NCreature.cs:916-955`) returns `Mathf.Min(a, 30f)` where `a =
GetCurrentAnimationLength()` — and `a` is only assigned **inside
`if (_spineAnimator != null)`** (`:933-946`). `DeathAnimLengthOverride` is a
**`MonsterModel`** property (`MonsterModel.cs:321-323`); a player has no such
escape hatch. The returned value is handed to `Hook.AfterDeath`
(`CreatureCmd.cs:513`, `:519`). Separately, the internal `AnimDie` task waits
`min(GetCurrentAnimationTimeRemaining() + 0.5, 20)` — again only if
`_spineAnimator != null` (`NCreature.cs:1006-1010`).

So for Ironclad: **the death animation's own length is the timing authority**, and
for a spine-less player body that authority is **0 and nothing waits**.

**Two audio facts that belong in this table, not just §G:**

1. **The player's attack/cast/power-up SFX are not gated on Spine.**
   `CreatureCmd.TriggerAnim` plays them in a `switch` *before* calling
   `SetAnimationTrigger` (`CreatureCmd.cs:933-946`). A spine-less player still
   gets those three sounds.
2. **`heavyAttack` is not in that switch.** The cases are exactly `"Attack"`,
   `"Cast"`, `"PowerUp"` (`CreatureCmd.cs:935-943`). Ironclad's nine heavy cards
   pass `"heavyAttack"`, which matches no case — so **`AttackSfx` does not play**
   for them, while the *same nine cards played by a non-Ironclad* return
   `"Attack"` from `GetHeavyAnimIfApplicable` and **do** play it. Verified in
   code by reading the full call chain; **`UNVERIFIED` by ear** — no capture
   tonight. Filed under NON-FINDINGS/UNKNOWN as a base-game observation, not as a
   defect we own. `cap-2` is designed to settle it.

---

## G. VFX and audio hooks

### VFX

- **Particle emitters: none.** Zero CPU, zero GPU. Everything visual beyond the
  skeleton is one shader on one slot.
- **Attachment points: one.** `SpineSlotNode "SlashVfxSlot"` → Spine slot
  **`slash_mesh`**. `slash_mesh` is confirmed present in the skeleton (string scan,
  offset 7116). No `SpineBoneNode` anywhere.
- **Driver script: `NIroncladVfx`** (`sts2src/MegaCrit.Sts2.Core.Nodes.Vfx/NIroncladVfx.cs`).
  This is the single most transferable thing in the file, so in full:

  - `_Ready` (`:89-96`) grabs the parent `SpineSprite`, reaches the slot node **by
    plain name**, pulls its `ShaderMaterial`, caches the authored `step` vector,
    and — the load-bearing line — calls
    `_megaSprite.ConnectAnimationEvent(...)` (`:95`).
  - `OnAnimationEvent` (`:98-112`) reads the **Spine event name** off the event
    payload and switches on exactly two strings: **`heavy_slash_start`** and
    **`attack_slash_start`**.
  - `OnHeavySlash` (`:114-121`): reset `step`, kill any running tween, then tween
    `shader_parameter/step` to `(1, 1.02)` over **0.35 s**, `EaseIn` + `Cubic`.
  - `OnAttackSlash` (`:123-131`): same reset, then **wait 0.15 s**, then tween to
    the same target over **0.20 s**, `EaseIn` + `Quad`. The delay is what makes
    the light attack's trail arrive later and snappier than the heavy's.
  - `_ExitTree` (`:133-136`) kills the tween. Correct lifetime handling.

  **The mechanism is: the animation itself emits a timed event, and a tween on a
  shader parameter listens for it.** The scene supplies the anchor, the skeleton
  supplies the *timing*, and the C# supplies the curve.

- **The skeleton's event table is exactly those two events.** The scan finds
  `attack_slash_start` at offset 47,061 and `heavy_slash_start` at 47,087,
  immediately before the first animation name at 47,113 — i.e. the complete
  events section. Nothing else in the skeleton emits.
- **Shared vs private:** the shader (`slash_shader_flat.tres`) and the mask
  (`ironclad_slash_base.png`) are Ironclad-only across all 126 creature scenes;
  the noise texture (`basic_fire_noise.png`) is shared with six other bodies.
- **Not part of the body, but adjacent:** `GetArchitectAttackVfx`
  (`Ironclad.cs:75-92`) names five one-shot VFX scenes — `vfx_attack_blunt`,
  `vfx_heavy_blunt`, `vfx_attack_slash`, `vfx_bloody_impact`, `vfx_rock_shatter` —
  used only when attacking The Architect. They live outside `creature_visuals/`.

### Audio

Player audio is derived from the character id, not authored per body
(`CharacterModel.cs:198-208`). For `ironclad`:

| property | FMOD event path | played from | Spine-gated? |
|---|---|---|---|
| `AttackSfx` | `event:/sfx/characters/ironclad/ironclad_attack` | `CreatureCmd.cs:936` | **no** |
| `CastSfx` | `event:/sfx/characters/ironclad/ironclad_cast` | `CreatureCmd.cs:939` | **no** |
| `PowerUpSfx` | *= `CastSfx`* (`CharacterModel.cs:204`) | `CreatureCmd.cs:942` | **no** |
| `DeathSfx` | `event:/sfx/characters/ironclad/ironclad_die` | `SfxCmd.PlayDeath(Player)` (`SfxCmd.cs:94-100`), called at `NCreature.cs:942` | **YES — inside `if (_spineAnimator != null)`** |
| `CharacterSelectSfx` | `event:/sfx/characters/ironclad/ironclad_select` | out of combat | — |
| `CharacterTransitionSfx` | `event:/sfx/ui/wipe_ironclad` | out of combat | — |

**There is no player hurt sound at all.** `HurtSfx` and `TakeDamageSfx` are
**`MonsterModel`** properties (`MonsterModel.cs:300-302`, `:327-329`), and the one
call site is explicitly gated `if (receiver.IsMonster …)` (`CreatureCmd.cs:326`).
So the player's whole in-combat audio surface is attack / cast / power-up / death,
and only the last of the four is Spine-gated.

**S19 join key** is the **trigger name** (schema §G): `Attack`, `Cast`, `PowerUp`,
`heavyAttack`, `Hit`, `Dead`, `Relaxed` — plus the two **Spine event** names
`attack_slash_start` and `heavy_slash_start`, which are a *second, finer-grained*
join key that exists only because the body is skeletal.

---

## H. Fallback behaviour

| failure | class | what actually happens |
|---|---|---|
| **Missing scene** (`ironclad.tscn` gone / unloadable) | **HARD** | `CharacterModel::CreateVisuals` (`CharacterModel.cs:212-215`) has **no try/catch**. It throws. **There is no player fallback scene** — `fallback.tscn` is reached only from `MonsterModel::CreateVisuals` (`MonsterModel.cs:420-437`). |
| **Missing required node** (`%Visuals` / `%Bounds` / `%IntentPos` / `%CenterPos`) | **HARD** | `NCreatureVisuals._Ready` uses `GetNode<T>` for all four (`NCreatureVisuals.cs:219`, `:221`, `:222`, `:223`), which throws. For a player that exception has nothing above it to catch. |
| **Missing optional node** (`%OrbPos`, `%TalkPos`, `%PhobiaModeVisuals`) | **silent, benign** | `%OrbPos` → falls back to `%IntentPos` (`:224`); `%TalkPos` → null (`:225`); `%PhobiaModeVisuals` → null, phobia mode does nothing. Ironclad ships without all three. |
| **Missing `.skel` / `.atlas` / bad skeleton data** | **silent DOWNGRADE** | `_Ready` checks `SpineBody.GetSkeleton()?.GetData()`; if null it pushes `"Spine skeleton data failed to load for {name}, disabling spine animation."` and sets `SpineBody = null` (`:226-234`). `HasSpineAnimation` then goes false and the body becomes a static pose: no animator is built (`NCreature.cs:503`), `SetAnimationTrigger` is a no-op (`:868-870`), **and no death SFX plays** (`:933-946`). |
| **Missing animation name** (a state the skeleton lacks) | **silent FREEZE** | `CreatureAnimator::SetNextState` logs `could not find '<id>' animation on '<node>'` and returns (`CreatureAnimator.cs:88-92`); the queued variant does the same (`:116-120`). Two consequences worth spelling out: (a) `_currentState` is assigned **before** the check (`:87`), so the animator's idea of its own state advances even though nothing plays; (b) the early return **skips the `NextState` queue**, so the automatic return to `idle_loop` is not scheduled — recovery happens only when the still-playing previous clip raises `OnAnimationCompleted` (`:143-159`). **Ironclad never hits this** (§D.3), but it is the single most important thing a visual-QA gate should catch. |
| **Missing `SlashVfxSlot`** | **HARD, but only for this body** | `NIroncladVfx._Ready:92` throws. |
| **Non-shader material on the slot** | **HARD** | unchecked cast dereference at `NIroncladVfx.cs:93`. |
| **Phobia mode with no `%PhobiaModeVisuals`** | **no-op, doubly** | `Visuals.UpdatePhobiaMode(Entity.Monster)` (`NCreature.cs:581-583`) passes **null** for a player, and `UpdatePhobiaMode` guards both halves (`NCreatureVisuals.cs:249-264`). Phobia mode cannot affect a player body at all. |
| **Skin not found** (`SetupSkins` / `OnPhobiaModeToggled`) | **not applicable** | `Visuals.SetUpSkin(...)` is called **only in the monster branch** of `NCreature._Ready` (`:511-512`) and takes a `MonsterModel` (`NCreatureVisuals.cs:266-276`). **Players have no skin system.** |

---

## I. Authoring dependency

**What the base body is made of.** A Spine 4.2 skeleton (`4.2.43`, from the file
header) exported to a binary `.skel` plus a text `.atlas` plus four PNG pages,
imported by the MegaDot editor through importers named `spine.skel` and
`spine.atlas` (`animations/characters/ironclad/*.import`) into
`SpineSkeletonFileResource` / `SpineAtlasResource`, and combined by a hand-written
`SpineSkeletonDataResource` `.tres` that also carries the mix table. At runtime
this is served by a **GDExtension**: `addons/spine/spine_godot_extension.gdextension`
(1,986 B) ships **inside the game's PCK**, and the native library
`libspine_godot.windows.template_release.x86_64.dll` (1,436,672 B) ships **loose in
the game directory** beside `SlayTheSpire2.exe`. Both read read-only; neither was
modified.

**The licence question, stated and not answered.** Authoring a `.skel` is done in
the Spine editor, which is commercial software. **Per charter §4/S16, no Spine
purchase or other proprietary authoring dependency may be `PROPOSED` as the
answer**, so this file does not propose one. What it can do is state precisely
what a no-paid-tools path would have to reproduce, because the runtime contract is
now fully described above:

1. a **`Node2D` under `%Visuals`** that the engine will accept — note
   `NCreatureVisuals` only treats it as Spine if `_body.GetClass() == "SpineSprite"`
   (`NCreatureVisuals.cs:179-189`), so **anything else is automatically the
   spine-less path**, which is not a failure, it is a different door;
2. seven named, addressable **states** matching the base default plus whatever
   bespoke ones the character needs;
3. per-pair **blend times** with an instant-cut option (Ironclad uses ten, six of
   them zero);
4. **desynchronised looping** (random time-scale and phase) or the co-op idle
   lockstep becomes visible;
5. a **timed event channel inside the animation** — this is the capability
   `NIroncladVfx` depends on and the one our current rig has no analogue for
   (see Q3);
6. a **draw-order-correct attachment slot** so a VFX layer can sit *inside* the
   body's z-order rather than in front of or behind all of it.

**What our own pipeline costs, for comparison** (the real baseline). A text
`.tscn` under `klee-mod/pck-src/`, no script in the scene by standing rule
(`klee-mod/pck-src/README.md`), a `resource=` line in the contract list at the
bottom of `tools/build_pck.ps1` (validate.ps1 S6c fails a deploy that omits one),
PNG layers staged from `ImageGen/`, and one MegaDot `--headless --import` +
export pass (`tools/build_pck.ps1:771-772`). Klee's combat rig
(`klee-mod/pck-src/klee/model/combat.tscn`) is **14,109 B of text source** — five
`Sprite2D` layers, **14 nodes**, 5 `ext_resource`s (the five PNG layers) and
**20 `sub_resource`s**: five hand-written `Animation` blocks, one
`AnimationLibrary`, four `AnimationNodeAnimation`s, nine
`AnimationNodeStateMachineTransition`s and one `AnimationNodeStateMachine`. The
whole thing is hand-authored keyframe text.

**Comparable object, both sides:** Ironclad = **2,701 B of scene + 167,402 B of
skeleton/atlas + 194,348 B of texture**, authored in a tool. Klee = **14,109 B of
scene**, authored by hand, plus five PNGs. Those are the two real numbers; what
they mean is a Lane-A bake-off question, not this file's.

**One unknown that matters and is cheap to close** — see UNKNOWN #1.

---

## J. Runtime / performance observables

Static, measured tonight from the pck directory. All figures are **packed bytes**.

| asset | packed bytes | shared? |
|---|---|---|
| `scenes/creature_visuals/ironclad.tscn` | **2,701** | private |
| `animations/characters/ironclad/ironclad_skel_data.tres` | **1,979** | private |
| `.godot/imported/ironclad.skel-…spskel` | **160,875** | private |
| `.godot/imported/ironclad.atlas-…spatlas` | **4,548** | private |
| `.godot/imported/ironclad.png-…ctex` (page 1) | **116,280** | private |
| `.godot/imported/ironclad_2.png-…ctex` | **44,420** | private |
| `.godot/imported/ironclad_3.png-…ctex` | **33,540** | private |
| `.godot/imported/ironclad_4.png-…ctex` | **108** | private |
| **body subtotal** | **364,451** | |
| `images/vfx/slash_shader_flat.tres` | 12,868 | private (1 user of 126) |
| `.godot/imported/ironclad_slash_base.png-…ctex` | 7,334 | private |
| `.godot/imported/basic_fire_noise.png-…ctex` | 339,824 | **shared, 7 creature scenes** |
| **VFX subtotal, private only** | **20,202** | |
| **VFX subtotal, incl. shared noise** | **360,026** | |

Reference points: `silent.tscn` 1,141 B and `silent_skel_data.tres` 1,075 B;
`fallback.tscn` 1,064 B. The whole pack is **15,658 entries**, **127 of them under
`res://scenes/creature_visuals/`** (126 `.tscn` + one stray `vantom.tres`).

**Draw-affecting materials: one** — the `ShaderMaterial` on `SlashVfxSlot`. The
`SpineSprite` itself carries no material override in the scene (one can be
injected at runtime by `SetScaleAndHue` when hue ≠ 0, `NCreatureVisuals.cs:283-298`).

**Emitters: zero**, so there is no `amount` to report.

**Note on the `.cs` entries.** `src/Core/Nodes/Combat/NCreatureVisuals.cs` and
`src/Core/Nodes/Vfx/NIroncladVfx.cs` are **1 byte each** in the pack — stubs. The
real code is in `SlayTheSpire2.exe`/the managed assembly; the pack only needs the
path so `[ScriptPath]` resolves. This is exactly why our pipeline's script-less
rule exists: we cannot mint entries in that namespace.

**Dynamic observables — `UNKNOWN`, capture pending.** Draw calls, frame cost, skeleton
update cost, scene instantiation time, and memory are **not measured and not
estimated**. The game was not launched.

---

## K. Three annotated capture slots — CAPTURE PENDING

Captures are impossible tonight: [USER] is playtesting mod `0.2-1155` and no agent
may launch, deploy to, or touch the game installation (PREFLIGHT). Each slot below
is a complete answer for tonight in the schema's sense: it says what it will
record and what it would settle.

### `cap-1` — idle

- `status:` **capture pending**
- `blocked_by:` [USER] playtest — no game launch (PREFLIGHT)
- `how_to_capture:` attended session; start a run as Ironclad, enter the first
  combat, hold on the idle pose for 3+ s without acting. For the loop-desync half,
  a co-op seat with a second Ironclad, or two frames of the same body at different
  wall-clock times.
- `what_it_would_settle:` whether the silhouette actually fills the 242 × 278
  `%Bounds` rect; where the intent marker sits relative to the head at
  `(30, −310)`; whether the idle-loop desync (`CreatureAnimator.cs:169-174`) is
  perceptible at all on a player body.
- *records when filled:* still frame + 3 s clip; `%Bounds` overlay; two-copy
  desync; intent marker placement.

### `cap-2` — the signature tell (`heavyAttack`)

- `status:` **capture pending**
- `blocked_by:` [USER] playtest — no game launch (PREFLIGHT)
- `how_to_capture:` attended session; play any of the nine heavy cards — Uppercut
  or Bludgeon are the easiest to reach — with audio recorded. Then play a normal
  Strike back to back as the control.
- `what_it_would_settle:` **(a)** the §F audio observation: does `heavyAttack`
  really play **no** `AttackSfx` while a normal Strike does? **(b)** the frame at
  which `heavy_slash_start` fires relative to contact, i.e. how much of the 0.35 s
  slash tween lands before the hit; **(c)** whether the 0.02 s
  `idle_loop → attack_heavy` mix reads as an instant snap next to the 0.10 s
  normal-attack blend.
- *records when filled:* clip from trigger to return-to-idle; contact frame;
  first frame of the slash trail; SFX presence/absence and cue time.

### `cap-3` — hit → death

- `status:` **capture pending**
- `blocked_by:` [USER] playtest — no game launch (PREFLIGHT)
- `how_to_capture:` attended session; take a multi-hit attack (for the `hurt→hurt`
  instant cut), then die. Audio recorded.
- `what_it_would_settle:` whether the `hurt → hurt` and `hurt → die` zero-mixes
  read as intended snaps; whether the death animation's own length is what the
  game actually waits on; whether `ironclad_die` plays; whether the corpse
  persists (players are not removed — `StartDeathAnim(shouldRemove)` is passed
  `… && creature.IsMonster`, `CreatureCmd.cs:513`).
- *records when filled:* clip covering `Hit` then `Dead`; measured death length
  vs §E; corpse persistence; death VFX/SFX presence.

---

## L. Closing sections

### 1. UNKNOWN

1. **Can a mod's build pipeline import a Spine skeleton at all?** Our
   `tools/build_pck.ps1` runs a **stock** MegaDot editor
   (`megadot-4.5.1-m.14-…-editor-csharp`, `build_pck.ps1:23`), whereas the Spine
   GDExtension ships inside the *game's* pack (`addons/spine/…`) and its native
   DLL sits in the *game's* directory. Whether the `spine.skel` / `spine.atlas`
   importers are registered in the editor we build with is **not known**.
   *What would answer it:* drop the extension descriptor + DLL into the throwaway
   scratch project and run `--headless --import` over a `.skel`/`.atlas` pair,
   then read the import log. That is a **tooling-lane** experiment (Lane A/C), not
   a research one; it was not run tonight.
2. **Clip durations** for all eight Ironclad animations. *What would answer it:* a
   Spine binary parser, or `MegaTrackEntry::GetAnimationEnd` read at runtime.
3. **Skeleton-internal bone and slot counts.** Same answer as #2.
4. **Every dynamic performance number** — draw calls, frame cost, load time,
   memory. *What would answer it:* `cap-1`…`cap-3` plus a profiler in an attended
   session.
5. **Does `weak_loop` predate the current Weak power, or is it forward-looking?**
   Nothing in the shipped build references it. *What would answer it:* the base
   game's own history, which we do not have.
6. **Is the `heavyAttack`-has-no-SFX asymmetry audible?** Code-verified, ear-
   unverified. `cap-2`.
7. **Can a non-Ironclad character actually acquire the nine heavy cards in a real
   run?** `GetHeavyAnimIfApplicable` exists precisely to handle that case, which
   implies yes, but the acquisition route was not traced.

### 2. NON-FINDINGS

Things looked for and genuinely absent. Search boundary stated for each.

1. **No conditional animation branches.** Searched every `AddAnyState` /
   `AddBranch` call in `Ironclad.cs` and `CharacterModel.cs`: every one passes
   `condition = null`. The `Func<bool>` machinery is unused by the simple player
   body.
2. **No `BoundsContainer` use.** Same boundary. Ironclad's silhouette never
   changes, so `CreatureAnimator.BoundsUpdated` never fires for him.
3. **No particles of any kind.** Full text search of the packed `.tscn` for
   `CPUParticles2D` / `GPUParticles2D`: zero.
4. **No `SpineBoneNode`.** Same file: zero. Ironclad anchors nothing to a bone;
   his one attachment is slot-based.
5. **No player skin system.** `SetUpSkin` takes a `MonsterModel` and is called
   only from the monster branch. Searched all `SetUpSkin` call sites in `sts2src`.
6. **No player phobia-mode body.** No `%PhobiaModeVisuals` in any of the five
   player scenes; and `UpdatePhobiaMode` receives null for players regardless.
7. **No player hurt SFX anywhere in the base game.** Searched `HurtSfx` and
   `TakeDamageSfx` across the whole decompile: `MonsterModel` only, one call site,
   monster-gated.
8. **No `Revive` on any player.** Searched `Models.Characters/` for `Revive`:
   zero hits across all five characters.
9. **No `.tres` animation state machine for any base creature.** Consistent with
   schema §1.2; re-confirmed for this body — the state machine is built in C# at
   spawn, nothing in the scene describes it.
10. **No code-side orphan states.** Every `AnimState` id Ironclad constructs
    appears in the skeleton scan. Boundary: string scan, so this is "no
    *detected* orphan".

### 3. Transfer questions

Numbered, against our BaseLib/Harmony path (schema §1.5). **Questions only** — no
recommendations, no numbers, no proposals.

**Q1 — `Relaxed` and `Revive`: do we inherit two dead wires?**
`CreatureAnimationRouter.TriggerToState` maps `Revive → idle`
(`klee-mod/KleeCode/Vfx/CreatureAnimationRouter.cs:48`) and has no `Relaxed` entry
at all. But `StartReviveAnim` only reaches `SetAnimationTrigger("Revive")` when
`HasTrigger("Revive")` is true, which requires a `_spineAnimator` — which a
spine-less body never has (`NCreature.cs:957-963`). So for our characters the
revive path always falls to `AnimTempRevive`, whose recovery step calls
`_spineAnimator?.SetTrigger("Idle")` **directly** (`NCreature.cs:985`), bypassing
the public `SetAnimationTrigger` our Harmony postfix patches. **Question: after a
mid-combat revive, does a modded player's `AnimationTree` ever leave the `death`
state?** Code says the trigger never arrives. Not observed in play.

**Q2 — `heavyAttack` and the unknown-trigger rule.** Our router deliberately
ignores unmapped triggers rather than forcing idle
(`CreatureAnimationRouter.cs:70-73`, and the comment at `:41-43` says why). The
base game's own bespoke player triggers — `heavyAttack`, `shiv`,
`sovereignBladeTrigger`, `summonTrigger` — are exactly such unmapped names.
**Question: is "ignore" still the right rule if one of our characters ever wants a
signature tell, or does a signature tell need a fifth state?** This is a design
question the moment it stops being a plumbing question; it is asked here, not
answered.

**Q3 — the timed-event channel.** `NIroncladVfx` is driven entirely by **Spine
animation events** fired from *inside* the clip (`NIroncladVfx.cs:95-112`), not by
game triggers. A Godot `AnimationPlayer` has a method-call track that could carry
the same information, but our five hand-written `Animation` sub-resources in
`klee/model/combat.tscn` are value tracks only. **Question: for a layered rig, is
the equivalent of `attack_slash_start` a method-call track inside the animation,
or does VFX timing move out of the animation and into the C# that fired the
trigger?** The two put the timing authority in different files.

**Q4 — draw-order-correct attachment.** `SpineSlotNode` puts a shader *inside* the
skeleton's slot ordering, so the slash can sit behind an arm and in front of a
torso. A layered `Sprite2D` rig has z-order only between its own sprites.
**Question: does anything we plan need a VFX layer *interleaved* with body parts
rather than in front of or behind the whole body?**

**Q5 — death timing and death sound.** For a spine-less player, `StartDeathAnim`
returns `0f` and plays **no** `DeathSfx` (`NCreature.cs:933-946`), and `AnimDie`
skips its wait (`:1006-1010`). Our mod patches `StartDeathAnim` with a postfix to
route the `Dead` trigger into the `AnimationTree`
(`CreatureAnimationRouter.cs:97-102`), which fixes the *animation* but not the
*length* or the *sound*. **Question: is a modded character's death currently
silent, and does combat currently not wait for it?** Both follow from the cited
code; neither was observed in play.

**Q6 — the naming skew, and what a public mod shows it costs.** The base game's
player states are `idle_loop / cast / attack / hurt / die / relaxed_loop`; our
scenes use `idle / attack / hurt / death` (`CreatureAnimationRouter.cs:45-54`).
Because we never build a `CreatureAnimator`, the skew is free for us. It is **not**
free for a mod that does. Reference-read only, at the pinned Downfall commit:
`Downfall@32e6113:ChampCode/Core/Champ.cs` and
`Downfall@32e6113:AwakenedCode/Core/Awakened.cs` both have their
`GenerateAnimator` overrides **commented out**, so those characters fall back to
`CharacterModel.GenerateAnimator` and its six state names — while a string scan of
`Downfall@32e6113:Champ/scenes/character/spine/champ.skel` (Spine `4.2.39`) finds
`attack`, `attack_jump`, `die`, `hurt`, `idle_loop`, `idle_loop_berserker`,
`idle_loop_defensive`, `idle_loop_gladiator`, `idle_loop_ultimate`,
`hurt_berserker`, `hurt_defensive`, `hurt_gladiator` — and **no `cast`, no
`relaxed_loop`**. **Question: does that combination put a shipped public mod on
the §1.4 silent-freeze path every time a Skill is played?** Scan-derived
(`UNVERIFIED`), reference-reading only, nothing copied, and **not our defect to
file** — it is cited because it is the clearest available evidence of what the
name contract costs when you *do* use the base animator.

**Q7 — script-in-scene.** Downfall's `Champ/scenes/character/combat.tscn:4,7`
attaches its own `NChampCreatureVisuals.cs` to the scene root; our pipeline
forbids scripts in scenes by standing rule (`klee-mod/pck-src/README.md`) and
routes behaviour through Harmony instead. Both ship. **Question: is our rule
costing us anything a body actually needs, or only costing us a convenience?**

**Q8 — the `Facing` node.** Our scenes carry a `%Facing` node driven by
`CreatureFacing` (`klee-mod/KleeCode/Vfx/CreatureFacing.cs:93`). No base creature
scene has one, and the house note on StS2 creature visuals records that no facing
concept exists in the base game. **Question: does a facing flip read as a
deliberate stylistic difference, or as a bug, when a modded character shares a
screen with a base one?** That is an eyes-on call, which is [USER]'s.

### 4. What this does NOT establish

This file describes one base-game player body as it exists on disk on
2026-08-26 — its scene, its resources, its state machine, its transitions, its
one VFX mechanism, its sounds, and how each of those fails. It does **not** say
which animation approach we should use, does not rank layered sprites against
skeletal 2D, does not propose buying or not buying anything, and does not say
that Ironclad — or any part of him — should be copied, reskinned, or matched. It
does not measure a single frame: the game was never launched, so every duration,
every frame cost, every "does that read right" question is capture-pending and
marked so rather than guessed. The skeleton contents are a string scan, not a
parse, and are labelled `UNVERIFIED` even where the corroboration is strong. The
two behaviours it identifies in our own mod (Q1, Q5) are read out of code, not
observed in play, and are written as questions for that reason. Nothing here is a
ruling, a recommendation, or a defect filing.
