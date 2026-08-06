# Skeleton2D spike — Kokomi pilot (Track AN)

**Date:** 2026-08-06 · **Track AN, findings-only.** No design decisions. Path C
(layered `Sprite2D`) remains the shipped path, untouched. Nothing was deployed;
no game process was launched. Every claim below is either an offline
measurement or explicitly marked unproven.

**Authority ([USER], verbatim):** "Let's do FREE-SPIKE and reconsider if the
results disappoint." The reconsider trigger on record: disappointing spike
results re-open the Spine licence question (**$379 Professional; Essential
cannot author meshes**) without a new sitting. The reconsider decision itself
is [USER]'s; §6 gives this spike's self-assessment against that trigger.

Builds on `docs/animation-capability-memo.md` (F1: three paths, Path B
"unconstrained but zero working examples") and
`docs/animation-downfall-investigation-2026-08-05.md` (M-Q3: the probe harness
this spike reuses; a SpineSprite rig packs and renders via our pipeline when
spelled `.spskel`/`.spatlas`).

---

## 0. Verdict in one line

**PROMISING.** A Skeleton2D + weighted-Polygon2D Kokomi rig, with every vertex
weight computed from layer-mask images by a committed script, **packs through
the exact `build_pck.ps1` steps with zero errors, is CONVERTED by the editor
(binary `.scn` + `.remap` — the thing the spine probe's scenes never got),
instantiates headlessly with all bones, weights and clips intact, and loads
back out of the mounted `.pck` with its skinning data intact.** The only
untested link is the one no offline method can test: seating it as creature
`Visuals` in a live combat (§5).

---

## 1. Inventory: Kokomi has no Path C layers (finding)

The brief asked for an inventory of Kokomi's existing layered art. The
inventory result is that **there is none**:

| Asset | Klee | Furina | Kokomi |
|---|---|---|---|
| `pck-src/<char>/model/combat.tscn` | yes (5 layers) | yes (4 layers) | **no** |
| `tools/combat_layer_fences/<char>.yaml` | 86 lines | 120 lines | **no** |
| Cut layer PNGs + masks | yes | yes | **no** |
| What combat draws today | rig | rig | `combat_model.png`, a static 240×280 still |

Her only prepared source is the 4900×5700 portrait cutout
(`ImageGen/images/kokomi/model/kokomi_portrait_cutout.png`, Tier F,
machine-local; alpha bbox 4464×5405 — wide because of the companion fish left
and the fin sweep right).

**Consequence for the spike:** the "computed weights from layer masks" idea
needs mask images, so the generator SYNTHESIZES spike-grade masks from the
cutout's alpha (four overlapping horizontal bands: head 0–26%, chest 22–50%,
hips 46–74%, legs 70–100% of subject height). For Klee or Furina the same
computation would take the real fence-cut layer masks as-is; the weight
derivation is identical either way. The synthesized bands are apparatus, not
shipped art, and are the main quality gap between this rig and a real one
(§5e).

## 2. What was built

Apparatus: `tools/skeleton2d_spike/` (`gen_kokomi_rig.py` +
`build_spike_pck.ps1`; README there). Wired into nothing. The generator
refuses to write inside the repo (the texture derives from Tier F pixels) and
produces, in one scratch directory: the rig scene, the texture, the four
masks, the validation scripts, and an offline deform preview.

The scene is shaped exactly like the shipped creature contract
(`klee-mod/pck-src/furina/model/combat.tscn`): root → `Visuals`/`Facing`/`Rig`
+ `Bounds` + `CenterPos` + `IntentPos` + `AnimationPlayer` (RESET/idle/attack/
hurt/death) + `AnimationTree` with the same 4-state machine and transition
table. The difference is inside `Rig`: instead of 4 `Sprite2D`, a
`Skeleton2D` (bone chain Hips → Chest → Neck → Head, plus Legs) and four
`Polygon2D` regions skinned to it.

| Measure | This rig | Base-game median (F1 §1b) |
|---|---:|---:|
| Bones | **5** (4 weighted + 1 structural) | 64 |
| Regions | **4** | 28 |
| Weighted vertices | 112 (26–30 per region) | n/a (mesh-deformed atlas regions) |
| Texture | one 560×677 page (cutout /8) | one page, median 153 KB |
| Scene text | ~40 KB `.tscn`, no scripts | `.skel` median 138 KB |

The 5/4 vs 64/28 gap is deliberate: this spike proves the *structure* end to
end, not authoring parity. Given masks, bones and regions are rows in two
tables in the generator — the marginal cost of more of them is authoring the
masks (a fence config, Path C's existing cost class), not new tooling.

## 3. Computed weights from layer masks — the attached idea, measured

Method: Gaussian-blur each layer mask (σ = 4.5% of subject height ≈ 30 px)
into a soft ownership field; normalize the fields per pixel; a vertex's weight
for bone *B* is the normalized field value of *B*'s layer at the vertex. The
blur width **is** the blend zone.

Measured on the pilot: 112 vertices weighted, of which 62 carry a real blend
(second bone above 5%); weight arrays verified to match vertex counts in the
loaded scene; all four bone paths resolve against the skeleton. No hand
weight-painting anywhere — the rig is byte-regenerable from the committed
script, which answers F1 §6 item 11 (hand-painted rigs would have been our
first non-regenerable asset) **in the affirmative for Path B: no hand painting
is needed at all.**

An offline linear-blend-skinning preview (chest −10°, head +8°, FK-chained;
`preview_deform.png`, rest|posed side by side) shows the cut-from-splash art
bending smoothly at the band boundaries with **no visible tearing** at spike
blur widths — first evidence on F1 §6 item 10, though a real-renderer look at
combat scale remains open (§5b, §5c).

## 4. Pipeline validation — measured, offline

Same two MegaDot steps as `tools/build_pck.ps1`, same `strict` export preset
byte-for-byte, harness pattern reused from the M-Q3 probe:

| Step | Result |
|---|---|
| `--headless --import` | exit 0, **zero ERROR lines** — the gate `build_pck.ps1` actually enforces stays green |
| `--export-pack strict` | exit 0, zero errors. `combat.tscn` **CONVERTED** to binary `.scn` (15.3 KB) + `.remap` — the editor parsed the whole rig. Contrast the spine probe, whose scenes survived only as unparsed text with 4 ERROR lines. No `include_filter` change needed; core types pack under the shipped preset as-is |
| pack read-back (S5 parser) | 19 entries; scene, remap, imported `.ctex` all present |
| `spike_check.gd` (headless instantiate, in-project) | root `Node2D/KokomiCombat`; skeleton found, **bones=5**; 4 Polygon2D, each **bones=4**, skeleton path resolves, all bone paths resolve, weight arrays match vertex counts; 5 clips present; idle advanced 0.6 s → chest bone rotation **−0.03** (the authored key) |
| `pack_check.gd` (second project, mounts the exported `.pck`) | pack mounts, scene EXISTS, LOADS via remap, instantiates; **skinning data survives the binary conversion** (4 bones per region after round-trip) |

Three engine facts were paid for in the process (measured, recorded in the
apparatus README so the next rig does not re-pay them):

1. **`bones/N/path` is a Godot-3-ism.** In Godot 4.5, setting it is a silent
   no-op; the live surface is one `bones` Array alternating `NodePath,
   PackedFloat32Array`. First spelling produced a rig that packed and loaded
   perfectly with **zero** skinning — a structurally invisible defect until the
   check script counted bones.
2. **Scalar animation keys must be spelled as floats in `.tscn` text.** A
   value track whose `values` array mixes `0` (parsed as int) with floats
   silently interpolates to 0.0 — the clip plays and moves nothing. This can
   bite any hand-authored clip, not just this rig; our shipped scenes happen
   to spell floats correctly.
3. In `--script` SceneTree runs the root enters the tree only at first
   iteration (`Skeleton2D.get_bone_count()` errors in `_initialize`), and the
   headless dummy renderer reports an invalid skeleton RID — render-side
   skinning is unobservable offline (§5b).

## 5. Remaining unknowns — none inferable offline

a. **Does it seat as creature `Visuals` in combat?** The single load-bearing
   unknown. Everything structural says yes — `NCreatureVisuals` binds children
   by NAME not type (S5/F1 §2a), the scene carries the exact node contract,
   and the pack mounts and loads in a foreign project — but it has not been
   run in-game. The M-Q3 probe apparatus (`tools/probe_spine_pck/SpineProbe`
   + `deploy_probe.ps1`/`cleanup_probe.ps1`) is the ready-made way to close
   this: point the same throwaway mod at `res://kokomi_spike/combat.tscn`.
   Deliberately not done in this spike (deploy is out of scope).
b. **Render-side skinning quality.** The dummy renderer computes no
   deformation; the offline preview is our own math, not Godot's rasterizer.
c. **Look at 240×280, in motion** — a taste pass, which is [USER]'s.
d. **Timing against `AttackAnimDelay`/`CastAnimDelay`** — a played-frame
   question (same as Path C, already solved there once).
e. **Band masks are not fence masks.** The row-span outlines bridge
   x-concavities (the fish is fused into whatever band it crosses); a real
   character pass would digitize a fence config first — Path C's measured
   0.5–1.5-day cost class, which Kokomi needs under ANY path.

## 6. Self-assessment against the reconsider trigger

**PROMISING, not disappointing.** The spike set out to prove or kill Path B's
two unknowns that were rated "unanswerable without doing it once"
(capability memo §2b, §6 items 9–11):

- *"Do `Polygon2D` bone weights survive headless import and pack export?"* —
  **Yes, measured**, including the binary `.scn` conversion round-trip, under
  the shipped export preset with no pipeline change.
- *"Does cut-from-splash art tolerate weighting without tearing?"* — **Yes at
  spike scale in offline LBS**; real-renderer confirmation open.
- *"Is a hand-painted rig our first non-regenerable asset?"* — **Mooted**:
  computed-weights-from-masks removes the hand painting entirely, and with it
  Path B's authoring-reproducibility objection.

What the spike did **not** show: base-game rig parity (5 bones vs median 64 —
a scope choice, not a wall), the in-game seat (§5a — one prepared probe away),
and how it looks (taste). No blocker of the kind that killed Path A's editor
route was found; every step that could be tested offline passed on the first
architecturally-correct attempt. Whether this is enough to keep the Spine
licence question closed is [USER]'s call, per the trigger recorded above.

## 7. Reproduction

```
python tools\skeleton2d_spike\gen_kokomi_rig.py --out <scratch outside repo> ^
    --cutout <main checkout>\ImageGen\images\kokomi\model\kokomi_portrait_cutout.png
powershell -File tools\skeleton2d_spike\build_spike_pck.ps1 -ProjectDir <scratch>
```

Requires the MegaDot 4.5.1 console editor (path parameter on the runner), the
repo venv's Python (PIL + numpy), and the machine-local Kokomi cutout. Output
is entirely under the scratch directory; delete it to undo.
