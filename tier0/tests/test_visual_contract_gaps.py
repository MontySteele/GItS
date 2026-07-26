"""Two shipped visual contracts whose consumer was never wired.

`missed-requirements.md` sec.4.2 and sec.4.3. Both were billed, both were
written up, neither landed, and neither is visible anywhere the suite looks —
they live in a requirements doc and a sprint log, which is precisely the class
of debt that gets rediscovered by playing the game instead of by running the
tests.

CURATED KNOWN-GAP LEDGER, not an aspirational assertion. Track B is
tests-only, so these do not fix anything; what they do is make each gap
**structural**. Two properties matter and both are asserted:

  * the arithmetic that IS settled is pinned hard, so the numbers a future fix
    will be written against cannot drift out from under it while nobody is
    looking;
  * the gap itself is listed with its receipt, and the ledger fails in BOTH
    directions -- a new character that inherits the gap without an entry
    fails, and an entry that survives its own fix fails too. A known-gap list
    that can only rot toward silence is the thing it was supposed to replace.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "klee-mod" / "KleeCode"
PCK_SRC = ROOT / "klee-mod" / "pck-src"


# =========================================================================
# sec.4.2 -- the character-icon outline asset was never produced
# =========================================================================

# Every character ships an icon SCENE (CustomIconPath -> character_icon.tscn)
# whose texture is the FILL icon, and separately an outline TEXTURE path.
# art-asset-manifest.md bills "Character icon 88x88 -- 1 (+outline) -- 2":
# two assets. One was made.
ROSTER_ICONS = ["Klee", "Furina", "Kokomi"]

# id -> the reason the outline path returns the fill asset. Delete an entry
# the day that character gets a real outline; the test below then ENFORCES
# the separation for it and fails if the wiring was forgotten.
OUTLINE_IS_FILL = {
    "Klee": "art-asset-manifest.md billed 88x88 icon '+outline' = 2 assets; "
            "only the fill was ever produced. No outline row exists in "
            "art/plan.tsv or art/SOURCES.tsv.",
    "Furina": "same missing asset; rediscovered independently as "
              "animation-sprint-2-log.md Playtest 2 Finding 1.",
    "Kokomi": "same missing asset; she ships on the shared bill.",
}


def _character_source(name: str) -> str:
    return (SOURCE / f"{name}.cs").read_text(encoding="utf-8")


def _pck_path(source: str, prop: str) -> str:
    m = re.search(rf"{prop}\s*=>\s*(?:\n\s*)?KleePck\.Path\(\"([^\"]+)\"\)",
                  source)
    assert m, f"{prop} must resolve through KleePck.Path"
    return m.group(1)


PCK_BUILDER = (ROOT / "tools" / "build_pck.ps1").read_text(encoding="utf-8")


def _icon_scene_texture(character: str) -> str:
    """The FILL texture the character's icon scene actually draws.

    Two authoring channels (animation sprint 1): a git-tracked scene under
    klee-mod/pck-src/, or a heredoc inside build_pck.ps1. character_icon.tscn
    is on the heredoc channel for the whole roster today, but the lookup tries
    both so moving one to pck-src does not silently blind this test.
    """
    scene = PCK_SRC / character.lower() / "ui" / "character_icon.tscn"
    texture_re = r'ext_resource type="Texture2D" path="res://([^"]+)"'
    if scene.exists():
        m = re.search(texture_re, scene.read_text(encoding="utf-8"))
        assert m, f"{scene} declares no Texture2D"
        return m.group(1)

    # Scope to THIS scene's heredoc. Each character has several `<char>/ui/`
    # textures in the builder (select_bg, selection_splash, transition_wipe),
    # so a filename-prefix match picks up whichever happens to be written
    # first and silently compares the wrong pair.
    marker = f"{character.lower()}\\ui\\character_icon.tscn'), @'"
    assert marker in PCK_BUILDER, (
        f"no character_icon.tscn for {character} in pck-src or the "
        "build_pck.ps1 heredocs")
    heredoc = PCK_BUILDER[PCK_BUILDER.index(marker):]
    heredoc = heredoc[:heredoc.index("'@)")]
    m = re.search(texture_re, heredoc)
    assert m, f"{character}'s icon heredoc declares no Texture2D"
    return m.group(1)


@pytest.mark.parametrize("character", ROSTER_ICONS)
def test_outline_icon_is_either_distinct_or_a_listed_gap(character: str):
    """The pin the base game's two-asset icon contract deserves.

    `CustomIconOutlineTexturePath` exists because the game draws the outline
    separately from the fill. Pointing both at one PNG is not a neutral
    placeholder -- it renders the outline pass as a second copy of the fill.
    """
    outline = _pck_path(_character_source(character),
                        "CustomIconOutlineTexturePath")
    fill = _icon_scene_texture(character)

    if outline != fill:
        assert character not in OUTLINE_IS_FILL, (
            f"{character} now has a real outline asset ({outline}), but is "
            "still listed in OUTLINE_IS_FILL. Delete the entry -- a known-gap "
            "ledger that outlives its gap is how the gap comes back.")
        return

    assert character in OUTLINE_IS_FILL, (
        f"{character}.CustomIconOutlineTexturePath returns the fill icon "
        f"({fill}). That is missed-requirements sec.4.2, and a new character "
        "may not inherit it silently: either ship an outline asset or add an "
        "entry to OUTLINE_IS_FILL saying why not.")


def test_the_outline_gap_ledger_covers_the_whole_roster():
    """Guards the ledger against a character being added and forgotten."""
    assert set(OUTLINE_IS_FILL) <= set(ROSTER_ICONS), (
        "OUTLINE_IS_FILL names a character not in ROSTER_ICONS")
    for character in ROSTER_ICONS:
        assert (SOURCE / f"{character}.cs").exists()


# =========================================================================
# sec.4.3 -- the salon member sprite scale was written up and never applied
# =========================================================================

CUT_TOOL = (ROOT / "tools" / "cut_salon_members.py").read_text(encoding="utf-8")
SALON_STAGE = (PCK_SRC / "furina" / "ui" / "salon_stage.tscn").read_text(
    encoding="utf-8")
SALON_BRIDGE = (SOURCE / "Vfx" / "SalonVisualsBridge.cs").read_text(
    encoding="utf-8")

# Read from the TOOL, not from ImageGen/images/furina/salon/members.json --
# that file is gitignored Tier F output and absent on a fresh clone. Track A's
# lesson: an assertion anchored on an ungenerable artifact reports the machine.
TARGET_H = int(re.search(r"^TARGET_H\s*=\s*(\d+)", CUT_TOOL, re.M).group(1))


def _rect(node: str) -> tuple[float, float]:
    """(width, height) of a ColorRect declared in the stage scene."""
    block = SALON_STAGE[SALON_STAGE.index(f'name="{node}"'):]
    block = block[:block.index("\n[node") if "\n[node" in block else len(block)]
    vals = {k: float(v) for k, v in re.findall(
        r"offset_(left|top|right|bottom) = (-?[\d.]+)", block)}
    return vals["right"] - vals["left"], vals["bottom"] - vals["top"]


def _slot_positions() -> list[float]:
    return [float(x) for x, _ in re.findall(
        r'name="Slot\d" type="Node2D".*?position = Vector2\((-?[\d.]+), (-?[\d.]+)\)',
        SALON_STAGE, re.S)]


def test_the_stage_geometry_is_uniform_across_the_three_slots():
    """The numbers a scale fix will be written against, pinned first."""
    ghosts = [_rect(f"Ghost{i}") for i in (1, 2, 3)]
    pools = [_rect(f"Pool{i}") for i in (1, 2, 3)]
    beams = [_rect(f"Beam{i}") for i in (1, 2, 3)]
    assert len(set(ghosts)) == 1, ghosts
    assert len(set(pools)) == 1, pools
    assert len(set(beams)) == 1, beams
    # The figures missed-requirements sec.4.3 quotes, so the write-up and the
    # scene cannot drift apart without one of them being wrong out loud.
    assert ghosts[0] == (34.0, 36.0), ghosts[0]
    xs = sorted(_slot_positions())
    assert len(xs) == 3, xs
    pitch = {round(b - a) for a, b in zip(xs, xs[1:])}
    assert pitch == {62}, f"slot pitch is no longer 62px: {pitch}"


def test_shipped_sprite_height_is_exactly_twice_the_stage_slot():
    """`TARGET_H = 144` is not free-floating: it is 2x the beam, deliberately.

    The tool says so in prose -- "the stage slots are ~72 px tall in creature
    space; 2x that gives headroom for the deploy pop without resampling
    artefacts". That sentence is the ONLY statement of the intended runtime
    scale (0.5), so it is asserted here rather than trusted.
    """
    _, beam_h = _rect("Beam1")
    assert beam_h == 72.0, beam_h
    assert TARGET_H == 2 * beam_h, (
        f"TARGET_H={TARGET_H} is no longer 2x the {beam_h}px stage slot; the "
        "house rule is pre-scaled art with no runtime minification, so this "
        "ratio IS the intended Sprite2D scale and cannot move silently")


def test_the_bridge_applies_no_scale_and_that_is_a_recorded_gap():
    """missed-requirements sec.4.3, made structural instead of documentary.

    `SalonVisualsBridge` sets `Texture`, `Visible` and `Modulate` on each slot
    sprite and nothing else, so 121x144 art renders at 1:1 into a 34x36 ghost
    on a 62px pitch. The fix was supplied as a code block in
    animation-sprint-2-log.md Playtest 2 Finding 2 and never applied, which is
    why the tracked D5 capture cannot be judged: silhouette legibility is D5's
    acceptance question and the silhouettes are 4x oversized.

    This asserts the gap, and it is the assertion that must FLIP when the fix
    lands: on the day a `Scale` is set, this test fails, and closing it means
    replacing it with the arithmetic check above (scale == beam_h / TARGET_H).
    """
    sprite_writes = set(re.findall(r"\bsprite\.(\w+)\s*=", SALON_BRIDGE))
    if "Scale" in sprite_writes:
        pytest.fail(
            "SalonVisualsBridge now sets sprite.Scale -- missed-requirements "
            f"sec.4.3 is FIXED. Replace this test with the real check: the "
            f"scale must equal {_rect('Beam1')[1] / TARGET_H} "
            f"(beam {_rect('Beam1')[1]}px / TARGET_H {TARGET_H}).")
    assert sprite_writes == {"Texture", "Visible", "Modulate"}, sprite_writes
    assert "Scale" not in SALON_STAGE.split('name="Sprite1"')[1][:200], (
        "the scene now carries a Sprite scale; see the note above")
