# Animation Sprint 1 — Execution Log

Governing doc: docs/animation-sprint-1-plan.md. Opened 2026-07-23.
DECISIONS entry: "Animation sprint 1 opens: scene binding architecture".

## Pre-flight (2026-07-23) — all sprint inputs verified

- Decompiled game v0.107.1: current (game binary unchanged since 07-18;
  decompile from 07-21).
- BaseLib.dll 2026-07-21: re-decompiled this session; the
  `CustomCharacterModel` override surface is UNCHANGED by the 07-21 update.
- Downfall: cloned to session scratchpad @ main (reference-reading only,
  never vendored — license note recorded in DECISIONS.md).
- Furina C# command layer exists (FurinaResources.cs, SalonPowers.cs), so
  Tracks C/D have their substrate.

**Architecture finding that reshapes A1/B3 (recorded in DECISIONS.md):**
the plan's "script extending NCreatureVisuals" is Downfall's mechanism and
depends on their Godot.NET.Sdk build (ScriptPath mapping for scene-script
resolution). Our assembly is plain Microsoft.NET.Sdk and our pck pipeline is
deliberately script-less. Equivalent behavior ships from the outside instead:

1. Script-less `klee/model/combat.tscn`; BaseLib's `NCreatureVisualsFactory`
   converts the root to a real `NCreatureVisuals` (named-node inventory
   `%Visuals / Bounds / %CenterPos / IntentPos` mirrored from the factory's
   own contract — geometry identical to what the old texture route
   generated, so Track A is pure re-plumbing).
2. `Vfx/KleeAnimationRouter.cs`: Harmony postfix pair on
   `NCreature.SetAnimationTrigger` / `StartDeathAnim` (Downfall's own patch
   shape, mirrored not copied) routes triggers into a scene's
   `%AnimationTree` when one exists. Inert for every creature without a
   tree — including Track A's static scene. This satisfies B3's
   "IAnimatedVisuals-equivalent surface against our own interface" without
   scene scripts; the interface is the trigger→state map in the router.

## Track A — Scene binding proof

Status: **CODE COMPLETE, gate check A4 PENDING (needs eyes-on boot).**

- A1 ✅ `klee-mod/pck-src/klee/model/combat.tscn` (new git-tracked scene
  source channel; see pck-src/README.md). Built into klee.pck — verified
  present in the pack (combat.tscn remap + 1217-byte exported scene).
- A2 ✅ Confirmed override names against decompile + BaseLib (NOT Downfall's
  names): `CustomVisualPath` (registered path-keyed for NCreatureVisuals
  conversion) + `CreateCustomVisuals()` (wins when non-null). Klee.cs is
  scene-first with loud fallback chain: combat.tscn → combat_model.png →
  null/base. GenerateAnimator comment rewritten with the new regime.
- A3 ✅ Permanent telemetry: `Diagnostics/KleeSceneTelemetry.cs` logs one
  line per convention scene (path, found/missing, root type via SceneState —
  no instantiation, no side effects) + the pck build id.
  build_pck.ps1 now stamps `klee/build_id.tres` (timestamp + git sha);
  this build: `20260723-161935+1752836`.
- A4 ⏳ **GATE — [USER] boot check.** Deploy (game closed), boot, enter
  combat as Klee. Expected in godot.log:
  - `[klee] pck build id: 20260723-161935+<sha>`
  - `[klee] convention scene ok: res://klee/model/combat.tscn root=Node2D`
    (+ ten more `convention scene ok` lines for the existing roster scenes)
  - BaseLib: `Auto-converted 'res://klee/model/combat.tscn' from Node2D to
    NCreatureVisuals` (first combat) and/or
    `[klee] combat visuals from convention scene ...: NCreatureVisuals`
  - In combat: Klee renders at the same position/scale as before (the scene
    mirrors the generated geometry exactly — any visible shift = a binding
    bug, not a tuning knob).
  - Screenshot into this log, then B–E open.

Gate hygiene: house checks were extended for the new authoring channel —
S6c and test_roster_runtime_contracts accept a resource authored EITHER as
a build_pck.ps1 heredoc OR as a klee-mod/pck-src file (contract line still
mandatory either way). Full repo suite green via validate.ps1 S7 (567
passed); staged-package validation: OK end-to-end.

## Track B–E

Blocked on A4 per the ordering law. Prep notes:

- B: AttackAnimDelay/CastAnimDelay already ship at Hexaghost's 0.15/0.25.
  Router trigger map (Cast/PowerUp→attack, Revive→idle, unknown→ignored)
  is in KleeAnimationRouter and tunes at the [USER] look pass.
- C: reference bridge = HexaghostVisualsBridge (dict + IsInstanceValid +
  CombatVfxContainer + Track/Refresh/DiscardDisplay) — pattern verified
  present in the clone. C3's call-site enumeration comes from grepping
  BurstResource/KitBurst (Burst) and FurinaResources (Encore) mutators.
- D: ghostflames.tscn wheel composition verified; ours is a flank line.
- E: GhostflameModel.SpawnVfx recipe verified (fire-and-forget,
  AddChildSafely, self-free).

## Open [USER] items

- A4 gate: boot + combat + screenshot (above).
- B motion look approval (opens after A4).
- D Salon layout/composition approval (opens after A4).
- E timing feel approval (opens after A4).
- Naming/lore audit for any player-visible gauge/Salon labels (opens with
  C/D; scene/node names are internal and exempt).
