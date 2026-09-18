## Art pipeline

Tier F art never ships and never enters the repo; only the ledgers
(`art/SOURCES.tsv`, `art/plan.tsv`) and the tools are tracked.

```sh
python3 tools/art_fetch.py && python3 tools/art_process.py [--apply-picks art/picks.tsv]
python3 tools/art_coverage.py            # CI runs it WITHOUT --strict (empty bill on a runner)
python3 tools/art_hunt.py Furina ; python3 tools/art_contact_sheet.py --list
.venv/Scripts/python tools/cut_combat_layers.py klee [--check]
.venv/Scripts/python tools/cut_combat_layers.py --all [--check|--verify]   # 8 configs
.venv/Scripts/python tools/gen_furina_stills.py    # and gen_kokomi_stills.py
.venv/Scripts/python tools/gen_char_icon_outlines.py [--check]   # all three outline halos
.venv/Scripts/python tools/gen_mod_image.py [--check]      # Mods-screen badge, EB-161
```

`cut_combat_layers.py` cuts one illustration into layers behind a hand-digitized
fence config (`tools/combat_layer_fences/<name>.yaml`; `teyvat/<body>.yaml` are
the six bespoke boss rigs, `operations/codegen.md` §Bespoke rigs). `--check`
proves the shipped pixels are what the fences say; `--verify` stacks them back
up at their manifest offsets and diffs against the source, and GATES on that
for a config declaring `recompose_exact: true` — which the six do and configs
#1/#2 never claimed. `--art-root <checkout>` lets a worktree cut against the
main tree's `ImageGen/`, which is the only supported way to reach it (never
link an asset tree into a worktree).

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

`art/plan.tsv` is UTF-8, LF in the index (`.gitattributes` normalises) — read with `encoding="utf-8", newline=""` and
`rstrip("\r\n")`, or the last column silently stops matching. Depth:
`docs/current/art/` and `docs/current/atlas/tools.md`.
