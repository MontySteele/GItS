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
    # The supporting pool (2026-09-26): Lyney and Escoffier make thirteen.
    assert len(performers) == 13, performers
    assert set(scenes) == set(performers), set(performers) ^ set(scenes)
    assert len(set(scenes.values())) == len(scenes), "two performers share a scene"
    for who, path in scenes.items():
        assert (ROOT / "klee-mod" / "pck-src" / path).is_file(), (who, path)
    # A guest the tool cuts before the card build adds its StagePerformer
    # (the supporting pool's art and cards land in parallel PRs) has its scene
    # on disk and no literal yet; once the enum names it, the set equality
    # above forces the literal and this pins its path.
    for name, who in tool.GUESTS.items():
        assert (MODEL / f"guest_{name}.tscn").is_file(), name
        if who in scenes:
            assert scenes[who] == f"furina/model/guest_{name}.tscn"
    assert 'GetScenePath("creature_visuals/osty")' in PETS, "fallback kept"


def test_the_guest_height_is_eighty_percent_of_furina():
    assert tool.furina_body_height() == tool.FURINA_BODY_H
    assert tool.TARGET_H == round(tool.GUEST_SHARE * tool.FURINA_BODY_H)


def test_every_guest_names_one_source_and_the_ledger_agrees():
    """A `game` guest is keyed through art_process's own `cut` grammar and
    cut at a sole row inside the work frame; a `wish` guest carries no sole.
    art/SOURCES.tsv names the render each sprite was actually cut from."""
    assert set(tool.SOURCES) == set(tool.GUESTS)
    tol, *_rest, rekey = tool.art_process._cut_spec(tool.GAME_CUT)
    assert (tol, rekey) == (100, 1)
    rows = dict(line.split("\t")[:2] for line in (ROOT / "art" / "SOURCES.tsv")
                .read_text(encoding="utf-8").splitlines() if "\t" in line)
    for name, (kind, sole) in tool.SOURCES.items():
        assert kind in ("game", "wish"), name
        if kind == "game":
            assert isinstance(sole, int) and 0 < sole < tool.WORK_H, name
        else:
            assert sole is None, name
        stem = "Game" if kind == "game" else "Full_Wish"
        url = rows[f"ImageGen/images/furina/salon/guest_{name}.png"]
        assert f"/Character_{tool.GUESTS[name]}_{stem}.png/" in url, (name, url)
        assert tool.source_path(ROOT, name).name == (
            f"Character_{tool.GUESTS[name]}_{stem}.png")


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


# ---- the passes after the matte, on synthetic work images ----------------

def _stance(raised: bool) -> Image.Image:
    """Two detailed 'shoes' on a 120-row frame whose last row is the sole;
    with `raised`, the left shoe ends 25 rows up and a flat 'reflection'
    fills the rows below it, as the mirror floor draws one."""
    h, w = 120, 100
    a = np.zeros((h, w, 4), np.uint8)
    rng = np.random.default_rng(7)
    for x0, bottom in ((10, 94 if raised else 119), (60, 119)):
        shoe = rng.integers(0, 255, (60, 30, 3))
        a[bottom - 59:bottom + 1, x0:x0 + 30, :3] = shoe
        a[bottom - 59:bottom + 1, x0:x0 + 30, 3] = 255
        if bottom < h - 1:                       # the flat reflection
            a[bottom + 1:, x0 - 3:x0 + 33, :3] = 60
            a[bottom + 1:, x0 - 3:x0 + 33, 3] = 255
    return Image.fromarray(a, "RGBA")


def test_a_raised_foots_reflection_is_dropped_and_a_planted_foot_kept():
    out = np.asarray(tool.drop_reflections(_stance(raised=True)))[..., 3]
    assert out[96:, 7:43].max() == 0, "reflection under the raised foot kept"
    assert out[40:95, 10:40].min() == 255, "the raised shoe itself was cut"
    assert out[60:, 60:90].min() == 255, "the planted shoe was cut"
    kept = np.asarray(tool.drop_reflections(_stance(raised=False)))[..., 3]
    assert (kept == np.asarray(_stance(raised=False))[..., 3]).all()


def test_small_islands_go_and_the_figure_stays():
    a = np.zeros((100, 100, 4), np.uint8)
    a[10:90, 30:70] = (200, 150, 120, 255)
    a[5:7, 5:7] = (255, 0, 255, 255)             # a two-by-two speck
    out = np.asarray(tool.keep_islands(Image.fromarray(a, "RGBA")))[..., 3]
    assert out[5:7, 5:7].max() == 0
    assert out[10:90, 30:70].min() == 255


def test_despill_neutralises_a_lilac_edge_but_not_saturated_blue_cloth():
    a = np.zeros((60, 60, 4), np.uint8)
    a[:, 10:50] = (40, 90, 200, 255)             # saturated blue coat
    a[:, 10:12] = (230, 225, 250, 255)           # lilac-cast white edge
    out = np.asarray(tool.despill(Image.fromarray(a, "RGBA"))).astype(int)
    edge, coat = out[30, 10], out[30, 30]
    assert edge[2] <= max(edge[0], edge[1]) + tool.SPILL_ALLOW
    assert tuple(coat[:3]) == (40, 90, 200), "blue cloth greyed"
