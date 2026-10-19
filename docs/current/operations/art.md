## Art pipeline

Tier F art never enters the repo. It may ship in a free public build
(`LAW.md`, amended 2026-10-12); only the ledgers (`art/SOURCES.tsv`,
`art/plan.tsv`) and the tools are tracked. Depth: `docs/current/art/` and
`docs/current/atlas/tools.md`; each tool's docstring has its outputs and flags.

```sh
python3 tools/art_fetch.py && python3 tools/art_process.py [--apply-picks art/picks.tsv]
python3 tools/art_coverage.py            # CI runs it WITHOUT --strict (empty bill on a runner)
python3 tools/art_hunt.py Furina ; python3 tools/art_contact_sheet.py --list
.venv/Scripts/python tools/cut_combat_layers.py klee [--check]
.venv/Scripts/python tools/cut_combat_layers.py --all [--check|--verify]   # 10 configs
.venv/Scripts/python tools/gen_furina_stills.py    # and gen_kokomi_stills.py
.venv/Scripts/python tools/gen_char_icons.py [--chars klee,varka,kokomi,furina] [--art-root <checkout>] [--out-root <dir>] [--check]   # top-bar icons, 85x85 like the base cast
.venv/Scripts/python tools/gen_char_icon_outlines.py [--check]   # every outline halo, after gen_char_icons
.venv/Scripts/python tools/gen_mod_image.py [--check]      # Mods-screen badge, EB-161
.venv/Scripts/python tools/gen_multiplayer_hands.py [--check] [--art-root <checkout>]   # co-op treasure hands, from the game pck
```

Rules that hold across the pipeline:

- **`ImageGen/` lives only in the main checkout.** From a worktree, pass
  `--art-root <main checkout>`; never link an asset tree in
  (`operations/worktrees.md`).
- **One producer per out-path** (`art_lint.GENERATOR_OWNED`). The model
  pipelines' `pack.py` own their frames, stills, select art and roster tiles.
- **The character models never enter the repo or `ImageGen/`** (their terms
  forbid redistribution); only the renders do. Renders, contact sheets and
  GIFs go to a scratch dir and are never committed.
- **Generated scenes are never hand-edited.** Every `pck-src/<char>/model/combat.tscn`
  and `merchant_character.tscn` comes from its `tools/<char>_rig/` generator
  and a committed frames manifest; edit the yaml or the manifest and run `gen`.
- `build_pck.ps1` copies each kit's frames with VRAM-compressed `.import`s
  and switches its rest and select art to the rendered files when they exist.
- **New cards bring their art rows.** `tools/deploy_round.py` prints an
  `art debt:` line naming every card that would draw blank;
  `test_every_shipped_key_has_planned_art_or_is_known_missing` holds every
  art key to a `plan.tsv` row and `tools/lint_relic_potion_icons.py` every
  relic and potion icon (both CI). A new card batch adds its plan rows in the
  same PR.
- **To place new rows without a full `art_process` pass** (which overwrites
  applied picks): render with `--assets <ids>` and promote with
  `--apply-picks <a picks file naming those ids at rank 1>`, both with
  `--art-root <main checkout>` from a worktree; `art_fetch.py --art-root`
  first.
- **`art/plan.tsv` is UTF-8, LF in the index** (`.gitattributes` normalises):
  read it with `encoding="utf-8", newline=""` and `rstrip("\r\n")`, or the
  last column silently stops matching.

### Layer cuts (`cut_combat_layers.py`)

One illustration cut into layers by a hand-digitized fence config
(`tools/combat_layer_fences/<name>.yaml`; `teyvat/<body>.yaml` are the six
bespoke boss rigs). `--check` proves the shipped pixels are what the fences
say; `--verify` restacks them and gates on an exact match for a config with
`recompose_exact: true` (the six bosses). Fence coordinates are in the
prepared canvas (after `source_crop` / `source_scale` / `source_pad`).
Kokomi, Klee, Varka and Furina no longer ship layer cuts (their scenes are
drawn from their models); Klee's Dodoco (`pck-src/klee/vfx/dodoco_pop.tscn`)
still does.

### Klee (`tools/klee_rig/`, `tools/klee_render/`)

Edit `tools/klee_rig/klee.yaml` (which sheet each state plays, its tint keys)
and regenerate. `tools/klee_rig/klee_frames.json` is the only art-derived
input, so `gen` and `tier0/tests/test_klee_rig.py` run anywhere.

```sh
.venv/Scripts/python -m tools.klee_rig gen [--check]            # write / check combat.tscn (no art)
.venv/Scripts/python -m tools.klee_rig verify --art-root <main checkout> [--godot]   # --godot steps the AnimationTree headless
.venv/Scripts/python -m tools.klee_rig render --art-root <main checkout> --out <scratch dir>   # contact sheet + GIF per state
.venv/Scripts/python tools/klee_render/build.py --pmx <scratch>/可莉2.0.pmx --work <scratch dir> --art-root <main checkout>
.venv/Scripts/python tools/klee_render/pack.py --renders <scratch dir> --art-root <main checkout> [--check]
```

### The other kits (`tools/char_render/`, `tools/<char>_rig/`)

The same pipeline for a kit whose `chars.py` entry names a pose library
(`<char>_clips.py`). `toon.py` is the one Blender STYLE both renderers share.
Visual papers: `review/active/varka-visual-paper-2026-10-13.md`,
`review/active/furina-visual-paper-2026-10-13.md`.

```sh
.venv/Scripts/python tools/char_render/build.py --char varka|furina|kokomi|yae --models <scratch>/models --work <scratch dir> --art-root <scratch art root>
.venv/Scripts/python tools/char_render/pack.py --char <char> --renders <scratch dir> --art-root <dir> [--check]
# review the sheets; copy <scratch art root>/ImageGen/images/<char> into the main checkout's ImageGen
.venv/Scripts/python -m tools.<char>_rig gen [--check]           # both scenes from <char>_frames.json (no art)
```

- Varka's and Furina's element layers share one shader tinted by
  `KleeMod.Vfx.ElementTrail` (the played card's element; Furina rests at
  Hydro). `tools.furina_rig gen` also writes her eleven `guest_<name>.tscn` and
  `guest_fx_<name>.tscn`.
- Furina's guest effects need no render (`review/active/furina-guest-fx-2026-10-16.md`):

  ```sh
  .venv/Scripts/python tools/char_render/pack.py --char furina --guest-fx-only --art-root <main checkout> [--check]
  .venv/Scripts/python tools/char_render/pack.py --char furina --guest-fx-sheet <scratch>/sheet.png
  .venv/Scripts/python tools/char_render/pack.py --char furina --stage-fx-only [spend drain repay] --art-root <main checkout> [--check]   # her stage effects, likewise
  ```

- Kokomi's skin layers 手 and 肌 are her `alpha_mats` and must render
  BLENDED: under DITHERED the toon ramp draws every cut texel opaque black.
- Yae's model is temporary; `Yae.cs` loads `yae/model/combat.tscn` first and
  falls back to Klee's borrowed still only where her file is missing.

### Character-select idle loops (`tools/select_loop.py`)

Klee, Varka, Furina and Kokomi play a rendered loop of the close-up; manifest
`tools/select_loop.json`. A character with no entry gets `tools/select_bg.py`'s
breathing still. Yae waits for her model to settle.

```sh
.venv/Scripts/python tools/select_loop.py build --char klee --pmx <klee pmx> --work <scratch dir> --art-root <main checkout>
.venv/Scripts/python tools/select_loop.py build --char varka|furina|kokomi --models <scratch>/models --work <scratch dir> --art-root <main checkout>
.venv/Scripts/python -m tools.<char>_rig gen     # the scene reads the manifest
```

### Enemy plates: the edge lint and the re-key

- **L13 (`art_lint.py --edges`)** flags a plate whose figure runs flat into a
  canvas edge (a run of 12 px or an opaque fraction of 0.10 at alpha 40),
  because in game that edge reads as the model's silhouette. It skips where
  `ImageGen/` or Pillow is absent; `--art-root` points it at the main
  checkout. `cover` is the wrong fit for a figure: it slices the body flat
  against the edge, which a contact sheet cannot show.
  `PENDING_EDGE_REPICK` holds plates whose source capture is itself cropped;
  it can only shrink.
- **`;rekey=1`** (`art_process.CUT_REKEY`, off by default) re-keys an Archive
  capture against the proven backdrop to remove the nebula halo; `rekey=2`
  eats real FX, so 1 is the value. Why and the measurements: the comment at
  `CUT_REKEY` in `tools/art_process.py`.
