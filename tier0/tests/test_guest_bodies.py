"""The eight Guest Stars' stage bodies (tools/cut_guest_bodies.py).

The scenes are git-tracked and the sprites are gitignored Tier F, so these
tests read the tool, the scenes and the C#, and build their own synthetic
render for the cut; none of them needs art on disk.
"""

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

np = pytest.importorskip("numpy")
pytest.importorskip("PIL")
from PIL import Image  # noqa: E402

import cut_guest_bodies as tool  # noqa: E402

MODEL = ROOT / "klee-mod" / "pck-src" / "furina" / "model"
PROTO = ROOT / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
PETS = (PROTO / "FurinaStagePets.cs").read_text(encoding="utf-8")
STAGE = (PROTO / "FurinaStage.cs").read_text(encoding="utf-8")


def _performers() -> list[str]:
    body = STAGE[STAGE.index("public enum StagePerformer"):]
    body = body[body.index("{") + 1:body.index("}")]
    body = re.sub(r"//[^\n]*", "", body)
    return [m for m in re.findall(r"\b([A-Z][A-Za-z]+)\b", body)]


def _scene_map() -> dict[str, str]:
    """StagePerformer -> the literal scene path ModVisualsPathFor names."""
    fn = PETS[PETS.index("ModVisualsPathFor(StagePerformer who)"):]
    fn = fn[:fn.index("};")]
    return dict(re.findall(
        r'StagePerformer\.(\w+)\s*=>\s*KleePck\.Path\("([^"]+)"\)', fn))


def _bounds(text: str) -> dict[str, float]:
    block = text[text.index('[node name="Bounds"'):]
    return {k: float(v) for k, v in re.findall(
        r"^offset_(left|top|right|bottom) = (-?[\d.]+)$", block, re.M)}


def test_every_performer_has_its_own_literal_scene():
    """No performer falls through to the Osty rig, and every literal names a
    scene the pack-src overlay carries (the deploy's S12 check refuses one it
    cannot find)."""
    scenes = _scene_map()
    performers = _performers()
    assert len(performers) == 11, performers
    assert set(scenes) == set(performers), set(performers) ^ set(scenes)
    assert len(set(scenes.values())) == len(scenes), "two performers share a scene"
    for who, path in scenes.items():
        assert (ROOT / "klee-mod" / "pck-src" / path).is_file(), (who, path)
    for name in tool.GUESTS:
        assert scenes[tool.GUESTS[name]] == f"furina/model/guest_{name}.tscn"
    assert 'GetScenePath("creature_visuals/osty")' in PETS, "fallback kept"


def test_the_guest_height_is_eighty_percent_of_furina():
    assert tool.furina_body_height() == tool.FURINA_BODY_H
    assert tool.TARGET_H == round(tool.GUEST_SHARE * tool.FURINA_BODY_H)


@pytest.mark.parametrize("name", list(tool.GUESTS))
def test_each_guest_scene_is_the_tools_template(name):
    """The committed scene is exactly what the tool writes for a sprite of
    the Bounds' size: texture, Rig at half the height, Bounds the sprite."""
    text = (MODEL / f"guest_{name}.tscn").read_text(encoding="utf-8")
    b = _bounds(text)
    w, h = round(b["right"] - b["left"]), round(b["bottom"] - b["top"])
    assert h == tool.TARGET_H
    assert b["left"] == -b["right"]
    assert f'path="res://furina/salon/guest_{name}.png"' in text
    assert f"position = Vector2(0, {-h // 2})" in text
    assert text == tool.scene_text(name, w, h)


def test_the_template_keeps_the_trios_animation_shape():
    """Scaled from usher.tscn: at the trio's own height the template
    reproduces usher's animation keys exactly."""
    usher = (MODEL / "usher.tscn").read_text(encoding="utf-8")
    ours = tool.scene_text("usher", 121, tool.TRIO_H)
    keys = re.compile(r'^"values": \[.*\]$', re.M)
    assert keys.findall(ours) == keys.findall(usher)


def test_the_cut_keeps_the_whole_alpha_box_and_leaves_no_fringe():
    """Synthetic render: a figure plus a faint haze and a coloured,
    fully transparent surround. The crop is the figure's box, the height is
    TARGET_H, and no transparent pixel carries colour."""
    src = np.zeros((400, 300, 4), np.uint8)
    src[..., :3] = (255, 0, 255)          # colour under alpha 0: must not bleed
    yy, xx = np.mgrid[:400, :300]
    disc = (yy - 250) ** 2 + (xx - 150) ** 2 < 100 ** 2   # box 200 x 200
    src[disc] = (40, 90, 200, 255)
    src[10:20, 10:20, 3] = tool.BBOX_ALPHA - 1   # haze below the bbox cut
    out = tool.cut_one(Image.fromarray(src, "RGBA"))
    assert out.height == tool.TARGET_H
    assert abs(out.width - tool.TARGET_H) <= 1   # the disc's box, not the haze
    arr = np.asarray(out)
    clear = arr[..., 3] == 0
    assert (arr[clear][:, :3] == 0).all()
    assert (arr[..., 3] < tool.ALPHA_FLOOR).sum() == clear.sum()
    edge = arr[arr[..., 3] > 0]
    # Premultiplied resampling: the magenta under alpha 0 never reaches a
    # visible pixel, so red stays near the figure's own 40 (48 measured). A
    # straight per-channel resample of the same crop reaches 248.
    assert edge[:, 0].max() < 80
