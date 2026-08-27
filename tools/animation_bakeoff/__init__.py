"""Lane A (dispatch3) native-animation bake-off.

ONE original synthetic rig and ONE required-motion suite, compiled four ways --
layered sprites, cutout/skeletal 2D, mesh deformation, particles/tweens -- and
pushed through the same headless-editor import/export pipeline `tools/
build_pck.ps1` uses, so the four can be compared on repeatability, source
burden, package cost, and failure modes rather than on taste.

Nothing here is production art, a production scene, or a design decision. The
rig is drawn from primitives by `art.py` (circles, capsules, rounded boxes,
a diamond); no game, Genshin, or fetched asset is read or copied. The four
scene builders all consume the SAME semantic motion spec in `spec.py`, which is
the point: source burden is only comparable if the motion being authored is
identical.

Entry points:

    python -m tools.animation_bakeoff.build --out <dir>
    python -m tools.animation_bakeoff.measure --projects <dir> --out <dir>

and the lane-local export driver `tools/animation_bakeoff/export_bakeoff.ps1`,
which is a SEPARATE script from `tools/build_pck.ps1` (which this lane must not
run or edit) and only borrows its editor path and headless flags.
"""
