## Art pipeline

Tier F art never enters the repo. It may ship in a free public build (`LAW.md`, amended 2026-10-12); only the ledgers
(`art/SOURCES.tsv`, `art/plan.tsv`) and the tools are tracked.

```sh
python3 tools/art_fetch.py && python3 tools/art_process.py [--apply-picks art/picks.tsv]
python3 tools/art_coverage.py            # CI runs it WITHOUT --strict (empty bill on a runner)
python3 tools/art_hunt.py Furina ; python3 tools/art_contact_sheet.py --list
.venv/Scripts/python tools/cut_combat_layers.py klee [--check]
.venv/Scripts/python tools/cut_combat_layers.py --all [--check|--verify]   # 10 configs
.venv/Scripts/python tools/gen_furina_stills.py    # and gen_kokomi_stills.py
.venv/Scripts/python tools/gen_char_icon_outlines.py [--check]   # all three outline halos
.venv/Scripts/python tools/gen_mod_image.py [--check]      # Mods-screen badge, EB-161
.venv/Scripts/python tools/gen_multiplayer_hands.py [--check] [--art-root <checkout>]   # co-op treasure hands, from the game pck
```

`cut_combat_layers.py` cuts one illustration into layers behind a hand-digitized
fence config (`tools/combat_layer_fences/<name>.yaml`; `teyvat/<body>.yaml` are
the six bespoke boss rigs, codegen.md §Bespoke rigs at the commit
`operations/teyvat-frame.md` names). `--check` proves the shipped pixels are
what the fences say; `--verify` stacks them back up at their manifest offsets and diffs against the source, and GATES on that
for a config declaring `recompose_exact: true` — which the six do and configs
#1/#2 never claimed. `--art-root <checkout>` lets a worktree cut against the
main tree's `ImageGen/`, which is the only supported way to reach it (never
link an asset tree into a worktree). Kokomi's and Varka's configs (#9/#10)
prepare the source before fencing with `source_crop`, `source_scale` and
`source_pad` (Kokomi's 4900x5700 master is scaled to a quarter; Varka's is
padded to the 240x280 aspect so the box resize does not stretch him); fence
coordinates are in the prepared canvas. Kokomi's rig is
`pck-src/kokomi/model/combat.tscn`, which carries the optional
`cast`, `power` and `idle_low` states beside the four the router requires.
Varka's layers no longer ship: his scene is drawn from his model since
2026-10-13 (below).

**Klee's combat scene (`tools/klee_rig/`).** Klee's
`pck-src/klee/model/combat.tscn` is GENERATED, with the router contract (node
paths, seven states plus `setoff` and `jumpy`, one-shot lengths, state machine). Edit
`tools/klee_rig/klee.yaml` (which sheet each state plays, its tint keys) and
regenerate; never hand-edit the scene.

```sh
.venv/Scripts/python -m tools.klee_rig gen [--check]            # write / check combat.tscn (no art)
.venv/Scripts/python -m tools.klee_rig verify --art-root <main checkout> [--godot]
.venv/Scripts/python -m tools.klee_rig render --art-root <main checkout> --out <scratch dir>
```

Every state, Set Off's cheer included, draws Klee as `Visuals/Facing/Model`,
one Sprite2D per frame sheet
rendered from the official Klee model by `tools/klee_render/` (Blender +
mmd_tools; `clips.py` poses, `render.py` renders (style H1 + H3 lite's shader half, H1, plus a
`style` pass: the face/bomb protect mask and her surface-space grain),
`post.py` paints the 2D half (style G's chain plus H3 lite) over every raw frame (numpy + Pillow),
`pack.py` packs, `build.py` runs the lot). **The model never enters the repo or ImageGen** (its terms
forbid redistribution); only the renders do.

```sh
.venv/Scripts/python tools/klee_render/build.py --pmx <scratch>/可莉2.0.pmx --work <scratch dir> --art-root <main checkout>
.venv/Scripts/python tools/klee_render/pack.py --renders <scratch dir> --art-root <main checkout> [--check]
```

`pack.py` is the one producer of `ImageGen/images/model/frames/*.png` (her
ground shadow `klee_shadow.png` among them),
`model/klee_rest.png`, `ui/select_closeup.png` and the roster tile
`ui/select_portrait.png` (+ `_locked`, derived from it), and writes the committed
manifest `tools/klee_rig/klee_frames.json` (cells, counts, times, feet
anchors, no pixels) that `gen` reads for `combat.tscn` and the merchant scene
`pck-src/klee/model/merchant_character.tscn`. The scale lives in `build.py`:
300 texture px per model unit drawn at 0.5, so about 165 px hat-to-boot standing (`clips.STAND`) at
1080p.

`klee_frames.json` is the only art-derived input, so `gen` and
`tier0/tests/test_klee_rig.py` run anywhere. `verify --godot` loads the scene
in MegaDot headless and steps the AnimationTree at 60 Hz through idle,
attack, hurt, setoff, jumpy and death, checking the visible sheet and its frame, and
that the merchant loop autoplays. `render` opens a MegaDot window briefly and
writes a contact sheet and GIF per state at 1x and 2x to a scratch dir
(renders are never committed). The Skeleton2D rig of the old floating splash
that `setoff` used to cross-fade to was retired on 2026-10-13 (owner: "I
regret keeping that around"); its cut layers no longer ship, except Dodoco,
which `pck-src/klee/vfx/dodoco_pop.tscn` draws.

**The other kits' model renders (`tools/char_render/`, Varka first, 2026-10-13).**
The same pipeline for a kit whose `chars.py` entry names a pose library:
`toon.py` is the Blender half both renderers import (style H1's STYLE, the
hull, the `style` pass, posing, framing; Klee's `render.py` uses it too, so
there is one STYLE), `render.py` renders a kit's clips and stills (its blades
are PMX props each closed in a hand by IK, and every clip's json records the
blades' projected base and tip), `tools/klee_render/post.py` paints them,
`fx.py` draws the colourless slash trails and impact bursts the game tints
per element, and `pack.py` writes `ImageGen/images/<char>/...` plus the
committed manifest `tools/char_render/<char>_frames.json`. Each frame is
trimmed to its own pixels and shelf-packed (`frames`: page, rect, and offset
in the clip's cell, an AtlasTexture margin in Godot); a clip too big for one
4096 sheet continues on `_p2`, `_p3` pages. Pixels under the ground line
are cut, so planted blades read as driven in. Varka's pose library is
`varka_clips.py`; his paper is `review/active/varka-visual-paper-2026-10-13.md`.
Furina's is `furina_clips.py` (phase A, `review/active/furina-visual-paper-2026-10-13.md`):
no blades, a phantom rapier off her far hand (`PHANTOM`) for the attack's
trail, her eleven guest stars as one still each (`render.py --guests`, at her
px per inch: `chars.guest_ppu`), and Spend, Drain and Repay as stage effect
clips (`fx.STAGE_EFFECTS`).

```sh
.venv/Scripts/python tools/char_render/build.py --char varka|furina --models <scratch>/models --work <scratch dir> --art-root <scratch art root>
.venv/Scripts/python tools/char_render/pack.py --char varka --renders <scratch dir> --art-root <dir> [--check]
```

**Varka's scenes (`tools/varka_rig/`, phase B, 2026-10-13).** His
`pck-src/varka/model/combat.tscn` and `merchant_character.tscn` are GENERATED
from `tools/varka_rig/varka.yaml` and `tools/char_render/varka_frames.json`,
Klee's shape: the router contract plus an `ascension` state, the shadow, one
Sprite2D per clip under `Visuals/Facing/Model`. Each frame is an AtlasTexture
(region = its rect on its page, margin = its offset and the trimmed
remainder of the cell) and a state steps the sprite's `texture`. Over the body,
`%AttackFx` and `%AscensionFx` draw the neutral element layer from the frame
the manifest names, and `%GroundBurst` (at the blade's point) and
`%TargetBurst` (mirrored by a negative x scale) play the ground burst from
the ascension's impact frame. One ShaderMaterial, local to each instance,
tints all four: `KleeMod.Vfx.ElementTrail` sets its `element` from the
played card's element (`ElementHitFx.ElementOf`; Anemo when there is none)
and moves `%TargetBurst` under the target. `CardPlayMotion` sends an
`Ascension` trigger for Four Winds' Ascension; the router plays `ascension`
and absorbs the card's own lunge. `build_pck.ps1` copies
`ImageGen/images/varka/model/frames/*.png` with an `.import` asking for VRAM
compression (`Write-TextureImport`, the manifest's `texture_import`), and
switches his rest scene to `varka_rest.png` and his select art to
`ui/select_closeup.png` when they exist. `char_render/pack.py` is the one
producer of all of them and of his roster tile (`art_lint.GENERATOR_OWNED`).
Never hand-edit the scenes:

```sh
.venv/Scripts/python -m tools.varka_rig gen [--check]           # write / check both scenes (no art)
```

**Furina's scenes (`tools/furina_rig/`, phase B, 2026-10-13).** Varka's
generator is the template and lends its primitives. Her
`pck-src/furina/model/combat.tscn` and `merchant_character.tscn` come from
`tools/furina_rig/furina.yaml` and `tools/char_render/furina_frames.json`:
the router contract plus a `rejoice` state (Let the People Rejoice;
`CardPlayMotion` sends `Rejoice`, the router absorbs the card's lunge), and
`%AttackFx`, the phantom rapier's trail, on the element shader resting at
Hydro (the node's `rest_element`, read by `ElementTrail`). The Spend, Drain
and Repay effects are sprites under `Visuals/Facing/StageFx` at her chest,
each on its manifest tint with an AnimationPlayer of its own at the root
(`%SpendFxPlayer` and so on); `StageDirector` asks the board for one on each
Spend, Drain and Repay (`IStageBoard.Effect`), and `KleeMod.Vfx.FurinaStageFx`
plays it without waiting, stretching Drain and Repay along x to the nearest
seated guest. `tools/furina_rig/guests.py` writes the eleven
`guest_<name>.tscn` from the manifest's `guests` (the trio's template, the
still's feet on the origin, Bounds the still's width). `build_pck.ps1` copies
`ImageGen/images/furina/model/frames/*.png` and `model/guests/*.png` with
VRAM-compressed imports, switches her rest scene to `furina_rest.png` and her
select art to `ui/select_closeup.png` when they exist, and no longer ships her
layer-cut rig or the guests' flat cutouts (`tools/cut_guest_bodies.py`, which
no longer writes scenes). `char_render/pack.py` is the one producer of all of
them and of her roster tile. Never hand-edit the scenes:

```sh
.venv/Scripts/python -m tools.furina_rig gen [--check]          # write / check her two scenes and the eleven guests (no art)
```

**The edge lint (L13, `art_lint.py --edges`).** `cover` is the wrong default for
a figure. It scales the trimmed subject to FILL the plate and crops the
overflow, so whenever the figure's aspect differs from the canvas it slices the
body flat against the edge — and a contact sheet cannot show that, because a
contact sheet draws every plate inside a rectangle and the slice reads as the
frame. In the game there is no frame: the plate composites onto the arena and
the flat edge reads as the model's own silhouette ([USER] on 0.2.3674,
2026-09-17: "many of our images have weirdly clipped assets around the edge of
the image ... [that] show up as the edge of the in-game model"). L13 measures
the shipped pixels rather than the plan — for each of the four canvas edges,
the longest contiguous run at alpha ≥ 40 and the opaque fraction — and flags a
run ≥ 12px or a fraction ≥ 0.10. It reads `plan.tsv` for its rows, lints the
composite plate only (the six bespoke bosses' layers are cut from it and
inherit its geometry), and SKIPS with a note where `ImageGen/` or Pillow is
absent, so it never fails on a runner; `main()` runs it, so the local
`art-lint` lane covers it, and `--art-root` points it at the main checkout's
pixels from a worktree. 104 plate rows moved to `cut.../contain` under it;
`PENDING_EDGE_REPICK` carries the residue, where the SOURCE capture is itself
cropped and no fit can invent the missing pixels, and that set can only shrink.

**What a side/top flag actually is (measured 2026-09-17 on all 13).** A bottom
flag is the capture cutting the figure off at its feet; a SIDE or TOP flag is
two different things and only one of them is a sourcing question. On 3 of the 13
the model or its FX really does run off the capture's frame (`frostarm_lawachurl`'s
ice arm, `mirror_maiden`'s aura glow, `tainted_water_spouting_phantasm`'s left
bubble). On the other 8 the pixels touching the edge are **the Archive backdrop's
own nebula**, which the matte keys as figure where its local colour sits inside
the tolerance, and that haze reaches the capture's border — so the plate carries a
dark blob to the canvas edge and L13 reads it as a cut. Re-picking cannot fix
those: every Archive capture is shot on the same nebula. The lever is the matte
(tolerance, the blue-chroma gate, or a post-trim margin), not the source. Only an
**alpha cut-out** source escapes it — `_backdrop_alpha` returns `None` when the
border ring is already transparent and the file's own matte is kept — which is
why the two bodies with an `Enemy <name> Full Artwork.png` render
(`jadeplume_terrorshroom`, `warden_of_oasis_prime`) came back clean on all four
edges from a title change alone, with every other knob untouched.

**The nebula re-key (`;rekey=N`, `art_process.CUT_REKEY`, measured 2026-09-18).**
The nebula above was not a sourcing defect and not a tolerance the row set too
low: it is `_refine_model` keying against a backdrop estimate that is wrong in
exactly the place it matters. That pass takes as certain backdrop the pixels
"within `max(10, 0.6×tolerance)` of the QUADRATIC" — which is precisely the set
that EXCLUDES a nebula cloud, since a cloud is what a quadratic cannot follow —
so the local estimate near a cloud is averaged from the plain sky around it and
lands 36–41 RGB off the cloud's real colour against a tolerance of 30. Measured
on six captures: the survivors are backdrop-BLUE (chroma deficit +2 to +10
against a gate of 12, so the gate is NOT the leak), the border ring itself fits
at 3–4, and the cloud's FRINGE keys normally while its core does not — which is
also the fix. After the first flood the run knows 47–75% of the frame to be
backdrop, the nebula's fringe included, so `;rekey=1` re-estimates the local
backdrop from THAT set and keys again; pixels the better model explains join the
background, and where no proven backdrop is within the radius the previous model
stands, so a body cannot be eaten from the inside. It converts 1.8–6.0 points of
frame per capture, 0.03–0.8 on bodies that were already clean. **Off by default**
(`CUT_REKEY = 0`), so a row without it renders byte-identically; 112 Archive-
capture rows carry it, 105 plates moved, and 12 `PENDING_EDGE_REPICK` entries —
every one of the 11 side/top rows above plus one bottom — went clean. The six
bespoke bosses and the four alpha cut-outs are excluded, and `rekey=2` starts
eating real FX (`mirror_maiden`'s aura), so 1 is the value. Sheet:
`art/contact_sheet_matte_2026-09-18.html`.

**Art debt is said out loud (2026-10-12).** Sting, Ward and thirty other
cards drew a blank portrait, and Varka's seven relics and three potions drew
Burning Blood and the base potion, until the owner noticed in play. The cards
sat on `art_coverage.KNOWN_MISSING` (the pixel check skips on CI); the relic
and potion paths are built by helpers no string-reading gate followed. Now:
`tools/deploy_round.py` prints an `art debt:` line naming every card that
would draw blank; `test_every_shipped_key_has_planned_art_or_is_known_missing`
holds every mod art key to an effective `plan.tsv` row in CI; and
`tools/lint_relic_potion_icons.py` (CI) holds every relic and potion icon to a
`plan.tsv` out-path. A new card batch adds its plan rows in the same PR, or
its blank cards show up in every deploy summary.

To place new rows without a full `art_process` pass (which would overwrite
applied picks), render with `--assets <ids>` and promote with
`--apply-picks <a picks file naming those ids at rank 1>`, both with
`--art-root <main checkout>` from a worktree; `art_fetch.py --art-root` first.

`art/plan.tsv` is UTF-8, LF in the index (`.gitattributes` normalises) — read with `encoding="utf-8", newline=""` and
`rstrip("\r\n")`, or the last column silently stops matching. Depth:
`docs/current/art/` and `docs/current/atlas/tools.md`.
