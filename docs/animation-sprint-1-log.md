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

Status: **COMPLETE — A4 gate PASSED 2026-07-23. Tracks B–E are open.**

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
- A4 ✅ **GATE PASSED (2026-07-23).** User deployed and booted; eyes-on
  combat entry as Klee confirmed correct position/scale (screenshot:
  `docs/animation-sprint-1-a4-gate.png` — act-1 combat vs. Sproutfang,
  Klee rendering identically to the pre-scene build, MODDED (3) badge,
  v0.107.1). godot.log verified — every expected line present, exact
  match:
  - `[klee] pck build id: 20260723-161935+1752836`
  - 11× `[klee] convention scene ok:` (combat.tscn root=Node2D + the ten
    existing roster scenes across klee/furina)
  - `[BaseLib] Auto-converted 'res://klee/model/combat.tscn' from Node2D
    to NCreatureVisuals`
  - `[klee] combat visuals from convention scene
    res://klee/model/combat.tscn: NCreatureVisuals`

Gate hygiene: house checks were extended for the new authoring channel —
S6c and test_roster_runtime_contracts accept a resource authored EITHER as
a build_pck.ps1 heredoc OR as a klee-mod/pck-src file (contract line still
mandatory either way). Full repo suite green via validate.ps1 S7 (567
passed); staged-package validation: OK end-to-end.

## Track B — Klee layered-PNG character

Status: **CODE COMPLETE — [USER] motion look pass pending (B4).**

- B1 ✅ Layer cut from the wish splash (1069x1245) — but NOT the plan's
  nominal body/head/backpack/Dodoco: in this pose a head cut runs through
  hair overlaps (visible seams, weak payoff), while the splash's big
  elements separate almost surgically. Shipped 5 layers (z back→front):
  **smoke / floaters / dumpty / body / dodoco** — full rationale + method
  in docs/art-asset-manifest.md ("AS SHIPPED" section). Cut is scripted
  end-to-end in `tools/cut_klee_combat_layers.py` (fence polylines + flood
  partition + priority dilation + fill-behind inpaint); at-rest
  recomposition is pixel-exact by construction, and a worst-case
  displacement render showed no holes. Masters + shipped combat-scale
  PNGs land in ImageGen/images/model/layers/ (gitignored, F in
  art/SOURCES.tsv).
- B2 ✅ Animated scene. Deviation from the plan's "klee2.tscn": the
  conversion registry is path-keyed to `res://klee/model/combat.tscn`
  (Track A), so the animation ships INSIDE combat.tscn rather than as a
  sibling scene — same content, no second registration. Structure:
  `%Visuals/Rig/{Smoke,Floaters,Dumpty,Body,Dodoco}` (Sprite2D each,
  offsets from layers_combat.json), AnimationPlayer + `%AnimationTree`
  (state machine: exactly idle/attack/hurt/death + RESET, graph shape and
  switch/advance modes mirrored from hexaghost2.tscn — pattern, not
  copy). active=true in-scene (no scripts; nobody else would enable it).
  - idle 3s loop: body sway ±2, dodoco bob ±3.2 + wiggle, dumpty ±3.6 +
    micro-rotate, smoke x-drift, floaters counter-bob (combat px).
  - attack 0.5s: rig lunge +42px, contact peak at 0.15s = AttackAnimDelay.
  - hurt 0.4s: rig shake + red flash on the Body layer only.
  - death 1.0s: whole-rig fade/slump/rotate; death is terminal
    (death→End, no auto-return).
- B3 ✅ Trigger routing was Track A plumbing (KleeAnimationRouter postfix
  pair). AttackAnimDelay/CastAnimDelay already ship at 0.15f/0.25f
  (Klee.cs:250-252). Trigger map: Attack/Cast/PowerUp→attack, Hit→hurt,
  Dead→death (StartDeathAnim postfix), Idle/Revive→idle, unknown ignored.
- B4 ⏳ **[USER] look pass.** Deploy (game closed), boot, fight as Klee:
  idle should visibly breathe (dodoco bob is the tell), attack lunge
  syncs with damage numbers, getting hit flinches + flashes, death fades
  once. Non-combat rooms: rest/merchant/select scenes untouched (they
  bind other paths). pck build id this build: `20260723-171308+a23d87f`.
  Gates green: pck built + contents verified (combat.scn 13.5KB with
  animation data, 5 layer ctex present), staged validate: OK, full suite
  586 passed.

## Track C–E

Blocked pending C/D/E work (B4 look pass can run in parallel). Prep notes:

- C: reference bridge = HexaghostVisualsBridge (dict + IsInstanceValid +
  CombatVfxContainer + Track/Refresh/DiscardDisplay) — pattern verified
  present in the clone. C3's call-site enumeration comes from grepping
  BurstResource/KitBurst (Burst) and FurinaResources (Encore) mutators.
- D: ghostflames.tscn wheel composition verified; ours is a flank line.
- E: GhostflameModel.SpawnVfx recipe verified (fire-and-forget,
  AddChildSafely, self-free).

## Open [USER] items

- ~~A4 gate~~ ✅ passed 2026-07-23.
- B motion look approval — **OPEN** (B4 above: deploy + fight as Klee).
- D Salon layout/composition approval (opens with D).
- E timing feel approval (opens with E).
- Naming/lore audit for any player-visible gauge/Salon labels (opens with
  C/D; scene/node names are internal and exempt).
