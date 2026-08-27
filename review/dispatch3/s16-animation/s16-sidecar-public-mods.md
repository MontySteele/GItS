# S16 sidecar — how PUBLIC StS2 mods animate custom bodies, natively

> **This file decides nothing.** It is a research artifact from surplus-dispatch-3.
> Everything below describes what other people's published code does. No art
> direction, no rights call, no spend, no scope, no ship choice is made or
> implied here. Where a technical option is named it is labelled `PROPOSED`, and
> the pick is [USER]'s. Nothing here opens a balance window, moves a stamp, mints
> an id, or interprets a playtest. **No code, scene, asset, or text was copied
> from any of these projects** — LAW permits them as reference-reading only, and
> only abstractions and questions travel.

**Read `s16-00-schema.md` first.** This file is the public-mod sidecar the
schema's §3 asks for. It sits beside the joined capability matrix
(`s16-05-matrix.md`, the integrator's file); it is not a corpus body file and
does not follow the A–K body schema. The four base-game bodies answer *what the
base game does*; this file answers *what other shipping mods do instead, without
the base game's Spine pipeline*.

**Read on:** 2026-08-26. Nothing here was executed. The game was not launched
(PREFLIGHT: [USER] is playtesting on mod `0.2-1155`). Every claim below is read
off committed source, a committed binary header, or an installed DLL's metadata.

---

## 1. The search boundary — read this before believing any row

The charter allows one widening step past the pinned Downfall clone. Here is
exactly how far this file looked and where it stopped.

| Step | What was searched | Result |
|---|---|---|
| Start (mandated) | `lamali292/Downfall@32e61132052ae58e32cd33342d24136ffe18be12`, local read-only clone. **All 171 `.tscn` outside `.godot/`, all `.tres`, all `.cs`.** | 10 player/creature bodies classified; full node-type census taken |
| Widen (one round) | GitHub search: repo topics `sts2-mods` and `slay-the-spire-2`; repo-name/description search for StS2 character mods; `Alchyr`'s repo list | ~70 repo names seen; 14 opened; **8 character mods + 3 infrastructure repos** inspected at a pinned SHA |
| Depth inside the widened set | Full recursive git tree for each of the 11; **body scene source actually read for 4** (Samus, Pael, Furina, plus Downfall's Hexaghost) and **partially read for 2** (AveMujica, Alchemist — file listing + extensions only) | see §3 |
| Local corroboration | Base-game decompile at `…/scratchpad/sts2src/`; the **installed** `BaseLib.dll` (Workshop `3737335127`); the extracted base-game pck at `…/scratchpad/s16/x/` | used only to check claims, never to substitute for a public source |

**Stopped here, deliberately.** Not searched: the Steam Workshop and Nexus
listings (most skin/character mods there ship a `.pck` with no source repo —
`Sts2SkinManager`'s own comments name several such mods, e.g. `ATA_IronClad`,
`AncientWaifus`, and treats them as opaque packs); Discord; any repo whose only
evidence would be a README claim. Several repos returned by the `sts2-mods`
topic (`Slay-the-Spire-2-Optimization`, `Spire-Performance-Tuning-Suite`,
`st2-stability-fixes`, …) have the shape of listing spam and were **not** opened
or counted.

**A filename match was never treated as proof.** Every "this mod uses X" row
below was decided by reading node types inside the scene file, or by reading the
C# that drives it.

---

## 2. Downfall: ten bodies, and the surprise inside them

The charter's framing was that Downfall is "the first source where there is
evidence". For animation that holds — but **not in the direction the schema's
§3 sentence implies.** The schema says Downfall "ships raw Spine per character".
That is true for seven of its characters and it is only half the story:

| Body | `%Visuals` node type | Skeleton source committed | What actually animates it | Cite |
|---|---|---|---|---|
| Champ | `SpineSprite` | `champ.skel` + `champ.atlas` + **`champ.spine` (Spine editor project)** | C# trigger switch → `MegaAnimationState` with explicit mixes; four stance-keyed idle names | `Downfall@32e6113:Champ/scenes/character/champ.tscn:3-15`; `ChampCode/Vfx/NChampCreatureVisuals.cs:30-48,51-76` |
| Automaton | `SpineSprite` | `.skel`/`.atlas`/`.spine` | same shape; `idle_loop`, `cast`, `hurt`, `die` | `AutomatonCode/Vfx/NAutomatonCreatureVisuals.cs:25-46` |
| Awakened | `SpineSprite` **+ 2 `GPUParticles2D` + a script-driven `Node2D`** | `.skel`/`.atlas`/`.spine` | same shape, plus `SetParticles()` gated on state | `Awakened/scenes/character/awakened.tscn:31-70`; `AwakenedCode/Vfx/NAwakenedCreatureVisuals.cs:40-66,110` |
| Guardian | `SpineSprite` | `.skel`/`.atlas`/`.spine` | idle + die only; `Attack`/`Hit`/`Cast` are empty cases | `GuardianCode/Vfx/NGuardianCreatureVisuals.cs:29-37` |
| Hermit | `SpineSprite` | `.skel`/`.atlas`/`.spine` | idle/hurt/die; attack + cast empty | `HermitCode/Vfx/NHermitCreatureVisuals.cs:31-43` |
| Snecko | `SpineSprite` | `.skel`/`.atlas`/`.spine` | full five-case switch | `SneckoCode/Vfx/NSneckoCreatureVisuals.cs:34-51` |
| Slime Boss | `SpineSprite` | `.skel`/`.atlas`/`.spine` | idle + die only | `SlimeBossCode/Vfx/NSlimeBossCreatureVisuals.cs:55-63` |
| Collector | `SpineSprite` | `.spskel` + `.spatlas` only (**no editor project**) | idle/hurt via Spine, **plus two shader `ColorRect` "eyes" positioned every frame from Spine bone world coords** | `Collector/scenes/character/combat.tscn:12-86,101-165`; `CollectorCode/Vfx/NCollectorCreatureVisuals.cs:57-80,97-113` |
| Gremlins | **bare `Node2D`** | none on the player body | **pure Godot `Tween`** — position, scale, `modulate`, `ZIndex`, with `Cubic`/`Back` easing; six separate gremlin scenes are rotated through slots | `Gremlins/scenes/character/combat.tscn:13-14`; `GremlinsCode/Vfx/NGremlinsCreatureVisuals.cs:36-41,71-82,117-148` |
| **Hexaghost** | **`Node2D`, zero Spine anywhere** | none | **`AnimationTree` + `AnimationNodeStateMachine`** with five hand-keyed clips over 4 `GPUParticles2D`, 3 shader-quad `MeshInstance2D`, 2 `Sprite2D` | `Hexaghost/scenes/character/combat.tscn:3-20`; `Hexaghost/scenes/character/hexaghost_main.tscn:850-949` |

**Node-type census over all 171 `.tscn` in Downfall@32e6113** (this is the whole
project, not just bodies): `SpineSprite` 30, `CPUParticles2D` 46,
`GPUParticles2D` 27, `Sprite2D` 22, `Line2D` 20, `AnimationPlayer` 18,
`AnimationTree` 17, `AnimationNodeStateMachine` 17,
`AnimationNodeStateMachineTransition` 62, `ColorRect` 15, `MeshInstance2D` 3,
`AnimatedSprite2D` 2, `Skeleton2D`/`Bone2D`/`Polygon2D` **0**.

### 2.1 The Hexaghost row is the load-bearing one

Hexaghost is a **complete, shipped, spine-free player body** in a released
Workshop mod, and it is the closest public analogue to our `klee-mod` rigs.

- Scene: `hexaghost_main.tscn`, 39,858 B. One `CanvasGroup` holding four
  `GPUParticles2D` (smoke 40, hurt 70, cinders 100, glow 50), three
  `MeshInstance2D` each a `QuadMesh` with a scrolling-noise `ShaderMaterial`
  (`inner`/`middle`/`outer_smoke`), and two `Sprite2D` (core glow + a dead-core
  layer behind it). `hexaghost_main.tscn:866-949`.
- Clips authored **in the scene, not in an external tool**: `attack`,
  `cast` (1.3 s), `die` (4.0 s), `hurt` (0.9 s), `idle` (8.0 s, `loop_mode = 1`),
  plus `RESET`. `hexaghost_main.tscn:334,381,441,701,761`.
- State machine: five states, eight transitions, `Start → idle` automatic, each
  tell returning to idle with `xfade_time = 0.1`. `hexaghost_main.tscn:824-864`
  (the `transitions = [...]` line itself is `:863`).
- Live shader coupling: `NHexaghostVisuals` **duplicates** each smoke material at
  `_Ready` so instances do not share state, then drives `spin_speed` from the
  number of ignited flames. `HexaghostCode/Vfx/NHexaghostVisuals.cs:37-46,49-61`.
- Six orbiting flames are a **separate scene instanced at runtime**
  (`hexaghost_flame.tscn`: one shader `TextureRect` + one `GPUParticles2D`),
  loaded by path from `HexaghostCode/Vfx/NGhostflames.cs:76`.

**And nothing in Downfall's own code travels that state machine.**
`NHexaghostVisuals` assigns `_playback` at `:29` and never uses it; the
`combat.tscn` root script is the **base game's** `NCreatureVisuals`
(`Hexaghost/scenes/character/combat.tscn:3`), so Hexaghost is not one of the
`IAnimatedVisuals` implementors that Downfall's own Harmony patch dispatches to.
Its five state names are *exactly* the names BaseLib's generic adapter probes
for (§4.2). The most economical reading is that **BaseLib drives this body and
Downfall wrote no routing code for it at all** — see §8 UNKNOWN-1, because that
join is an inference from two verified halves, not an observed frame.

### 2.2 The slimes: an attack tell with no attack clip

Fifteen slime bodies (`SlimeBoss/scenes/slimes/combat/*.tscn`) each pair a Spine
`Visuals` that only really idles with a **native `AnimationPlayer` +
`AnimationTree` that keyframes the body's own transform**. `spiky_slime.tscn`'s
entire `attack` animation is one bezier track on `Visuals:position:x`, 0.5 s
long, two keys — a lunge (`:9-22`). The state machine is two states
(`:61-66`). This is the cheapest credible attack tell in the whole corpus:
**no new art, no new clip, one keyframe pair.**

Their skin economy is worth naming separately: `protector.tscn` binds its own
`protector.spatlas` to the **shared** `slime_m.spskel`
(`SlimeBoss/scenes/slimes/visuals/protector.tscn:3-4`). Across the 15 slime
visual scenes there are **5 distinct skeletons** (`slime_s`, `slime_m`,
`slime_alt_s`, `slime_alt_m`, `darkling`) and **21 atlases** — one rig, many
skins, where the only per-variant authoring is a texture and an atlas.

### 2.3 The atlas half of Spine is plain text

`protector.spatlas` is a 1,459-byte JSON envelope whose single key holds the
ordinary libGDX atlas text (`{"atlas_data":"\r\nprotector.png\r\nsize: 512,128\r\nformat: RGBA8888\r\n…"}`).
Only the `.spskel`/`.skel` half is binary. Downfall's raw `champ.atlas` is the
same text uncompressed, and carries `pma:true` — which is why every Downfall
visuals class sets `CanvasItemMaterial.BlendModeEnum.PremultAlpha` at `_Ready`
(e.g. `ChampCode/Vfx/NChampCreatureVisuals.cs:82-88`).

### 2.4 Three Spine data versions coexist in files that ship

Read from the binary headers (`…/scratchpad` scan, 2026-08-26):

| Where | Files | Spine data version |
|---|---|---|
| Base game v0.107.1 pck | `ironclad.skel`, `ceremonial_beast.spskel` | **4.2.43** |
| Downfall, raw exports beside a `.spine` project | 7 × `.skel` | **4.2.39** |
| Downfall, imported form only | 13 × `.spskel` | **4.2.11** |

Downfall is a released Workshop mod (README badge, item `3747508091`), so these
three coexist in a shipping configuration. That is evidence the runtime tolerates
minor-version skew inside Spine 4.2 — **not** proof, since nothing was run here.

---

## 3. The widened sample — 11 public repositories, pinned

Retrieved 2026-08-26. "License" is what the GitHub API reports; **absent means no
LICENSE file was detected**, which by default means all rights reserved. That is
a fact, not a rights opinion; the rights call is [USER]'s.

| Repo | Pinned SHA | License | Body approach found | Read depth |
|---|---|---|---|---|
| `lamali292/Downfall` | `32e61132052ae58e32cd33342d24136ffe18be12` | MIT (`LICENSE:1-3`, "Copyright (c) 2026 lamali") | Spine ×8, Tween-only ×1, **native AnimationTree ×1** | full |
| `Alchyr/BaseLib-StS2` | `4a97642d7843309cdf35c46a11e3f46132cee049` (= installed `BaseLib.dll` 3.4.5.0) | MIT | **infrastructure**: generic native-animation adapter + a synthesised sprite body | targeted, full files |
| `Alchyr/ModTemplate-StS2` | `55ca2c606e6c78dd39689a5cf979b243a49652e7` | none detected | **NON-FINDING** — no body scene at all | full tree |
| `ing-gom/Sts2SkinManager` | `d6c6c4bf05eac24d1e1c576170fa84f4d50f6dfb` | MIT | **infrastructure**: pck-level body swap/revert | targeted |
| `RobynLTW/Samus` | `fb64680b95cec5461746ab2f2bfea293faa2344b` | none detected | `AnimatedSprite2D` flipbook **and** a `.glb` `Skeleton3D` rig **and** a modulate-crossfade body | tree + 4 scenes |
| `Krakenmeister/PaelCharacter` | `067d391ceb6ac422f449930d4a992362d46b1166` | none detected | **one static `Sprite2D`**, animated entirely in `_Process` | tree + scene + script |
| `YeyuNeuvillette/STS2-FurinaMod` | `910e7417c6067b85b1cb88f813a6f53aad34a5e7` | none detected | **two static `Sprite2D` layers**, one visible at a time | tree + scene + script |
| `sethmcleod/sts2-the-alchemist` | `2ba315275ec74d54ae525244b4b79eb0683f0562` | MIT | raw Spine `.skel`+`.atlas`, **no editor project committed** | tree only |
| `Darkglade1/AveMujica` | `16a93e8a51609302ece2115506d9f00c67ca5265` | none detected | Spine `.spskel`/`.spatlas` per character, **plus a full second rig per `skin/`** | tree only |
| `MT-SUPER-POWER/Sts2ArknightsMod` | `e21bb4dd695e0d1bb32689ddacb18399a51441f6` | MIT | Spine, `.spine` editor project committed | tree only |
| `Blizzarre/Runesmith2-StS2` | `308b9423ac55cedc15304ee5e1dd17713fe7199b` | MIT | Spine, but for **runes/props**, not a body | tree only |

Also opened and set aside: `spencerqfox/sts2-custom-mods@5a39417…` (MIT) — seven
gameplay mods, **zero** `.tscn`/`.skel`/`.atlas` in the entire tree, so it has no
bearing on this question; `EchoNoName/FlandreScarletSts2CharacterMod@8603afb…` —
rich VFX scenes but the body scene was not located in the tree, so it is counted
only as an unresolved lead.

### 3.1 The three non-Spine bodies, in detail

**Samus — three different techniques in one repo.**
- `Samus/images/charui/Samus-Idle.tscn:7-29`: an `AnimatedSprite2D` over a
  `SpriteFrames` sub-resource; three PNG frames, `"speed": 5.0`, `"loop": true`.
  `Samus-Death` is the same shape over ten frames
  (`Samus/animations/Sprites/Samus-Death-01..10.png`).
- `Samus/animations/SamusExports/samus__Anim_imported.tscn:3-7`: instances
  `Samus-Animations.glb` and overrides a **`Skeleton3D` with 40+ bones**
  (quaternion rotations, per-bone positions). `Samus_Animations.tscn:5-44` wraps
  it in an `AnimationTree` state machine with `attack`/`die`/`hurt`/`idle`. This
  is the only *mesh-deforming skeletal* rig found anywhere in the sample — and it
  is 3D, imported into a 2D game.
- `Samus/scenes/samus/watcher.tscn:8-44`: a third body with states
  `Attack`/`Dead`/`Idle` (capitalised — see §4.2) whose death is a **bezier
  crossfade on `modulate:a`** between the live body and a `corpse.png`
  `TextureRect` (`:46-69`). A death tell with no death animation.
- Which of these is the shipped combat body is **UNKNOWN-2**:
  `SamusCode/Character/Samus.cs:27` points `CustomVisualPath` at
  `res://scenes/creature_visuals/samus-samus.tscn`, and that file is **not in the
  repository** and not covered by its `.gitignore`.

**Pael — the cheapest body that still reads as alive.**
`PaelCharacter/scenes/pael.tscn:21-27` makes `%Visuals` a single static
`Sprite2D`. All motion is code: `PaelCreatureVisuals._Process` runs a sine
"breath" on the body's scale (period 5.0 s, amplitude 0.03, X at half amplitude
so it squashes rather than pulses — `:79-90`), lerps a gold-pile child's scale
toward a target derived from `player.Gold` at rate `delta * 8`, and spawns drip
sprites from three marker nodes on a timer (`:38-53`). Three PNGs, one script,
no animation resource of any kind.

**Furina (a third-party Genshin mod, unrelated to ours) — layer swap as state.**
`Furina/scenes/Furina/furina.tscn:10-22`: `%Visuals` is a `Sprite2D` parent with
two `Sprite2D` children, `Furina` and `FurinaPneuma`, the second
`visible = false`. `Scripts/FurinaCreatureVisuals.cs:20-27` is the whole
animation system: `SetArkheState(bool)` flips the two `Visible` flags. Named here
only because it is the minimum viable "the body changed" tell in a shipped mod.

---

## 4. The four approaches, joined

Columns are the ones the dispatch asked for. **No approach is ranked.**

| Approach | Found in (pinned) | Authoring dependency | Runtime contract | License of the exemplar | What it does NOT prove |
|---|---|---|---|---|---|
| **Layered sprites** (static `Sprite2D`/`TextureRect` layers, moved or swapped by code, `AnimationPlayer`, or `Tween`) | Pael body; Furina layer swap; Downfall `WingFlare`; Hexaghost's core+dead-core pair; our own `klee-mod` rigs | **None beyond a raster editor.** PNGs + a `.tscn`. No importer, no external tool, no licence | `%Visuals` must be a `Node2D`-derived node; the base contract's 4 required nodes must exist; `HasSpineAnimation` is `false`, so the game's own animator never spawns and something must route triggers (§4.1) | PaelCharacter: **none detected**. Downfall: MIT | It does not prove the *look* is acceptable, that layer count scales to a complex silhouette, or that the result reads at combat distance. No frame was seen. It also does not prove parity with what Spine gives free: per-instance idle desync, mix/blend between clips, and bone attachment points |
| **Cutout / skeletal 2D** — *in the Godot sense* (`Skeleton2D` + `Bone2D` + `Polygon2D`) | **NOWHERE.** Zero occurrences across all Downfall `.tscn`/`.tres`/`.cs`, and none in any body scene read in the widened set | n/a | n/a | n/a | The absence is a real non-finding within the boundary in §1, **not** proof the engine lacks it or that nobody has done it. Four repos were read at tree depth only |
| **Cutout / skeletal 2D — as the ecosystem actually does it: Spine** | 8 of Downfall's 10 bodies; Alchemist; AveMujica; Arknights; Runesmith2 | **Spine editor.** Six Downfall characters commit the `.spine` editor project itself; Arknights commits `shamare.spine`. The runtime half is fetched at build time from Esoteric's S3 (`Downfall@32e6113:build/setup.ps1:22`) | `%Visuals` is a `SpineSprite`; `NCreatureVisuals._Ready` (`:217`) wraps it as `MegaSprite` and **nulls it with a warning if skeleton data fails to load** (`sts2src/MegaCrit.Sts2.Core.Nodes.Combat/NCreatureVisuals.cs:226-232`), silently demoting the body to a static pose. Two dispatch styles exist (§4.1) | Spine Runtimes License Agreement (last updated 2025-04-05, retrieved 2026-08-26): *"each user of the Products must obtain their own Spine Editor license"*. The mods' own MIT covers their code, **not** this | It does not prove a Spine-free authoring route to the same result exists. Per charter §4/S16 this cannot be PROPOSED as our answer; it is recorded as the thing a no-paid-tools path would have to reproduce |
| **Mesh deformation** | Two different things wear this name. (a) **Shader quads**: Hexaghost's three `MeshInstance2D`/`QuadMesh` smoke planes — a mesh used as a shader canvas, not deformed (`hexaghost_main.tscn:884-909`). (b) **Actual skeletal deformation**: Samus's `.glb` + `Skeleton3D` (`samus__Anim_imported.tscn:3-45`) | (a) a shader + noise textures; (b) **a full 3D DCC** (Blender or equivalent) exporting glTF, plus Godot's glTF importer — which `Downfall@32e6113:project.godot:69` explicitly disables for Blender (`import/blender/enabled=false`) | (a) an ordinary `CanvasItem` child, no special contract; (b) UNKNOWN — a `Skeleton3D` is not a `Node2D`, and how it is hosted inside the 2D body contract was not determined (see UNKNOWN-2) | Samus: **none detected** | (a) proves nothing about character animation — it is atmosphere. (b) is a single unreplicated instance whose shipped status could not be confirmed |
| **Particles / tweens** | Every mod in the sample. Downfall alone: 46 `CPUParticles2D`, 27 `GPUParticles2D`, 20 `Line2D`. Gremlins is animated by `Tween` and nothing else; `WingFlare` is a hand-rolled particle system in C# | **None.** One texture per emitter, or zero (`WingFlare` loads a single `spike.png`) | Emitters are ordinary children of the body. `Tween` is created per call (`node.CreateTween().SetParallel()`), so nothing persists in the scene. `Downfall@32e6113:GremlinsCode/Vfx/NGremlinsCreatureVisuals.cs:117-148` shows position + scale + a chained visibility callback | Downfall MIT | It does not prove particles can carry a *body*. In every case found they decorate a body that exists by some other means — except Gremlins, where the "body" is six separate creature scenes and the tween only arranges them |

**One authoring pattern is orthogonal to all four and worth its own line:**
one rig, many atlases (§2.2). Fifteen slimes on five skeletons — the only
per-variant authoring is a texture plus its atlas. (AveMujica also ships a
per-character `skin/` directory, but that one duplicates **both** halves —
`char_4185_amoris_avemujica.skel.spskel` *and* `.atlas.spatlas` — so it is a
second full rig, not the same economy. The slime case is the one that
demonstrates rig reuse.) Whatever rigging technique is chosen, the variant cost
*can* be a texture rather than a rig — that is a technique-independent finding.

### 4.1 Three different ways a public mod gets the game's triggers into a native animator

This is the seam. The base game's `NCreature.SetAnimationTrigger` is
`_spineAnimator?.SetTrigger(...)` and is a guaranteed no-op without Spine
(schema §1.3), yet **the method still runs**, so a Harmony patch on it fires
regardless. All three shapes below exploit exactly that.

| Shape | Who | Patch points | Dispatch target | Cite |
|---|---|---|---|---|
| **Interface on a scene script** | Downfall | `SetAnimationTrigger` **postfix**, `StartDeathAnim` postfix (→ `"Dead"`), `StartReviveAnim` postfix (→ `"Revive"`) | `if (__instance.Visuals is IAnimatedVisuals v) v.OnAnimationTrigger(trigger)` — 9 classes implement it | `Downfall@32e6113:DownfallCode/Patches/NCreatureAnimationPatch.cs:11-39`; `DownfallCode/Interfaces/IAnimatedVisuals.cs:3-6` |
| **Node lookup, no scene script** | our `klee-mod` | `SetAnimationTrigger` postfix + `StartDeathAnim` postfix | `visuals.GetNodeOrNull<AnimationTree>("%AnimationTree")` then `playback.Travel(state)` | `klee-mod/KleeCode/Vfx/CreatureAnimationRouter.cs:56-81,84-103` |
| **Generic adapter in the shared library** | BaseLib | `SetAnimationTrigger` **prefix** (gated `if (__instance.HasSpineAnimation) return true;`), `StartDeathAnim` postfix that overwrites the returned death length, an **async transpiler** on `AnimDie`, and a prefix on `AnimTempRevive` | `CustomAnimation.PlayCustomAnimation(node, names…)` → first of `AnimationTree` / `AnimationPlayer` / `AnimatedSprite2D` found | `BaseLib@4a97642:Patches/UI/CustomAnimationPatch.cs:16-27,30-47,50-57,59-78` |

Our own router's doc comment already credits Downfall for the patch shape
(`klee-mod/KleeCode/Vfx/CreatureAnimationRouter.cs:20-27`) — the pattern was
mirrored, not copied, and this file confirms that reading of their source.

### 4.2 BaseLib already ships a native-animation adapter, and it is installed on this machine

`BaseLib@4a97642:Utils/CustomAnimation.cs` is a general adapter nobody in our
docs currently names.

- **Discovery order** (`:11-19`): direct child `AnimationTree` → recursive
  `AnimationTree` → direct child `AnimationPlayer` → direct child
  `AnimatedSprite2D` → recursive `AnimationPlayer` → recursive
  `AnimatedSprite2D`. `FindNode` also probes the literal paths `Visuals/<name>`
  and `Body/<name>` (`:121-141`).
- **`AnimationTree` support is conditional**: the tree root must be an
  `AnimationNodeStateMachine`, else it logs *"BaseLib only supports AnimationTree
  using AnimationNodeStateMachine as tree root"* and refuses (`:54-61`).
- **The name probe** (`Patches/UI/CustomAnimationPatch.cs:67-75`), tried in order,
  first hit wins:

| Game trigger | Names BaseLib tries |
|---|---|
| `Hit` | `Hit`, `Hurt`, `hit`, `hurt` |
| `Dead` | `Dead`, `Die`, `dead`, `die` |
| anything else (`Idle`, `Attack`, `Cast`, `PowerUp`, …) | `<Trigger>`, `<trigger>` |
| revive (`AnimTempRevive` prefix, `:50-57`) | `revive`, `Revive` |
| death wait (`AnimDie` transpiler, `:40`) | `Dead`, `Die`, `die` |

  Hexaghost's five states (`idle`/`attack`/`cast`/`hurt`/`die`) and Samus's two
  sets (`attack`/`die`/`hurt`/`idle`; `Attack`/`Dead`/`Idle`) are all inside this
  probe list. **Our scenes name the death state `death`, which is not.**
- **BaseLib will synthesise a body from a single texture.**
  `Utils/NodeFactories/NCreatureVisualsFactory.cs:21-47` turns a `Texture2D` into
  an `NCreatureVisuals` with a `Sprite2D` `%Visuals` and an auto-sized `Bounds`;
  `:49-86` generates missing `Bounds`, `IntentPos`, `CenterPos`, and `FormVfx`
  with computed offsets. That is a zero-authoring floor for a custom body.
- **`FormVfx` is a mod-side convention, not a base-game node.** It appears in
  BaseLib's required list (`:9-19`) and in every Downfall `combat.tscn`, and
  **does not appear anywhere in the base decompile** (grep over
  `sts2src/MegaCrit.Sts2.Core.Nodes.Combat/`, 0 hits). The base contract's
  required set remains the four in schema §1.1.
- **Death length is taken over.** `CustomAnimationPatch.cs:16-27` replaces
  `StartDeathAnim`'s return with `min(CustomCharacterModel.DeathAnimTime, 5f)`
  whenever a custom animation exists — i.e. for a spine-less player body the
  combat pause is a **model property**, not a clip length. Downfall's monsters do
  the same the other way, via `DeathAnimLengthOverride => 0.2f` with
  `HasHurtSfx`/`HasDeathSfx` both `false`
  (`Downfall@32e6113:GremlinsCode/Core/GremlinsMonsterModel.cs:18-20`).

**Installed-version fact.** The BaseLib this machine builds against
(`klee-mod/local.props` → Workshop `3737335127`) reports FileVersion **3.4.5.0**
and ProductVersion `3.4.5+4a97642d7843309cdf35c46a11e3f46132cee049`; that commit
resolves in `Alchyr/BaseLib-StS2` (2026-08-14, "fix patches"). A UTF-8 string
scan of that DLL finds `CustomAnimation`, `PlayCustomAnimation`,
`HasCustomAnimation`, `CustomAnimationPatch`, `SendTriggerToOtherAnimators`,
`NCreatureVisualsFactory`, `UseAnimationTree`, `UseAnimatedSprite2D` — all
present. **`docs/current/STATE.md:159` records the pin as BaseLib 3.3.7.0**; the
installed DLL is 3.4.5.0. Recorded as a fact; reconciling the pin is not this
file's call.

---

## 5. Gotchas, from primary sources only

1. **The game's Spine binding API changed under mods between 0.107 and 0.108.**
   `Downfall@32e6113:DownfallCode/Compatibility/CompatibilityAnimation.cs:7-13`
   states it plainly: *"107 SetAnimation/AddAnimation/AddEmptyAnimation return
   MegaTrackEntry; 108 returns void (PRG-6985) and adds AddAnimationTracked"*,
   and warns that a direct call *"bakes one version's signature into IL and
   JIT-crashes the entire containing method on the other version."* Their fix is
   299 lines of cached reflection (`:32-92`), including re-implementing the base
   game's idle-loop desync by hand (`:262-299`) because they bypass
   `CreatureAnimator`. A native `AnimationTree` body does not touch this surface
   at all — its API is Godot's.
2. **A missing bone silently does nothing.** `MegaSpriteCompatibility.cs:13-27`
   probes `HasMethod("get_global_bone_transform")` and returns `null` rather than
   throwing. `NCollectorCreatureVisuals.cs:53-54` prints an error and carries on
   with un-positioned eyes.
3. **UID collisions are real.** `Downfall@32e6113:build/nuke_uids.py:16` strips
   every `uid="uid://…"` from scene files before packing.
4. **Raw images must not be packed.** `build/pack_mod.gd:3-6,83-92` skips
   `.png/.jpg/.webp/.ogg/.wav` and packs the `.import` plus the `.ctex` from
   `.godot/imported/` instead. `.tscn`, `.tres`, `.spatlas`, `.spskel` go in as
   text.
5. **Two incompatible packaging routes exist in the wild.** Downfall packs
   `.tscn` text directly with `PCKPacker` (`pack_mod.gd:25-26,87`).
   `Sts2SkinManager@d6c6c4b:…/VanillaBodyOverlayBuilder.cs:18-21,65-76` reads
   other mods' pcks and finds `X.tscn.remap` entries — the Godot *export*
   pipeline's form, pointing at a binary `.scn`. A tool that only understands one
   form will misread the other.
6. **Downfall junctions the extracted base-game asset tree into the project
   root** — `src`, `images`, `scenes`, `animations`, `addons`, and eight more
   (`build/link-assets.ps1:22-42`), sourced from a GDRE extraction
   (`README.md`, Path B). Our house rule forbids exactly this
   (`CLAUDE.md`: never link a gitignored asset directory into a worktree). Noted
   as a difference, not a recommendation — see transfer question 6.
7. **A shipped body scene can be absent from a public repo.** Samus's
   `CustomVisualPath` names `res://scenes/creature_visuals/samus-samus.tscn`,
   which is in the base-game namespace and not committed. Reading a mod's repo is
   not the same as reading what it ships.

---

## 6. NON-FINDINGS

Each of these was looked for and is genuinely absent within §1's boundary.

- **NF-1 — Godot 2D cutout rigs.** No `Skeleton2D`, `Bone2D`, or `Polygon2D`
  node in any file of Downfall@32e6113 (all `.tscn`, `.tres`, `.cs`), and none in
  any body scene read in the widened set. When public StS2 mods say "skeletal 2D"
  they mean Spine.
- **NF-2 — the community character template teaches no body technique.**
  `Alchyr/ModTemplate-StS2@55ca2c6`'s `CharacterModTemplate` contains **no
  `.tscn`, no `.skel`, no `.atlas`, no `.spine`** anywhere in its tree — only card
  and UI PNGs, localisation JSON, and C# content classes. Its character extends
  `PlaceholderCharacterModel` and inherits base-game placeholder visuals
  (`content/CharacterModTemplate/CharModCode/Character/CharMod.cs:12`). A new mod
  author is given no body at all.
- **NF-3 — no public mod in the sample documents its animation choice.** Not one
  of the 11 repos has a README section, ADR, or comment explaining *why* it chose
  Spine over native, or native over Spine. Every classification in this file was
  derived from source, never from prose.
- **NF-4 — no measured runtime cost anywhere.** No frame timings, draw-call
  counts, memory figures, or load-time numbers appear in any of the 11 repos.
  Nothing in this file supports a performance comparison of any kind.
- **NF-5 — no gameplay-scene 3D beyond one instance.** Samus's `.glb` is the only
  3D asset found in any sampled mod.

---

## 7. Facts this file establishes that were not previously in the repo

Stated separately so they are easy to check and easy to reject.

1. A shipped, released public StS2 mod animates a **player** body with a native
   Godot `AnimationTree` state machine and no Spine at all (Downfall's Hexaghost).
2. `BaseLib` — already a hard dependency of ours — ships a generic adapter that
   routes the game's triggers to `AnimationTree` / `AnimationPlayer` /
   `AnimatedSprite2D`, and the installed 3.4.5.0 DLL contains it.
3. BaseLib's death-name probe is `Dead`/`Die`/`dead`/`die`; our scenes name the
   state `death`.
4. `FormVfx` is a BaseLib/Downfall convention absent from the base game.
5. The Spine atlas format used by both the base game and mods is plain text
   inside a JSON envelope.
6. The game's Spine binding changed shape between 0.107 and 0.108, and public
   mods absorb that with reflection.
7. Skeleton reuse with per-variant atlases is an established public practice
   (5 rigs → 15 slimes).
8. A credible attack tell can be one bezier keyframe pair on the body's own
   `position:x`.

---

## 8. UNKNOWN

- **UNKNOWN-1 — who drives Hexaghost's state machine.** Both halves are verified
  (Downfall's code never travels it; BaseLib's probe list exactly covers its state
  names) but the join was not observed. *What would answer it:* an attended
  capture with Downfall installed, or a log read of BaseLib's
  `"SetAnimationTrigger called for …"` debug line during a Hexaghost fight.
- **UNKNOWN-2 — Samus's actual shipped body.** The repo contains three candidate
  techniques; `CustomVisualPath` points at an uncommitted file. *What would answer
  it:* reading the released Samus `.pck` index for
  `scenes/creature_visuals/samus-samus.tscn`.
- **UNKNOWN-3 — whether a `Skeleton3D` can host a body under the 2D contract, and
  at what cost.** *What would answer it:* Lane A, or reading the shipped Samus pck.
- **UNKNOWN-4 — whether BaseLib's prefix and our postfix both fire, and whether
  that double-travels a state.** Harmony runs postfixes even when a prefix skips
  the original; BaseLib's recursive search would find our `%AnimationTree`.
  *What would answer it:* a targeted `KleeTests` case or one attended log read.
- **UNKNOWN-5 — clip durations and blend behaviour for every Spine body.** Binary
  `.skel`; not parsed. Same limit the corpus files record.
- **UNKNOWN-6 — anything about how these bodies look or feel.** No frame was
  captured; no mod was run.
- **UNKNOWN-7 — the four tree-depth-only repos** (Alchemist, AveMujica,
  Arknights, Runesmith2). Their `.tscn` node contents were not read, so their rows
  in §3 rest on file extensions plus directory layout, which is weaker evidence
  than the rest of this file.

---

## 9. Transfer questions — questions only, no recommendations

Numbered for a pick list; each is [USER]'s or a lane's to answer, not this
file's.

1. **Naming.** Our scenes use `death`; BaseLib probes `Dead`/`Die`/`dead`/`die`
   and the base game's own constant is `die` (schema §1.2). Is our name a
   deliberate divergence, and should it stay?
2. **Ownership of the seam.** BaseLib already implements the generic route
   (§4.2). Does our `CreatureAnimationRouter` still need to exist, does it need to
   coexist deliberately, or is the answer to check UNKNOWN-4 first?
3. **Trigger coverage.** Downfall patches `StartReviveAnim` as well; we patch
   `SetAnimationTrigger` and `StartDeathAnim` only. Is revive a surface we care
   about?
4. **Idle desync.** The base game randomises loop timescale and phase per
   instance (schema §1.2) and Downfall re-implemented it by hand for Spine
   (`CompatibilityAnimation.cs:262-299`). Do our `AnimationTree` rigs need an
   equivalent, and is that a Lane A question?
5. **Attack tells without new art.** The slime pattern — one bezier track on the
   body's `position:x` — costs nothing to author. Is that a technique we want
   Lane A to include in its required-motion suite?
6. **Asset-tree access.** Downfall junctions the GDRE-extracted base-game tree
   into its project root; our LAW forbids linking gitignored asset trees into a
   worktree. Does anything in our pipeline need what that junction buys them, and
   if so by what permitted route?
7. **Scene scripts.** Downfall attaches a C# script to every body scene and
   dispatches through an interface; our pipeline rule makes scenes script-less.
   Does the script-less rule cost us anything the node-lookup route cannot
   recover?
8. **Variant economy.** If any future body needs variants, is the "one rig, many
   atlases" shape (§2.2) the right target for our own pipeline, whatever the
   rigging technique?
9. **Version-drift exposure.** Public mods absorbed a Spine-binding signature
   change with reflection. Does a native-`AnimationTree` route materially reduce
   that class of exposure for us, and is that worth measuring rather than
   assuming?
10. **The STATE pin.** `STATE.md:161` says BaseLib 3.3.7.0; the installed DLL is
    3.4.5.0. Which is the intended pin?

---

## 10. What this file does NOT establish

It does not say which animation approach we should use, what any body should look
like, whether any of these mods is good, or whether anything they do is legal for
us to do. No frame was captured, no mod was launched, no game was started, and no
runtime cost was measured — so nothing here supports a claim about how any of
these bodies looks, feels, or performs. Four of the eleven repositories were read
at directory-listing depth only. The absence of Godot 2D cutout rigs is an
absence inside a stated search boundary, not a statement about the engine. The
Spine licensing lines are quotations from a vendor document retrieved on one
date, recorded so [USER] can make a rights call; they are not legal advice and
not a call. Every "PROPOSED" in this file would still be a proposal after it is
read.
