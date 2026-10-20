"""Derive Yae's two fallback stills from her model renders.

Yae art pass (2026-10-19). Until now both paths shipped Klee's files at Yae's
paths (build_pck.ps1 Copy-YaeFallback). Neither is drawn while her model art
is in the pack: her combat scene (yae/model/combat.tscn) and her generated
select scene (tools/yae_rig) take precedence. They are the R9 safety net,
the files the game finds if a build ships without those scenes, so they show
HER rather than Klee:

    ImageGen/images/yae/model/combat_model.png     240x280  static combat body:
                                                   frame 0 of her idle sheet,
                                                   feet on the bottom edge
    ImageGen/images/yae/ui/selection_splash.png   1920x1200 her select close-up
                                                   on the 1200-row canvas, the
                                                   60-row bands the scene's
                                                   KEEP_ASPECT_COVERED crop cuts
                                                   left empty

Unlike Varka's and Kokomi's (official portraits), the source is her model
render (tools/char_render/pack.py: the idle sheet and the close-up), so the
fallbacks match what ships. The other shell surfaces have their own producers:
the map marker tools/gen_map_markers.py, the top-bar icon gen_char_icons.py
and its halo gen_char_icon_outlines.py, the wipe gen_transition_wipe.py, the
select loop select_loop.py, the backdrop an art/plan.tsv row.

Usage: .venv/Scripts/python tools/gen_yae_stills.py [--art-root <checkout>] [--check]

--art-root reads and writes ImageGen/ under another checkout (a worktree never
links the gitignored tree in); --check re-derives in memory and fails if a
shipped file differs. A missing source is SKIPPED (exit 0), as every Tier F
generator is on a runner.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from char_stills import fit  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FRAMES = ROOT / "tools" / "char_render" / "yae_frames.json"
IDLE_REL = Path("ImageGen") / "images" / "yae" / "model" / "frames" / "yae_idle.png"
CLOSEUP_REL = Path("ImageGen") / "images" / "yae" / "ui" / "select_closeup.png"
COMBAT_REL = Path("ImageGen") / "images" / "yae" / "model" / "combat_model.png"
SPLASH_REL = Path("ImageGen") / "images" / "yae" / "ui" / "selection_splash.png"
SPLASH_BOX = (1920, 1200)


def _take(argv, flag):
    if flag not in argv:
        return None
    i = argv.index(flag)
    if i + 1 >= len(argv):
        sys.exit(f"{flag} needs a value")
    value = argv[i + 1]
    del argv[i:i + 2]
    return value


def idle_frame0(sheet: Image.Image) -> Image.Image:
    rec = json.loads(FRAMES.read_text(encoding="utf-8"))["sheets"]["idle"]
    f = rec["frames"][0]
    x, y, w, h = f["rect"]
    cell = Image.new("RGBA", tuple(rec["cell"]), (0, 0, 0, 0))
    cell.paste(sheet.crop((x, y, x + w, y + h)), tuple(f["offset"]))
    return cell


def render(base: Path) -> dict:
    out = {}
    idle = base / IDLE_REL
    if idle.exists():
        out[COMBAT_REL] = fit(idle_frame0(Image.open(idle).convert("RGBA")), 240, 280)
    closeup = base / CLOSEUP_REL
    if closeup.exists():
        im = Image.open(closeup).convert("RGBA")
        splash = Image.new("RGBA", SPLASH_BOX, (0, 0, 0, 0))
        splash.alpha_composite(im, (0, (SPLASH_BOX[1] - im.height) // 2))
        out[SPLASH_REL] = splash
    return out


def main(argv):
    argv = list(argv)
    art_root = _take(argv, "--art-root")
    base = Path(art_root).resolve() if art_root else ROOT
    check = "--check" in argv
    images = render(base)
    if not images:
        print(f"SKIPPED: no Yae model renders under {base}")
        return 0
    stale = []
    for rel, img in images.items():
        path = base / rel
        if check:
            if not path.exists():
                stale.append(f"{rel.as_posix()} does not exist")
            elif Image.open(path).convert("RGBA").tobytes() != img.tobytes():
                stale.append(f"{rel.as_posix()} differs from a fresh derivation")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path)
        print(f"  {rel.as_posix()}  {img.width}x{img.height}")
    for s in stale:
        print("STALE: " + s, file=sys.stderr)
    if check and not stale:
        print("gen_yae_stills --check: OK")
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
