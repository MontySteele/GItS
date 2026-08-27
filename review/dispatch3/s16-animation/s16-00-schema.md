# S16-00 — native-animation grammar: the common evidence schema, and the four body picks

> **This file decides nothing.** It is a research artifact from surplus-dispatch-3.
> Every recommendation below is a **technical** pick labelled `PROPOSED`; taste,
> lore, art direction, rights, spend, scope and ship calls remain [USER]'s.
> Nothing here opens a balance window, moves a stamp, mints an id, or interprets
> a playtest.

**Read this before writing any `s16-*` corpus file.** It defines, once, the
evidence schema every body file must follow, so the four bodies join into one
matrix instead of four essays. Section 5 names the four bodies and says exactly
which file each agent opens first.

---

## 0. How the evidence was obtained, and what you may cite

| Source | Where | How to cite |
|---|---|---|
| Base-game decompile (ILSpy 8.2, `SlayTheSpire2.dll` @ v0.107.1) | `…/scratchpad/sts2src/<Flat.Namespace>/<Type>.cs` | `MegaCrit.Sts2.Core.Animation.CreatureAnimator::SetNextState` + `sts2src/MegaCrit.Sts2.Core.Animation/CreatureAnimator.cs:85-112` |
| Same decompile, S13's mirror | `…/scratchpad/S13/sts2/MegaCrit/sts2/Core/…` | byte-identical to `sts2src` (md5 checked on `CreatureAnimator.cs`, `MonsterModel.cs`); cite either, but say which |
| Base-game packed assets | `SlayTheSpire2.pck`, listed/extracted **read-only** into `…/scratchpad/s16/` | `pck:res://scenes/creature_visuals/mawler.tscn` + the extracted copy's line |
| Our mod's scene sources | `klee-mod/pck-src/**` in the primary checkout (read-only) | repo `file:line` |
| Our mod's C# | `klee-mod/KleeCode/**` | repo `file:line` |
| Public mod reference | Downfall @ `32e6113` | `Downfall@32e6113:<path>:<line>` — reference-reading only, never copied |

**The PCK is readable without any licensed tool.** `SlayTheSpire2.pck` is a
MegaDot 4.5.1 pack, header magic `GDPC`, **pack format 3**. Format 3 differs
from the widely documented format 2 in two ways that break naive parsers, both
verified against this file:

1. The header carries `pack_flags` (uint32) then `file_base` (uint64) then a
   **directory offset** (uint64) before the 16 reserved uint32s. The file table
   is **at the end of the pack** (here, byte `1899867440`), not after the header.
2. `pack_flags = 2` (relative file base): every entry offset must have
   `file_base` (here, `112`) **added** to it. Forget this and every extracted
   file is shifted 112 bytes and silently corrupt at both ends.

The two throwaway scripts that do this live at
`…/scratchpad/s16/pcklist.py` (list) and `…/scratchpad/s16/pckget.py` (extract
by regex). They are scratch, not repo tooling; if a body agent wants them in the
repo that is a Lane-C question, not an S16 one.

**Good news for the corpus: the scenes are plain text.** `.tscn` and `.tres`
ship un-converted inside the pack — 15,658 entries, 127 of them under
`res://scenes/creature_visuals/`. Node trees, node types, positions, materials,
particle parameters and Spine mix tables are all directly readable. Only the
Spine `.skel`/`.atlas`/`.png` payloads are binary (they live in
`res://.godot/imported/*.spskel` / `*.spatlas` / `*.ctex`).

---

## 1. The shared grammar — facts a body file may cite but must NOT re-derive

Establishing these once is the point of this file. A corpus file that restates
them wastes its budget; a corpus file that **contradicts** them has found
something and should say so loudly.

### 1.1 One scene contract, keyed by id

A creature body is a `.tscn` under `res://scenes/creature_visuals/<id>.tscn`,
resolved from the model id by `SceneHelper.GetScenePath`
(`sts2src/MegaCrit.Sts2.Core.Helpers/SceneHelper.cs:12-20`), reached as
`MonsterModel::VisualsPath` (`…/Models/MonsterModel.cs:216`) and
`CharacterModel::VisualsPath` (`…/Models/CharacterModel.cs:104`). Players and
monsters use the **same** directory and the **same** root script,
`NCreatureVisuals`.

`NCreatureVisuals::_Ready` (`…/Nodes/Combat/NCreatureVisuals.cs:217-225`) fixes
the node contract by unique-name lookup:

| Node | Required? | Type | Missing ⇒ |
|---|---|---|---|
| `%Visuals` | **required** | `Node2D` (usually `SpineSprite`) | `GetNode` throws → whole body falls back (1.4) |
| `%Bounds` | **required** | `Control` | same |
| `%IntentPos` | **required** | `Marker2D` | same |
| `%CenterPos` | **required** | `Marker2D` — this is `VfxSpawnPosition` | same |
| `%PhobiaModeVisuals` | optional | `Node2D` | phobia mode has no alternate body |
| `%OrbPos` | optional | `Marker2D` | silently falls back to `%IntentPos` |
| `%TalkPos` | optional | `Marker2D` | stays null |

`HasSpineAnimation` is simply `SpineBody != null`
(`NCreatureVisuals.cs:191-195`). That one boolean gates everything in 1.2.

### 1.2 The animation state machine is code, not scene data

There is no `.tres` state machine. `NCreature` builds one at spawn:

- `NCreature.cs:503-513` — **only if** `HasSpineAnimation`, call
  `Character.GenerateAnimator(Visuals.SpineBody)` or
  `Monster.GenerateAnimator(...)`, then `Visuals.SetUpSkin(monster)`.
- Every `GenerateAnimator` builds `AnimState` objects (id = the **Spine
  animation name**) and wires them into a `CreatureAnimator`
  (`sts2src/MegaCrit.Sts2.Core.Animation/AnimState.cs`,
  `…/Animation/CreatureAnimator.cs`).
- `CreatureAnimator` exposes seven canonical **triggers**
  (`CreatureAnimator.cs:11-23`): `Idle`, `Attack`, `PowerUp`, `Cast`, `Dead`,
  `Hit`, `Revive`. Models add bespoke ones freely (`heavyAttack`, `Shiv`,
  `Unstun`, `summonTrigger`, `sovereignBladeTrigger`, `Plow`, `EndPlow`, …).
- Trigger resolution is **anyState first, then current state**
  (`CreatureAnimator.cs:67-78`), and a branch may carry a `Func<bool>` condition
  (`AnimState.cs:54-82`) — that is how a boss picks between two death animations.
- `AnimState.NextState` queues a follow-on animation on the same track
  (`CreatureAnimator.cs:114-132`); `AnimState.BoundsContainer` re-points the
  hitbox when a body changes silhouette (`AnimState.cs:45`,
  `CreatureAnimator.cs:104-107`, consumed via `NCreature.cs:560-572`).
- Named animation constants exist (`AnimState.cs:15-27`): `attack`, `cast`,
  `die`, `hurt`, `idle_loop`, `revive`, `stun`. **They are conventions, not
  enforcement** — every model passes string literals.

Idle loops are deliberately desynchronised: each looping track gets a random
time-scale in `[0.9, 1.1]` and a random phase offset of ±0.1 s
(`CreatureAnimator.cs:169-174`), and a body that starts on `idle_loop` also
starts at a random time within the loop (`CreatureAnimator.cs:44-59`). Two
copies of the same enemy therefore never breathe in lockstep. Any replacement
grammar that loses this loses a visible quality of the base game.

### 1.3 Where the tells actually fire

- **Attack / cast / power-up:** `CreatureCmd.TriggerAnim` plays the *player's*
  SFX in a `switch` on the trigger name and *then* calls
  `SetAnimationTrigger` (`sts2src/MegaCrit.Sts2.Core.Commands/CreatureCmd.cs:926-947`).
  Player attack/cast/power-up audio is therefore **not** gated on Spine.
- **Hit:** `NCreature::SetAnimationTrigger` is `_spineAnimator?.SetTrigger(...)`
  (`NCreature.cs:868-870`) — a guaranteed no-op without Spine. `DoomPower`
  fires `"Hit"` directly (`…/Models.Powers/DoomPower.cs:125`).
- **Death:** `NCreature::StartDeathAnim` (`NCreature.cs:916-954`). Everything
  interesting is inside `if (_spineAnimator != null)`: the **death SFX**
  (`:936-943`) and the returned **death-animation length** (`:945`). Without
  Spine the method returns `0f` unless the monster sets
  `DeathAnimLengthOverride` (`MonsterModel.cs:321-323`), and **plays no death
  sound at all**. This is a real, cited defect surface for any spine-less body.
- **Intent:** intents are their own nodes (`NIntent`) positioned at
  `%IntentPos`; they are not animation states. Do not conflate the two.

### 1.4 Fallback behaviour

`MonsterModel::CreateVisuals` (`MonsterModel.cs:420-437`) wraps the scene load
in `try/catch`: on any exception it logs, reports to Sentry, and instantiates
`res://scenes/creature_visuals/fallback.tscn` (`MonsterModel.cs:171`). A
**missing animation** is softer: `CreatureAnimator::SetNextState` logs
`could not find '<id>' animation on '<node>'` and simply does nothing
(`CreatureAnimator.cs:88-92`; queued variant `:116-120`). So a body with a good
scene and a bad animation name **freezes silently** rather than crashing — the
single most important failure mode for a visual-QA gate to catch.

### 1.5 Our mod does none of this, on purpose

`klee-mod` ships spine-less bodies: layered `Sprite2D` rigs driven by an
`AnimationTree`, with a Harmony postfix pair mapping the game's triggers onto
state-machine `Travel` calls — because `SetAnimationTrigger` is a no-op for us
(`klee-mod/KleeCode/Vfx/CreatureAnimationRouter.cs:35-82`, patches at `:84-103`).
Our trigger table is four states — `idle` / `attack` / `hurt` / `death` — with
`Cast` and `PowerUp` folded into `attack` and `Revive` into `idle`
(`CreatureAnimationRouter.cs:45-54`). Note the naming skew: the base game says
**`die`**, our scenes say **`death`**. Our scenes are script-less by pipeline
rule (`klee-mod/pck-src/README.md`), so the routing target is found by node
lookup. Klee's own combat rig is
`klee-mod/pck-src/klee/model/combat.tscn` — five `Sprite2D` layers under
`Visuals/Facing/Rig`, plus `Bounds` / `CenterPos` / `IntentPos`, an
`AnimationPlayer` and an `AnimationTree`.

**Every corpus file must therefore answer the transfer question:** what does the
base body get from Spine that our layered rig does not, and is that difference
mechanical, cosmetic, or invisible?

---

## 2. The evidence schema — sections A–K, in this order, in every corpus file

Field key: **R** = required, must be filled or explicitly marked `UNKNOWN` /
`NON-FINDING`; **O** = optional, omit the row if it does not apply.

### A. Identity and provenance (R)

| Field | Content |
|---|---|
| `body_id` | the model id as the engine spells it, lowercase (`mawler`) |
| `role` | `player-simple` / `player-complex` / `enemy-normal` / `elite-boss` |
| `class` | C# type name (`MegaCrit.Sts2.Core.Models.Monsters.Mawler`) |
| `scene` | `res://scenes/creature_visuals/<id>.tscn` + byte size from the pck listing |
| `reachability` | how a human reaches this body in play (act, encounter, pin) — needed for capture planning |
| `read_on` | date + game version + pck path |

### B. Scene / resource topology (R)

One table, one row per node, in tree order: `path`, `type`, `unique_name?`,
`purpose`, `depends_on` (ext_resource it pulls). Follow it with the
`ext_resource` list: type, `res://` path, and whether it is shared across
bodies (e.g. `themes/canvas_item_material_additive_shared.tres`) or private.
Call out any node the 1.1 contract does **not** require, and say what breaks if
it is absent.

### C. Node / layer / bone counts (R, with an honesty rule)

`nodes_total`, `spine_sprites`, `particle_emitters` (split CPU vs GPU),
`bone_nodes`, `slot_nodes`, `markers`, `sprite_layers`, `driver_scripts`.
**Bone and slot counts inside the Spine skeleton are a different number** from
`SpineBoneNode`/`SpineSlotNode` counts in the scene — the scene number is
verifiable tonight, the skeleton's internal count is not. Report the scene
number as fact; report the skeleton's as `UNVERIFIED` unless you actually parse
the `.skel`.

### D. Animation / state names (R)

Two disjoint lists, never merged:

1. **Referenced states** — every `AnimState` id constructed in this body's
   `GenerateAnimator`, with the trigger(s) that reach it and any branch
   condition. Cite `file:line`. This list is *complete and verified*.
2. **Skeleton-resident animations** — names present in the Spine data. Verified
   sources you may union without a parser: the `preview_animation` in the
   `.tscn`; every `from`/`to` in the `_skel_data.tres` mix table; every name
   probed by `MonsterModel::GetBestiaryMoves` (`MonsterModel.cs:497-508` probes
   `revive`, `hurt`, `die`). A raw-string scan of the `.spskel` may **suggest**
   more; mark anything from that scan `UNVERIFIED`.

Report **orphans** in both directions: skeleton animations no code plays, and
`AnimState` ids the skeleton may not contain. Worked example: Ironclad's
skeleton carries a `weak_loop` string, and `weak_loop` appears **nowhere** in
the decompile — an orphan (scan `UNVERIFIED`; the absence in code is verified).

### E. Durations and transitions (R for what is in the file, UNKNOWN otherwise)

From `<id>_skel_data.tres`: `default_mix` (0.05 is the house default) and every
`SpineAnimationMix` row as `from → to = mix` (a mix with no `mix =` line means
**0**, an instant cut — that is a deliberate authoring choice, not a missing
value). From code: every `NextState` chain and every `AddBranch`. **Clip
durations are UNKNOWN tonight** — they live in the binary `.skel`; the runtime
reads them via `MegaTrackEntry::GetAnimationEnd`. Say so; do not estimate.

### F. Intent / attack / hit / death tells (R)

One row per tell: `tell`, `trigger name`, `state played`, `who fires it`
(`file:line`), `blocking?` (does combat await it), `co-op visible?`. Include the
non-obvious ones: `Unstun`/`Revive` where present, the conditional death
variants, and the `BoundsContainer` swap if the silhouette changes. Explicitly
record whether death length comes from the animation (`GetCurrentAnimationLength`)
or from `DeathAnimLengthOverride`.

### G. VFX and audio hooks (R)

- **VFX:** every particle emitter (CPU/GPU, one-shot vs looping, texture,
  material), every `SpineSlotNode` / `SpineBoneNode` attachment point and which
  Spine slot/bone it names, and any per-body driver script
  (`NIroncladVfx`, `NRegentVfx`, `NCeremonialBeastVfx`, …) with what it drives.
- **Audio:** the FMOD event paths the model exposes — `AttackSfx`, `CastSfx`,
  `DeathSfx`, `HurtSfx`, `TakeDamageSfx` (`MonsterModel.cs:292-329`) — plus
  where each is played from. Flag the death-SFX gating from 1.3.
- Join key for S19: use the **trigger name**, not the animation name.

### H. Fallback behaviour (R)

What happens on: missing scene; missing required node; missing animation name;
missing `.skel`/atlas; phobia mode with no `%PhobiaModeVisuals`; skin
(`SetupSkins` / `OnPhobiaModeToggled`, `MonsterModel.cs:598`, `:643-650`) not
found. State which of those are **hard** (fallback scene / exception) and which
are **silent** (log + frozen pose). Anything you have not verified is `UNKNOWN`.

### I. Authoring dependency (R)

What a human needs to *make* this body: authoring tool, file formats, the
importer that consumes them, and the licence question. Base bodies are Spine
(`SpineSkeletonDataResource`, `SpineAtlasResource`, `SpineSkeletonFileResource`;
runtime `libspine_godot.windows.template_release.x86_64.dll` ships in the game
directory). **Per charter §4/S16, no Spine purchase or other proprietary
authoring dependency may be PROPOSED as the answer** — inspect the runtime
contract, then state plainly what a no-paid-tools path would have to reproduce.
Also record what our own pipeline needs (`pck-src` text scene, MegaDot import,
`build_pck.ps1`, contract line) — that is the real cost baseline.

### J. Runtime / performance observables (R where measurable, UNKNOWN otherwise)

Static observables you can get tonight: packed byte size of scene, skeleton,
atlas, texture(s); emitter counts and `amount`; number of draw-affecting
materials; whether textures are shared or private. Dynamic observables
(draw calls, frame cost, load time) are **UNKNOWN — capture pending** (see K).
Never guess a frame cost.

### K. Three annotated capture slots — **CAPTURE PENDING**

Captures are **not possible tonight**: [USER] is playtesting on mod `0.2-1155`
and no agent may launch, deploy to, or touch the game installation
(PREFLIGHT §Deployed mod). Every corpus file therefore ships **three empty
capture slots in the schema below**, each stating what it *will* record, so a
later attended session can fill them without redesigning the evidence.

| slot | moment to capture | what the slot records when filled |
|---|---|---|
| `cap-1` | idle, two copies on screen where possible | still frame + 3 s clip; silhouette vs `%Bounds` rect; loop desync visible (1.2); intent marker placement |
| `cap-2` | the body's signature tell (attack / bespoke trigger) | clip from trigger to return-to-idle; frame at contact; VFX emitter first frame; SFX cue time relative to the contact frame |
| `cap-3` | hit → death | clip covering `Hit` then `Dead`; whether death length matches E; whether the corpse is removed or persists; death VFX and SFX presence |

Each slot's row must carry: `status: capture pending`, `blocked_by: [USER]
playtest — no game launch (PREFLIGHT)`, `how_to_capture:` one line naming the
attended route, and `what_it_would_settle:` one line. A filled slot later adds
`file:` and three annotation bullets. **A capture-pending slot is a legitimate,
complete answer for tonight** — do not substitute a description of a frame you
did not see.

### L. Closing sections (R)

Every corpus file ends with, in this order:

1. **UNKNOWN** — questions the file could not answer, each with what would
   answer it.
2. **NON-FINDINGS** — things looked for and genuinely absent, with the search
   boundary. A non-finding is a result.
3. **Transfer questions** — numbered, against our BaseLib/Harmony path (1.5).
   Questions only; no recommendations, no numbers.
4. **What this does NOT establish** — one short paragraph, plain English.

---

## 3. The joined capability matrix (who builds it, and its columns)

The four corpus files feed **one** joined matrix, owned by a single integrator,
comparing the four approaches the charter names: **layered sprites**,
**cutout / skeletal 2D**, **mesh deformation**, **particles / tweens**.

Proposed columns, one row per approach: engine support (cited); authoring tool +
licence; what the base game uses it for (cited body); what our pipeline already
does; source-file burden; packed size behaviour; failure mode when an asset is
missing; visual-QA seam; and a `PROPOSED` note. **No approach is ranked**; the
matrix reports capability, and the pick is [USER]'s (and is partly Lane A's
bake-off evidence, not ours).

The public-mod sidecar (charter §4/S16) belongs beside the matrix, not inside a
body file: Downfall ships raw Spine per character at
`Downfall@32e6113:<Character>/scenes/character/spine/*.skel` + `*.atlas`, with
the body scene at `<Character>/scenes/character/combat.tscn` — which is the
directly comparable object to our `klee-mod/pck-src/klee/model/combat.tscn`.

---

## 4. Filename and ownership map

| File | Owner | Body |
|---|---|---|
| `s16-00-schema.md` | this file | — |
| `s16-01-player-simple.md` | one agent | Ironclad |
| `s16-02-player-complex.md` | one agent | Regent |
| `s16-03-enemy-normal.md` | one agent | Mawler |
| `s16-04-elite-boss.md` | one agent | Ceremonial Beast |
| `s16-05-matrix.md` | integrator | joined capability matrix + public-mod sidecar |

No two agents edit the same file (charter §6).

---

## 5. The four bodies — TECHNICAL picks, `PROPOSED`

All four are picked to be **disjoint in what they teach** and **reachable in the
default Act 1 or the base character roster**, so the corpus spans the real range
instead of sampling the same body four times. Sizes are packed byte sizes from
the pck directory.

### 5.1 Player — simple: **Ironclad** (`PROPOSED`)

**Rationale.** The smallest complete *player* body that still carries one VFX
affordance: `SpineSprite` + a single `SpineSlotNode` bound to the Spine slot
`slash_mesh` with a shader material, plus one driver script (`NIroncladVfx`).
Six `ext_resource`s, seven nodes, 2,701 B. Its animator is the canonical
seven-state player shape with exactly one bespoke trigger (`heavyAttack`), so it
documents the player grammar's floor-plus-one. It is also the house's
measurement anchor (`ref_ironclad` / `real_ironclad`), and its card pool is
already extracted into `game_ref/`, so anything found here joins work we already
have. **Contrast to note in the file, not to write a second file about:**
`silent.tscn` (1,141 B, two `ext_resource`s, four nodes, no VFX at all) is the
strict floor — Ironclad minus the slash slot and its driver.

**Where to open first, in order:**
1. `…/scratchpad/s16/x/scenes/creature_visuals/ironclad.tscn` (extract from
   `pck:res://scenes/creature_visuals/ironclad.tscn` if absent)
2. `…/scratchpad/s16/x/animations/characters/ironclad/ironclad_skel_data.tres`
   (`default_mix = 0.05`, ten explicit mixes)
3. `sts2src/MegaCrit.Sts2.Core.Models.Characters/Ironclad.cs:94-116`
4. `sts2src/MegaCrit.Sts2.Core.Models/CharacterModel.cs:104`, `:190`, `:214`, `:222-243`
5. `pck:res://src/Core/Nodes/Vfx/NIroncladVfx.cs` — decompiled at
   `sts2src/MegaCrit.Sts2.Core.Nodes.Vfx/NIroncladVfx.cs`
6. `…/scratchpad/s16/x/scenes/creature_visuals/silent.tscn` (the floor contrast)

### 5.2 Player — complex: **Regent** (`PROPOSED`)

**Rationale.** By a wide margin the most structurally complex shipped player
body: 75,694 B, 406 lines, **three** `SpineSprite`s (body plus two weapon
skeletons nested under a `SpineSlotNode`), a **second** skeleton data resource
(`regent_weapon_skel_data.tres`), **six** `GPUParticles2D` emitters — five of them
hung off four different `SpineBoneNode`s, one (`Explosion`) directly under the
body — a shared additive material, and a driver script (`NRegentVfx`). It is the only base body that proves skeleton-inside-skeleton
composition and bone-anchored particles at once — exactly the two capabilities
our layered-sprite rig has no answer for. Its animator is still the same
seven-state shape (bespoke trigger `sovereignBladeTrigger`), which makes the
point cleanly: **on the player side, complexity lives in the scene, not in the
state machine.** Necrobinder (19,435 B) is the intermediate rung; name it, do
not profile it.

**Where to open first, in order:**
1. `…/scratchpad/s16/x/scenes/creature_visuals/regent.tscn` — node list at
   lines 239-406, `ext_resource` block at 3-8
2. `…/scratchpad/s16/x/animations/characters/regent/regent_skel_data.tres`
3. the second skeleton: `pck:res://animations/characters/regent/regent_weapon_skel_data.tres`
4. `sts2src/MegaCrit.Sts2.Core.Models.Characters/Regent.cs:97-119`
5. `sts2src/MegaCrit.Sts2.Core.Nodes.Vfx/NRegentVfx.cs`
6. `sts2src/MegaCrit.Sts2.Core.Nodes.Combat/NCreatureVisuals.cs:207-225`
   (`GetCurrentBody`, node contract) — needed to explain the nesting

### 5.3 Normal enemy: **Mawler** (`PROPOSED`)

**Rationale.** The most ordinary enemy the game ships, and the most capturable:
Act 1 (`Overgrowth`) only, a **solo** `MawlerNormal` encounter, and on a
player's first-ever run the act **pins it to normal-encounter slot 5** — a
scripted teaching fight (`docs/current/dossiers/enemies/mawler.md:5-10`). The
body is the enemy floor: 1,204 B, two `ext_resource`s, five nodes total — one
`SpineSprite`, one `Bounds` control, two markers — no particles, no driver
script, no phobia body. Its animator override
is the single most common variation in the whole monster corpus — rename `cast`
to a bespoke idle-adjacent tell (`roar`) and change nothing else
(`Mawler.cs:70-87`; compare `Nibbit.cs:117-133` renaming to `hiss`). Its
`_skel_data.tres` carries only four mixes — two blends at `0.02`
(`idle_loop→hurt`, `idle_loop→die`) and two **instant cuts** with no `mix =`
line at all (`hurt→hurt`, `hurt→die`) — which is a legible authoring signal. This is the body Lane D
would have to match if it ever replaces an ordinary enemy's presentation.

**Rejected alternatives, and why (record them, do not re-litigate):**
Leaf Slime (S) is even smaller and uses the pure default animator, but it never
appears alone and teaches nothing Mawler does not. Wriggler also uses the pure
default, but it is only reachable through the Dense Vegetation event or as the
Phrog Parasite's second phase — bad for a capture slot. Two-Tailed Rat lives in
the *alternate* Act 1 (`Underdocks`).

**Where to open first, in order:**
1. `…/scratchpad/s16/x/scenes/creature_visuals/mawler.tscn`
2. `…/scratchpad/s16/x/animations/monsters/mawler/mawler_skel_data.tres`
3. `sts2src/MegaCrit.Sts2.Core.Models.Monsters/Mawler.cs:70-87`
4. `sts2src/MegaCrit.Sts2.Core.Models/MonsterModel.cs:171`, `:216`, `:292-329`,
   `:420-437`, `:497-508`, `:598`, `:602-618`, `:643-650`
5. `docs/current/dossiers/enemies/mawler.md` (reachability and move set only —
   it is a REFERENCE doc, do not restate its mechanics)
6. `…/scratchpad/s16/x/scenes/creature_visuals/fallback.tscn` (1,064 B) — the
   thing a broken enemy body becomes

### 5.4 Elite / boss: **Ceremonial Beast** (`PROPOSED`)

**Rationale.** An Act 1 (`Overgrowth`) boss — second in that act's boss
discovery order (`docs/current/dossiers/enemies/ceremonial-beast.md:6-15`) — so
it is reachable without unlocks, unlike the Act 2/3 bosses. It is the richest
*animation* body in the game that is still readable in one sitting: **eleven**
`AnimState`s including a `stun` → `stun_loop` → `wake_up` chain and a `plow` →
`plow_end` charge chain, **conditional** branches (two different death states
chosen by `InMidCharge`, and a per-state `Hit` branch guarded by
`ShouldPlayRegularHurtAnim` / `IsStunnedByPlowRemoval`), and per-state branches
rather than only `anyState` ones (`CeremonialBeast.cs:262-294+`). Its scene
(69,046 B, 206 lines) adds what neither player body has: **both** `CPUParticles2D`
and `GPUParticles2D`, `SpineBoneNode` targets used as *gameplay* anchors
(`PlowStartTarget` / `PlowEndTarget`), a death-particle texture, and a driver
script wired by `node_paths`. Together that is the full "what a boss needs"
surface in a single file.

**Rejected alternatives, and why:** Test Subject (139,319 B) and Knowledge Demon
(83,838 B) are larger but are later-act and use `BoundsContainer` respawn
machinery that would dominate the file; Kaiser Crab splits across
`kaiser_crab_boss.tscn` + `kaiser_crab_boss_setup.tscn`, an interesting pattern
worth **one sentence** in the corpus file and no more. Phrog Parasite is the Act
1 *elite* and is the natural fifth body if capacity appears — it is **not**
commissioned here.

**Where to open first, in order:**
1. `…/scratchpad/s16/x/scenes/creature_visuals/ceremonial_beast.tscn` —
   `ext_resource` block at 3-8, node tree at 101-206
2. `…/scratchpad/s16/x/animations/monsters/ceremonial_beast/ceremonial_beast_skel_data.tres`
3. `sts2src/MegaCrit.Sts2.Core.Models.Monsters/CeremonialBeast.cs:262` to end of
   `GenerateAnimator`, plus `:35` and `:219` for the `Unstun` trigger site
4. `sts2src/MegaCrit.Sts2.Core.Nodes.Vfx/NCeremonialBeastVfx.cs`
5. `sts2src/MegaCrit.Sts2.Core.Animation/AnimState.cs:43-82` (branch conditions
   and `NextState` — the beast is the reason this machinery exists)
6. `sts2src/MegaCrit.Sts2.Core.Nodes.Combat/NCreature.cs:916-954` (death length,
   death SFX gating) — the beast has two death states, so this is load-bearing
7. `docs/current/dossiers/enemies/ceremonial-beast.md` (phase structure only)

---

## 6. What this file does NOT establish

It does not say which animation approach we should use, what any body should
look like, or that any of these four bodies will be reskinned, remapped, or
built. It establishes only *how* to describe a body so four descriptions join,
and *which four* bodies give the widest evidence for the least reading. No
animation timing was measured, no frame was captured, and no runtime cost was
observed — the game was not launched. Clip durations, skeleton bone counts, and
every dynamic performance number remain UNKNOWN tonight and are marked as such
in the schema rather than estimated.
