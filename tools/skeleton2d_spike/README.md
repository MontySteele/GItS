# Skeleton2D spike (Track AN, 2026-08-06) — apparatus

One question: **can a Godot-native `Skeleton2D` + weighted `Polygon2D` rig,
with every vertex weight COMPUTED from layer-mask images instead of
hand-painted, survive our pack build and load back out of the pack?**
Path B of the animation capability memo had zero working examples anywhere in
reach (`git show pre-simplification-2026-08-06:docs/archive/animation-capability-memo.md`);
this directory built one, with Kokomi as the pilot.

Findings live in the spike's verdict memo: `git show d69b7a0`. The one link
that memo could not test offline — **does the rig seat as creature Visuals in a
LIVE combat** — was probed on 2026-08-08 and came back **YES** on every leg:
`PROBE-2026-08-08.md`, next to this file.

This is the apparatus, kept so the result is regenerable. It is wired into
nothing: no lint, no gate, no `build_pck.ps1` change, no CI, and **Path C
(layered `Sprite2D`) remains the shipped fallback untouched.**

## Rules this spike obeys

- **Pixels never enter the repo.** The rig texture derives from the Tier F
  Kokomi portrait cutout (`ImageGen/images/kokomi/model/`, machine-local);
  `gen_kokomi_rig.py` *refuses* an `--out` inside the repo.
- **Nothing is deployed.** No game process is launched by anything here. The
  in-game seat was answered by a separate probe that built its own throwaway
  package and reverted it (`PROBE-2026-08-08.md`); nothing in this directory
  ships, and Kokomi's shipped visuals are still the static
  `combat_model.png`.
- **No hand work.** The whole rig — masks, mesh, weights, clips, scene text —
  is regenerable from this script, the same invariant Path C's `--check`
  enforces.

## Run it

```
python tools\skeleton2d_spike\gen_kokomi_rig.py --out <scratch outside repo> ^
    [--cutout <path to kokomi_portrait_cutout.png>]
powershell -File tools\skeleton2d_spike\build_spike_pck.ps1 -ProjectDir <scratch>
```

The runner does the same two MegaDot steps `tools/build_pck.ps1` does
(headless `--import`, `--export-pack` with a byte-equivalent `strict` preset),
reads the pack back with `tools/probe_spine_pck/pck_read.py`, then runs two
headless SceneTree scripts: `spike_check.gd` (instantiate in-project, count
bones/polygons/weights, advance the idle clip) and `packcheck/pack_check.gd`
(mount the exported `.pck` from a second empty project and load the CONVERTED
scene out of it).

## Two engine facts this spike paid for (measured on MegaDot 4.5)

1. **`bones/N/path` is a Godot-3-ism.** `Polygon2D.set("bones/0/path", ...)`
   is a silent no-op in Godot 4; the live surface is one `bones` Array
   alternating `NodePath, PackedFloat32Array`.
2. **Scalar animation keys must be spelled as floats.** A value track whose
   `"values"` array contains `0` (int) alongside floats interpolates to 0.0
   silently — the clip "plays" and moves nothing. `0.0` fixes it. This can
   bite any hand-authored `.tscn` clip, not just this rig.

Also: in a `--script` SceneTree run, the root window enters the tree only when
iteration starts — `Skeleton2D.get_bone_count()` errors during
`_initialize()`, so checks run on the first `_process` frame. Under the
headless dummy renderer the skeleton's RenderingServer RID reports invalid;
render-side skinning is unobservable offline. **Both halves of that behave
differently live** (`PROBE-2026-08-08.md`): the RID is valid, and it is valid
*before* the bone count is — at `tree_entered` the skeleton still answers
`bones=0` while its RID already reads valid, so a live reader must sample a
frame late, not at construction.
