# S5 — What the base game animates enemies with

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

**Question:** Godot-native skeletal (Skeleton2D/Bone2D), Spine runtime, sprite sheets /
AnimatedSprite, AnimationPlayer on textures, or something else?

**Answer: Spine.** Esoteric Software's Spine, via the official `spine-godot` GDExtension,
skeleton format 4.2.43. Not one enemy in the shipped game is animated any other way.
Godot's own skeletal nodes (`Skeleton2D`/`Bone2D`) appear **zero** times in the entire pack.

Read against `SlayTheSpire2.pck` (v0.107.1, commit 59260271, Godot 4.5.1) and
`data_sts2_windows_x86_64/sts2.dll`. Read-only; nothing extracted into the repo.

## Evidence

**1. The runtime ships next to the executable.**
`libspine_godot.windows.template_release.x86_64.dll` sits in the game root, and the pack
carries `addons/spine/spine_godot_extension.gdextension` (`entry_symbol =
spine_godot_library_init`, platform table for win/linux/mac/ios/android/web). This is the
upstream Esoteric `spine-godot` extension, unmodified in shape.

**2. Every monster ships a rig, and only a rig.**
`animations/monsters/` holds **101 folders — 101 of them Spine**, zero exceptions. Each is
the same four files: `<name>.skel`, `<name>.atlas`, `<name>.png`, and a
`<name>_skel_data.tres` of type `SpineSkeletonDataResource`. Pack-wide extension census:
163 `.spskel` + 169 `.spatlas` imported resources; **no** `SpriteFrames`, no per-enemy
frame sheets.

**3. The creature scenes bind the rig directly.**
`scenes/creature_visuals/*.tscn` — 126 scenes, **118 contain a `SpineSprite`**. The node
census across those scenes: 131 `SpineSprite`, 105 `SpineBoneNode`, 99 `SpineSlotNode`, and
**0 `AnimationPlayer`, 0 `AnimatedSprite2D`, 0 `Skeleton2D`**. Shape of a real one
(`bowlbug_egg.tscn`): a `Node2D` scripted with
`res://src/Core/Nodes/Combat/NCreatureVisuals.cs`, whose child is
`[node name="Visuals" type="SpineSprite"]` pointing at `bowlbug_skel_data.tres`, plus
`SpineSlotNode` children for attachment points. This is the `Visuals` node our own memory
already knew about — it is a `SpineSprite`.

**4. State transitions are Spine's, not Godot's.**
`bowlbug_skel_data.tres` declares `default_mix = 0.05` and nine explicit
`SpineAnimationMix` entries between named clips — `idle_loop`, `attack`, `hurt`, `die`,
`stunned_loop`, `headbutt_stunned`, `hurt_stunned`. Blending is Spine's AnimationState
mixing. There is no `AnimationTree` anywhere in the pack.

**5. The C# assembly agrees.**
`sts2.dll` strings: `src/Core/Nodes/Animation/NSpineAutoPlayer.cs`,
`src/Core/Nodes/Vfx/Utilities/NVfxSpine.cs`, `Core.Helpers.SpineNodeExtensions`,
`Core.Bindings.MegaSpine` / `MegaSpineBinding`, `WaitForSpineReady`, `RunWhenSpineReady`,
`ConnectSpineAnimatorSignals`, `SpineAnimationAccess`, `GetChildSpineNodes`,
`get_HasSpineAnimation`, `get_IsSpineNode`, `get_SpineClassName`, `_usesSpine`,
`get_HasPhobiaSpineSkin`. The game talks to Spine through GDExtension class-name binding
(`spineClassName`, `SpineMethods`, `SpineSignals`), not typed C# bindings — which is why
`SpineSprite` as a literal C# type name does not appear.

**6. Version.** The `.skel` binaries carry `4.2.43` in their header — Spine 4.2.

## Two corrections to what the repo currently believes

- `docs/art-asset-manifest.md` §"The combat model: no Spine required (Hexaghost proves it)"
  is **stale**. Neither `hexaghost` nor `champ` exists anywhere in v0.107.1's pack — the
  monster roster was replaced. There is no longer a shipped enemy built from TextureRect
  layers + `AnimationPlayer`. That road was real once; it is not the base game's road now.
- The eight non-Spine `creature_visuals` scenes are **not** an alternative pipeline. They
  are placeholders and an error state: `fallback.tscn` points at `images/monsters/error.png`,
  the three `the_adversary_mk_*` scenes share
  `images/monsters/the_adversary_placeholder.png`, `crusher.tscn` has a `Visuals` with no
  texture and `visible = false`.

But they are still useful, and this is the one operationally load-bearing find:
**`NCreatureVisuals` accepts a plain `Sprite2D` as its `Visuals` child.** The contract the
script needs is the node names — `Visuals`, `Bounds`, `CenterPos`, `IntentPos` — not the
node *type*. A mod creature can therefore be a static or hand-animated Sprite2D and still
sit correctly in combat. Whether that looks acceptable is a separate question, and it is
not this spike's question.

## Licensing, since the answer is Spine

Two different obligations, and only one of them touches us.

**Redistribution of the runtime: not our problem.** The Spine Runtimes License permits
distributing a Product containing the runtime, and MegaCrit already ships
`libspine_godot...dll` with the game. A Teyvat Spire mod adds no runtime binary; it would
load the one already present.

**Authoring rigs: our problem.** The Spine Runtimes License Agreement defers to §2 of the
Spine Editor License Agreement, which requires that "You have a valid Spine Editor license
at the time the Spine Runtimes are integrated into each Product," and §2.4 extends that
per-person: each individual creating or modifying a product containing the Runtimes must
hold their own Editor license — the SDK/library carve-out explicitly says "each user of
such an SDK, game toolkit, or software library must obtain a Spine Editor license." Nothing
in the agreement exempts free, non-commercial, or hobby work. Producing a `.skel`/`.atlas`
in the first place requires the Editor regardless; there is no free authoring path, and no
open-source exporter that is licence-clean.

Tiers: Essential and Professional are one-time purchases (Essential from ~$69; Professional
higher, upgrade-by-difference), and both are only available while gross revenue/financing
is under $500k USD in the trailing 12 months — above that, Enterprise. Meshes — which every
shipped enemy rig uses — are a **Professional** feature; Essential exports but does not
author them.

So the honest cost line for a Spine-native custom enemy is: one Professional seat per person
who touches the rig, plus an animator who knows Spine. The Sprite2D path in §"corrections"
above costs neither. That trade is item 2's decision, not this note's.

Sources: [Spine Runtimes License](https://en.esotericsoftware.com/spine-runtimes-license),
[Spine Editor License](https://en.esotericsoftware.com/spine-editor-license),
[Purchase Spine](https://en.esotericsoftware.com/spine-purchase).

## Method (for anyone re-running it)

The `.pck` is format 3: the file table lives at the **end**, its offset stored as a u64 at
header byte `0x20`, and entry offsets are relative to `file_base = 112`. 15,658 entries
parse with ~30 lines of Python — no GDRE Tools needed, and none was downloaded. Individual
`.tscn`/`.tres` are stored as plain text and read out by offset+size. Everything above came
from path listings and five small text reads; no bulk extraction, nothing written outside
the scratchpad.
