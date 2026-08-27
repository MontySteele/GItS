# S16 — corpus body: **elite or boss = Ceremonial Beast**

> **This file decides nothing.** It is a research artifact from surplus-dispatch-3
> (charter §4/S16). Every recommendation is a **technical** note labelled
> `PROPOSED`; taste, lore, art direction, rights, spend, scope and ship calls
> remain [USER]'s. Nothing here opens a balance window, moves a stamp, mints an
> id, or interprets a playtest. **No frame was captured — the game was not
> launched** ([USER] is playtesting on mod `0.2-1155`; PREFLIGHT forbids it).

Written against the common schema at
`review/dispatch3/s16-animation/s16-00-schema.md`, sections A–L in order.
Facts the schema already establishes in its §1 are cited, not re-derived.
Section **M** records three places where this body's evidence **corrects** the
schema's own text, per the §1 instruction to say so loudly.

Sibling corpus file already on disk and deliberately not duplicated:
`s16-body-normal-enemy.md` (Mawler). Its §D.4 — the `Idle` trigger is registered
across the engine and **never fired** — is used here as an established result and
is not re-proved.

---

## A. Identity and provenance

| Field | Content |
|---|---|
| `body_id` | `ceremonial_beast` |
| `role` | `elite-boss` — specifically a **boss**, not an elite |
| `class` | `MegaCrit.Sts2.Core.Models.Monsters.CeremonialBeast`, `sealed`, extends `MonsterModel` — `sts2src/MegaCrit.Sts2.Core.Models.Monsters/CeremonialBeast.cs:25` |
| `scene` | `res://scenes/creature_visuals/ceremonial_beast.tscn` — **69,046 B** packed, 206 lines, `format=3`, `load_steps=24`, `uid://cjwbcvu53vfj6` (line 1 of the extracted copy) |
| `reachability` | **Act 1 (`Overgrowth`)**, the default act (`Index => 0`, `IsDefault => true`, `sts2src/MegaCrit.Sts2.Core.Models.Acts/Overgrowth.cs:49`, `:51`). **Second of three** in `BossDiscoveryOrder`, between `VantomBoss` and `TheKinBoss` (`Overgrowth.cs:19-24`). Encounter `CeremonialBeastBoss`: `RoomType.Boss`, generates **exactly one** monster and nothing else, custom BGM `event:/music/act1_boss_ceremonial_beast`, custom background, camera scaled to `0.9×` and offset `Vector2.Down * 50` (`sts2src/MegaCrit.Sts2.Core.Models.Encounters/CeremonialBeastBoss.cs:11-34`). |
| `read_on` | 2026-08-26. Game install `C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2` (path from `klee-mod/local.props:3`), pack `SlayTheSpire2.pck`. Decompile per schema §0 (ILSpy 8.2, `SlayTheSpire2.dll` @ v0.107.1 — **version asserted by the schema, not independently re-checked here**). |

**Extraction provenance for this file.** Text resources were read from the
schema's existing extraction at
`…/scratchpad/s16/x/scenes/creature_visuals/ceremonial_beast.tscn` and
`…/scratchpad/s16/x/animations/monsters/ceremonial_beast/ceremonial_beast_skel_data.tres`.
Two artifacts were extracted **new** for this file, read-only, by byte offset
out of the pack (no tool installed, nothing written into any repo):

- `…/scratchpad/s16/x/skel/ceremonial_beast.spskel` — 334,655 B, the imported
  Spine skeleton. Header reads `4.2.43` and `./images/`.
- the imported atlas resource (2,660 B) and three `.import` stubs, dumped
  transiently and not kept.

> **Gotcha for anyone reusing `…/scratchpad/s16/pck.tsv` (worth Lane C knowing).**
> The `off` column in that TSV is **112 bytes short** of the true file offset —
> it predates the `file_base` fix now present in `pcklist.py:24`. `pckget.py`
> extracts correctly because it re-reads the pack; a raw `dd` from the TSV
> offset does not, and yields silently shifted data. Every offset used in this
> file is the TSV value **+112**, verified by the extracted content starting on
> a legible header. **Only sizes and paths were taken from the TSV**, and those
> are correct.

---

## B. Scene / resource topology

`res://scenes/creature_visuals/ceremonial_beast.tscn`, in tree order. Line
numbers are the extracted copy.

| # | path | type | unique name? | purpose | depends_on |
|---|---|---|---|---|---|
| 1 | `.` (`CeremonialBeast`) | `Node2D` + script `NCreatureVisuals` | — | the body root; satisfies schema §1.1 | ext `1_icv6p` (`:101-103`) |
| 2 | `EnergyParticlesBack` | `CPUParticles2D` | no | rear halo of drifting motes, behind the body | ext `4_tj5rw` texture, ext `shared_additive_mat` (`:105-125`) |
| 3 | `%Visuals` | `SpineSprite` | **yes** | the skeleton; `preview_skin="default"`, `preview_animation="attack"`, `position=(30,-19)`, `scale=(0.434394, 0.434394)`, `_edit_lock_` | ext `2_u1yuw` skeleton data (`:127-136`) |
| 4 | `Visuals/NCeremonialBeastVfx` | `Node` + script | no | the driver: subscribes to Spine animation events and owns the death gate | ext `3_qw6ot`; five `node_paths` (`:138-145`) |
| 5 | `Visuals/PlowStartTarget` | `SpineBoneNode` | no | binds bone `plow_target`; `bone_mode=1`, `show_behind_parent=true`, `position=(-9779.14, 119.707)` | — (`:147-151`) |
| 6 | `Visuals/PlowEndTarget` | `SpineBoneNode` | no | binds bone `plow_end_target`; `bone_mode=1`, `position=(3169.93, 128.915)` | — (`:153-157`) |
| 7 | `%Bounds` | `Control` | **yes** | hitbox rect: `offset_left=-298`, `offset_top=-560`, `offset_right=246`, `mouse_filter=2` | — (`:159-166`) |
| 8 | `%CenterPos` | `Marker2D` | **yes** | `VfxSpawnPosition`; `position=(-1,-211)` | — (`:168-170`) |
| 9 | `%IntentPos` | `Marker2D` | **yes** | intent anchor; `position=(-94,-577)` | — (`:172-174`) |
| 10 | `DeathParticles` | `GPUParticles2D` | no | the death burst: `amount=1500`, `lifetime=7.0`, `explosiveness=0.94`, `fixed_fps=0` | ext `7_tnfd6` texture, ext `shared_additive_mat`, sub `ParticleProcessMaterial_1w4kb` (`:176-184`) |
| 11 | `EnergyParticles` | `CPUParticles2D` | no | front halo, twin of #2 with `lifetime_randomness=0.2` instead of `0.37` and `position=(-28,-64)` instead of `(-28,-85)` | ext `4_tj5rw`, ext `shared_additive_mat` (`:186-206`) |

### `ext_resource` list (6)

| id | type | `res://` path | shared? |
|---|---|---|---|
| `1_icv6p` | Script | `src/Core/Nodes/Combat/NCreatureVisuals.cs` | shared by **every** creature body (schema §1.1) |
| `2_u1yuw` | SpineSkeletonDataResource | `animations/monsters/ceremonial_beast/ceremonial_beast_skel_data.tres` | private |
| `3_qw6ot` | Script | `src/Core/Nodes/Vfx/NCeremonialBeastVfx.cs` | private — one consumer |
| `4_tj5rw` | Texture2D | `images/vfx/monsters/ceremonial_beast/ceremonial_beast_death_particle.png` | private (5 raw occurrences of the name in the pack, all accounted for by its own `.import`, uid cache and the two directory entries plus this scene) |
| `7_tnfd6` | Texture2D | `images/vfx/short_rice_no_glow_particle.png` | **shared** — 11 raw occurrences pack-wide |
| `shared_additive_mat` | Material | `themes/canvas_item_material_additive_shared.tres` | **shared** — 205 raw occurrences of the resource path pack-wide |

Note the id `shared_additive_mat` is a **hand-written** `ext_resource` id, not a
generated one, and the same literal id string appears **1,119** times across the
pack — a house convention for the shared additive material. (Raw
`grep -a -o … | wc -l` counts over `SlayTheSpire2.pck`; these are upper bounds on
distinct references because directory entries and the uid cache also carry the
strings.)

### Nodes the §1.1 contract does not require, and what breaks without them

- **All six** of `EnergyParticlesBack`, `NCeremonialBeastVfx`,
  `PlowStartTarget`, `PlowEndTarget`, `DeathParticles`, `EnergyParticles` are
  optional to `NCreatureVisuals` — none is looked up by `_Ready`
  (`sts2src/MegaCrit.Sts2.Core.Nodes.Combat/NCreatureVisuals.cs:217-225`).
- But they are **not** optional to each other. `NCeremonialBeastVfx::_Ready`
  dereferences all five exported node paths with **no null guard**
  (`sts2src/MegaCrit.Sts2.Core.Nodes.Vfx/NCeremonialBeastVfx.cs:141-146`).
  Delete any one particle node or bone target and the driver throws at `_Ready`.
- Delete the **driver** instead and the scene still loads — but `DeathParticles`
  keeps the scene's default `emitting = true` (the driver is the only thing that
  sets `OneShot = true; Emitting = false`, `:141-142`), so **1,500 particles fire
  once at spawn instead of at death**, and the death gate in §F disappears.
  This is the cleanest single example in the corpus of a scene that is valid,
  loads, and is wrong.
- Contract nodes **absent** from this body: `%PhobiaModeVisuals` (no alternate
  body — phobia mode does nothing for the beast), `%OrbPos` (silently falls back
  to `%IntentPos`, `NCreatureVisuals.cs:224`), `%TalkPos` (stays null, `:225`).

### Sub-resources (17) — and why the file is 69 KB

`load_steps=24` = 6 `ext_resource` + 17 `sub_resource` + 1. Sixteen of the
seventeen are small curves/gradients feeding `ParticleProcessMaterial_1w4kb`. The
seventeenth is `Image_t2esa` (`:38-45`): a `2048 × 1` **`RGFloat`** image whose
`PackedByteArray` is a **single 60,071-byte line** — 87 % of the whole scene
file. It is the `emission_point_texture` for `emission_shape = 4` with
`emission_point_count = 1732` (`:80-81`): the death burst spawns from 1,732
baked point positions, embedded in the scene as decimal text.

**This is the single most transferable authoring fact in the file.** The scene's
size is not node complexity; it is one baked emission mask serialised inline.

---

## C. Node / layer / bone counts

| metric | value | source |
|---|---|---|
| `nodes_total` | **11** | `grep -c '^\[node'` on the extracted scene |
| `spine_sprites` | **1** | node #3 |
| `particle_emitters` | **3** — CPU **2**, GPU **1** | nodes #2, #10, #11 |
| `bone_nodes` (`SpineBoneNode` **in the scene**) | **2** | nodes #5, #6 |
| `slot_nodes` (`SpineSlotNode`) | **0** | none present |
| `markers` (`Marker2D`) | **2** | `%CenterPos`, `%IntentPos` |
| `sprite_layers` (`Sprite2D`) | **0** | none — the body is one skeleton |
| `driver_scripts` | **2** in the scene (`NCreatureVisuals` root, `NCeremonialBeastVfx`), **plus 1 outside it** (`NCeremonialBeastBgVfx`, §G) | `:102`, `:139` |
| `ext_resource` / `sub_resource` | **6** / **17** | `load_steps=24` |

**Skeleton-internal counts (schema §C honesty rule).**

- **Atlas: one page, `ceremonial_beast.png`, `size:650,1032`, `filter:Linear,Linear`,
  `scale:0.32`, `54` regions.** This is **verified** — the imported
  `SpineAtlasResource` stores the atlas as readable JSON-wrapped text
  (`.godot/imported/ceremonial_beast.atlas-e9cfb7b1d9ef9125ba44698e4885db59.spatlas`,
  2,660 B); no `_n`/`_s` normal or specular page exists (0 occurrences pack-wide).
- **Bone / slot / constraint counts inside the `.skel`: UNKNOWN.** A raw
  identifier scan of the 334,655-byte `.spskel` yields **62 distinct
  snake_case tokens** (`tail_2`…`tail_18`, `leg_*`, `arm_*_ik`, `antler_twist`,
  `neck_rotator`, `plow_target`, `plow_end_target`, `plow_start_const`,
  `plow_end_const`, `root_adjust`, …) mixed with 54 space-separated attachment
  names from the atlas. Bones, slots and constraints are **not separable without
  a real Spine binary parser** — `UNVERIFIED`, and deliberately reported as a
  token count rather than a bone count.
- **Verified cross-check that does matter:** the two bone names the scene binds
  by string, `plow_target` and `plow_end_target`, both **exist** in the skeleton
  (byte offsets 5241 and 7042 region of the extracted `.spskel`). A visual-QA
  gate can do exactly this check without a parser.

**Comparison to the other three corpus bodies** (packed scene bytes, from the pck
directory): `silent.tscn` 1,141 · `mawler.tscn` 1,204 · `ironclad.tscn` 2,701 ·
`necrobinder.tscn` 19,435 · **`ceremonial_beast.tscn` 69,046** · `regent.tscn`
75,694 · `test_subject.tscn` 139,319. The beast is *not* the biggest scene — but
it is the biggest **state machine** (§D).

---

## D. Animation / state names

### D.1 Referenced states — complete and verified

All eleven from `CeremonialBeast::GenerateAnimator`
(`sts2src/MegaCrit.Sts2.Core.Models.Monsters/CeremonialBeast.cs:262-307`). None
sets `BoundsContainer` — **the beast never re-points its hitbox**, unlike the
`BoundsContainer` bodies the schema §5.4 rejects.

| state id | looping | reached by | condition on the branch | `NextState` |
|---|---|---|---|---|
| `idle_loop` | **yes** | initial state (`:283`) | — | — |
| `attack` | no | anyState `Attack` (`:303`); `Hit`-branch source | — | `idle_loop` (`:277`) |
| `shrill` | no | anyState `Cast` (`:304`) | — | `idle_loop` (`:276`) |
| `plow` | no | anyState `Plow` (`:302`); **also** a branch on `idle_loop` (`:275`) — see D.4 | — | — |
| `plow_end` | no | branch `EndPlow` on `plow` **only** (`:279`) | — | `idle_loop` (`:280`) |
| `plow_end_die` | no | anyState `Dead` (`:286`) | `() => InMidCharge` | — |
| `die` | no | anyState `Dead` (`:285`) | `() => !InMidCharge` | — |
| `stun` | no | anyState `Stun` (`:301`); **and** the second `Hit` branch on 7 states (`:294-300`) | `() => IsStunnedByPlowRemoval` on the `Hit` form | `stun_loop` (`:281`) |
| `stun_loop` | **yes** | queued from `stun` | — | — |
| `wake_up` | no | anyState `Unstun` (`:284`) | — | `idle_loop` (`:282`) |
| `hurt` | no | the first `Hit` branch on 7 states (`:287-293`); anyState `PlowHit` (`:305`) — see D.4 | `() => ShouldPlayRegularHurtAnim` on the `Hit` form | `idle_loop` (`:278`) |

**The conditional machinery, stated plainly.** `ShouldPlayRegularHurtAnim` is
`!IsStunnedByPlowRemoval && !InMidCharge` (`:105-115`). Branches are evaluated in
insertion order and the first satisfied one wins (`AnimState::CallTrigger`,
`sts2src/MegaCrit.Sts2.Core.Animation/AnimState.cs:68-82`). The regular-hurt
branch is registered **before** the stun branch on all seven source states
(`:287-293` then `:294-300`). Therefore a `"Hit"` on this body resolves three
ways:

1. normal → `hurt`;
2. `IsStunnedByPlowRemoval == true` → `stun` (the phase break plays as a flinch
   that becomes the stun);
3. **`InMidCharge == true` and not stunned → neither branch matches, `CallTrigger`
   returns `null` on both the anyState and the current state, and
   `CreatureAnimator::SetTrigger` does nothing at all**
   (`…/Animation/CreatureAnimator.cs:67-78`). **The beast does not flinch during
   its charge.** No log line, no state change — a deliberate silent no-op, and
   the reason the whole `Func<bool>` mechanism exists.

The beast makes **eight** anyState registrations covering **seven** distinct
trigger names — `Unstun`, `Dead` (twice, conditionally), `Stun`, `Plow`,
`Attack`, `Cast`, `PlowHit` — against the
`MonsterModel` default's five (`Idle`, `Cast`, `Attack`, `Dead`, `Hit`,
`sts2src/MegaCrit.Sts2.Core.Models/MonsterModel.cs:602-618`). It registers
**`Idle` nowhere and `Revive` nowhere**: return-to-idle is done entirely by
`NextState` queuing (four of the eleven states carry it), and
`NCreature::StartReviveAnim` finds `HasTrigger("Revive") == false` and, for a
non-player, does nothing (`…/Nodes/Combat/NCreature.cs:957-963`).

### D.2 Skeleton-resident animations

`ceremonial_beast.skel` contains **12 animations**. The count is read directly
from the Spine 4.2 binary layout: the animations section's count varint is the
byte `0x0C` at offset **56270** of the extracted `.spskel`, immediately followed
by `0x07` and `attack` — the string-length-plus-one prefix of the first
animation name. (`dd` + `od` on
`…/scratchpad/s16/x/skel/ceremonial_beast.spskel`; **`UNVERIFIED` per schema §D**
in the sense that no real Spine parser was run, but the layout is unambiguous
and the twelve names below are each individually located by byte offset.)

Names, in the order they appear (alphabetical, as Spine stores them):

| # | name | byte offset | in D.1? |
|---|---|---|---|
| 1 | `attack` | 56272 | yes |
| 2 | `die` | 86715 | yes |
| 3 | `hurt` | 122013 | yes |
| 4 | `idle_loop` | 142339 | yes |
| 5 | `plow` | 150006 | yes |
| 6 | `plow_end` | 186519 | yes |
| 7 | `plow_end_die` | 202757 | yes |
| 8 | `shrill` | 248515 | yes |
| 9 | `stun` | 266759 | yes |
| 10 | `stun_loop` | 283059 | yes |
| 11 | `wake_up` | 291737 | yes |
| 12 | **`_ignore/die_deluxe`** | 295817 | **no** |

Independent corroboration of the eleven, per the schema's permitted sources:
`preview_animation = "attack"` in the scene (`:130`); the four `from`/`to` names
in the mix table (`idle_loop`, `hurt`, `attack`, `die`); and
`MonsterModel::GenerateBestiaryMoveList`'s probes for `revive`/`hurt`/`die`
(`MonsterModel.cs:497-509`) — of which **`revive` is absent from the skeleton
(0 occurrences in the 334,655-byte scan)**, so the beast contributes no revive
row to its bestiary entry.

### D.3 Orphans, both directions

- **Skeleton → code: one orphan.** `_ignore/die_deluxe`. The `_ignore/` prefix is
  a Spine folder-naming convention; the string appears **exactly once in the
  entire pack** and nothing in the decompile references it. It is an alternate
  death animation that shipped and cannot be reached.
- **Code → skeleton: zero orphans.** All eleven `AnimState` ids exist in the
  skeleton. This body would never emit the
  `could not find '<id>' animation on '<node>'` warning
  (`CreatureAnimator.cs:88-92`) in normal play.
- **Events: zero orphans, both directions.** The skeleton's event table declares
  **5** events (count byte `0x05` at offset 56174, immediately before the
  length prefix and `deathParticles` at 56176): `deathParticles`, `plowEnd`,
  `plowStart`, `turnOffEnergy`,
  `turnOnEnergy`. `NCeremonialBeastVfx::OnAnimationEvent` handles **exactly those
  five and no others** (`NCeremonialBeastVfx.cs:149-169`). A clean 1:1 contract
  between animator and code — the only such contract in the corpus, and the
  strongest single argument that Spine *events* (not Spine *bones*) are what a
  boss body actually needs from its authoring tool.
- **One unreferenced shipped texture.** `death_emitter.png` sits in the beast's
  own `animations/monsters/ceremonial_beast/` directory and its imported form
  costs **11,128 B** in the pack
  (`.godot/imported/death_emitter.png-c35cda4f712661a42396050384158dc0.ctex`).
  Its uid `uid://ceduigvfxfe17` appears **exactly once** pack-wide — inside its
  own `.import` file — and the string `death_emitter` appears only in that
  `.import`, the uid cache, and the two pack-directory path entries. **Nothing
  references it.** (Method: two `grep -a -o` passes over the whole 1.9 GB pack;
  offsets resolved against the directory table.) The scene uses
  `ceremonial_beast_death_particle.png` instead.

### D.4 Two dead registrations in the animator itself

1. **`PlowHit` is registered and never fired.** The trigger is declared as a
   const (`CeremonialBeast.cs:37`) and wired `AddAnyState("PlowHit", hurt)`
   (`:305`). The literal `"PlowHit"` occurs in **exactly those two places** in
   the whole decompile. ILSpy inlines `const string` at every use site, so a
   firing site would have shown as a third occurrence. There is none.
2. **The `idle_loop --Plow--> plow` branch is unreachable.** It is registered at
   `:275`, but `Plow` is *also* an anyState (`:302`), and
   `CreatureAnimator::SetTrigger` consults the anyState **first** and returns as
   soon as it matches (`CreatureAnimator.cs:69-73`). The anyState always matches,
   so the per-state branch can never fire. Harmless, and a good worked example of
   the resolution order for anyone writing a replacement animator.

Contrast worth recording: `EndPlow` is registered **only** as a per-state branch
on `plow` (`:279`), never as an anyState. That is the one place the per-state
mechanism is load-bearing on this body — it makes `plow_end` unplayable unless
the beast is actually mid-charge.

---

## E. Durations and transitions

### From `ceremonial_beast_skel_data.tres` (1,098 B packed)

`default_mix = 0.05` (the house default, schema §1.2). **Four** explicit mixes,
and the interesting fact is how few there are for eleven animations:

| from | to | mix | reading |
|---|---|---|---|
| `idle_loop` | `hurt` | **0.03** | the only blend faster than default: the flinch snaps |
| `attack` | `attack` | **0** (no `mix =` line) | instant cut — back-to-back attacks re-strike, they do not cross-fade |
| `hurt` | `hurt` | **0** | instant cut — rapid multi-hit reads as separate impacts |
| `hurt` | `die` | **0** | instant cut — dying out of a flinch does not smear |

Everything else — the whole `plow → plow_end` chain, the whole
`stun → stun_loop → wake_up` chain, `idle_loop → die`, `idle_loop → plow`,
`shrill` in and out — runs on `default_mix = 0.05`. **The boss's signature
sequences are all default-blended; only the hit/attack/death micro-transitions
were hand-authored.** Compare Mawler, whose four mixes are two `0.02` blends and
two instant cuts (schema §5.3).

### From code — `NextState` chains

`shrill → idle_loop` · `attack → idle_loop` · `hurt → idle_loop` ·
`plow_end → idle_loop` · `stun → stun_loop` · `wake_up → idle_loop`
(`CeremonialBeast.cs:276-282`). `plow`, `die` and `plow_end_die` deliberately
have **no** successor: the charge holds until `EndPlow`, and the two deaths hold
forever.

`NextState` is queued on the same Spine track at `SetNextState` time
(`CreatureAnimator.cs:108-111`, `:114-132`) — so `stun` queues `stun_loop`
immediately, and `stun_loop` inherits the looping desync treatment
(`OffsetLoopingAnimation`, `:169-174`).

### Caller-side waits — authored in C#, **not** read from the clip

`CreatureCmd::TriggerAnim` awaits a `waitTime` the *caller* passes, then
`Cmd.CustomScaledWait(min(waitTime*0.5, 0.25), waitTime)`
(`sts2src/MegaCrit.Sts2.Core.Commands/CreatureCmd.cs:915-948`). The clip length
is never consulted. The beast's six values:

| trigger | fired at | `waitTime` |
|---|---|---|
| `Attack` (Stamp) | `CeremonialBeast.cs:173` | **0.6 s** |
| `Plow` | `:182` | **0 s** (the move then hand-waits `0.5 + 0.5` around its own VFX, `:183-185`) |
| `EndPlow` | `:203` | **0 s** (then `0.5 s`, `:204`) |
| `Cast` (Beast Cry) | `:225` | **0 s** (then `0.3 s`, `:226`, and `0.75 s`, `:228`) |
| `Stun` | `:213` | **0.6 s** |
| `Unstun` | `:219` | **0.6 s** |

**Clip durations are UNKNOWN tonight** — they live in the binary `.skel` and are
read at runtime via `MegaTrackEntry::GetAnimationEnd`. Not estimated.

The one place a real clip length *is* used is death: `StartDeathAnim` returns
`GetCurrentAnimationLength()` clamped to 30 s (`NCreature.cs:945`, `:954`) and
that value is handed to `Hook.AfterDeath(...)` (`CreatureCmd.cs:513`, `:519`) —
so **the length of `die` (or `plow_end_die`) gates the boss reward screen.**

---

## F. Intent / attack / hit / death tells

Join key for S19 is the **trigger name**, per schema §G.

| tell | trigger | state played | who fires it (`file:line`) | blocking? | co-op visible? |
|---|---|---|---|---|---|
| idle | *(none)* | `idle_loop` | initial state, `CreatureAnimator` ctor `:39-59`; random start time and `0.9–1.1` time-scale | n/a | yes |
| Stamp (self-buff, turn 1) | `Attack` | `attack` → `idle_loop` | `CeremonialBeast.cs:173` | yes, **0.6 s** | yes |
| **Plow charge (signature)** | `Plow` | `plow` (holds) | `:182` | no wait on the trigger; the move blocks ~1.0 s around it | yes |
| Plow landing | `EndPlow` | `plow_end` → `idle_loop` | `:203` | no wait on the trigger; `0.5 s` after | yes |
| Beast Cry | `Cast` | `shrill` → `idle_loop` | `:225` | no wait on the trigger; `1.05 s` after | yes |
| Stomp | `Attack` | `attack` → `idle_loop` | `DamageCmd…WithAttackerAnim("Attack", 1f)`, `:234` | yes, 1 s | yes |
| Crush | `Attack` | `attack` → `idle_loop` | same shape, `:249` | yes, 1 s | yes |
| **Phase break** | `Stun` | `stun` → `stun_loop` | `CeremonialBeast::SetStunned`, `:213`, called from `PlowPower::AfterDamageReceived`, `…/Models.Powers/PlowPower.cs:42-45` | yes, **0.6 s** | yes |
| stunned turn | *(none — VFX only)* | `stun_loop` continues | `CreatureCmd::Stun` spawns `NStunnedVfx` on the creature's VFX container (`CreatureCmd.cs:885-907`) | — | yes |
| wake | `Unstun` | `wake_up` → `idle_loop` | `CeremonialBeast::StunnedMove`, `:219` | yes, **0.6 s** | yes |
| hit (normal) | `Hit` | `hurt` → `idle_loop` | `CreatureCmd.cs:325`, only when `damage > 0`, `receiver != dealer`, and not `ValueProp.SkipHurtAnim` (`:320-330`) | awaited via `Task.WhenAll` (`:337`) but `waitTime = 0` | yes |
| hit (at the break) | `Hit` | `stun` → `stun_loop` | same site; branch guarded by `IsStunnedByPlowRemoval` | as above | yes |
| **hit mid-charge** | `Hit` | **nothing** | same site; no branch matches, `SetTrigger` no-ops silently | no | n/a |
| death (normal) | `Dead` | `die` (holds) | `NCreature::StartDeathAnim`, `:944`; branch guard `!InMidCharge` | **yes** — the returned clip length gates `Hook.AfterDeath` | yes |
| **death mid-charge** | `Dead` | `plow_end_die` (holds) | same site; branch guard `InMidCharge` | same | yes |

**Death, in the detail the schema §1.3 asks for.** `StartDeathAnim`
(`NCreature.cs:916-955`) does everything interesting inside
`if (_spineAnimator != null)`: it plays `SfxCmd.PlayDeath` (`:936-939`), fires
`"Dead"` (`:944`), and reads the clip length (`:945`). The beast **does not**
override `DeathAnimLengthOverride`, so the base `0f` applies
(`MonsterModel.cs:321-323`) and the returned value is
`Mathf.Min(clipLength, 30f)` — **the animation is the authority.** It also sets
`ShouldFadeAfterDeath => false` (`CeremonialBeast.cs:73`), so the generic
`NMonsterDeathVfx` fade is skipped (`NCreature.cs:1027-1037`); the corpse
disappears by its own particle burst instead.

**The death gate — unique in the game.** `NCeremonialBeastVfx` implements
`IDeathDelayer` (`NCeremonialBeastVfx.cs:15`), whose contract is *"stop the
`NCreature` from being freed until the task returned from `GetDelayTask` is
complete"* (`…/Nodes/Vfx/IDeathDelayer.cs:5-11`). `NCreature::AnimDie` awaits
every `IDeathDelayer` child before `QueueFreeSafely()` (`NCreature.cs:1044-1053`).
The beast's task completes only when the `deathParticles` Spine event has fired
`Restart()` on the 1,500-particle emitter **and that emitter has emitted its
`Finished` signal** (`NCeremonialBeastVfx.cs:176-186`).

**`CeremonialBeast` is the only implementor of `IDeathDelayer` in the entire
decompile** (`grep -rn "IDeathDelayer" sts2src/` → the interface, this class, and
the one consumer). Two consequences worth carrying to the matrix: the death of
this boss is gated on a *particle system*, not on an animation; and the gate is
**skipped entirely** when the player has `FastMode == Instant`
(`NCreature.cs:1038`).

**`BoundsContainer`: not used.** None of the eleven states sets it, so
`UpdateBounds` fires once at spawn (`NCreature.cs:527`) and never again — the
`%Bounds` rect of `544 × 560` px is fixed for the whole fight even during the
charge.

**Two states reachable only through a retaliation window.** `InMidCharge` is
`true` for exactly lines `:181`–`:200` of `PlowMove` — the beast's own turn,
between setting the flag and clearing it after `DamageCmd.Attack(...)`.
`plow_end_die` therefore requires the beast to *die while attacking*, which needs
damage dealt back to it during its own move. Classes that could do that exist
(`sts2src/MegaCrit.Sts2.Core.Models.Powers/ThornsPower.cs`,
`…/ReflectPower.cs`) — **whether any Act 1 card, relic or potion can actually put
one on the player before this fight is UNKNOWN and was not traced.** The same
window is the only route to the silent mid-charge `Hit` no-op.

---

## G. VFX and audio hooks

### VFX — in the scene

| emitter | type | one-shot / looping | amount | texture | material |
|---|---|---|---|---|---|
| `EnergyParticlesBack` | `CPUParticles2D` | looping (`Emitting = true` at `_Ready`, `:143`) | 3 | `ceremonial_beast_death_particle.png` | `canvas_item_material_additive_shared.tres` |
| `EnergyParticles` | `CPUParticles2D` | looping (`:144`) | 3 | same | same |
| `DeathParticles` | `GPUParticles2D` | **one-shot, off at start** (`OneShot = true; Emitting = false`, `:141-142`) | **1500** | `short_rice_no_glow_particle.png` | same |

Both energy emitters use `local_coords = true`, `preprocess = 7.0`, `lifetime =
8.0`, a `280 × 75` rect emission shape, `direction = (0,-1)`, `spread = 20°`, and
the same colour `(0.45, 0.908, 1)` with the same 9-stop gradient — a rising cyan
haze in front of and behind the body. `preprocess = 7.0` means both are already
saturated on the first visible frame.

`DeathParticles` uses `emission_shape = 4` (points) with 1,732 baked points and
`explosiveness = 0.94` — effectively a single silhouette-shaped burst.

**A naming trap worth flagging for any art ledger (S17 / Lane B):** the texture
called `ceremonial_beast_death_particle.png` is used by the two **energy** haze
emitters, and the actual **death** burst uses the shared
`short_rice_no_glow_particle.png`. The filename is the opposite of the usage.
This is exactly the "a filename match is not proof" case from charter §3.5.

### VFX — attachment points

Two `SpineBoneNode`s, `bone_mode = 1`, `show_behind_parent = true`, bound to
skeleton bones `plow_target` and `plow_end_target`. Their authored local
positions are extreme — `x = -9779.14` and `x = +3169.93` — which at the
`Visuals` scale of `0.434394` is roughly **4,248 px left** and **1,377 px right**
of the body: off-screen charge endpoints.

What the driver does with them is narrow and worth stating exactly:
`_Ready` caches each node's `GlobalPosition` (`NCeremonialBeastVfx.cs:145-146`),
and the Spine events `plowStart` / `plowEnd` **restore that cached global
position** (`:200-208`). Nothing else in the decompile reads either field. The
semantics of `bone_mode = 1` live in the native
`libspine_godot.windows.template_release.x86_64.dll` and are **UNKNOWN** — it is
not decompilable with ILSpy. See **M.2**: the schema calls these *gameplay*
anchors; the evidence says they are *presentation* anchors.

### VFX — command-side, not in the body

The Plow move alone spawns, from C#: `NHorizontalLinesVfx` speed lines
(`CeremonialBeast.cs:184`), a `RadialBlur` from the left
(`:186`), `vfx/vfx_attack_blunt` on every target centre (`:187`),
`NLineBurstVfx` on the first target (`:193`), a strong `ScreenShake` at a
randomised 180±10° angle (`:196`), and a `DoHitStop` (`:199`). Beast Cry adds
`vfx/vfx_scream` (`:227`); Stomp and Crush each add `vfx/vfx_attack_slash` plus an
`NSpikeSplashVfx` in `VfxColor.Cyan` (`:241-242`, `:256-257`).

### VFX — the room, driven by the boss's own state

`NCeremonialBeastBgVfx`
(`sts2src/MegaCrit.Sts2.Core.Nodes.Vfx.Backgrounds/NCeremonialBeastBgVfx.cs`) is
a **second Spine skeleton**, in the background scene, that subscribes to
`CombatStateChanged` (`:102`) and plays:

| condition | background animation(s) |
|---|---|
| beast alive, `IsInSecondPhase == false` | background hidden entirely (`:134-137`) |
| second phase, HP > 33 % | `glow_spawn` → `glow_idle` (`:157-166`) |
| second phase, HP ≤ 33 %, alive | `skulls_spawn` → `glow_and_skulls_idle` (`:168-177`) |
| beast dead or gone | `glow_and_skulls_idle` → `plants_spawn` at 4.5 s (`:179-184`) |

**This is a surface neither player body has and the normal enemy does not have
either: the boss's phase and HP drive a separate skeleton in the room.** It is
also where the fight's music parameters are set — `ceremonial_beast_progress`
(1 while fighting, 5 once resolved) and `ringing` (1 while the local player
carries `RingingPower`, `:119-123`), both via
`NRunMusicController.UpdateMusicParameter`.

### Audio

| FMOD path | source | actually played? |
|---|---|---|
| `event:/sfx/enemy/enemy_attacks/ceremonial_beast/ceremonial_beast_attack` | inherited `MonsterModel::AttackSfx` (`MonsterModel.cs:292`) | **yes** — Stamp `:172`, Crush `:248`, and via `WithAttackerFx` on Stomp `:235` and Crush `:250` |
| `…/ceremonial_beast_cast` | inherited `MonsterModel::CastSfx` (`:294`) | **NO.** Beast Cry fires the `Cast` *trigger* but plays the explicit `ceremonial_beast_shrill` event instead (`:224-225`). `CastSfx` is inherited and dead on this body. |
| `…/ceremonial_beast_die` | **overridden** `DeathSfx` (`CeremonialBeast.cs:75`) | yes — but only inside `if (_spineAnimator != null)` (`NCreature.cs:933-939`) |
| `HurtSfx` | inherited `null` (`MonsterModel.cs:300`) | no — `HasHurtSfx` false, so `CreatureCmd.cs:326-329` skips it |
| `event:/sfx/enemy/enemy_impact_enemy_size/enemy_impact_fur` | `TakeDamageSfxType => DamageSfxType.Fur` (`CeremonialBeast.cs:77`) through `MonsterModel::TakeDamageSfx` (`:329`) | yes — `SfxCmd::PlayDamage` (`…/Commands/SfxCmd.cs:78-84`) from `CreatureCmd.cs:352`, with `EnemyImpact_Intensity = 2` |
| `…/ceremonial_beast_plow` | explicit literal `:180` | yes |
| `…/ceremonial_beast_plow_end` | explicit literal `:202` | yes |
| `…/ceremonial_beast_shrill` | explicit literal `:224` | yes |
| `…/ceremonial_beast_stun` | explicit literal `:212` | yes |
| `event:/music/act1_boss_ceremonial_beast` | `CeremonialBeastBoss::CustomBgm` (`:13`) | yes |

**The death-SFX gate from schema §1.3 bites here.** A spine-less replacement for
this body plays **no death sound at all** and returns a death length of `0`,
because both live inside the `_spineAnimator != null` block. The beast has no
`DeathAnimLengthOverride` to fall back on.

---

## H. Fallback behaviour

| failure | hard or silent | what actually happens |
|---|---|---|
| **missing scene** (`ceremonial_beast.tscn` absent or unparseable) | **hard, recovered** | `MonsterModel::CreateVisuals` catches, logs, reports to Sentry, and instantiates `res://scenes/creature_visuals/fallback.tscn` (1,064 B) — `MonsterModel.cs:420-437`, `:171` |
| **missing required `%` node** (`%Visuals`/`%Bounds`/`%IntentPos`/`%CenterPos`) | **hard, NOT recovered** | see **M.1** — the throw happens in `NCreatureVisuals::_Ready`, which runs when `NCreature::_Ready` adds the node to the tree (`NCreature.cs:487`), *after* `CreateVisuals()` already returned at `NCreature.cs:454`. The `try/catch` is not on the stack. |
| **missing animation name** | **silent** | `Log.Warn("could not find '<id>' animation on '<node>'")` and no state change (`CreatureAnimator.cs:88-92`, queued form `:116-120`). Not reachable for this body today — D.3 shows zero code→skeleton orphans. |
| **missing `.skel` / atlas** | **silent, catastrophic** | `NCreatureVisuals::_Ready` pushes `"Spine skeleton data failed to load for <name>, disabling spine animation."` and sets `SpineBody = null` (`NCreatureVisuals.cs:229-233`). `HasSpineAnimation` then false → **no animator is built at all** (`NCreature.cs:503-513`) → every trigger is a no-op (`:868-870`), no death SFX, death length 0. The body renders as a static `SpineSprite` with nothing on it. |
| **missing Spine bone for a `SpineBoneNode`** (`plow_target` / `plow_end_target`) | **UNKNOWN** | resolution happens in the native spine-godot DLL; not decompilable. Worth a Lane C probe. |
| **driver script absent** | **silent, wrong** | §B: `DeathParticles` keeps the scene's `emitting = true` and the death gate vanishes |
| **driver present, particle node absent** | **hard** | `NCeremonialBeastVfx::_Ready` null-derefs (`:141-146`) |
| **phobia mode** | **no-op** | no `%PhobiaModeVisuals` node, and `HasPhobiaSpineSkin` is the inherited `false` (`MonsterModel.cs:304`), so `OnPhobiaModeToggled` does nothing (`:643-653`) |
| **skin not found** | **not applicable** | `CeremonialBeast` does not override `SetupSkins`, so the base no-op runs (`MonsterModel.cs:598-600`); the atlas has one skin (`preview_skin = "default"`) |

---

## I. Authoring dependency

**What made this body.** Spine 2D — the extracted skeleton's header carries the
editor version **`4.2.43`** and images path `./images/`. The three consumed
formats are `SpineSkeletonFileResource` (`.skel`), `SpineAtlasResource`
(`.atlas` + one `.png` page), and `SpineSkeletonDataResource` (the `.tres` that
binds them and carries the mix table). The runtime is native:
`libspine_godot.windows.template_release.x86_64.dll` ships in the game
directory. Export settings visible in the artifacts: atlas `scale:0.32`,
`filter:Linear,Linear`, single `650 × 1032` page, 54 regions, no normal/specular
pages, and the imported texture is **not** VRAM-compressed
(`"vram_texture": false` in `ceremonial_beast.png.import`) — unlike the boss room
backgrounds, which are `.bptc.ctex`.

**Charter §4/S16 forbids proposing Spine or any paid/proprietary authoring as the
answer.** So, stated as a requirements list rather than a recommendation — what
a no-paid-tools path would have to reproduce **for a body of this class**:

1. **Named animation clips addressable by string**, because the entire
   `AnimState` machine keys on the Spine animation name.
2. **Animation events with string names, fired from inside a clip.** This is the
   beast's hard requirement and the one our current pipeline has no analogue
   for: five events drive every VFX transition, including the death gate.
   A `Godot.AnimationPlayer` method-call track is the obvious native
   equivalent — *stating the equivalence, not proposing it*.
3. **A queued follow-on clip on the same track** (`AddAnimation`), for the six
   `NextState` chains.
4. **Per-transition blend times, including exact zero**, for the four-row mix
   table — the instant cuts are authored, not missing.
5. **Randomised loop phase and time-scale** (`0.9–1.1`, ±0.1 s), or two copies of
   an enemy visibly breathe in lockstep (schema §1.2). Not relevant to a solo
   boss, but it is part of the grammar.
6. **A world-space attachment point that a script can pin**, for the charge
   endpoints.
7. **A completion signal on the death effect**, for `IDeathDelayer`.

**Our own pipeline, as the cost baseline.** `klee-mod/pck-src/**` text scenes,
MegaDot import, `tools/build_pck.ps1`, and the script-less-scene contract —
*"NO scripts in scenes… the pipeline's standing rule is script-less"*
(`klee-mod/pck-src/README.md:14-17`). Klee's combat rig is five `Sprite2D` layers under
`Visuals/Facing/Rig` plus `Bounds`/`CenterPos`/`IntentPos`, an `AnimationPlayer`
and an `AnimationTree` — 14,109 B of `.tscn`
(`klee-mod/pck-src/klee/model/combat.tscn:393-448`). Furina's is the same shape
at 15,359 B. **`klee-mod/pck-src/` contains `furina/`, `klee/` and `shared/` and
no monster or enemy directory at all** — we have never built a body of this
class, and there is no in-repo precedent to price against.

---

## J. Runtime / performance observables

### Static — verified tonight

| artifact | packed bytes |
|---|---|
| `res://scenes/creature_visuals/ceremonial_beast.tscn` | 69,046 |
| `…/ceremonial_beast_skel_data.tres` | 1,098 |
| imported skeleton `.spskel` | 334,655 |
| imported atlas `.spatlas` | 2,660 |
| atlas page `ceremonial_beast.png` → `.ctex` (no VRAM compression) | 363,794 |
| `ceremonial_beast_death_particle.png` → `.ctex` | 2,310 |
| **body subtotal** | **773,563 B ≈ 755 KiB** |
| shared, not charged to the body: `short_rice_no_glow_particle` `.ctex` | 180 |
| shared: `canvas_item_material_additive_shared.tres` | 102 |
| **orphaned, charged to nobody:** `death_emitter.png` `.ctex` | 11,128 |

Everything in the pack whose path contains `ceremonial_beast` — 68 entries —
totals **7,124,437 B ≈ 6.79 MiB**. That includes the boss *room* background
(two skeletons plus an 11-layer scene set, ~2.15 MiB), the map node skeleton and
its 1.65 MiB `.bptc` texture, two run-history icons, and eight "bead" textures
associated by filename only. **Caveat: filename association is not proof
(charter §3.5)** — the room and bead art are attributed to this boss by path, not
by a traced reference.

Emitter budget: **1,500** GPU particles one-shot with `fixed_fps = 0` (uncapped),
plus **6** CPU particles looping continuously with `preprocess = 7.0`.
Draw-affecting materials: **1**, and it is the shared additive material, so the
body adds no unique material to the frame.

### Dynamic — UNKNOWN, capture pending

Draw calls, frame cost, load time, particle cost of the death burst, and whether
the `IDeathDelayer` wait is perceptible: **all UNKNOWN**. The game was not
launched. Not estimated.

---

## K. Three annotated capture slots — **CAPTURE PENDING**

| field | `cap-1` — idle | `cap-2` — the Plow charge | `cap-3` — hit → death |
|---|---|---|---|
| `status` | capture pending | capture pending | capture pending |
| `blocked_by` | [USER] playtest — no game launch (PREFLIGHT) | same | same |
| `how_to_capture` | attended run, Act 1 default (`Overgrowth`), boss room; still frame + 3 s clip of `idle_loop` with the `%Bounds` rect overlaid (dev overlay or a measured screen-space rect from `offset_left=-298 / top=-560 / right=246`) | attended, same fight, phase 1 turn 2+; clip from the `Plow` trigger through `EndPlow` to return-to-idle, with audio, at ≥60 fps | attended, same fight; clip covering the last player hit, `die`, the 1,500-particle burst, and the moment the corpse is freed |
| `what_it_would_settle` | whether the fixed `544 × 560` bounds rect actually contains the silhouette (§F: it never moves, even during the charge), and where `%IntentPos` at `(-94,-577)` puts the intent relative to the antlers | the clip durations that are UNKNOWN in §E; whether the `plowStart`/`plowEnd` global-position pin (§G) produces a screen-fixed charge or a body-relative one; whether the authored `0 s` C# waits leave the animation visibly unfinished when the move's own `0.5 s` waits elapse | whether the death length returned to `Hook.AfterDeath` matches what is seen; **whether the `IDeathDelayer` particle gate is perceptible as a pause before the reward screen**; whether `enemy_impact_fur` and `ceremonial_beast_die` both land |
| extra worth grabbing | — | — | a second run with `FastMode = Instant` to observe the gate being skipped (`NCreature.cs:1038`) |

A fourth capture would be genuinely valuable and is **not** one of the schema's
three: **the phase break**, `Hit → stun → stun_loop`, then `Unstun → wake_up`,
with `NStunnedVfx` layered on top and the background switching from hidden to
`glow_spawn`. It is the only place the conditional-branch machinery is visible.

---

## L. Closing sections

### 1. UNKNOWN

| question | what would answer it |
|---|---|
| Every clip duration | parse the `.skel`, or capture `cap-2`/`cap-3` |
| Bone / slot / constraint counts inside the skeleton | a real Spine binary parser; the 62-token scan does not separate them |
| What `bone_mode = 1` means, and what happens if a `SpineBoneNode`'s `bone_name` does not resolve | native `libspine_godot` — not decompilable; needs an attended probe |
| Whether the mid-charge window (`InMidCharge`) is reachable in real play — i.e. whether an Act 1 player can put `ThornsPower`/`ReflectPower` on themselves before this boss | trace the Act 1 card/relic/potion pools; not done here |
| Therefore whether `plow_end_die` is reachable at all | same |
| Whether the room background, bead textures and map-node art are actually referenced by this boss's scenes | trace the background scene's `ext_resource`s; filename match is not proof |
| Whether monster animation triggers replicate per-seat in co-op or are re-derived locally | trace the multiplayer command path; `LocalContext.GetMe` is used for the *ringing* music parameter (`NCeremonialBeastBgVfx.cs:121`) but that is not the body |
| All dynamic performance numbers | capture |

### 2. NON-FINDINGS

- **No `.tres` state machine, no animation-tree resource, no timeline asset** for
  this body. Searched the whole `res://animations/monsters/ceremonial_beast/`
  directory in the pack directory listing: it contains **only** the `skel_data`
  `.tres`, three `.import` stubs, and the orphaned `death_emitter.png.import`.
  The state machine is C#, exactly as schema §1.2 says.
- **No `SpineSlotNode` anywhere on this body.** Slot-attached VFX is a real
  pattern in the game (Ironclad's `slash_mesh`, Kaiser Crab's five slots) — the
  beast simply does not use it. Its VFX hang off the root and two bone nodes.
- **No `BoundsContainer` on any of the eleven states.** The schema §5.4 rejects
  Test Subject and Knowledge Demon because their respawn machinery would dominate
  the file; the beast has none, which is why it reads cleanly.
- **No revive animation** in the skeleton and no `Revive` trigger registered.
- **No phobia-mode body and no skin variation.**
- **No second skeleton in the body.** Unlike Regent (three `SpineSprite`s,
  schema §5.2), the beast's structural complexity is entirely in its state
  machine. The *second* skeleton for this boss lives in the room background and
  is driven by a separate script.
- **No enemy or monster body exists in `klee-mod/pck-src/`.** Directories are
  `furina/`, `klee/`, `shared/` only.
- **`CastSfx` is inherited and never played** (§G) — searched every `SfxCmd`
  call in `CeremonialBeast.cs`.
- **`PlowHit` is registered and never fired** (§D.4) — searched every occurrence
  of the literal in the decompile.
- **`_ignore/die_deluxe` is referenced nowhere** (§D.3) — searched the whole
  1.9 GB pack for the string.

Search boundary for all of the above: the ILSpy decompile at
`…/scratchpad/sts2src/`, the extracted text resources under
`…/scratchpad/s16/x/`, the pack directory listing (15,658 entries), and raw
string searches over `SlayTheSpire2.pck`. **No search was done outside the game
pack, the decompile, and this repo.**

### 3. Transfer questions — questions only, against our BaseLib/Harmony path (schema §1.5)

Our router maps seven game triggers onto four `AnimationTree` states and
**ignores unknown triggers** (`klee-mod/KleeCode/Vfx/CreatureAnimationRouter.cs`,
`TriggerToState` table). Against this body that produces the following open
questions. **No recommendation, no numbers.**

1. Five of the beast's eight anyState triggers — `Plow`, `EndPlow`, `Stun`,
   `Unstun`, `PlowHit` — are not in our table and would be dropped silently. Is a
   bespoke-trigger extension point something our router should have, or is the
   right question whether a mod boss should need bespoke triggers at all?
2. Our `Dead` maps to a single `death` state. The beast has **two** deaths chosen
   by a `Func<bool>` at trigger time. Does our path need conditional branches, or
   is a single death animation the boundary of what a mod body attempts?
3. The base game's `Hit` on this body can resolve to `hurt`, to `stun`, or to
   **nothing**. Our router always travels to `hurt`. Is "never flinch during
   move X" a capability we would want, and if so does it belong in the router or
   in the scene?
4. The beast's five VFX transitions are driven by **Spine animation events**
   fired from inside the clip. `AnimationPlayer` method-call tracks are the
   native equivalent. What is the failure mode of a method-call track when the
   target node is missing, and how does that compare to §H's silent-freeze class?
5. `IDeathDelayer` is a `Node` interface checked by `GetChildrenRecursive<T>` on
   the `NCreature` (`NCreature.cs:1044`). Our scenes are **script-less by
   pipeline rule** (`klee-mod/pck-src/README.md`). Can a mod attach a
   `IDeathDelayer` implementor to a creature at runtime from `KleeCode`, and if
   so is that a Lane-C question or a Lane-D one?
6. §G's death-SFX gate means a spine-less enemy body plays no death sound and
   returns length 0. `DeathAnimLengthOverride` is the base game's own escape
   hatch (`MonsterModel.cs:321-323`). Is that hatch reachable from a mod monster,
   and does anything in our current player-only path exercise it?
7. The beast's `%Bounds` is a fixed `544 × 560` rect that never moves. Our rigs
   also have a static `Bounds`. Is there any body shape we intend to build where
   that is wrong, or is `BoundsContainer` a capability we can declare out of
   scope?
8. The boss's presentation extends into the **room background** as a second
   skeleton keyed to phase and HP, and into two FMOD music parameters. If a mod
   boss ever existed, where would that surface live — and is it reachable at all
   without a custom background?
9. The scene's 69 KB is one baked emission mask serialised as decimal text. Our
   `build_pck.ps1` path packs text scenes. Is a baked point emitter something our
   pipeline can produce, and does anyone want it to?
10. `_ignore/die_deluxe` and `death_emitter.png` are both shipped-and-unreachable
    in the base game. Is "declared but unreferenced" a class our own art ledger
    (S17 / Lane B) and QA gates (Lane C) should detect, and on which side —
    ledger or gate?

### 4. What this does NOT establish

This file describes one shipped body and nothing else. It does not say that the
Ceremonial Beast will be reskinned, remapped, or built; it does not propose an
animation approach, an authoring tool, a budget, or a scope; and it does not rank
Spine against anything. Every duration in the fight is authored in C# and every
clip length is unmeasured, so nothing here says how long any animation is. No
frame was captured, no performance number was observed, and the game was never
launched. The claims about what a replacement grammar "would have to reproduce"
are a requirements list read off this one body, not a specification and not a
recommendation. Where a fact could not be verified — bone counts, native
spine-godot behaviour, co-op replication, whether the mid-charge death is
reachable in play — it is marked UNKNOWN above rather than estimated.

---

## M. Three corrections to the schema's own text

Schema §1 instructs a corpus file that contradicts the shared grammar to say so
loudly. None of these changes the body pick — Ceremonial Beast remains the right
elite/boss body for every reason §5.4 gives — or the evidence contract.

### M.1 — §1.1 is wrong about what happens when a required `%` node is missing

The §1.1 table says a missing `%Visuals` / `%Bounds` / `%IntentPos` / `%CenterPos`
means *"`GetNode` throws → whole body falls back (1.4)"*. It does not.

`MonsterModel::CreateVisuals`'s `try/catch` wraps only
`PreloadManager.Cache.GetScene(VisualsPath).Instantiate<NCreatureVisuals>(...)`
(`MonsterModel.cs:420-432`). Instantiating a `PackedScene` does **not** run
`_Ready`. The call happens at `NCreature::Create` line **454**, and the visuals
node is added to the tree at `NCreature::_Ready` line **487** — a different call
stack entirely. The `GetNode<Control>("%Bounds")` throws in
`NCreatureVisuals::_Ready` (`:217-225`) **after** the `try/catch` has already
returned.

So the failure classes split three ways, not two:

| failure | outcome |
|---|---|
| scene **file** missing or unparseable | caught → `fallback.tscn` |
| scene loads, required `%` node missing | **uncaught throw at tree entry — no fallback scene** |
| scene loads, animation name missing | logged warning, frozen pose |

The middle row is the one a visual-QA gate should care about most, because it is
the one the engine does *not* recover from. **PROPOSED, technical:** a gate that
asserts the four required `%` names exist in every creature scene is cheap and
catches exactly this class. (Whether to build it is Lane C's question, not this
file's.)

### M.2 — §5.4 calls `PlowStartTarget` / `PlowEndTarget` "gameplay anchors"; the evidence says presentation anchors

§5.4's rationale cites *"`SpineBoneNode` targets used as **gameplay** anchors
(`PlowStartTarget` / `PlowEndTarget`)"*. Nothing in the decompile reads either
node for a gameplay purpose. The **only** consumers are
`NCeremonialBeastVfx::OnPlowStart` and `::OnPlowEnd`, which restore a cached
`GlobalPosition` (`NCeremonialBeastVfx.cs:200-208`). Damage, targeting, intent
placement and hit detection do not touch them: `PlowMove` computes nothing from
them (`CeremonialBeast.cs:178-206`), targeting is `DamageCmd.Attack(...)`, and
the hitbox is the fixed `%Bounds` rect.

They are still the right thing to point at — a script pinning a Spine bone to a
world position is a capability our layered rig has no answer for — but the claim
should carry to the joined matrix (`s16-joined-capability-matrix.md`, which the
schema §4 table calls `s16-05-matrix.md`) as **presentation** anchoring, not
gameplay anchoring.

### M.3 — §5.4 undersells the body: the strongest reason to pick it is not in the rationale

§5.4 justifies the pick on eleven `AnimState`s, conditional branches, both
particle types, and a `node_paths`-wired driver. All verified. But the most
transferable facts in this body are two the rationale does not mention:

- **`CeremonialBeast` is the only implementor of `IDeathDelayer` in the game.**
  Its death is gated on a particle system's `Finished` signal, not on an
  animation length — a whole mechanism that exists for exactly one body.
- **Its animator/skeleton event contract is exactly 1:1** — five Spine events
  declared, five handled, none orphaned in either direction — and that contract,
  not the bone rig, is what actually drives every VFX transition on the body.

Recorded so the matrix integrator carries the right reason forward. Neither
changes the pick; both strengthen it.
