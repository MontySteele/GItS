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

## Track C — Shared tracked gauge (Burst + Encore)

Status: **CODE COMPLETE — acceptance rides the B4/D playtest passes.**

- C1 ✅ `pck-src/shared/gauge.tscn` (script-less): %BarBack/%BarFill/%Flash
  ColorRects + %ValueLabel + AnimationPlayer (RESET + "flash" double-pulse).
  One scene, two instantiations. Deviation (house-forced): the plan's
  "exposed knobs" can't be scene exports without a script — they live in
  GaugeBridge.GaugeSpec (fill color, anchor offset, visual span, label max,
  flash predicate) and the bridge applies them. Energy-orb-slot alternative
  rejected for v1: both gauges anchor to the creature (decision logged per
  C1; the orb slot stays open for a later pass).
- C2 ✅ `Vfx/GaugeBridge.cs` follows HexaghostVisualsBridge line-for-line
  where it can (Displays dict + IsInstanceValid staleness + lazy re-Setup +
  CombatVfxContainer + discard-before-setup). One structural deviation:
  the reference tracks its creature from a scene script's _Process; our
  scenes are script-less AND the plan bans _Process polling, so tracking
  is a RemoteTransform2D child of the creature node (engine transform
  propagation, no per-frame script). Setup entry = Harmony postfix on
  `NCombatUi.Activate(CombatState)` — the same surface the reference
  patches (verified present in decompiled v0.107.1).
- C3 ✅ Refresh call-site enumeration. Both resources already funnel every
  mutation through canonical methods (house rule predating this sprint),
  so the enumeration is short and closed:
  - **Klee Burst** (all in Powers/BurstResource.cs):
    `Gain` (reactions, burst_energy op, powers), `GainPreResolution`
    (skill-tag bonus in BeforeCardPlayed), `SyncBadge` (after EVERY card
    play — this is what makes the kit-cast whole-meter drain visible; the
    Spend override runs inside BaseLib's cost machinery with no Creature
    in scope). BaseLib PrepForCombat zeroing is covered by Setup's
    initial refresh at NCombatUi.Activate.
  - **Furina Encore** (all in Powers/FurinaResources.cs):
    `GainEncore` (gain), `SpendEncore` (deliberate spend — also the
    funnel under SpendEncoreOrHp's overdraw), `AbsorbDamage` (post-Block
    absorption). Fanfare/Burst side-effects don't touch the Encore gauge.
  - Future-proofing note: BaseLib's CustomResource exposes AmountChanged;
    if the funnels ever multiply, switch the bridge to that event instead
    of chasing call sites (recorded in the GaugeBridge doc comment).
- C4 ⏳ acceptance in playtest: tracking through position changes
  (RemoteTransform2D is engine-driven), no orphaned displays across room
  transitions (staleness dict + discard-before-setup), threshold flashes
  (Burst reaching 40 = "ready"; Encore draining to 0 = overdraw moment).
  Gauge label is bare numbers ("12/40") — no lore/naming audit surface.

Gates green: dotnet build 0 errors, pck rebuilt (gauge.scn in pack,
build id 20260723-173024+102e99a), staged validate OK, suite 586 passed.

## Track D — Onscreen Salon members

Status: **CODE COMPLETE — [USER] layout/composition look pass pending (D4).**

- D1 ✅ `pck-src/furina/ui/salon.tscn`: three square slots (StyleBoxFlat
  frame + TextureRect portrait + badge dot) in a flank line rising behind
  Furina's left shoulder (slots at (0,0)/(-36,-46)/(-72,-92) around a
  (-88,-70) creature anchor). Portraits are NOT placeholder discs after
  all: the three members are cards, so their loose card art already ships
  — the bridge assigns gentilhomme_usher / surintendante_chevalmarin /
  mademoiselle_crabaletta via KleeArt.CardPortrait; a missing PNG leaves
  a framed empty slot. Empty slots render as ghost frames (28% alpha).
- D2 ✅ `Vfx/SalonVisualsBridge.cs`: GaugeBridge skeleton verbatim
  (Displays dict, staleness, lazy re-Setup, RemoteTransform2D tracking,
  same NCombatUi.Activate postfix). Common-base extraction deliberately
  NOT done yet, per the plan's own rule (refactor after the second
  concrete bridge survives a playtest).
- D3 ✅ Minimal state animation: activate = scene-authored slotN_pop
  scale pop (multi-member deploys queue into a cascade — one
  AnimationPlayer can't play two pops at once); deactivate/dry =
  bridge-set desaturation (occupied+dry slots grey out and the badge dot
  flips hydro-blue→grey when Encore < the tick cost, i.e. members will
  attack dry at 0.75x).
- D4 ⏳ acceptance: composition changes within the same action resolution
  (Refresh sites: SalonMemberPower.Deploy — the single composition
  funnel, every gain goes through it and members are never removed
  mid-combat — plus FurinaResources.SyncMeters for the dry badge at
  every meter-sync moment); displays die with the room (staleness dict);
  non-Furina players never spawn the scene (IFurinaCharacter guard,
  mirroring the reference's is-not-Hexaghost check). [USER] look pass on
  layout/composition. No player-visible text on the scene — badge is a
  color dot, so no naming audit surface.

Gates green: dotnet build 0 errors, pck rebuilt (salon.scn in pack,
build id 20260723-174007+6d75d37), staged validate OK, suite 587 passed.
(One build stumble recorded for posterity: unique_name_in_owner on three
nodes all literally named "Portrait" collides — unique names are
per-scene, so the NODES must be named Slot1Portrait/Slot2Portrait/…;
MegaDot's export warning caught it.)

## Track E prep notes

- E: GhostflameModel.SpawnVfx recipe verified (fire-and-forget,
  AddChildSafely, self-free).

## Open [USER] items

- ~~A4 gate~~ ✅ passed 2026-07-23.
- B motion look approval — **OPEN** (B4 above: deploy + fight as Klee).
- D Salon layout/composition approval (opens with D).
- E timing feel approval (opens with E).
- Naming/lore audit for any player-visible gauge/Salon labels (opens with
  C/D; scene/node names are internal and exempt).
